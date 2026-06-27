import os

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


def calcularItemsFrequentes(pedidos):
    frequencia = {}
    for pedidoId, items in pedidos.items():
        for itemId in items:
            if itemId in frequencia:
                frequencia[itemId] += 1
            else:
                frequencia[itemId] = 1
    return sorted(frequencia.items(), key=lambda x: x[1], reverse=True)


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


def setCoverGuloso(demanda, corredores):
    melhoresCorredores = []
    itemsRestantes = demanda.copy()
    estoqueAcumulado = {}

    while itemsRestantes:
        melhorCorredor = None
        melhorContribuicao = 0

        for corredorId, items in corredores.items():
            if corredorId in melhoresCorredores:
                continue
            contribuicao = 0
            for itemId, qtd in itemsRestantes.items():
                if itemId in items:
                    falta = max(0, qtd - estoqueAcumulado.get(itemId, 0))
                    contribuicao += min(items[itemId], falta)
            if contribuicao > melhorContribuicao:
                melhorCorredor = corredorId
                melhorContribuicao = contribuicao

        if melhorCorredor is None:
            break

        for itemId, qtd in corredores[melhorCorredor].items():
            estoqueAcumulado[itemId] = estoqueAcumulado.get(itemId, 0) + qtd

        for itemId in list(itemsRestantes):
            if estoqueAcumulado.get(itemId, 0) >= itemsRestantes[itemId]:
                itemsRestantes.pop(itemId)

        melhoresCorredores.append(melhorCorredor)

    return melhoresCorredores


def calcularMelhorPedido(pedidos, pedidosSelecionados, corredores, corredoresAtivos, maxWave, unidadesAtuais):
    melhorPedido = None
    melhorScore = -1

    for pedidoId, itens in pedidos.items():
        if pedidoId in pedidosSelecionados:
            continue
        unidadesPedido = sum(itens.values())
        if unidadesAtuais + unidadesPedido > maxWave:
            continue
        cobertos = 0
        novos = 0
        for itemId in itens:
            coberto = False
            for corredorId in corredoresAtivos:
                if itemId in corredores[corredorId]:
                    coberto = True
                    break
            if coberto:
                cobertos += 1
            else:
                novos += 1
        score = cobertos - novos
        if score > melhorScore:
            melhorScore = score
            melhorPedido = pedidoId

    return melhorPedido


def verificaCoberturaCompleta(pedidosSelecionados, corredoresSelecionados, pedidos, corredores):
    demanda = calcularDemanda(pedidos, pedidosSelecionados)
    estoque = {}
    for cId in corredoresSelecionados:
        for iId, q in corredores[cId].items():
            if iId in estoque:
                estoque[iId] += q
            else:
                estoque[iId] = q
    for iId, q in demanda.items():
        disponivel = 0
        if iId in estoque:
            disponivel = estoque[iId]
        if disponivel < q:
            return False
    return True


def gerarSaida(pedidosSelecionados, corredoresAtivos, filename="saida.txt"):
    with open(filename, 'w') as f:
        f.write(f"{len(pedidosSelecionados)}\n")
        for pedidoId in pedidosSelecionados:
            f.write(f"{pedidoId}\n")
        f.write(f"{len(corredoresAtivos)}\n")
        for corredorId in corredoresAtivos:
            f.write(f"{corredorId}\n")


if __name__ == "__main__":
    for i in range(1, 21):
        nomeArquivo = f"data/instance_{i:04d}.txt"
        if not os.path.exists(nomeArquivo):
            continue
        nomeSaida = f"saidas/saida_{i:04d}.txt"
        os.makedirs("saidas", exist_ok=True)

        pedidos, corredores, waveMin, waveMax = organizaPedidosCorredores(nomeArquivo)
        itemsFrequentes = calcularItemsFrequentes(pedidos)

        melhoresPedidos = []
        quantidadePedidos = 0

        for itemFrequente, _ in itemsFrequentes:
            for pedidoId, items in pedidos.items():
                if itemFrequente in items:
                    novaDemanda = calcularDemanda(pedidos, melhoresPedidos + [pedidoId])
                    if verificaEstoqueDisponivel(novaDemanda, corredores):
                        melhoresPedidos.append(pedidoId)
                        quantidadePedidos += sum(pedidos[pedidoId].values())
            if melhoresPedidos:
                break

        demanda = calcularDemanda(pedidos, melhoresPedidos)
        melhoresCorredores = setCoverGuloso(demanda, corredores)

        wave = quantidadePedidos
        waveMin = int(waveMin)
        waveMax = int(waveMax)

        if len(melhoresCorredores) == 0 or len(melhoresPedidos) == 0:
            print(f"Instância {i:04d} inviável")
            continue

        objetivoAtual = wave / len(melhoresCorredores)

        while wave < waveMax:
            proximoMelhorPedido = calcularMelhorPedido(
                pedidos, melhoresPedidos, corredores, melhoresCorredores, waveMax, wave
            )
            if proximoMelhorPedido is None:
                break

            novaWave = wave + sum(pedidos[proximoMelhorPedido].values())
            novaDemanda = calcularDemanda(pedidos, melhoresPedidos + [proximoMelhorPedido])

            if not verificaEstoqueDisponivel(novaDemanda, corredores):
                break

            novosCorredores = setCoverGuloso(novaDemanda, corredores)

            if len(novosCorredores) == 0:
                break

            if not verificaCoberturaCompleta(melhoresPedidos + [proximoMelhorPedido], novosCorredores, pedidos, corredores):
                break

            novoObjetivo = novaWave / len(novosCorredores)

            if novoObjetivo >= objetivoAtual or wave < waveMin:
                melhoresPedidos.append(proximoMelhorPedido)
                wave = novaWave
                melhoresCorredores = novosCorredores
                objetivoAtual = novoObjetivo
            else:
                break

        print(f"Instância {i:04d} | unidades={wave} | corredores={len(melhoresCorredores)} | objetivo={objetivoAtual:.2f}")
        gerarSaida(melhoresPedidos, melhoresCorredores, filename=nomeSaida)