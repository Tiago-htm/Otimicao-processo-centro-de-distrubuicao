def melhorPedidoInicialDicionario(pedidosValidos, corredores):
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


def calcularMelhorPedidoDicionario(pedidos, pedidosSelecionados, corredores, corredoresAtivos, maxWave, unidadesAtuais):
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


def setCoverGulosoDicionario(demanda, corredores):
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
                    jaTemos = estoqueAcumulado.get(itemId, 0)
                    falta = qtd - jaTemos
                    if falta > 0:
                        contribuicao += min(items[itemId], falta)
            if contribuicao > melhorContribuicao:
                melhorContribuicao = contribuicao
                melhorCorredor = corredorId

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
