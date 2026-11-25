import { expect, test } from 'claude-code/testing'
import type { CommandRunInput, On, TurnStartInput } from 'claude-code'

/** A chamada do comando, do jeito que a pessoa digita `/pixel <args>`. */
function pixel(args: string): CommandRunInput {
  return { command: 'pixel', args } as CommandRunInput
}

/** O mundo embaixo do plugin: um armazenamento de mentira e uma janela que desenha temas. */
function mundo(on: On, guardado: Record<string, unknown> = {}): { temas: Array<unknown>; guardado: Record<string, unknown> } {
  const temas: Array<unknown> = []
  on('store.get', (_, e) => ({ value: guardado[e.key] }))
  on('store.set', (_, e) => {
    guardado[e.key] = e.value

    return { value: undefined }
  })
  on('store.delete', (_, e) => {
    delete guardado[e.key]

    return { value: undefined }
  })
  on('theme.set', (_, e) => {
    temas.push(e)

    return { value: { isDrawn: true, requestId: 'fundo-1' } }
  })
  on('theme.clear', () => ({ value: { isDrawn: false, reason: 'tirado' } }))

  return { temas, guardado }
}

test('/pixel sem nada lista os temas por tipo', async ($, on) => {
  mundo(on)
  const { text } = await $.command.run(pixel(''))

  expect(text).toContain('Estáticos: synthwave (escuro)')
  expect(text).toContain('Animados:')
  expect(text).toContain('Zoeira:')
})

test('/pixel <nome> salva a escolha e põe a cena no fundo', async ($, on) => {
  const { temas, guardado } = mundo(on)
  const { text } = await $.command.run(pixel('Cidade à Noite'))

  expect(text).toContain('Cidade à Noite aplicado (janela escura).')
  expect(guardado.escolha).toBe('cidade')
  expect(JSON.stringify(temas)).toContain('"scene":"cidade"')

  const fundo = await $.ui.mount({
    plugin: 'pixel-temas',
    surface: 'desktop',
    component: 'Backdrop',
    props: { scene: 'cidade', plugin: 'pixel-temas', glass: false },
  })

  expect(await fundo.find({ type: 'Svg' })).toBeDefined()
  await fundo.unmount()
})

test('nome desconhecido não troca a escolha', async ($, on) => {
  const { guardado } = mundo(on, { escolha: 'praia' })
  const { text } = await $.command.run(pixel('nao-existe'))

  expect(text).toContain('Não achei')
  expect(guardado.escolha).toBe('praia')
})

test('/pixel off apaga a escolha', async ($, on) => {
  const { guardado } = mundo(on, { escolha: 'praia' })
  await $.command.run(pixel('off'))

  expect(guardado.escolha).toBeUndefined()
})

test('uma troca feita em outra sessão chega aqui no próximo turno', async ($, on) => {
  const { temas, guardado } = mundo(on)
  on('turn.start', (_, e) => ({ turnId: e.turnId }))

  await $.command.run(pixel('praia'))
  guardado.escolha = 'cidade' // outra sessão escolheu a cidade
  await $.turn.start({ text: 'oi', turnId: 't-1' } as TurnStartInput)

  expect(JSON.stringify(temas.at(-1))).toContain('"scene":"cidade"')

  const antes = temas.length
  await $.turn.start({ text: 'oi de novo', turnId: 't-2' } as TurnStartInput)
  expect(temas.length).toBe(antes) // sem mudança, não põe o tema de novo
})
