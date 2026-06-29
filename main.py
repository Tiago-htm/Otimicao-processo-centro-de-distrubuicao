import networkx as nx


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

# verifico qual os items que tem junto com o melhor item dentro de pedidos
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




def gerarSaida(pedidosSelecionados, corredoresAtivos, filename="saida2.txt"):
    with open(filename, 'w') as f:
        f.write(f"{len(pedidosSelecionados)}\n")
        for pedidoId in pedidosSelecionados:
            f.write(f"{pedidoId}\n")
        f.write(f"{len(corredoresAtivos)}\n")
        for corredorId in corredoresAtivos:
            f.write(f"{corredorId}\n")


if __name__ == "__main__":
    pedidos, corredores, waveMin, waveMax= organizaPedidosCorredores("data/instance_0002.txt")    
    
    grafo = criaGrafo(pedidos, corredores)
    print(f"Pedidos: {len([n for n in grafo.nodes if n[0] == 'p'])}")
    print(f"Itens: {len([n for n in grafo.nodes if n[0] == 'i'])}")
    print(f"Corredores: {len([n for n in grafo.nodes if n[0] == 'c'])}")
    print(f"Arestas p->i: {len([e for e in grafo.edges if e[0][0] == 'p'])}")
    print(f"Arestas i->c: {len([e for e in grafo.edges if e[0][0] == 'i'])}")
    waveMin = int(waveMin)
    waveMax = int(waveMax)
