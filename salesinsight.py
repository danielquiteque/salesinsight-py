"""
SalesInsight PY - Analise e Visualizacao de Dados de Vendas com Python
Mini-Projeto Avaliativo - Modulo 01 - Semana 07

Fluxo (pipeline = sequencia organizada de funcoes):
    gerar/carregar -> inspecionar -> tratar -> transformar
    -> analisar -> visualizar -> exportar
"""

import json
import os
import random
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")  # salva os PNG sem precisar abrir janela (funciona no terminal e no Colab)
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
import seaborn as sns


# ----------------------------------------------------------------------
# Configuracoes gerais
# ----------------------------------------------------------------------
CAMINHO_CSV = "vendas.csv"
PASTA_SAIDA = "outputs"
PASTA_GRAFICOS = os.path.join(PASTA_SAIDA, "graficos")

# .dt.strftime("%B") devolve o mes em ingles, por isso o dicionario
MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Marco", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

# Paleta escolhida a mao (nao e a padrao da biblioteca)
COR_PRINCIPAL = "#1F4E79"   # azul petroleo
COR_DESTAQUE = "#E07A1F"    # laranja
CORES_CATEGORIA = {
    "Computadores": "#1F4E79",
    "Celulares": "#E07A1F",
    "Perifericos": "#2E8B57",
}
CORES_BARRAS = ["#1F4E79", "#2F6690", "#3A7CA5", "#81A4CD", "#B8D0EB"]

# Mostra todas as colunas no console
pd.set_option("display.max_columns", 20)
pd.set_option("display.width", 140)


# ----------------------------------------------------------------------
# RF01 - Criar o dataset de vendas (gerador fornecido no enunciado)
# ----------------------------------------------------------------------
def gerar_dataset_vendas(n_registros=200, seed=42):
    """Gera um dataset sintetico de vendas com dados sujos."""
    random.seed(seed)
    np.random.seed(seed)

    produtos = ["Notebook", "Smartphone", "Tablet", "Monitor",
                "Teclado", "Mouse", "Headset"]
    categorias = {"Notebook": "Computadores", "Smartphone": "Celulares",
                  "Tablet": "Celulares", "Monitor": "Computadores",
                  "Teclado": "Perifericos", "Mouse": "Perifericos",
                  "Headset": "Perifericos"}
    precos = {"Notebook": 3500, "Smartphone": 2200, "Tablet": 1800,
              "Monitor": 1200, "Teclado": 250, "Mouse": 120,
              "Headset": 350}
    regioes = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]

    data_inicio = datetime(2025, 1, 1)
    dados = []

    for i in range(n_registros):
        produto = random.choice(produtos)
        categoria = categorias[produto]
        quantidade = random.randint(1, 10)
        preco = round(precos[produto] * random.uniform(0.85, 1.15), 2)
        data = data_inicio + timedelta(days=random.randint(0, 364))
        data_txt = data.strftime("%Y-%m-%d")
        cliente = f"Cliente_{random.randint(1, 50):03d}"

        # --- sujeira proposital para a etapa de limpeza ---
        if random.random() < 0.03:
            data_txt = "DATA INVALIDA"

        dados.append({
            "id_venda": i + 1,
            "data_venda": data_txt,
            "cliente": cliente,
            "produto": produto,
            "categoria": categoria,
            "regiao": random.choice(regioes),
            "quantidade": quantidade,
            "preco_unitario": preco,
        })

    return pd.DataFrame(dados)


# ----------------------------------------------------------------------
# RF02 - Inspecionar a estrutura dos dados
# ----------------------------------------------------------------------
def inspecionar_dados(df):
    """Exibe as informacoes estruturais do DataFrame e o devolve sem alterar."""
    print("\n=== INSPECAO INICIAL DO DATASET ===")
    print(f"Shape: {df.shape}")
    print(f"\nColunas: {list(df.columns)}")
    print(f"\nTipos de dados:\n{df.dtypes}")
    print(f"\nValores nulos por coluna:\n{df.isnull().sum()}")
    print(f"\nPrimeiros registros:\n{df.head()}")
    return df


