import os
import networkx as nx


# ---------------------------------------------------------------------------
# 1. LEITURA E CONSTRUÇÃO DO GRAFO TRIPARTIDO
# ---------------------------------------------------------------------------

def construirGrafoTripartido(filename):
    """
    Lê o arquivo de instância e devolve:
      - G   : grafo tripartido ponderado (DiGraph)
      - pedidos   : dict  pedidoId  -> {itemId: qtd}
      - corredores: dict  corredorId -> {itemId: qtd}
      - waveMin, waveMax : limites LB/UB

    Nós do grafo:
      ('p', id)  – pedidos   (camada esquerda)
      ('i', id)  – itens     (camada central)
      ('c', id)  – corredores (camada direita)

    Arestas:
      ('p', o) -> ('i', i)  peso = u_oi  (unidades demandadas)
      ('i', i) -> ('c', a)  peso = u_ai  (unidades disponíveis)
    """
    with open(filename, 'r') as f:
        linhas = f.readlines()

    primeiraLinha     = list(map(int, linhas[0].split()))
    quantidadePedidos  = primeiraLinha[0]
    quantidadeCorredores = primeiraLinha[2]

    G           = nx.DiGraph()
    pedidos     = {}
    corredores  = {}

    # --- pedidos ----------------------------------------------------------
    for i in range(quantidadePedidos):
        numeros = list(map(int, linhas[i + 1].split()))
        items   = {}
        k = 1
        while k < len(numeros):
            itemId, qtd = numeros[k], numeros[k + 1]
            items[itemId] = qtd
            G.add_node(('p', i), camada='pedido')
            G.add_node(('i', itemId), camada='item')
            G.add_edge(('p', i), ('i', itemId), peso=qtd)
            k += 2
        pedidos[i] = items

    # --- corredores -------------------------------------------------------
    for i in range(quantidadeCorredores):
        numeros = list(map(int, linhas[1 + quantidadePedidos + i].split()))
        items   = {}
        k = 1
        while k < len(numeros):
            itemId, qtd = numeros[k], numeros[k + 1]
            items[itemId] = qtd
            G.add_node(('c', i), camada='corredor')
            G.add_node(('i', itemId), camada='item')
            G.add_edge(('i', itemId), ('c', i), peso=qtd)
            k += 2
        corredores[i] = items

    ultimaLinha = linhas[-1].split()
    return G, pedidos, corredores, int(ultimaLinha[0]), int(ultimaLinha[1])


# ---------------------------------------------------------------------------
# 2. CONSULTAS AO GRAFO
# ---------------------------------------------------------------------------

def itemsFrequentesNoGrafo(G):
    """
    Retorna itens ordenados pela quantidade de pedidos que os demandam,
    usando as arestas p->i do grafo.
    """
    frequencia = {}
    for no in G.nodes:
        if no[0] != 'p':
            continue
        for vizinho in G.successors(no):          # ('i', itemId)
            itemId = vizinho[1]
            frequencia[itemId] = frequencia.get(itemId, 0) + 1
    return sorted(frequencia.items(), key=lambda x: x[1], reverse=True)


def calcularDemandaPeloGrafo(G, pedidosSelecionados):
    """
    Soma as quantidades demandadas de cada item percorrendo as arestas
    p->i dos pedidos selecionados.
    """
    demanda = {}
    for pedidoId in pedidosSelecionados:
        no_pedido = ('p', pedidoId)
        for no_item in G.successors(no_pedido):
            itemId = no_item[1]
            qtd    = G[no_pedido][no_item]['peso']
            demanda[itemId] = demanda.get(itemId, 0) + qtd
    return demanda


def estoqueGlobalPeloGrafo(G, itemId):
    """
    Soma o estoque total de um item somando os pesos das arestas i->c
    (usado como pré-filtro de viabilidade global).
    """
    no_item = ('i', itemId)
    if no_item not in G:
        return 0
    return sum(G[no_item][suc]['peso'] for suc in G.successors(no_item))


def verificaEstoqueDisponivelNoGrafo(G, demanda):
    """
    Verificação rápida: o armazém inteiro possui estoque suficiente
    para cada item demandado?
    """
    for itemId, qtdNecessaria in demanda.items():
        if estoqueGlobalPeloGrafo(G, itemId) < qtdNecessaria:
            return False
    return True


def corredoresQueContemItem(G, itemId):
    """
    Retorna os IDs de corredores que possuem pelo menos uma unidade do item,
    navegando as arestas i->c no grafo.
    """
    no_item = ('i', itemId)
    if no_item not in G:
        return []
    return [suc[1] for suc in G.successors(no_item)]


