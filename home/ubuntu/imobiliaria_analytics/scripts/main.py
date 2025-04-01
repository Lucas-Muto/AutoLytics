#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script principal para automação de análise de dados imobiliários
Este script orquestra todo o processo de análise, desde a extração de dados
até a geração do relatório PDF com insights estratégicos
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), '..', 'output', 'automacao.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('main')

# Adicionar diretório de scripts ao path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Importar módulos do projeto
try:
    from data_generator import DataGenerator
    from data_processor import DataProcessor
    from data_analyzer import DataAnalyzer
    from report_generator import ReportGenerator
    logger.info("Módulos importados com sucesso")
except ImportError as e:
    logger.error(f"Erro ao importar módulos: {str(e)}")
    sys.exit(1)

def main():
    """
    Função principal que orquestra todo o processo de automação.
    """
    # Configurar argumentos de linha de comando
    parser = argparse.ArgumentParser(description='Automação de Análise de Dados Imobiliários')
    parser.add_argument('--gerar-dados', action='store_true', help='Gerar dados de exemplo')
    parser.add_argument('--pular-processamento', action='store_true', help='Pular etapa de processamento de dados')
    parser.add_argument('--pular-analise', action='store_true', help='Pular etapa de análise de dados')
    parser.add_argument('--apenas-relatorio', action='store_true', help='Gerar apenas o relatório final')
    args = parser.parse_args()
    
    # Definir diretórios do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    output_dir = os.path.join(base_dir, 'output')
    
    # Criar diretórios se não existirem
    for directory in [data_dir, output_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Diretório criado: {directory}")
    
    # Registrar início da execução
    logger.info("Iniciando processo de automação de análise de dados imobiliários")
    inicio = datetime.now()
    
    # Etapa 1: Geração de dados (opcional)
    if args.gerar_dados:
        logger.info("Iniciando geração de dados de exemplo")
        generator = DataGenerator(data_dir)
        sucesso = generator.gerar_todos_dados(num_producao=200, num_leads=500, periodo_dias=100)
        
        if not sucesso:
            logger.error("Falha na geração de dados. Abortando processo.")
            sys.exit(1)
        
        logger.info("Dados de exemplo gerados com sucesso")
    
    # Verificar se existem arquivos de dados
    arquivos = os.listdir(data_dir)
    arquivo_producao = next((f for f in arquivos if 'producao' in f.lower() or 'vendas' in f.lower()), None)
    arquivo_ganhos = next((f for f in arquivos if 'ganhos' in f.lower() or 'comissoes' in f.lower()), None)
    arquivo_leads = next((f for f in arquivos if 'leads' in f.lower() or 'conversao' in f.lower()), None)
    
    if not all([arquivo_producao, arquivo_ganhos, arquivo_leads]):
        logger.error("Arquivos de dados necessários não encontrados. Use a opção --gerar-dados para criar dados de exemplo.")
        sys.exit(1)
    
    # Etapa 2: Processamento de dados
    if not args.pular_processamento and not args.apenas_relatorio:
        logger.info("Iniciando processamento de dados")
        processor = DataProcessor(data_dir)
        resultado_processamento = processor.processar_todos_dados(arquivo_producao, arquivo_ganhos, arquivo_leads)
        
        if not resultado_processamento:
            logger.error("Falha no processamento de dados. Abortando processo.")
            sys.exit(1)
        
        # Salvar resultado em JSON (sem DataFrames)
        resultado_json = resultado_processamento.copy()
        if 'dataframes' in resultado_json:
            del resultado_json['dataframes']
        
        caminho_resultado = os.path.join(output_dir, 'metricas_processadas.json')
        with open(caminho_resultado, 'w', encoding='utf-8') as f:
            json.dump(resultado_json, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Processamento de dados concluído. Resultados salvos em: {caminho_resultado}")
        
        # Armazenar DataFrames para a próxima etapa
        dataframes = resultado_processamento.get('dataframes', {})
    else:
        # Se pular processamento, carregar dados diretamente
        logger.info("Etapa de processamento de dados ignorada")
        
        # Carregar métricas processadas se existirem
        caminho_resultado = os.path.join(output_dir, 'metricas_processadas.json')
        if not os.path.exists(caminho_resultado) and not args.apenas_relatorio:
            logger.error("Arquivo de métricas processadas não encontrado. Execute o processamento de dados primeiro.")
            sys.exit(1)
        
        if not args.apenas_relatorio:
            with open(caminho_resultado, 'r', encoding='utf-8') as f:
                resultado_json = json.load(f)
            
            # Carregar DataFrames diretamente dos arquivos
            processor = DataProcessor(data_dir)
            processor.carregar_dados(arquivo_producao, arquivo_ganhos, arquivo_leads)
            
            dataframes = {
                'producao': processor.limpar_dados_producao(),
                'ganhos': processor.limpar_dados_ganhos(),
                'leads': processor.limpar_dados_leads()
            }
    
    # Etapa 3: Análise de dados
    if not args.pular_analise and not args.apenas_relatorio:
        logger.info("Iniciando análise de dados")
        
        # Verificar se temos os DataFrames e métricas necessários
        if 'dataframes' not in locals():
            logger.error("DataFrames não disponíveis para análise. Execute o processamento de dados primeiro.")
            sys.exit(1)
        
        if 'resultado_json' not in locals():
            caminho_resultado = os.path.join(output_dir, 'metricas_processadas.json')
            if not os.path.exists(caminho_resultado):
                logger.error("Arquivo de métricas processadas não encontrado. Execute o processamento de dados primeiro.")
                sys.exit(1)
            
            with open(caminho_resultado, 'r', encoding='utf-8') as f:
                resultado_json = json.load(f)
        
        # Executar análise
        analyzer = DataAnalyzer(dataframes, resultado_json)
        resultados_analise = analyzer.executar_analise_completa()
        
        if not resultados_analise:
            logger.error("Falha na análise de dados. Abortando processo.")
            sys.exit(1)
        
        logger.info("Análise de dados concluída com sucesso")
    else:
        logger.info("Etapa de análise de dados ignorada")
    
    # Etapa 4: Geração de relatório
    logger.info("Iniciando geração de relatório")
    
    # Verificar se temos os resultados da análise
    caminho_analise = os.path.join(output_dir, 'resultados_analise.json')
    if not os.path.exists(caminho_analise):
        logger.error("Arquivo de resultados de análise não encontrado. Execute a análise de dados primeiro.")
        sys.exit(1)
    
    # Carregar resultados da análise
    with open(caminho_analise, 'r', encoding='utf-8') as f:
        resultados_analise = json.load(f)
    
    # Gerar relatório
    data_atual = datetime.now().strftime("%Y%m%d")
    nome_arquivo = f"relatorio_estrategico_{data_atual}.pdf"
    
    generator = ReportGenerator(resultados_analise, output_dir)
    caminho_relatorio = generator.gerar_relatorio(nome_arquivo)
    
    if not caminho_relatorio:
        logger.error("Falha na geração do relatório. Abortando processo.")
        sys.exit(1)
    
    logger.info(f"Relatório gerado com sucesso: {caminho_relatorio}")
    
    # Registrar fim da execução
    fim = datetime.now()
    duracao = (fim - inicio).total_seconds()
    logger.info(f"Processo de automação concluído em {duracao:.2f} segundos")
    
    # Resumo final
    print("\n" + "="*80)
    print("RESUMO DO PROCESSO DE AUTOMAÇÃO")
    print("="*80)
    print(f"Data de execução: {fim.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Duração total: {duracao:.2f} segundos")
    print(f"Arquivos de dados processados:")
    print(f"  - Produção: {arquivo_producao}")
    print(f"  - Ganhos: {arquivo_ganhos}")
    print(f"  - Leads: {arquivo_leads}")
    print(f"Relatório gerado: {os.path.basename(caminho_relatorio)}")
    print("="*80)
    print("\nProcesso concluído com sucesso!")
    print(f"O relatório está disponível em: {caminho_relatorio}")
    print("="*80)


if __name__ == "__main__":
    main()
