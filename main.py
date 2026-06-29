import sys

import networkx as nx


def organizaPedidosCorredores(filename):
    with open(filename, 'r') as f:
        linhas = f.readlines()

    primeiraLinha = list(map(int, linhas[0].split()))
    quantidadePedidos = primeiraLinha[0]
    quantidadeCorredor = primeiraLinha[2]

    pedidos = {}
    corredores = {}

    for i in range(quantidadePedidos):
        capturaItem = linhas[i + 1].split()
        numeros = []
        for j in capturaItem:
            numeros.append(int(j))
        items = {}
        k = 1
        while k < len(numeros):
            items[numeros[k]] = numeros[k + 1]
            k += 2
        pedidos[i] = items

    for i in range(quantidadeCorredor):
        capturaItem = linhas[1 + quantidadePedidos + i].split()
        numeros = []
        for j in capturaItem:
            numeros.append(int(j))
        items = {}
        k = 1
        while k < len(numeros):
            items[numeros[k]] = numeros[k + 1]
            k += 2
        corredores[i] = items

    ultimaLinha = linhas[-1].split()
    return pedidos, corredores, ultimaLinha[0], ultimaLinha[1]


def gerarSaida(pedidosSelecionados, corredoresAtivos, filename="saida.txt"):
    with open(filename, 'w') as f:
        f.write(f"{len(pedidosSelecionados)}\n")
        for pedidoId in pedidosSelecionados:
            f.write(f"{pedidoId}\n")
        f.write(f"{len(corredoresAtivos)}\n")
        for corredorId in corredoresAtivos:
            f.write(f"{corredorId}\n")



def calcularDemanda(pedidos, pedidosSelecionados):
    demanda = {}
    for pedidoId in pedidosSelecionados:
        for itemId, qtd in pedidos[pedidoId].items():
            demanda[itemId] = demanda.get(itemId, 0) + qtd
    return demanda


def verificaEstoqueDisponivel(demanda, corredores):
    for itemId, qtdNecessaria in demanda.items():
        totalEstoque = 0
        for corredorId, items in corredores.items():
            if itemId in items:
                totalEstoque += items[itemId]
        if totalEstoque < qtdNecessaria:
            return False
    return True



def criaGrafo(pedidos, corredores):
    G = nx.DiGraph()
    for pedidoId, items in pedidos.items():
        G.add_node(('p', pedidoId), camada='pedido')
        for itemId, qtd in items.items():
            G.add_node(('i', itemId), camada='item')
            G.add_edge(('p', pedidoId), ('i', itemId), peso=qtd)
    for corredorId, items in corredores.items():
        G.add_node(('c', corredorId), camada='corredor')
        for itemId, qtd in items.items():
            G.add_node(('i', itemId), camada='item')
            G.add_edge(('i', itemId), ('c', corredorId), peso=qtd)
    return G


def executaWave(pedidos, corredores, pedidosValidos, waveMin, waveMax,
                 melhoresPedidos, quantidadePedidos,
                 fnMelhorPedido, fnSetCover):

    demanda = calcularDemanda(pedidos, melhoresPedidos)
    melhoresCorredores = fnSetCover(demanda)

    if len(melhoresCorredores) == 0:
        return None, None, None

    wave = quantidadePedidos
    objetivoAtual = wave / len(melhoresCorredores)

    while wave < waveMax:
        proximoMelhorPedido = fnMelhorPedido(
            pedidosValidos, melhoresPedidos, melhoresCorredores, waveMax, wave
        )
        if proximoMelhorPedido is None:
            break
        novaWave = wave + sum(pedidosValidos[proximoMelhorPedido].values())
        if novaWave > waveMax:
            break
        novaDemanda = calcularDemanda(pedidosValidos, melhoresPedidos + [proximoMelhorPedido])
        if not verificaEstoqueDisponivel(novaDemanda, corredores):
            break
        novosCorredores = fnSetCover(novaDemanda)
        if len(novosCorredores) == 0:
            break
        novoObjetivo = novaWave / len(novosCorredores)
        if novoObjetivo >= objetivoAtual or wave < waveMin:
            melhoresPedidos.append(proximoMelhorPedido)
            wave = novaWave
            melhoresCorredores = novosCorredores
            objetivoAtual = novoObjetivo
        else:
            break

    while wave < waveMin:
        adicionou = False
        for pedidoId in pedidosValidos:
            if pedidoId in melhoresPedidos:
                continue
            novaWave = wave + sum(pedidosValidos[pedidoId].values())
            if novaWave > waveMax:
                continue
            novaDemanda = calcularDemanda(pedidosValidos, melhoresPedidos + [pedidoId])
            if not verificaEstoqueDisponivel(novaDemanda, corredores):
                continue
            novosCorredores = fnSetCover(novaDemanda)
            if len(novosCorredores) == 0:
                continue
            melhoresPedidos.append(pedidoId)
            wave = novaWave
            melhoresCorredores = novosCorredores
            adicionou = True
            break
        if not adicionou:
            break

    return melhoresPedidos, melhoresCorredores, objetivoAtual



if __name__ == "__main__":
    from src.runner import rodaInstancias

    if len(sys.argv) > 1:
        instancias = [int(arg) for arg in sys.argv[1:]]
    else:
        instancias = list(range(1, 21))

    rodaInstancias(instancias)
