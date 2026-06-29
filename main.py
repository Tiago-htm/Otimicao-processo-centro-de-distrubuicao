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


def criaGrafo(pedidos, correio):
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

def calcularMelhorPedido(grafo, pedidosValidos, pedidosSelecionados, corredoresAtivos, maxWave, unidadesAtuais):
    melhorPedido = None
    melhorScore = -1

    for pedidoId in pedidosValidos:
        if pedidoId in pedidosSelecionados:
            continue

        unidadesPedido = sum(pedidosValidos[pedidoId].values())
        if unidadesAtuais + unidadesPedido > maxWave:
            continue

        cobertos = 0
        novos = 0
        noPedido = ('p', pedidoId)
        
        for noItem in grafo.successors(noPedido):  # p -> i
            itemId = noItem[1]
            corredoresDoItem = {suc[1] for suc in grafo.successors(noItem)}  # i -> c
            if corredoresDoItem & set(corredoresAtivos):
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


def setCoverGuloso(grafo, demanda):
    corredoresSelecionados = []
    itemsRestantes = demanda.copy()
    estoqueAcumulado = {}

    candidatos = {n[1] for n in grafo.nodes if n[0] == 'c'}

    while itemsRestantes:
        melhorCorredor = None
        melhorContribuicao = 0

        for corredorId in candidatos:
            if corredorId in corredoresSelecionados:
                continue
            contribuicao = 0
            noCorredor = ('c', corredorId)
            for noItem in grafo.predecessors(noCorredor):  
                itemId = noItem[1]
                if itemId in itemsRestantes:
                    disponivel = grafo[noItem][noCorredor]['peso']
                    falta = itemsRestantes[itemId] - estoqueAcumulado.get(itemId, 0)
                    if falta > 0:
                        contribuicao += min(disponivel, falta)
            if contribuicao > melhorContribuicao:
                melhorContribuicao = contribuicao
                melhorCorredor = corredorId

        if melhorCorredor is None:
            break

        noCorredor = ('c', melhorCorredor)
        for noItem in grafo.predecessors(noCorredor):
            itemId = noItem[1]
            qtd = grafo[noItem][noCorredor]['peso']
            estoqueAcumulado[itemId] = estoqueAcumulado.get(itemId, 0) + qtd

        for itemId in list(itemsRestantes):
            if estoqueAcumulado.get(itemId, 0) >= itemsRestantes[itemId]:
                itemsRestantes.pop(itemId)

        corredoresSelecionados.append(melhorCorredor)

    return corredoresSelecionados


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


def melhorPedidoInicial(grafo, pedidosValidos):
    melhorPedido = None
    melhorScore = -1
    
    for pedidoId, items in pedidosValidos.items():
        score = 0
        corredoresDoPedido = []
        noPedido = ('p', pedidoId)
        corredoresDoPedido = set()
        for noItem in grafo.successors(noPedido):      
           for noCorredor in grafo.successors(noItem): 
                    corredoresDoPedido.add(noCorredor[1])
                    
   
        for outroPedidoId in pedidosValidos:
            if outroPedidoId == pedidoId:
                continue
            noOutroPedido = ('p', outroPedidoId)
            corredoresOutroPedido = set()
            for noItem in grafo.successors(noOutroPedido):
                for noCorredor in grafo.successors(noItem):
                    corredoresOutroPedido.add(noCorredor[1])
            
            if corredoresDoPedido & corredoresOutroPedido:
                score += 1
        
        if score > melhorScore:
            melhorScore = score
            melhorPedido = pedidoId
    
    return melhorPedido

if __name__ == "__main__":
    import os
    passaAqui = [5, 8, 9, 13,17]
    for i in passaAqui:
        nomeArquivo = f"data/instance_{i:04d}.txt"
        if not os.path.exists(nomeArquivo):
            continue
        nomeSaida = f"saidas/saida_{i:04d}.txt"
        os.makedirs("saidas", exist_ok=True)

        pedidos, corredores, waveMin, waveMax = organizaPedidosCorredores(nomeArquivo)
        grafo = criaGrafo(pedidos, corredores)
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

        melhorPedido = melhorPedidoInicial(grafo, pedidosValidos)
        melhoresPedidos = [melhorPedido]
        quantidadePedidos = sum(pedidosValidos[melhorPedido].values())

        demanda = calcularDemanda(pedidos, melhoresPedidos)
        melhoresCorredores = setCoverGuloso(grafo, demanda)

        if len(melhoresCorredores) == 0:
            print(f"Instância {i:04d} inviável")
            continue

        wave = quantidadePedidos
        objetivoAtual = wave / len(melhoresCorredores)

        while wave < waveMax:
            proximoMelhorPedido = calcularMelhorPedido(
                grafo, pedidosValidos, melhoresPedidos, melhoresCorredores, waveMax, wave
            )
            if proximoMelhorPedido is None:
                break

            novaWave = wave + sum(pedidosValidos[proximoMelhorPedido].values())
            if novaWave > waveMax:
                break

            novaDemanda = calcularDemanda(pedidosValidos, melhoresPedidos + [proximoMelhorPedido])
            if not verificaEstoqueDisponivel(novaDemanda, corredores):
                break

            novosCorredores = setCoverGuloso(grafo, novaDemanda)
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

        # força atingir waveMin se necessário
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
                novosCorredores = setCoverGuloso(grafo, novaDemanda)
                if len(novosCorredores) == 0:
                    continue
                melhoresPedidos.append(pedidoId)
                wave = novaWave
                melhoresCorredores = novosCorredores
                adicionou = True
                break
            if not adicionou:
                break

        wave = sum(sum(pedidosValidos[p].values()) for p in melhoresPedidos)

        if wave < waveMin or wave > waveMax:
            print(f"Instância {i:04d} inviável - wave fora dos limites")
            continue

        demandaFinal = calcularDemanda(pedidosValidos, melhoresPedidos)
        estoqueTotal = {}
        for corredorId in melhoresCorredores:
            for itemId, qtd in corredores[corredorId].items():
                if itemId in estoqueTotal:
                    estoqueTotal[itemId] += qtd
                else:
                    estoqueTotal[itemId] = qtd

        solucaoValida = True
        for itemId, qtdNecessaria in demandaFinal.items():
            if estoqueTotal.get(itemId, 0) < qtdNecessaria:
                solucaoValida = False
                break

        if not solucaoValida:
            print(f"Instância {i:04d} inviável - estoque insuficiente")
            continue

        print(f"Instância {i:04d} | unidades={wave} | corredores={len(melhoresCorredores)} | objetivo={objetivoAtual:.2f}")
        gerarSaida(melhoresPedidos, melhoresCorredores, filename=nomeSaida)