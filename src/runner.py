
import os
import time

from main import (
    organizaPedidosCorredores, gerarSaida,
    calcularDemanda, verificaEstoqueDisponivel,
    criaGrafo, executaWave,
)
from src.abordagem_dicionario import (
    melhorPedidoInicialDicionario,
    calcularMelhorPedidoDicionario,
    setCoverGulosoDicionario,
)
from src.abordagem_grafo import (
    melhorPedidoInicialGrafo,
    calcularItemMaisFrequente,
    calcularMelhorPedidoGrafo,
    setCoverGulosoGrafo,
)

#define os tres tipos de abordagem que temos
NOMES_ABORDAGENS = ['dicionario_pedido', 'grafo_pedido', 'grafo_item']


#rediriciona para calculaPedidoInicial  conforme abordagem utilizada
def calculaPedidoInicial(nomeAbordagem, pedidosValidos, corredores, grafo):
    if nomeAbordagem == 'dicionario_pedido':
        pedidoId = melhorPedidoInicialDicionario(pedidosValidos, corredores)
        melhoresPedidos = [pedidoId]

    elif nomeAbordagem == 'grafo_pedido':
        pedidoId = melhorPedidoInicialGrafo(grafo, pedidosValidos)
        melhoresPedidos = [pedidoId]

    elif nomeAbordagem == 'grafo_item':
        itemMaisFrequente = calcularItemMaisFrequente(grafo, pedidosValidos)
        melhoresPedidos = [
            pedidoId for pedidoId in pedidosValidos
            if itemMaisFrequente in pedidosValidos[pedidoId]
        ]

    else:
        raise ValueError(f"abordagem desconhecida: {nomeAbordagem}")

    quantidadePedidos = sum(
        sum(pedidosValidos[pedidoId].values()) for pedidoId in melhoresPedidos
    )
    return melhoresPedidos, quantidadePedidos

#rediriciona para calcularMelhorPedido conforme abordagem utilizada
def calculaMelhorPedido(nomeAbordagem, corredores, grafo,
                         pedidosValidos, pedidosSelecionados, corredoresAtivos,
                         maxWave, unidadesAtuais):
    if nomeAbordagem == 'dicionario_pedido':
        return calcularMelhorPedidoDicionario(
            pedidosValidos, pedidosSelecionados, corredores, corredoresAtivos, maxWave, unidadesAtuais
        )

    elif nomeAbordagem in ('grafo_pedido', 'grafo_item'):
        return calcularMelhorPedidoGrafo(
            grafo, pedidosValidos, pedidosSelecionados, corredoresAtivos, maxWave, unidadesAtuais
        )

    else:
        raise ValueError(f"abordagem desconhecida: {nomeAbordagem}")

# redireciona para  setCover conforme a abordagem
def calculaSetCover(nomeAbordagem, corredores, grafo, demanda):
    if nomeAbordagem == 'dicionario_pedido':
        return setCoverGulosoDicionario(demanda, corredores)

    elif nomeAbordagem in ('grafo_pedido', 'grafo_item'):
        return setCoverGulosoGrafo(grafo, demanda)

    else:
        raise ValueError(f"abordagem desconhecida: {nomeAbordagem}")


# Valida se a solução respeita waveMin, waveMax e estoque
def validaSolucao(pedidosValidos, corredores, melhoresPedidos, melhoresCorredores, waveMin, waveMax):
    wave = sum(sum(pedidosValidos[p].values()) for p in melhoresPedidos)

    if wave < waveMin or wave > waveMax:
        return False, "wave fora dos limites", wave

    demandaFinal = calcularDemanda(pedidosValidos, melhoresPedidos)
    estoqueTotal = {}
    for corredorId in melhoresCorredores:
        for itemId, qtd in corredores[corredorId].items():
            estoqueTotal[itemId] = estoqueTotal.get(itemId, 0) + qtd

    for itemId, qtdNecessaria in demandaFinal.items():
        if estoqueTotal.get(itemId, 0) < qtdNecessaria:
            return False, "estoque insuficiente", wave

    return True, None, wave

