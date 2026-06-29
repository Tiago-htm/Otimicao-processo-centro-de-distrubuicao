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

# esta funcao transforma pedido item e corredores em um grafo tripartido, conforme Figura  1 da documentacação.
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

if __name__ == "__main__":
    pedidos, corredores, waveMin, waveMax= organizaPedidosCorredores("data/instance_0002.txt")    
    grafo = criaGrafo(pedidos, corredores)

    waveMin = int(waveMin)
    waveMax = int(waveMax)

