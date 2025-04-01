#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de processamento de dados para análise imobiliária
Este script contém funções para extrair, limpar e processar dados de planilhas Excel
relacionadas a produção (vendas), ganhos (comissões) e leads.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output', 'processamento.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('data_processor')

class DataProcessor:
    """
    Classe para processamento de dados imobiliários.
    Responsável por extrair, limpar e processar dados de planilhas Excel.
    """
    
    def __init__(self, data_dir):
        """
        Inicializa o processador de dados.
        
        Args:
            data_dir (str): Diretório onde as planilhas Excel estão armazenadas
        """
        self.data_dir = data_dir
        self.producao_df = None
        self.ganhos_df = None
        self.leads_df = None
        logger.info(f"Processador de dados inicializado. Diretório de dados: {data_dir}")
    
    def carregar_dados(self, arquivo_producao, arquivo_ganhos, arquivo_leads):
        """
        Carrega os dados das planilhas Excel.
        
        Args:
            arquivo_producao (str): Nome do arquivo Excel de produção
            arquivo_ganhos (str): Nome do arquivo Excel de ganhos
            arquivo_leads (str): Nome do arquivo Excel de leads
            
        Returns:
            bool: True se os dados foram carregados com sucesso, False caso contrário
        """
        try:
            # Carrega dados de produção (vendas, corretores, VGV)
            caminho_producao = os.path.join(self.data_dir, arquivo_producao)
            self.producao_df = pd.read_excel(caminho_producao)
            logger.info(f"Dados de produção carregados: {len(self.producao_df)} registros")
            
            # Carrega dados de ganhos (comissões)
            caminho_ganhos = os.path.join(self.data_dir, arquivo_ganhos)
            self.ganhos_df = pd.read_excel(caminho_ganhos)
            logger.info(f"Dados de ganhos carregados: {len(self.ganhos_df)} registros")
            
            # Carrega dados de leads (taxa de conversão)
            caminho_leads = os.path.join(self.data_dir, arquivo_leads)
            self.leads_df = pd.read_excel(caminho_leads)
            logger.info(f"Dados de leads carregados: {len(self.leads_df)} registros")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {str(e)}")
            return False
    
    def limpar_dados_producao(self):
        """
        Limpa e prepara os dados de produção.
        
        Returns:
            pandas.DataFrame: DataFrame limpo de produção
        """
        if self.producao_df is None:
            logger.error("Dados de produção não foram carregados")
            return None
        
        try:
            df = self.producao_df.copy()
            
            # Remover linhas duplicadas
            df = df.drop_duplicates()
            
            # Converter datas para o formato correto
            if 'data_venda' in df.columns:
                df['data_venda'] = pd.to_datetime(df['data_venda'], errors='coerce')
            
            # Tratar valores ausentes
            for col in df.select_dtypes(include=['number']).columns:
                df[col] = df[col].fillna(0)
            
            # Remover outliers extremos (opcional, dependendo dos dados)
            # Exemplo para valor de venda:
            if 'valor_venda' in df.columns:
                q1 = df['valor_venda'].quantile(0.01)
                q3 = df['valor_venda'].quantile(0.99)
                df = df[(df['valor_venda'] >= q1) & (df['valor_venda'] <= q3)]
            
            logger.info(f"Dados de produção limpos: {len(df)} registros após limpeza")
            return df
        except Exception as e:
            logger.error(f"Erro ao limpar dados de produção: {str(e)}")
            return None
    
    def limpar_dados_ganhos(self):
        """
        Limpa e prepara os dados de ganhos.
        
        Returns:
            pandas.DataFrame: DataFrame limpo de ganhos
        """
        if self.ganhos_df is None:
            logger.error("Dados de ganhos não foram carregados")
            return None
        
        try:
            df = self.ganhos_df.copy()
            
            # Remover linhas duplicadas
            df = df.drop_duplicates()
            
            # Converter datas para o formato correto
            if 'data_pagamento' in df.columns:
                df['data_pagamento'] = pd.to_datetime(df['data_pagamento'], errors='coerce')
            
            # Tratar valores ausentes
            for col in df.select_dtypes(include=['number']).columns:
                df[col] = df[col].fillna(0)
            
            logger.info(f"Dados de ganhos limpos: {len(df)} registros após limpeza")
            return df
        except Exception as e:
            logger.error(f"Erro ao limpar dados de ganhos: {str(e)}")
            return None
    
    def limpar_dados_leads(self):
        """
        Limpa e prepara os dados de leads.
        
        Returns:
            pandas.DataFrame: DataFrame limpo de leads
        """
        if self.leads_df is None:
            logger.error("Dados de leads não foram carregados")
            return None
        
        try:
            df = self.leads_df.copy()
            
            # Remover linhas duplicadas
            df = df.drop_duplicates()
            
            # Converter datas para o formato correto
            if 'data_captacao' in df.columns:
                df['data_captacao'] = pd.to_datetime(df['data_captacao'], errors='coerce')
            
            if 'data_conversao' in df.columns:
                df['data_conversao'] = pd.to_datetime(df['data_conversao'], errors='coerce')
            
            # Tratar valores ausentes em campos categóricos
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].fillna('Não informado')
            
            logger.info(f"Dados de leads limpos: {len(df)} registros após limpeza")
            return df
        except Exception as e:
            logger.error(f"Erro ao limpar dados de leads: {str(e)}")
            return None
    
    def calcular_metricas_producao(self, df_producao_limpo):
        """
        Calcula métricas derivadas para dados de produção.
        
        Args:
            df_producao_limpo (pandas.DataFrame): DataFrame limpo de produção
            
        Returns:
            dict: Dicionário com métricas calculadas
        """
        if df_producao_limpo is None or len(df_producao_limpo) == 0:
            logger.error("DataFrame de produção vazio ou nulo")
            return {}
        
        try:
            metricas = {}
            
            # Total de vendas
            metricas['total_vendas'] = len(df_producao_limpo)
            
            # Volume Geral de Vendas (VGV)
            if 'valor_venda' in df_producao_limpo.columns:
                metricas['vgv_total'] = df_producao_limpo['valor_venda'].sum()
                metricas['vgv_medio'] = df_producao_limpo['valor_venda'].mean()
            
            # Vendas por corretor
            if 'corretor' in df_producao_limpo.columns:
                vendas_por_corretor = df_producao_limpo.groupby('corretor').size()
                metricas['top_corretores'] = vendas_por_corretor.sort_values(ascending=False).head(5).to_dict()
                
                # VGV por corretor
                if 'valor_venda' in df_producao_limpo.columns:
                    vgv_por_corretor = df_producao_limpo.groupby('corretor')['valor_venda'].sum()
                    metricas['top_corretores_vgv'] = vgv_por_corretor.sort_values(ascending=False).head(5).to_dict()
            
            # Vendas por tipo de imóvel
            if 'tipo_imovel' in df_producao_limpo.columns:
                vendas_por_tipo = df_producao_limpo.groupby('tipo_imovel').size()
                metricas['vendas_por_tipo'] = vendas_por_tipo.to_dict()
                
                # VGV por tipo de imóvel
                if 'valor_venda' in df_producao_limpo.columns:
                    vgv_por_tipo = df_producao_limpo.groupby('tipo_imovel')['valor_venda'].sum()
                    metricas['vgv_por_tipo'] = vgv_por_tipo.to_dict()
            
            # Análise temporal (últimos 30 dias)
            if 'data_venda' in df_producao_limpo.columns:
                hoje = datetime.now()
                inicio_mes = hoje.replace(day=1)
                df_mes_atual = df_producao_limpo[df_producao_limpo['data_venda'] >= inicio_mes]
                
                metricas['vendas_mes_atual'] = len(df_mes_atual)
                
                if 'valor_venda' in df_producao_limpo.columns:
                    metricas['vgv_mes_atual'] = df_mes_atual['valor_venda'].sum()
            
            logger.info(f"Métricas de produção calculadas: {len(metricas)} métricas")
            return metricas
        except Exception as e:
            logger.error(f"Erro ao calcular métricas de produção: {str(e)}")
            return {}
    
    def calcular_metricas_ganhos(self, df_ganhos_limpo):
        """
        Calcula métricas derivadas para dados de ganhos.
        
        Args:
            df_ganhos_limpo (pandas.DataFrame): DataFrame limpo de ganhos
            
        Returns:
            dict: Dicionário com métricas calculadas
        """
        if df_ganhos_limpo is None or len(df_ganhos_limpo) == 0:
            logger.error("DataFrame de ganhos vazio ou nulo")
            return {}
        
        try:
            metricas = {}
            
            # Total de comissões
            if 'valor_comissao' in df_ganhos_limpo.columns:
                metricas['total_comissoes'] = df_ganhos_limpo['valor_comissao'].sum()
                metricas['comissao_media'] = df_ganhos_limpo['valor_comissao'].mean()
            
            # Comissões por corretor
            if 'corretor' in df_ganhos_limpo.columns and 'valor_comissao' in df_ganhos_limpo.columns:
                comissoes_por_corretor = df_ganhos_limpo.groupby('corretor')['valor_comissao'].sum()
                metricas['top_corretores_comissao'] = comissoes_por_corretor.sort_values(ascending=False).head(5).to_dict()
            
            # Análise temporal (mês atual)
            if 'data_pagamento' in df_ganhos_limpo.columns:
                hoje = datetime.now()
                inicio_mes = hoje.replace(day=1)
                df_mes_atual = df_ganhos_limpo[df_ganhos_limpo['data_pagamento'] >= inicio_mes]
                
                if 'valor_comissao' in df_ganhos_limpo.columns:
                    metricas['comissoes_mes_atual'] = df_mes_atual['valor_comissao'].sum()
            
            logger.info(f"Métricas de ganhos calculadas: {len(metricas)} métricas")
            return metricas
        except Exception as e:
            logger.error(f"Erro ao calcular métricas de ganhos: {str(e)}")
            return {}
    
    def calcular_metricas_leads(self, df_leads_limpo):
        """
        Calcula métricas derivadas para dados de leads.
        
        Args:
            df_leads_limpo (pandas.DataFrame): DataFrame limpo de leads
            
        Returns:
            dict: Dicionário com métricas calculadas
        """
        if df_leads_limpo is None or len(df_leads_limpo) == 0:
            logger.error("DataFrame de leads vazio ou nulo")
            return {}
        
        try:
            metricas = {}
            
            # Total de leads
            metricas['total_leads'] = len(df_leads_limpo)
            
            # Leads convertidos
            if 'convertido' in df_leads_limpo.columns:
                leads_convertidos = df_leads_limpo[df_leads_limpo['convertido'] == True]
                metricas['leads_convertidos'] = len(leads_convertidos)
                metricas['taxa_conversao'] = len(leads_convertidos) / len(df_leads_limpo) if len(df_leads_limpo) > 0 else 0
            
            # Leads por origem
            if 'origem' in df_leads_limpo.columns:
                leads_por_origem = df_leads_limpo.groupby('origem').size()
                metricas['leads_por_origem'] = leads_por_origem.to_dict()
                
                # Taxa de conversão por origem
                if 'convertido' in df_leads_limpo.columns:
                    conversao_por_origem = df_leads_limpo.groupby('origem')['convertido'].mean()
                    metricas['conversao_por_origem'] = conversao_por_origem.to_dict()
            
            # Análise temporal (últimos 30 dias)
            if 'data_captacao' in df_leads_limpo.columns:
                hoje = datetime.now()
                inicio_mes = hoje.replace(day=1)
                df_mes_atual = df_leads_limpo[df_leads_limpo['data_captacao'] >= inicio_mes]
                
                metricas['leads_mes_atual'] = len(df_mes_atual)
                
                if 'convertido' in df_leads_limpo.columns:
                    leads_convertidos_mes = df_mes_atual[df_mes_atual['convertido'] == True]
                    metricas['leads_convertidos_mes'] = len(leads_convertidos_mes)
                    metricas['taxa_conversao_mes'] = len(leads_convertidos_mes) / len(df_mes_atual) if len(df_mes_atual) > 0 else 0
            
            logger.info(f"Métricas de leads calculadas: {len(metricas)} métricas")
            return metricas
        except Exception as e:
            logger.error(f"Erro ao calcular métricas de leads: {str(e)}")
            return {}
    
    def processar_todos_dados(self, arquivo_producao, arquivo_ganhos, arquivo_leads):
        """
        Processa todos os dados e retorna as métricas calculadas.
        
        Args:
            arquivo_producao (str): Nome do arquivo Excel de produção
            arquivo_ganhos (str): Nome do arquivo Excel de ganhos
            arquivo_leads (str): Nome do arquivo Excel de leads
            
        Returns:
            dict: Dicionário com todas as métricas calculadas
        """
        resultado = {}
        
        # Carregar dados
        sucesso = self.carregar_dados(arquivo_producao, arquivo_ganhos, arquivo_leads)
        if not sucesso:
            logger.error("Falha ao carregar dados. Processamento interrompido.")
            return resultado
        
        # Limpar dados
        df_producao_limpo = self.limpar_dados_producao()
        df_ganhos_limpo = self.limpar_dados_ganhos()
        df_leads_limpo = self.limpar_dados_leads()
        
        # Calcular métricas
        metricas_producao = self.calcular_metricas_producao(df_producao_limpo)
        metricas_ganhos = self.calcular_metricas_ganhos(df_ganhos_limpo)
        metricas_leads = self.calcular_metricas_leads(df_leads_limpo)
        
        # Consolidar resultados
        resultado = {
            'producao': metricas_producao,
            'ganhos': metricas_ganhos,
            'leads': metricas_leads,
            'data_processamento': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'dataframes': {
                'producao': df_producao_limpo,
                'ganhos': df_ganhos_limpo,
                'leads': df_leads_limpo
            }
        }
        
        logger.info("Processamento de todos os dados concluído com sucesso")
        return resultado


# Função para uso direto do script
def main():
    """
    Função principal para execução direta do script.
    """
    # Diretório base do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_
(Content truncated due to size limit. Use line ranges to read in chunks)