# ----------------------------------------------------------------------
# RF03 - Tratar os dados (texto, datas e tipos)
# ----------------------------------------------------------------------
def tratar_dados(df):
    """
    Trata o DataFrame de vendas.
    Retorna: (df_limpo, relatorio), onde relatorio e um dicionario
    com as contagens de registros iniciais, convertidos e finais.
    """
    df = df.copy()
    relatorio = {"registros_iniciais": len(df)}
    linhas_alteradas = pd.Series(False, index=df.index)

    # 1. remover espacos extras nas colunas de texto
    colunas_texto = ["cliente", "produto", "categoria", "regiao"]
    for coluna in colunas_texto:
        original = df[coluna].astype(str)
        limpo = original.str.strip()
        linhas_alteradas = linhas_alteradas | (original != limpo)
        df[coluna] = limpo
    relatorio["texto_com_espacos_corrigido"] = int(linhas_alteradas.sum())

    # 2. converter data_venda; o que nao for data vira NaT e sai do dataset
    df["data_venda"] = pd.to_datetime(df["data_venda"], format="%Y-%m-%d", errors="coerce")
    datas_invalidas = df["data_venda"].isna()
    relatorio["datas_invalidas_removidas"] = int(datas_invalidas.sum())
    df = df[~datas_invalidas].copy()
    relatorio["datas_convertidas_texto_para_datetime"] = len(df)

    # 3. garantir int para quantidade e float para preco_unitario
    tipos_desejados = {"quantidade": "int64", "preco_unitario": "float64"}
    relatorio["conversoes_de_tipo"] = {}
    for coluna, tipo in tipos_desejados.items():
        tipo_antes = str(df[coluna].dtype)
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
        invalidos = df[coluna].isna()
        if invalidos.any():
            df = df[~invalidos].copy()
        df[coluna] = df[coluna].astype(tipo)
        convertidos = len(df) if tipo_antes != tipo else 0
        relatorio["conversoes_de_tipo"][coluna] = {
            "de": tipo_antes, "para": tipo,
            "registros_convertidos": convertidos,
            "invalidos_removidos": int(invalidos.sum()),
        }

    # 4. relatorio de limpeza
    relatorio["registros_finais"] = len(df)
    relatorio["registros_removidos"] = relatorio["registros_iniciais"] - len(df)
    relatorio["registros_sem_ajuste_de_conteudo"] = int((~linhas_alteradas[df.index]).sum())

    print("\n=== RELATORIO DE LIMPEZA ===")
    print(f"Registros que entraram:              {relatorio['registros_iniciais']}")
    print(f"Textos com espacos extras corrigidos: {relatorio['texto_com_espacos_corrigido']}")
    print(f"Datas invalidas removidas:            {relatorio['datas_invalidas_removidas']}")
    print(f"Datas convertidas (texto -> datetime): {relatorio['datas_convertidas_texto_para_datetime']}")
    for coluna, info in relatorio["conversoes_de_tipo"].items():
        print(f"{coluna}: {info['de']} -> {info['para']} | "
              f"convertidos: {info['registros_convertidos']} | "
              f"invalidos removidos: {info['invalidos_removidos']}")
    print(f"Registros sem ajuste de conteudo:     {relatorio['registros_sem_ajuste_de_conteudo']}")
    print(f"Registros finais:                     {relatorio['registros_finais']}")

    return df, relatorio


# ----------------------------------------------------------------------
# RF04 - Colunas derivadas e transformacao condicional
# ----------------------------------------------------------------------
def criar_colunas_derivadas(df):
    """Cria receita_total, mes, mes_nome, trimestre, ano e faixa_receita_item."""
    df = df.copy()

    # operacao vetorizada: multiplica as duas colunas inteiras de uma vez
    df["receita_total"] = (df["quantidade"] * df["preco_unitario"]).round(2)

    # componentes de data com o acessor .dt
    df["mes"] = df["data_venda"].dt.month
    df["mes_nome"] = df["mes"].map(MESES_PT)
    df["trimestre"] = "Q" + df["data_venda"].dt.quarter.astype(str)
    df["ano"] = df["data_venda"].dt.year

    # transformacao condicional vetorizada com df.loc[condicao, coluna]
    condicoes = [
        df["receita_total"] < 500,
        (df["receita_total"] >= 500) & (df["receita_total"] < 5000),
        df["receita_total"] >= 5000,
    ]
    faixas = ["Baixo Valor", "Medio Valor", "Alto Valor"]
    df["faixa_receita_item"] = "Nao Classificado"
    for condicao, faixa in zip(condicoes, faixas):
        df.loc[condicao, "faixa_receita_item"] = faixa

    return df


# ----------------------------------------------------------------------
# RF08 - Funcao de ordem superior (recebe outra funcao como argumento)
# ----------------------------------------------------------------------
def processar_coluna(df, coluna, funcao_transformacao, nome_saida=None):
    """
    Aplica uma funcao de transformacao a uma coluna do DataFrame.
    Demonstra o uso de funcoes como argumento.
    """
    nome_saida = nome_saida or f"{coluna}_transformado"
    df[nome_saida] = df[coluna].apply(funcao_transformacao)
    return df