def estoqueCorredorNoGrafo(G, corredorId, itemId):
    """Quantidade do item disponível em um corredor específico."""
    no_item     = ('i', itemId)
    no_corredor = ('c', corredorId)
    if G.has_edge(no_item, no_corredor):
        return G[no_item][no_corredor]['peso']
    return 0


# ---------------------------------------------------------------------------
# 3. SET COVER GULOSO (usando o grafo)
# ---------------------------------------------------------------------------

def setCoverGulosoNoGrafo(G, demanda):
    """
    Seleciona o menor subconjunto de corredores que cobre toda a demanda.
    Usa as arestas i->c do grafo para calcular a contribuição de cada corredor.
    """
    corredoresSelecionados = []
    itemsRestantes         = demanda.copy()
    estoqueAcumulado       = {}

    # Conjunto de corredores candidatos (todos os nós 'c' do grafo)
    candidatos = {n[1] for n in G.nodes if n[0] == 'c'}

    while itemsRestantes:
        melhorCorredor      = None
        melhorContribuicao  = 0

        for corredorId in candidatos:
            if corredorId in corredoresSelecionados:
                continue
            contribuicao = 0
            for itemId, qtdRestante in itemsRestantes.items():
                disponivel = estoqueCorredorNoGrafo(G, corredorId, itemId)
                if disponivel > 0:
                    falta         = max(0, qtdRestante - estoqueAcumulado.get(itemId, 0))
                    contribuicao += min(disponivel, falta)
            if contribuicao > melhorContribuicao:
                melhorCorredor     = corredorId
                melhorContribuicao = contribuicao

        if melhorCorredor is None:
            break

        # Incorpora o estoque do corredor escolhido
        for no_item in G.predecessors(('c', melhorCorredor)):
            itemId = no_item[1]
            qtd    = G[no_item][('c', melhorCorredor)]['peso']
            estoqueAcumulado[itemId] = estoqueAcumulado.get(itemId, 0) + qtd

        # Remove itens já cobertos
        for itemId in list(itemsRestantes):
            if estoqueAcumulado.get(itemId, 0) >= itemsRestantes[itemId]:
                itemsRestantes.pop(itemId)

        corredoresSelecionados.append(melhorCorredor)

    return corredoresSelecionados


# ---------------------------------------------------------------------------
# 4. VERIFICAÇÃO DE COBERTURA COMPLETA (usando o grafo)
# ---------------------------------------------------------------------------

def verificaCoberturaCompletaNoGrafo(G, pedidosSelecionados, corredoresSelecionados):
    """
    Confirma que os corredores selecionados suprem toda a demanda
    dos pedidos selecionados, percorrendo as arestas do grafo.
    """
    demanda = calcularDemandaPeloGrafo(G, pedidosSelecionados)
    estoque = {}
    for corredorId in corredoresSelecionados:
        no_corredor = ('c', corredorId)
        for no_item in G.predecessors(no_corredor):      # arestas i->c
            itemId = no_item[1]
            qtd    = G[no_item][no_corredor]['peso']
            estoque[itemId] = estoque.get(itemId, 0) + qtd

    for itemId, qtdNecessaria in demanda.items():
        if estoque.get(itemId, 0) < qtdNecessaria:
            return False
    return True


# ---------------------------------------------------------------------------
# 5. PONTUAÇÃO DE CANDIDATOS (usando o grafo)
# ---------------------------------------------------------------------------

def pontuarCandidatoNoGrafo(G, pedidoId, corredoresSelecionados):
    """
    Heurística de adição: preferir pedidos cujos itens já estão cobertos
    pelos corredores ativos (menor dispersão no armazém).
    Retorna (itens_cobertos - itens_novos) — quanto maior, melhor.
    """
    no_pedido = ('p', pedidoId)
    cobertos  = 0
    novos     = 0
    for no_item in G.successors(no_pedido):
        itemId    = no_item[1]
        corredores_do_item = set(corredoresQueContemItem(G, itemId))
        if corredores_do_item & set(corredoresSelecionados):
            cobertos += 1
        else:
            novos += 1
    return cobertos - novos


# ---------------------------------------------------------------------------
# 6. SAÍDA
# ---------------------------------------------------------------------------

def gerarSaida(pedidosSelecionados, corredoresAtivos, filename="saida.txt"):
    with open(filename, 'w') as f:
        f.write(f"{len(pedidosSelecionados)}\n")
        for pedidoId in pedidosSelecionados:
            f.write(f"{pedidoId}\n")
        f.write(f"{len(corredoresAtivos)}\n")
        for corredorId in corredoresAtivos:
            f.write(f"{corredorId}\n")


