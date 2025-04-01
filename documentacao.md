# Documentação do Sistema de Automação de Análise de Dados Imobiliários

## Visão Geral

Este sistema automatiza a análise de dados imobiliários, gerando insights estratégicos e recomendações para auxiliar na tomada de decisões. O sistema processa dados de produção (vendas), ganhos (comissões) e leads, realizando análises estatísticas e gerando um relatório PDF completo com visualizações, insights e recomendações estratégicas.

## Estrutura do Projeto

```
imobiliaria_analytics/
├── data/               # Armazena as planilhas Excel de entrada
├── scripts/            # Contém os scripts Python para processamento e análise
│   ├── main.py         # Script principal que orquestra todo o processo
│   ├── data_generator.py # Gerador de dados de exemplo para testes
│   ├── data_processor.py # Processamento e limpeza de dados
│   ├── data_analyzer.py  # Análise estatística e geração de insights
│   ├── report_generator.py # Geração do relatório PDF
│   └── architecture.md  # Documentação da arquitetura da solução
├── templates/          # Templates para geração de relatórios
└── output/             # Relatórios PDF e arquivos de resultados
```

## Requisitos do Sistema

- Python 3.10 ou superior
- Bibliotecas Python:
  - pandas
  - numpy
  - matplotlib
  - seaborn
  - scikit-learn
  - statsmodels
  - reportlab
  - openpyxl
  - jinja2
  - weasyprint

## Instalação

1. Clone o repositório ou extraia os arquivos para o diretório desejado
2. Instale as dependências necessárias:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn statsmodels reportlab openpyxl jinja2 weasyprint
```

## Uso Básico

### Executando o Sistema Completo

Para executar o sistema completo, use o script principal:

```bash
python scripts/main.py
```

Este comando irá:
1. Processar os dados das planilhas Excel na pasta `data/`
2. Realizar análises estatísticas e gerar insights
3. Criar um relatório PDF com recomendações estratégicas na pasta `output/`

### Opções de Linha de Comando

O script principal aceita as seguintes opções:

- `--gerar-dados`: Gera dados de exemplo para testes
- `--pular-processamento`: Pula a etapa de processamento de dados
- `--pular-analise`: Pula a etapa de análise de dados
- `--apenas-relatorio`: Gera apenas o relatório final usando dados já processados

Exemplo:
```bash
python scripts/main.py --gerar-dados
```

## Preparação dos Dados

O sistema espera encontrar os seguintes arquivos Excel na pasta `data/`:

1. **Dados de Produção**: Arquivo com "producao" ou "vendas" no nome
   - Colunas esperadas: data_venda, corretor, tipo_imovel, valor_venda

2. **Dados de Ganhos**: Arquivo com "ganhos" ou "comissoes" no nome
   - Colunas esperadas: data_pagamento, corretor, valor_comissao

3. **Dados de Leads**: Arquivo com "leads" ou "conversao" no nome
   - Colunas esperadas: data_captacao, origem, convertido

## Fluxo de Processamento

1. **Extração de Dados**: O sistema lê as planilhas Excel da pasta `data/`
2. **Processamento e Limpeza**: Os dados são limpos e transformados
3. **Análise Estatística**: São calculadas métricas e identificadas tendências
4. **Geração de Insights**: Algoritmos detectam padrões e oportunidades
5. **Criação de Relatório**: É gerado um relatório PDF com visualizações e recomendações

## Estrutura do Relatório PDF

O relatório PDF gerado contém as seguintes seções:

1. **Resumo Executivo**: Principais métricas e insights do dia
2. **Análise de Produção**: Tendências de vendas e desempenho de corretores
3. **Análise de Ganhos**: Comissões e rentabilidade
4. **Análise de Leads**: Conversões e oportunidades
5. **Recomendações Estratégicas**: Sugestões baseadas em dados para aumentar lucros
6. **Conclusão**: Resumo e próximos passos

## Manutenção e Atualização

### Atualização de Dados

Para atualizar os dados analisados:

1. Substitua os arquivos Excel na pasta `data/` com as versões mais recentes
2. Execute o script principal para gerar um novo relatório:
   ```bash
   python scripts/main.py
   ```

### Personalização do Relatório

Para personalizar o formato do relatório:

1. Modifique o arquivo `scripts/report_generator.py`
2. Ajuste os estilos, seções e conteúdo conforme necessário

### Adição de Novas Análises

Para adicionar novas análises:

1. Modifique o arquivo `scripts/data_analyzer.py`
2. Implemente novos métodos de análise na classe `DataAnalyzer`
3. Atualize o método `executar_analise_completa()` para incluir as novas análises

## Solução de Problemas

### Erros Comuns

1. **Arquivos não encontrados**:
   - Verifique se os arquivos Excel estão na pasta `data/`
   - Verifique se os nomes dos arquivos contêm as palavras-chave esperadas

2. **Erros de formato de dados**:
   - Verifique se as planilhas Excel contêm as colunas esperadas
   - Verifique se os tipos de dados estão corretos (datas, números, texto)

3. **Erros de geração de relatório**:
   - Verifique se todas as bibliotecas estão instaladas corretamente
   - Verifique se a pasta `output/` existe e tem permissões de escrita

### Logs

O sistema gera logs detalhados na pasta `output/`:

- `processamento.log`: Logs do processamento de dados
- `analise.log`: Logs da análise estatística
- `relatorio.log`: Logs da geração do relatório
- `automacao.log`: Logs do processo completo

## Exemplos de Uso Avançado

### Geração de Dados de Teste

Para gerar dados de exemplo para testes:

```bash
python scripts/main.py --gerar-dados
```

### Processamento de Dados Específicos

Para processar apenas determinados arquivos:

1. Coloque apenas os arquivos desejados na pasta `data/`
2. Execute o script principal

### Geração de Apenas o Relatório

Se os dados já foram processados e analisados:

```bash
python scripts/main.py --apenas-relatorio
```

## Contato e Suporte

Para suporte ou dúvidas sobre o sistema, entre em contato com a equipe de desenvolvimento.
