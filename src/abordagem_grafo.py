

# Seleciona o pedido inicial que compartilha corredores com o maior número de pedidos válidos.
def melhorPedidoInicialGrafo(grafo, pedidosValidos):
    melhorPedido = None
    melhorScore = -1

    for pedidoId in pedidosValidos:
        score = 0
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

#Busca o item que mais se repete entre os pedidos
def calcularItemMaisFrequente(grafo, pedidosValidos):
    frequencia = {}
    for pedidoId in pedidosValidos:
        noPedido = ('p', pedidoId)
        for noItem in grafo.successors(noPedido):
            itemId = noItem[1]
            if itemId in frequencia:
                frequencia[itemId] += 1
            else:
                frequencia[itemId] = 1
    melhorItem = None
    melhorFreq = -1
    for itemId, freq in frequencia.items():
        if freq > melhorFreq:
            melhorFreq = freq
            melhorItem = itemId
    return melhorItem

# Seleciona o próximo pedido que melhor aproveita os corredores já ativos,
# respeitando o limite máximo de unidades da wave.
def calcularMelhorPedidoGrafo(grafo, pedidosValidos, pedidosSelecionados, corredoresAtivos, maxWave, unidadesAtuais):
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
        for noItem in grafo.successors(noPedido):
            corredoresDoItem = {suc[1] for suc in grafo.successors(noItem)}
            if corredoresDoItem & set(corredoresAtivos):
                cobertos += 1
            else:
                novos += 1
        score = cobertos - novos
        if score > melhorScore:
            melhorScore = score
            melhorPedido = pedidoId

    return melhorPedido

#Utiliza o setCover com o metódo guloso para achar o melhor corredor 
def setCoverGulosoGrafo(grafo, demanda):
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
