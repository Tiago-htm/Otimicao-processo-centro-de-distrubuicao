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
    wave.append(ultimaLinha[0])
    wave.append(ultimaLinha[1])

    return pedidos, corredores, wave

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


if __name__ == "__main__":
    pedidos, corredores, wave= organizaPedidosCorredores("data/instance_0001.txt")    
    
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
    #[11, 23, 24, 42] os indices começam do 0 :) entao a linha 13 é a correta!!!!!!!!!!!!!!!!!!!!
    demanda = calcularDemanda(pedidos, melhoresPedidos)
    print(demanda)
  

    

    