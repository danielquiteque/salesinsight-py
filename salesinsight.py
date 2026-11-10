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