# Responsável por executar uma abordagem específica numa instância
# Mede o tempo, chama executaWave e valida o resultado
def rodaAbordagem(nomeAbordagem, pedidos, corredores, grafo, pedidosValidos,
                   waveMin, waveMax, indiceInstancia):
    tempoInicio = time.perf_counter()

    melhoresPedidos, quantidadePedidos = calculaPedidoInicial(
        nomeAbordagem, pedidosValidos, corredores, grafo
    )

    if not melhoresPedidos:
        tempoExecucao = time.perf_counter() - tempoInicio
        print(f"Instância {indiceInstancia:04d} [{nomeAbordagem}] inviável | tempo={tempoExecucao:.4f}s")
        return

    def melhorPedido(pv, ps, ca, mw, ua):
        return calculaMelhorPedido(nomeAbordagem, corredores, grafo, pv, ps, ca, mw, ua)

    def setCover(demanda):
        return calculaSetCover(nomeAbordagem, corredores, grafo, demanda)

    resultado = executaWave(
        pedidos, corredores, pedidosValidos, waveMin, waveMax,
        melhoresPedidos, quantidadePedidos,
        melhorPedido, setCover
    )
    melhoresPedidos, melhoresCorredores, objetivoAtual = resultado
    tempoExecucao = time.perf_counter() - tempoInicio

    if melhoresPedidos is None:
        print(f"Instância {indiceInstancia:04d} [{nomeAbordagem}] inviável | tempo={tempoExecucao:.4f}s")
        return

    valido, motivo, wave = validaSolucao(
        pedidosValidos, corredores, melhoresPedidos, melhoresCorredores, waveMin, waveMax
    )
    if not valido:
        print(f"Instância {indiceInstancia:04d} [{nomeAbordagem}] inviável - {motivo} | tempo={tempoExecucao:.4f}s")
        return

    nomeSaida = f"saidas/saida_{indiceInstancia:04d}_{nomeAbordagem}.txt"
    print(
        f"Instância {indiceInstancia:04d} [{nomeAbordagem}] | unidades={wave} | "
        f"corredores={len(melhoresCorredores)} | objetivo={objetivoAtual:.2f} | "
        f"tempo={tempoExecucao:.4f}s"
    )
    gerarSaida(melhoresPedidos, melhoresCorredores, filename=nomeSaida)



#Executa as instancia e começa a marcar o tempo total.
def rodaInstancias(indices):
    tempoTotalInicio = time.perf_counter()

    for indiceInstancia in indices:
        nomeArquivo = f"data/instance_{indiceInstancia:04d}.txt"
        if not os.path.exists(nomeArquivo):
            continue

        os.makedirs("saidas", exist_ok=True)

        pedidos, corredores, waveMin, waveMax = organizaPedidosCorredores(nomeArquivo)
        waveMin = int(waveMin)
        waveMax = int(waveMax)

        pedidosValidos = {}
        for pedidoId, items in pedidos.items():
            unidadesPedido = sum(items.values())
            if unidadesPedido <= waveMax and verificaEstoqueDisponivel(items, corredores):
                pedidosValidos[pedidoId] = items

        if not pedidosValidos:
            print(f"Instância {indiceInstancia:04d} inviável")
            continue

        grafo = criaGrafo(pedidos, corredores)

        for nomeAbordagem in NOMES_ABORDAGENS:
            rodaAbordagem(
                nomeAbordagem, pedidos, corredores, grafo, pedidosValidos,
                waveMin, waveMax, indiceInstancia
            )

    tempoTotalExecucao = time.perf_counter() - tempoTotalInicio
    print(f"\nTempo total de execução: {tempoTotalExecucao:.4f}s")
