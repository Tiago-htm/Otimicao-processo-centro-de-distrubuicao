def organizaPedidosCorredores(filename):
    with open(filename, 'r') as f:
        linhas = f.readlines()
    
    primeiraLinha = list(map(int, linhas[0].split()))
    quantidadePedidos = primeiraLinha[0]
    quantidadeCorredor = primeiraLinha[2]

    pedidos = {}
    corredores = {}
    wave = []

    for i in range(quantidadePedidos):
        capturaItem = linhas[i + 1].split()
        numeros = []
        for j in capturaItem:
          numeros.append(int(j))
        n = numeros[0]
        items = {}
        k = 1
        while k < len(numeros):
            itemId = numeros[k]
            quantidade = numeros[k + 1]
            items[itemId] = quantidade
            k += 2         

        pedidos[i] = items
   
    for i in range(quantidadeCorredor):
        capturaItem =  linhas[1 + quantidadePedidos + i].split()
        numeros = []
        for j in capturaItem:
            numeros.append(int(j))
        n = numeros[0]
        items = {}
        k = 1
        while k < len(numeros):
            itemId = numeros[k]
            quantidade = numeros[k + 1]
            items[itemId] = quantidade
            k += 2
        
        corredores[i] = items

    ultimaLinha = linhas[-1].split() 


    return pedidos, corredores, ultimaLinha[0], ultimaLinha[1]


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


# verifico qual os items que tem junto com o melhor item dentro de pedidos
def calcularDemanda(pedidos, pedidosSelecionados):
    demanda = {}
    for pedidoId in pedidosSelecionados:
        for itemId, qtd in pedidos[pedidoId].items():
             demanda[itemId] = demanda.get(itemId, 0) + qtd
    return demanda


def setCoverGuloso(demanda, corredores):
    melhoresCorredores = []
    itemsRestantes = demanda.copy()
    estoqueAcumulado = {}

    while itemsRestantes:
        melhorCorredor = None
        qtdItemColetados = 0

        for corredorId, items in corredores.items():
            if corredorId in melhoresCorredores:
                continue
            coletado = 0
            for itemId, qtd in itemsRestantes.items():
                jaTemos = 0
                if itemId in estoqueAcumulado:
                    jaTemos = estoqueAcumulado[itemId]
                qtdCorredor = 0
                if itemId in items:
                    qtdCorredor = items[itemId]
                if jaTemos + qtdCorredor >= qtd:
                    coletado += 1
            if coletado > qtdItemColetados:
                melhorCorredor = corredorId
                qtdItemColetados = coletado

        if melhorCorredor is None:
            break

        for itemId, qtd in corredores[melhorCorredor].items():
            if itemId in estoqueAcumulado:
                estoqueAcumulado[itemId] += qtd
            else:
                estoqueAcumulado[itemId] = qtd

        for itemId in list(itemsRestantes):
            if itemId in estoqueAcumulado:
                if estoqueAcumulado[itemId] >= itemsRestantes[itemId]:
                    itemsRestantes.pop(itemId)

        melhoresCorredores.append(melhorCorredor)

    return melhoresCorredores
         

def verificaEstoqueDisponivel(demanda, corredores):
    for itemId, qtdNecessaria in demanda.items():
        totalEstoque = 0
        for corredorId, items in corredores.items():
            if itemId in items:
                totalEstoque += items[itemId]
        if totalEstoque < qtdNecessaria:
            return False
    return True


def gerarSaida(pedidosSelecionados, corredoresAtivos, filename="saida2.txt"):
    with open(filename, 'w') as f:
        f.write(f"{len(pedidosSelecionados)}\n")
        for pedidoId in pedidosSelecionados:
            f.write(f"{pedidoId}\n")
        f.write(f"{len(corredoresAtivos)}\n")
        for corredorId in corredoresAtivos:
            f.write(f"{corredorId}\n")


def melhorPedidoInicial(pedidosValidos, corredores):
    melhorPedido = None
    melhorScore = -1
    
    for pedidoId, items in pedidosValidos.items():
        score = 0
        corredoresDoPedido = []
        for corredorId, itensCorreedor in corredores.items():
            for itemId in items:
                if itemId in itensCorreedor:
                    corredoresDoPedido.append(corredorId)
                    break
        
   
        for outroPedidoId, outroItens in pedidosValidos.items():
            if outroPedidoId == pedidoId:
                continue
            for corredorId in corredoresDoPedido:
                for itemId in outroItens:
                    if itemId in corredores[corredorId]:
                        score += 1
                        break
        
        if score > melhorScore:
            melhorScore = score
            melhorPedido = pedidoId
    
    return melhorPedido

if __name__ == "__main__":
    import os
    for i in range(1, 21):
        nomeArquivo = f"data/instance_{i:04d}.txt"
        if not os.path.exists(nomeArquivo):
            continue
        nomeSaida = f"saidas/saida_{i:04d}.txt"
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
            print(f"Instância {i:04d} inviável")
            continue

        melhorPedido = melhorPedidoInicial(pedidosValidos, corredores)
        melhoresPedidos = [melhorPedido]
        quantidadePedidos = sum(pedidosValidos[melhorPedido].values())

        demanda = calcularDemanda(pedidos, melhoresPedidos)
        melhoresCorredores = setCoverGuloso(demanda, corredores)

        if len(melhoresCorredores) == 0:
            print(f"Instância {i:04d} inviável")
            continue

        wave = quantidadePedidos
        objetivoAtual = wave / len(melhoresCorredores)

        while wave < waveMax:
            proximoMelhorPedido = calcularMelhorPedido(
                pedidosValidos, melhoresPedidos, corredores, melhoresCorredores, waveMax, wave
            )

            if proximoMelhorPedido is None:
                break

            novaWave = wave + sum(pedidosValidos[proximoMelhorPedido].values())
            novaDemanda = calcularDemanda(pedidosValidos, melhoresPedidos + [proximoMelhorPedido])
            novosCorredores = setCoverGuloso(novaDemanda, corredores)

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

        print(f"Instância {i:04d} | unidades={wave} | corredores={len(melhoresCorredores)} | objetivo={objetivoAtual:.2f}")
        gerarSaida(melhoresPedidos, melhoresCorredores, filename=nomeSaida)