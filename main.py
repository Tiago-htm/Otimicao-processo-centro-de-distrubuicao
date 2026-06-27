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
        numeros = [int(j) for j in capturaItem]
        items = {}
        k = 1
        while k < len(numeros):
            items[numeros[k]] = numeros[k + 1]
            k += 2
        pedidos[i] = items
   
    for i in range(quantidadeCorredor):
        capturaItem = linhas[1 + quantidadePedidos + i].split()
        numeros = [int(j) for j in capturaItem]
        items = {}
        k = 1
        while k < len(numeros):
            items[numeros[k]] = numeros[k + 1]
            k += 2
        corredores[i] = items

    ultimaLinha = linhas[-1].split()
    return pedidos, corredores, int(ultimaLinha[0]), int(ultimaLinha[1])


def calcularItemsFrequentes(pedidos):
    frequencia = {}
    for pedidoId, items in pedidos.items():
        for itemId in items:
            frequencia[itemId] = frequencia.get(itemId, 0) + 1
    return sorted(frequencia.items(), key=lambda x: x[1], reverse=True)


def calcularDemanda(pedidos, pedidosSelecionados):
    demanda = {}
    for pedidoId in pedidosSelecionados:
        for itemId, qtd in pedidos[pedidoId].items():
            demanda[itemId] = demanda.get(itemId, 0) + qtd
    return demanda


def verificaEstoqueDisponivel(demanda, corredores):
    for itemId, qtdNecessaria in demanda.items():
        totalEstoque = sum(items.get(itemId, 0) for items in corredores.values())
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


def verificaCoberturaCompleta(pedidosSelecionados, corredoresSelecionados, pedidos, corredores):
    demanda = calcularDemanda(pedidos, pedidosSelecionados)
    estoque = {}
    for cId in corredoresSelecionados:
        for iId, q in corredores[cId].items():
            estoque[iId] = estoque.get(iId, 0) + q
            
    for iId, q in demanda.items():
        if estoque.get(iId, 0) < q:
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
            print(f"Arquivo {nomeArquivo} não encontrado.")
            continue
            
        nomeSaida = f"saidas/saida_{i:04d}.txt"
        os.makedirs("saidas", exist_ok=True)

        pedidos, corredores, waveMin, waveMax = organizaPedidosCorredores(nomeArquivo)
        itemsFrequentes = calcularItemsFrequentes(pedidos)

        solucao_encontrada = False

        for semente_atual, _ in itemsFrequentes:
            melhoresPedidos = []
            quantidadePedidos = 0

            for pedidoId, items in pedidos.items():
                if semente_atual in items:
                    unidadesPedido = sum(items.values())
                    if quantidadePedidos + unidadesPedido <= waveMax:
                        novaDemanda = calcularDemanda(pedidos, melhoresPedidos + [pedidoId])
                        if verificaEstoqueDisponivel(novaDemanda, corredores):
                            melhoresPedidos.append(pedidoId)
                            quantidadePedidos += unidadesPedido
            
            if not melhoresPedidos:
                continue 

            demanda = calcularDemanda(pedidos, melhoresPedidos)
            melhoresCorredores = setCoverGuloso(demanda, corredores)
            wave = quantidadePedidos

            if len(melhoresCorredores) == 0 or not verificaCoberturaCompleta(melhoresPedidos, melhoresCorredores, pedidos, corredores):
                continue 

            objetivoAtual = wave / len(melhoresCorredores)

            while wave < waveMax:
                candidatos = []
                for pedidoId, itens in pedidos.items():
                    if pedidoId in melhoresPedidos:
                        continue
                    unidadesPedido = sum(itens.values())
                    if wave + unidadesPedido > waveMax:
                        continue
                    
                    cobertos = sum(1 for itemId in itens if any(itemId in corredores[cId] for cId in melhoresCorredores))
                    novos = len(itens) - cobertos
                    candidatos.append((cobertos - novos, pedidoId, unidadesPedido))
                
                candidatos.sort(key=lambda x: x[0], reverse=True)
                
                pedidoAceito = False
                for score, pedidoId, unidadesPedido in candidatos:
                    novaWave = wave + unidadesPedido
                    novaDemanda = calcularDemanda(pedidos, melhoresPedidos + [pedidoId])
                    
                    if not verificaEstoqueDisponivel(novaDemanda, corredores):
                        continue
                    
                    novosCorredores = setCoverGuloso(novaDemanda, corredores)
                    if len(novosCorredores) == 0 or not verificaCoberturaCompleta(melhoresPedidos + [pedidoId], novosCorredores, pedidos, corredores):
                        continue
                    
                    novoObjetivo = novaWave / len(novosCorredores)
                    
                    if novoObjetivo >= objetivoAtual or wave < waveMin:
                        melhoresPedidos.append(pedidoId)
                        wave = novaWave
                        melhoresCorredores = novosCorredores
                        objetivoAtual = novoObjetivo
                        pedidoAceito = True
                        break 
                
                if not pedidoAceito:
                    break

            if waveMin <= wave <= waveMax and verificaCoberturaCompleta(melhoresPedidos, melhoresCorredores, pedidos, corredores):
                print(f"Instância {i:04d} | semente={semente_atual} | unidades={wave} | corredores={len(melhoresCorredores)} | objetivo={objetivoAtual:.2f}")
                gerarSaida(melhoresPedidos, melhoresCorredores, filename=nomeSaida)
                solucao_encontrada = True
                break 

        if not solucao_encontrada:
            print(f"Instância {i:04d} inviável ")