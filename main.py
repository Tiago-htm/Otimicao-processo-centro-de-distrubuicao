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
    

if __name__ == "__main__":
    pedidos, corredores, wave = organizaPedidosCorredores("data/instance_0001.txt")
    teste = calcularitemsFrequentes(pedidos)
    print(teste)