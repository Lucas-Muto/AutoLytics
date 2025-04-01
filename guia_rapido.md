# Guia Rápido de Uso - Sistema de Automação de Análise de Dados Imobiliários

Este guia apresenta as instruções básicas para utilizar o sistema de automação de análise de dados imobiliários.

## Instalação

1. Certifique-se de ter Python 3.10 ou superior instalado
2. Execute o script de instalação para configurar todas as dependências:

```bash
python setup.py
```

## Uso Diário

### 1. Preparação dos Dados

Coloque suas planilhas Excel na pasta `data/`:

- **Dados de Produção**: Planilha com informações de vendas (nome deve conter "producao" ou "vendas")
- **Dados de Ganhos**: Planilha com informações de comissões (nome deve conter "ganhos" ou "comissoes")
- **Dados de Leads**: Planilha com informações de leads (nome deve conter "leads" ou "conversao")

### 2. Execução da Análise

Execute o script principal para processar os dados e gerar o relatório:

```bash
python scripts/main.py
```

### 3. Visualização dos Resultados

O relatório PDF será gerado na pasta `output/` com o nome `relatorio_estrategico_AAAAMMDD.pdf`

## Opções Adicionais

- **Gerar dados de exemplo**: `python scripts/main.py --gerar-dados`
- **Apenas gerar relatório**: `python scripts/main.py --apenas-relatorio`

## Estrutura do Relatório

O relatório PDF contém:

1. **Resumo Executivo**: Principais métricas e insights
2. **Análise de Produção**: Tendências de vendas e desempenho de corretores
3. **Análise de Ganhos**: Comissões e rentabilidade
4. **Análise de Leads**: Conversões e oportunidades
5. **Recomendações Estratégicas**: Sugestões para aumentar lucros

## Suporte

Para informações detalhadas, consulte a documentação completa em `documentacao.md`