# ----------------------------------------------------------------------
# RF05 - Metricas agregadas com groupby
# ----------------------------------------------------------------------
def calcular_metricas(df):
    """
    Calcula as metricas agregadas do dataset.
    Retorna um dicionario no formato {nome_da_metrica: DataFrame}.
    """
    metricas = {}

    metricas["por_mes"] = (
        df.groupby(["mes", "mes_nome"])
        .agg(receita_total=("receita_total", "sum"),
             quantidade=("quantidade", "sum"),
             n_vendas=("id_venda", "count"))
        .reset_index()
        .sort_values("mes")
    )

    metricas["por_trimestre"] = (
        df.groupby("trimestre")
        .agg(receita_total=("receita_total", "sum"),
             n_vendas=("id_venda", "count"))
        .reset_index()
    )

    metricas["top_produtos"] = (
        df.groupby("produto")["receita_total"].sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )

    metricas["por_categoria"] = (
        df.groupby("categoria")["receita_total"].sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    metricas["por_regiao"] = (
        df.groupby("regiao")
        .agg(receita_total=("receita_total", "sum"),
             ticket_medio=("receita_total", "mean"),
             n_vendas=("id_venda", "count"))
        .sort_values("receita_total", ascending=False)
        .reset_index()
    )

    # Bonus B03 - tabela cruzada mes x categoria com pivot_table
    metricas["mes_x_categoria"] = df.pivot_table(
        index="mes_nome", columns="categoria", values="receita_total",
        aggfunc="sum", fill_value=0, sort=False,
    ).reindex([MESES_PT[m] for m in sorted(df["mes"].unique())])

    return metricas


def mostrar_metricas(metricas):
    """Imprime cada tabela do dicionario de metricas de forma legivel."""
    for nome, tabela in metricas.items():
        print(f"\n=== {nome.upper().replace('_', ' ')} ===")
        print(tabela.round(2).to_string(index=(nome == "mes_x_categoria")))
    return metricas


# ----------------------------------------------------------------------
# RF06 - Segmentacao de clientes por nivel de gasto
# ----------------------------------------------------------------------
def segmentar_clientes(df):
    """
    Agrupa por cliente, soma a receita e classifica em
    Bronze / Prata / Ouro.
    Retorna um DataFrame com: cliente, total_gasto, segmento.
    """
    clientes = (
        df.groupby("cliente")["receita_total"].sum()
        .reset_index()
        .rename(columns={"receita_total": "total_gasto"})
        .sort_values("total_gasto", ascending=False)
    )

    # funcao lambda aplicada com .apply()
    clientes["segmento"] = clientes["total_gasto"].apply(
        lambda valor: "Bronze" if valor < 5000 else ("Prata" if valor <= 15000 else "Ouro")
    )

    print("\n=== TOP 10 CLIENTES ===")
    print(clientes.head(10).round(2).to_string(index=False))
    print("\n=== CLIENTES POR SEGMENTO ===")
    print(clientes["segmento"].value_counts().to_string())

    return clientes


# ----------------------------------------------------------------------
# Estatisticas gerais e projecao simples (bonus B01 e B05)
# ----------------------------------------------------------------------
def descrever_tendencia(variacao_percentual):
    """Traduz a variacao percentual em uma palavra (if / elif / else)."""
    if variacao_percentual > 5:
        return "alta"
    elif variacao_percentual < -5:
        return "queda"
    else:
        return "estavel"


def calcular_estatisticas(df, metricas, clientes, janela=3):
    """
    Monta um dicionario com os numeros gerais do periodo.
    Inclui quartis da receita por venda (B05) e uma projecao do proximo
    mes pela media movel dos ultimos `janela` meses (B01).
    """
    por_mes = metricas["por_mes"]
    media_movel = por_mes["receita_total"].rolling(window=janela).mean()
    ultimo_mes = por_mes["receita_total"].iloc[-1]
    projecao = media_movel.iloc[-1]
    variacao = (projecao - ultimo_mes) / ultimo_mes * 100

    estatisticas = {
        "receita_total": df["receita_total"].sum(),
        "quantidade_total": df["quantidade"].sum(),
        "numero_de_vendas": len(df),
        "ticket_medio": df["receita_total"].mean(),
        "clientes_unicos": df["cliente"].nunique(),
        "clientes_ouro": (clientes["segmento"] == "Ouro").sum(),
        "receita_q1_quartil_25": df["receita_total"].quantile(0.25),
        "receita_mediana": df["receita_total"].quantile(0.50),
        "receita_q3_quartil_75": df["receita_total"].quantile(0.75),
        "projecao_proximo_mes_media_movel": projecao,
        "tendencia_proximo_mes": descrever_tendencia(variacao),
    }
    return estatisticas


# ----------------------------------------------------------------------
# RF07 - Visualizacoes com Matplotlib e Seaborn
# ----------------------------------------------------------------------
def configurar_estilo():
    """Define o visual global dos graficos."""
    sns.set_theme(style="whitegrid")
    plt.rcParams["figure.figsize"] = (12, 6)
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["axes.labelsize"] = 11


def formatar_reais(valor, _posicao=None):
    """Formata o eixo em reais: 120000 -> 'R$ 120 mil'."""
    if abs(valor) >= 1000:
        return f"R$ {valor / 1000:,.0f} mil".replace(",", ".")
    return f"R$ {valor:,.0f}"


def salvar_figura(fig, nome_arquivo, pasta=PASTA_GRAFICOS, dpi=150):
    """Ajusta o layout, salva o PNG e fecha a figura. Retorna o caminho."""
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, nome_arquivo)
    plt.tight_layout()
    fig.savefig(caminho, dpi=dpi)
    plt.close(fig)
    print(f"Grafico salvo: {caminho}")
    return caminho


