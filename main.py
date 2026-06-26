def organiza_pedidos_e_corredores(filename):
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
        itens = {}
        k = 1
        while k < len(numeros):
            item_id = numeros[k]
            quantidade = numeros[k + 1]
            itens[item_id] = quantidade
            k += 2         

        pedidos[i] = itens
   
    for i in range(quantidadeCorredor):
        capturaItem =  linhas[1 + quantidadePedidos + i].split()
        numeros = []
        for j in capturaItem:
            numeros.append(int(j))
        n = numeros[0]
        itens = {}
        k = 1
        while k < len(numeros):
            item_id = numeros[k]
            quantidade = numeros[k + 1]
            itens[item_id] = quantidade
            k += 2
        
        corredores[i] = itens

    ultimaLinha = linhas[-1].split() 
    wave.append(ultimaLinha[0])
    wave.append(ultimaLinha[1])

    return pedidos, corredores, wave


if __name__ == "__main__":
    pedidos, corredores, wave = organiza_pedidos_e_corredores("data/instance_0001.txt")
