import type { EngineInterface, Register } from 'claude-code'

import { CENAS } from './cenas'
import type { Cena } from './cenas'

const PLUGIN = 'pixel-temas'
// O tema escolhido vale para todas as sessões, até alguém trocar ou tirar.
const CHAVE = 'escolha'

const TIPOS: Array<[Cena['tipo'], string]> = [
  ['estatico', 'Estáticos'],
  ['animado', 'Animados'],
  ['zoeira', 'Zoeira'],
  ['gif', 'GIFs'],
]

function normalizar(texto: string): string {
  return texto
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

function achar(nome: string): Cena | undefined {
  const alvo = normalizar(nome)

  return CENAS.find(c => c.id === alvo || normalizar(c.titulo) === alvo)
}

function lista(): string {
  const grupos = TIPOS.map(([tipo, rotulo]) => {
    const deste = CENAS.filter(c => c.tipo === tipo)

    if (deste.length === 0) {
      return undefined
    }

    const nomes = deste.map(c => `${c.id} (${c.janela === 'dark' ? 'escuro' : 'claro'})`).join(', ')

    return `${rotulo}: ${nomes}`
  })

  return [...grupos.filter(g => g !== undefined), 'Use /pixel <nome>, /pixel aleatorio ou /pixel off.'].join('\n')
}

async function aplicar($: EngineInterface, cena: Cena): Promise<string | undefined> {
  const set = await $.theme.set({
    backdrop: { scene: cena.id, glass: cena.vidro },
    overrideColorScheme: cena.janela,
  })

  return set.isDrawn ? undefined : set.reason
}

// O tema que esta sessão pôs por último. Cada sessão tem o seu; a escolha guardada é uma só para todas.
let aplicado: string | undefined

/**
 * Põe nesta sessão o tema guardado, se ele mudou desde a última vez. Roda ao abrir a sessão e a cada
 * turno, então uma troca feita em outra sessão chega aqui na próxima mensagem.
 */
async function sincronizar($: EngineInterface): Promise<void> {
  const escolha = await $.store.get(CHAVE)
  const cena = typeof escolha === 'string' ? achar(escolha) : undefined

  if (cena?.id === aplicado) {
    return
  }

  if (cena !== undefined) {
    await aplicar($, cena)
  } else if (aplicado !== undefined) {
    // Só tira o tema que esta sessão mesma pôs, para não apagar o de outro plugin.
    await $.theme.clear()
  }

  aplicado = cena?.id
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'pixel',
      description: 'Temas em pixel art: lista, aplica (/pixel <nome>) ou tira (/pixel off)',
      argumentHint: '[nome | aleatorio | off]',
    })
    await sincronizar($)

    return next(e)
  })

  on('turn.start', async ($, e, next) => {
    await sincronizar($)

    return next(e)
  })

  on('command.run', { command: 'pixel' }, async ($, e) => {
    const pedido = e.args.trim()

    if (pedido === '' || pedido === 'lista' || pedido === 'list') {
      return { text: lista() }
    }

    if (pedido === 'off') {
      await $.store.delete(CHAVE)
      await $.theme.clear()
      aplicado = undefined

      return { text: 'Tema tirado em todas as sessões.' }
    }

    const cena =
      pedido === 'aleatorio' || pedido === 'aleatório'
        ? CENAS[Math.floor(Math.random() * CENAS.length)]
        : achar(pedido)

    if (cena === undefined) {
      return { text: `Não achei "${pedido}".\n${lista()}` }
    }

    await $.store.set(CHAVE, cena.id)
    const motivo = await aplicar($, cena)
    aplicado = cena.id
    const janela = cena.janela === 'dark' ? 'janela escura' : 'janela clara'

    if (motivo !== undefined) {
      return { text: `${cena.titulo} salvo (${janela}), mas esta janela não desenhou: ${motivo}` }
    }

    return { text: `${cena.titulo} aplicado (${janela}). As outras sessões trocam na próxima mensagem.` }
  })

  on('ui.render', { component: 'Backdrop' }, ($, e, next) => {
    if (e.props.plugin !== PLUGIN || (e.surface !== 'desktop' && e.surface !== 'mobile')) {
      return next(e)
    }

    const cena = CENAS.find(c => c.id === e.props.scene)

    if (cena === undefined) {
      return next(e)
    }

    const { Svg } = $.ui.resolve(e)

    return <Svg source={cena.svg} alt={cena.alt} isInteractive />
  })
}