# ---------------------------------------------------------------------------
# 7. ALGORITMO PRINCIPAL
# ---------------------------------------------------------------------------

def resolverInstancia(G, pedidos, corredores, waveMin, waveMax):
    itemsFrequentes = itemsFrequentesNoGrafo(G)

    for semente_atual, _ in itemsFrequentes:

        # --- Fase 1: construção inicial com base na semente ---------------
        melhoresPedidos   = []
        quantidadeUnidades = 0

        for pedidoId, items in pedidos.items():
            if semente_atual not in items:
                continue
            unidadesPedido = sum(items.values())
            if quantidadeUnidades + unidadesPedido > waveMax:
                continue
            novaDemanda = calcularDemandaPeloGrafo(G, melhoresPedidos + [pedidoId])
            if verificaEstoqueDisponivelNoGrafo(G, novaDemanda):
                melhoresPedidos.append(pedidoId)
                quantidadeUnidades += unidadesPedido

        if not melhoresPedidos:
            continue

        demanda           = calcularDemandaPeloGrafo(G, melhoresPedidos)
        melhoresCorredores = setCoverGulosoNoGrafo(G, demanda)
        wave              = quantidadeUnidades

        if not melhoresCorredores or not verificaCoberturaCompletaNoGrafo(
                G, melhoresPedidos, melhoresCorredores):
            continue

        objetivoAtual = wave / len(melhoresCorredores)

        # --- Fase 2: expansão gulosa da wave ------------------------------
        while wave < waveMax:

            # Pontua todos os pedidos candidatos usando o grafo
            candidatos = []
            for pedidoId, items in pedidos.items():
                if pedidoId in melhoresPedidos:
                    continue
                unidadesPedido = sum(items.values())
                if wave + unidadesPedido > waveMax:
                    continue
                score = pontuarCandidatoNoGrafo(G, pedidoId, melhoresCorredores)
                candidatos.append((score, pedidoId, unidadesPedido))

            candidatos.sort(key=lambda x: x[0], reverse=True)

            pedidoAceito = False
            for score, pedidoId, unidadesPedido in candidatos:
                novaWave    = wave + unidadesPedido
                novaDemanda = calcularDemandaPeloGrafo(
                    G, melhoresPedidos + [pedidoId])

                if not verificaEstoqueDisponivelNoGrafo(G, novaDemanda):
                    continue

                novosCorredores = setCoverGulosoNoGrafo(G, novaDemanda)

                if novosCorredores and verificaCoberturaCompletaNoGrafo(
                        G, melhoresPedidos + [pedidoId], novosCorredores):
                    novoObjetivo = novaWave / len(novosCorredores)

                    if novoObjetivo >= objetivoAtual or wave < waveMin:
                        melhoresPedidos.append(pedidoId)
                        wave               = novaWave
                        melhoresCorredores = novosCorredores
                        objetivoAtual      = novoObjetivo
                        pedidoAceito       = True
                        break          # ← break só após aceitar um pedido

            if not pedidoAceito:
                break

        # --- Valida solução encontrada ------------------------------------
        if (waveMin <= wave <= waveMax and
                verificaCoberturaCompletaNoGrafo(G, melhoresPedidos, melhoresCorredores)):
            return melhoresPedidos, melhoresCorredores, wave, objetivoAtual

    return None  # nenhuma semente produziu solução viável


# ---------------------------------------------------------------------------
# 8. ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    for i in range(1, 21):
        nomeArquivo = f"data/instance_{i:04d}.txt"
        if not os.path.exists(nomeArquivo):
            print(f"Arquivo {nomeArquivo} não encontrado.")
            continue

        nomeSaida = f"saidas/saida_{i:04d}.txt"
        os.makedirs("saidas", exist_ok=True)

        G, pedidos, corredores, waveMin, waveMax = construirGrafoTripartido(nomeArquivo)

        resultado = resolverInstancia(G, pedidos, corredores, waveMin, waveMax)

        if resultado:
            pedidosSel, corredoresSel, wave, objetivo = resultado
            print(f"Instância {i:04d} | unidades={wave} "
                  f"| corredores={len(corredoresSel)} | objetivo={objetivo:.2f}")
            gerarSaida(pedidosSel, corredoresSel, filename=nomeSaida)
        else:
            print(f"Instância {i:04d} inviável")