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

def calcularItemsFrequentes(pedidos):
    frequencia = {}    

    for pedidoId, items in pedidos.items():
            for itemId in items:
               if itemId in frequencia:
                     frequencia[itemId] += 1
               else: 
                    frequencia[itemId] = 1 

    return sorted(frequencia.items(), key=lambda x: x[1], reverse=True)

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
    
    while itemsRestantes: 
        melhorCorredor = None
        qtdItemColetados = 0
        
        for corredorId, items in corredores.items():
            if corredorId in melhoresCorredores:
                continue
            coletado = 0
            for itemId, qtd in itemsRestantes.items():
                if itemId in items:
                    if items[itemId] >= qtd:
                        coletado += 1
            if coletado > qtdItemColetados:
                melhorCorredor = corredorId
                qtdItemColetados = coletado
        
        if melhorCorredor is None:
            break
        
        for itemId in list(itemsRestantes):
            if itemId in corredores[melhorCorredor]:
                if corredores[melhorCorredor][itemId] >= itemsRestantes[itemId]:
                    itemsRestantes.pop(itemId)
        
        melhoresCorredores.append(melhorCorredor)
    
    return melhoresCorredores
         




if __name__ == "__main__":
    pedidos, corredores, waveMin, waveMax= organizaPedidosCorredores("data/instance_0001.txt")    
    
    itemsFrequentes = calcularItemsFrequentes(pedidos)

    melhorItem = itemsFrequentes[0][0]

    print(melhorItem)

    melhoresPedidos =  []

    quantidadePedidos = 0

    for pedidoId, items in pedidos.items():  # dentro de pedidos eu busco todos os items
        if melhorItem in items:      # eu verifico se existe o Item que mais repete no dataset em items
                melhoresPedidos.append(pedidoId)
                quantidadePedidos += sum(pedidos[pedidoId].values())

    print(melhoresPedidos) 
    demanda = calcularDemanda(pedidos, melhoresPedidos)
    print(demanda)
    melhoresCorredores = setCoverGuloso(demanda, corredores)
    print(melhoresCorredores)
  
    wave = quantidadePedidos
    waveMin = int(waveMin)
    waveMax = int(waveMax)
    objetivoAtual = wave / len(melhoresCorredores)

    while wave < waveMax:
        proximoMelhorPedido = calcularMelhorPedido(
            pedidos, melhoresPedidos, corredores, melhoresCorredores, waveMax, wave
        )

        if proximoMelhorPedido is None:
            break

        novaWave = wave + sum(pedidos[proximoMelhorPedido].values())
        novaDemanda = calcularDemanda(pedidos, melhoresPedidos + [proximoMelhorPedido])
        novosCorredores = setCoverGuloso(novaDemanda, corredores)
        novoObjetivo = novaWave / len(novosCorredores)
        # só vou parar quando tiver testado melhor combinação possivel da wave
        if novoObjetivo >= objetivoAtual or wave < waveMin:
            melhoresPedidos.append(proximoMelhorPedido)
            wave = novaWave
            melhoresCorredores = novosCorredores
            objetivoAtual = novoObjetivo
        else:
            break

    print(f"Wave final: {melhoresPedidos}")
    print(f"Unidades: {wave}")
    print(f"Corredores: {melhoresCorredores}")
    print(f"Objetivo: {objetivoAtual:.2f}")
