# Kanban · SalesInsight PY

Quadro usado para organizar o trabalho antes e durante o desenvolvimento.

## Backlog

- Ler o projeto com um dataset real (Kaggle ou dados.gov.br)
- Testes automáticos para a limpeza e a segmentação
- Argumentos de linha de comando para caminho do CSV e pasta de saída

## A Fazer

- Gravar o vídeo de demonstração (até 5 minutos)
- Inserir o link do vídeo no README e enviar os links no AVA

## Em Andamento

- Revisar o README final

## Concluído

- Criar o repositório no GitHub e o arquivo `salesinsight.py`
- Criar as branches `main`, `develop`, `feat/pipeline-dados` e `docs/readme`
- Implementar a geração do dataset CSV
- Implementar a função de inspeção dos dados
- Implementar a limpeza (espaços, datas inválidas, tipos) com relatório
- Implementar as colunas derivadas com datetime e `df.loc`
- Implementar a função de ordem superior `processar_coluna()`
- Implementar as agregações com `groupby` e a tabela cruzada com `pivot_table`
- Implementar a segmentação de clientes com lambda
- Criar o gráfico de linha (receita por mês + média móvel)
- Criar o gráfico de barras (top produtos)
- Criar o gráfico de dispersão (quantidade × receita)
- Criar o painel com subplots 2×2
- Exportar as figuras em PNG
- Implementar a exportação em CSV e JSON com releitura do JSON
- Criar a classe `AnalisadorDeVendas`
- Criar a função `main()` e o bloco `if __name__ == "__main__":`
- Testar o fluxo completo do zero