def desenhar_linha_receita(ax, por_mes, janela=3):
    """Linha da receita mensal + media movel (duas series, por isso a legenda)."""
    rotulos = por_mes["mes_nome"].str[:3]
    ax.plot(rotulos, por_mes["receita_total"], marker="o", linewidth=2.5,
            color=COR_PRINCIPAL, label="Receita mensal")
    ax.plot(rotulos, por_mes["receita_total"].rolling(window=janela).mean(),
            linestyle="--", linewidth=2, color=COR_DESTAQUE,
            label=f"Media movel ({janela} meses)")
    ax.set_title("Receita Total por Mes - 2025")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Receita Total")
    ax.yaxis.set_major_formatter(FuncFormatter(formatar_reais))
    ax.legend()


def desenhar_barras_produtos(ax, top_produtos):
    """Barras horizontais do Top 5 produtos por receita."""
    sns.barplot(data=top_produtos, y="produto", x="receita_total",
                hue="produto", legend=False, palette=CORES_BARRAS, ax=ax)
    ax.set_title("Top 5 Produtos por Receita")
    ax.set_xlabel("Receita Total")
    ax.set_ylabel("Produto")
    ax.xaxis.set_major_formatter(FuncFormatter(formatar_reais))


def desenhar_dispersao(ax, df):
    """Dispersao quantidade x receita por transacao, uma cor por categoria."""
    for categoria, cor in CORES_CATEGORIA.items():
        dados = df[df["categoria"] == categoria]  # filtro booleano
        ax.scatter(dados["quantidade"], dados["receita_total"], color=cor,
                   alpha=0.75, s=55, edgecolor="white", label=categoria)
    ax.set_title("Quantidade x Receita por Transacao")
    ax.set_xlabel("Quantidade vendida (unidades)")
    ax.set_ylabel("Receita da transacao")
    ax.yaxis.set_major_formatter(FuncFormatter(formatar_reais))
    ax.legend(title="Categoria")


def desenhar_barras_regiao(ax, por_regiao):
    """Barras verticais da receita por regiao."""
    ax.bar(por_regiao["regiao"], por_regiao["receita_total"], color=CORES_BARRAS)
    ax.set_title("Receita por Regiao")
    ax.set_xlabel("Regiao")
    ax.set_ylabel("Receita Total")
    ax.yaxis.set_major_formatter(FuncFormatter(formatar_reais))


def grafico_receita_por_mes(por_mes):
    """Figura 1 - linha."""
    fig, ax = plt.subplots(figsize=(12, 6))
    desenhar_linha_receita(ax, por_mes)
    return salvar_figura(fig, "receita_por_mes.png")


def grafico_top_produtos(top_produtos):
    """Figura 2 - barras."""
    fig, ax = plt.subplots(figsize=(11, 6))
    desenhar_barras_produtos(ax, top_produtos)
    return salvar_figura(fig, "top_produtos.png")


def grafico_quantidade_vs_receita(df):
    """Figura 3 - dispersao."""
    fig, ax = plt.subplots(figsize=(11, 7))
    desenhar_dispersao(ax, df)
    return salvar_figura(fig, "quantidade_vs_receita.png")


def grafico_painel_resumo(df, metricas):
    """Figura 4 - painel 2x2 com os eixos acessados um a um."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    desenhar_linha_receita(axes[0, 0], metricas["por_mes"])
    desenhar_barras_produtos(axes[0, 1], metricas["top_produtos"])
    desenhar_dispersao(axes[1, 0], df)
    desenhar_barras_regiao(axes[1, 1], metricas["por_regiao"])
    fig.suptitle("SalesInsight PY - Painel Resumo de Vendas 2025",
                 fontsize=18, fontweight="bold", color=COR_PRINCIPAL)
    return salvar_figura(fig, "painel_resumo.png")
