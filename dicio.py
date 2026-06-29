#MODELAGEM DICIONARIO

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


 verifico qual os items que tem junto com o melhor item dentro de pedidos

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
         