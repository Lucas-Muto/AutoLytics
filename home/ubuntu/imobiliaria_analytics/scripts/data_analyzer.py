#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de análise de dados para imobiliária
Este script contém funções para análise estatística e geração de insights
a partir dos dados processados de produção, ganhos e leads.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import logging
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.seasonal import seasonal_decompose
import json

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output', 'analise.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('data_analyzer')

class DataAnalyzer:
    """
    Classe para análise de dados imobiliários.
    Responsável por gerar insights e recomendações estratégicas.
    """
    
    def __init__(self, dataframes, metricas):
        """
        Inicializa o analisador de dados.
        
        Args:
            dataframes (dict): Dicionário com DataFrames processados
            metricas (dict): Dicionário com métricas calculadas
        """
        self.dataframes = dataframes
        self.metricas = metricas
        self.insights = []
        self.recomendacoes = []
        self.figuras = []
        logger.info("Analisador de dados inicializado")
    
    def analisar_tendencias_vendas(self):
        """
        Analisa tendências de vendas ao longo do tempo.
        
        Returns:
            dict: Resultados da análise de tendências
        """
        if 'producao' not in self.dataframes or self.dataframes['producao'] is None:
            logger.error("DataFrame de produção não disponível para análise de tendências")
            return {}
        
        try:
            df = self.dataframes['producao']
            resultados = {}
            
            # Verificar se temos dados de data e valor
            if 'data_venda' not in df.columns or 'valor_venda' not in df.columns:
                logger.warning("Colunas necessárias não encontradas para análise de tendências")
                return resultados
            
            # Agrupar vendas por data
            df_agrupado = df.groupby(df['data_venda'].dt.date)['valor_venda'].agg(['sum', 'count']).reset_index()
            df_agrupado.columns = ['data', 'valor_total', 'quantidade']
            
            # Ordenar por data
            df_agrupado = df_agrupado.sort_values('data')
            
            # Calcular média móvel de 7 dias
            if len(df_agrupado) >= 7:
                df_agrupado['media_movel_valor'] = df_agrupado['valor_total'].rolling(window=7).mean()
                df_agrupado['media_movel_qtd'] = df_agrupado['quantidade'].rolling(window=7).mean()
            
            # Identificar tendência (últimos 30 dias)
            if len(df_agrupado) >= 30:
                df_recente = df_agrupado.tail(30).copy()
                
                # Preparar dados para regressão linear
                X = np.array(range(len(df_recente))).reshape(-1, 1)
                y_valor = df_recente['valor_total'].values
                y_qtd = df_recente['quantidade'].values
                
                # Regressão linear para valor
                modelo_valor = LinearRegression()
                modelo_valor.fit(X, y_valor)
                tendencia_valor = modelo_valor.coef_[0]
                
                # Regressão linear para quantidade
                modelo_qtd = LinearRegression()
                modelo_qtd.fit(X, y_qtd)
                tendencia_qtd = modelo_qtd.coef_[0]
                
                # Determinar direção da tendência
                resultados['tendencia_valor'] = {
                    'coeficiente': float(tendencia_valor),
                    'direcao': 'crescente' if tendencia_valor > 0 else 'decrescente' if tendencia_valor < 0 else 'estável'
                }
                
                resultados['tendencia_quantidade'] = {
                    'coeficiente': float(tendencia_qtd),
                    'direcao': 'crescente' if tendencia_qtd > 0 else 'decrescente' if tendencia_qtd < 0 else 'estável'
                }
                
                # Adicionar insight sobre tendência
                if tendencia_valor > 0 and tendencia_qtd > 0:
                    self.insights.append({
                        'categoria': 'tendencia_vendas',
                        'descricao': 'Tendência de crescimento tanto em valor quanto em quantidade de vendas nos últimos 30 dias.',
                        'impacto': 'alto',
                        'confianca': 'média'
                    })
                elif tendencia_valor < 0 and tendencia_qtd < 0:
                    self.insights.append({
                        'categoria': 'tendencia_vendas',
                        'descricao': 'Tendência de queda tanto em valor quanto em quantidade de vendas nos últimos 30 dias.',
                        'impacto': 'alto',
                        'confianca': 'média'
                    })
                elif tendencia_valor > 0 and tendencia_qtd < 0:
                    self.insights.append({
                        'categoria': 'tendencia_vendas',
                        'descricao': 'Tendência de aumento no valor total de vendas, mas redução na quantidade, indicando possível foco em imóveis de maior valor.',
                        'impacto': 'médio',
                        'confianca': 'média'
                    })
                elif tendencia_valor < 0 and tendencia_qtd > 0:
                    self.insights.append({
                        'categoria': 'tendencia_vendas',
                        'descricao': 'Tendência de aumento na quantidade de vendas, mas redução no valor total, indicando possível foco em imóveis de menor valor.',
                        'impacto': 'médio',
                        'confianca': 'média'
                    })
            
            # Criar gráfico de tendência
            plt.figure(figsize=(12, 6))
            plt.subplot(2, 1, 1)
            plt.plot(df_agrupado['data'], df_agrupado['valor_total'], label='Valor Total')
            if 'media_movel_valor' in df_agrupado.columns:
                plt.plot(df_agrupado['data'], df_agrupado['media_movel_valor'], 'r--', label='Média Móvel (7 dias)')
            plt.title('Tendência de Valor de Vendas')
            plt.xlabel('Data')
            plt.ylabel('Valor Total (R$)')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plt.subplot(2, 1, 2)
            plt.plot(df_agrupado['data'], df_agrupado['quantidade'], label='Quantidade')
            if 'media_movel_qtd' in df_agrupado.columns:
                plt.plot(df_agrupado['data'], df_agrupado['media_movel_qtd'], 'r--', label='Média Móvel (7 dias)')
            plt.title('Tendência de Quantidade de Vendas')
            plt.xlabel('Data')
            plt.ylabel('Quantidade')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Salvar figura
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
            figura_path = os.path.join(output_dir, 'tendencia_vendas.png')
            plt.savefig(figura_path)
            plt.close()
            
            self.figuras.append({
                'titulo': 'Tendência de Vendas',
                'descricao': 'Análise de tendências de valor e quantidade de vendas ao longo do tempo',
                'arquivo': figura_path
            })
            
            logger.info("Análise de tendências de vendas concluída")
            return resultados
        except Exception as e:
            logger.error(f"Erro ao analisar tendências de vendas: {str(e)}")
            return {}
    
    def analisar_desempenho_corretores(self):
        """
        Analisa o desempenho dos corretores.
        
        Returns:
            dict: Resultados da análise de desempenho
        """
        if 'producao' not in self.dataframes or self.dataframes['producao'] is None:
            logger.error("DataFrame de produção não disponível para análise de corretores")
            return {}
        
        try:
            df = self.dataframes['producao']
            resultados = {}
            
            # Verificar se temos dados de corretor e valor
            if 'corretor' not in df.columns or 'valor_venda' not in df.columns:
                logger.warning("Colunas necessárias não encontradas para análise de corretores")
                return resultados
            
            # Análise por corretor
            desempenho_corretores = df.groupby('corretor').agg({
                'valor_venda': ['sum', 'mean', 'count']
            }).reset_index()
            
            desempenho_corretores.columns = ['corretor', 'valor_total', 'valor_medio', 'quantidade']
            
            # Ordenar por valor total
            desempenho_corretores = desempenho_corretores.sort_values('valor_total', ascending=False)
            
            # Top 10 corretores
            top_corretores = desempenho_corretores.head(10)
            resultados['top_corretores'] = top_corretores.to_dict('records')
            
            # Identificar corretores de alto desempenho (outliers positivos)
            q3 = desempenho_corretores['valor_total'].quantile(0.75)
            iqr = desempenho_corretores['valor_total'].quantile(0.75) - desempenho_corretores['valor_total'].quantile(0.25)
            limite = q3 + 1.5 * iqr
            
            alto_desempenho = desempenho_corretores[desempenho_corretores['valor_total'] > limite]
            resultados['corretores_alto_desempenho'] = alto_desempenho.to_dict('records')
            
            # Adicionar insights sobre corretores
            if not alto_desempenho.empty:
                self.insights.append({
                    'categoria': 'desempenho_corretores',
                    'descricao': f'Identificados {len(alto_desempenho)} corretores com desempenho excepcional, significativamente acima da média.',
                    'impacto': 'alto',
                    'confianca': 'alta'
                })
                
                # Adicionar recomendação
                self.recomendacoes.append({
                    'categoria': 'desempenho_corretores',
                    'descricao': 'Analisar as práticas dos corretores de alto desempenho para identificar estratégias que possam ser replicadas pela equipe.',
                    'prioridade': 'alta'
                })
            
            # Criar gráfico de desempenho
            plt.figure(figsize=(12, 10))
            
            plt.subplot(2, 1, 1)
            sns.barplot(x='corretor', y='valor_total', data=top_corretores)
            plt.title('Top 10 Corretores por Valor Total de Vendas')
            plt.xlabel('Corretor')
            plt.ylabel('Valor Total (R$)')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            plt.subplot(2, 1, 2)
            sns.barplot(x='corretor', y='quantidade', data=top_corretores)
            plt.title('Top 10 Corretores por Quantidade de Vendas')
            plt.xlabel('Corretor')
            plt.ylabel('Quantidade')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Salvar figura
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
            figura_path = os.path.join(output_dir, 'desempenho_corretores.png')
            plt.savefig(figura_path)
            plt.close()
            
            self.figuras.append({
                'titulo': 'Desempenho de Corretores',
                'descricao': 'Análise dos corretores com melhor desempenho em valor e quantidade de vendas',
                'arquivo': figura_path
            })
            
            logger.info("Análise de desempenho de corretores concluída")
            return resultados
        except Exception as e:
            logger.error(f"Erro ao analisar desempenho de corretores: {str(e)}")
            return {}
    
    def analisar_conversao_leads(self):
        """
        Analisa a conversão de leads.
        
        Returns:
            dict: Resultados da análise de conversão
        """
        if 'leads' not in self.dataframes or self.dataframes['leads'] is None:
            logger.error("DataFrame de leads não disponível para análise de conversão")
            return {}
        
        try:
            df = self.dataframes['leads']
            resultados = {}
            
            # Verificar se temos dados de conversão
            if 'convertido' not in df.columns:
                logger.warning("Coluna de conversão não encontrada para análise de leads")
                return resultados
            
            # Taxa de conversão geral
            taxa_conversao = df['convertido'].mean()
            resultados['taxa_conversao_geral'] = float(taxa_conversao)
            
            # Análise por origem
            if 'origem' in df.columns:
                conversao_por_origem = df.groupby('origem').agg({
                    'convertido': ['mean', 'count']
                }).reset_index()
                
                conversao_por_origem.columns = ['origem', 'taxa_conversao', 'quantidade']
                
                # Ordenar por taxa de conversão
                conversao_por_origem = conversao_por_origem.sort_values('taxa_conversao', ascending=False)
                
                resultados['conversao_por_origem'] = conversao_por_origem.to_dict('records')
                
                # Identificar origens de alta conversão
                media_conversao = conversao_por_origem['taxa_conversao'].mean()
                alta_conversao = conversao_por_origem[conversao_por_origem['taxa_conversao'] > media_conversao * 1.5]
                
                if not alta_conversao.empty:
                    resultados['origens_alta_conversao'] = alta_conversao.to_dict('records')
                    
                    # Adicionar insight sobre origens de alta conversão
                    self.insights.append({
                        'categoria': 'conversao_leads',
                        'descricao': f'Identificadas {len(alta_conversao)} origens de leads com taxa de conversão significativamente acima da média.',
                        'impacto': 'alto',
                        'confianca': 'alta'
                    })
                    
                    # Adicionar recomendação
                    self.recomendacoes.append({
                        'categoria': 'conversao_leads',
                        'descricao': 'Aumentar investimento nas origens de leads com maior taxa de conversão para maximizar o retorno.',
                        'prioridade': 'alta'
                    })
                
                # Identificar origens de baixa conversão
                baixa_conversao = conversao_por_origem[conversao_por_origem['taxa_conversao'] < media_conversao * 0.5]
                
                if not baixa_conversao.empty:
                    resultados['origens_baixa_conversao'] = baixa_conversao.to_dict('records')
                    
                    # Adicionar insight sobre origens de baixa conversão
                    self.insights.append({
                        'categoria': 'conversao_leads',
                        'descricao': f'Identificadas {len(baixa_conversao)} origens de leads com taxa de conversão significativamente abaixo da média.',
                        'impacto': 'médio',
                        'confianca': 'alta'
                    })
                    
                    # Adicionar recomendação
                    self.recomendacoes.append({
                        'categoria': 'conversao_leads',
                        'descricao': 'Revisar e otimizar estratégias para origens de leads com baixa conversão.',
                        'prioridade': 'média'
                    })
            
            # Criar gráfico de conversão
            plt.figure(figsize=(10, 6))
            sns.barplot(x='origem', y='taxa_conversao', data=conversao_por_origem)
            plt.title('Taxa de Conversão por Origem de Lead')
            plt.xlabel('Origem')
            plt.ylabel('Taxa de Conversão')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            # Salvar figura
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
            figura_path = os.path.join(output_dir, 'conversao_leads.png')
            plt.savefig(figura_path)
            plt.close()
            
            self.figuras.append({
                'titulo': 'Conversão de Leads',
                'descricao': 'Análise da taxa de conversão por origem de leads',
                'arquivo': figura_path
            })
            
            logger.info("Análise de conversão de leads concluída")
            return resultados
        except Exception as e:
            logger.error(f"Erro ao analisar conversão de leads: {str(e)}")
            return {}

    def executar_analise_completa(self):
        """
        Executa todas as análises disponíveis.
        
        Returns:
            dict: Resultados consolidados de todas as análises
        """
        logger.info("Iniciando análise completa dos dados")
        
        # Executar todas as análises
        resultados_tendencias = self.analisar_tendencias_vendas()
        resultados_corretores = self.analisar_desempenho_corretores()
        resultados_leads = self.analisar_conversao_leads()
        
        # Consolidar resultados
        resultados = {
            'tendencias_vendas': resultados_tendencias,
            'desempenho_corretores': resultados_corretores,
            'conversao_leads': resultados_leads,
            'insights': self.insights,
            'recomendacoes': self.recomendacoes,
            'figuras': self.figuras
        }
        
        # Salvar resultados em JSON
        try:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
            caminho_json = os.path.join(output_dir, 'resultados_analise.json')
            
            with open(caminho_json, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, ensure_ascii=False, indent=4)
            
            logger.info(f"Resultados da análise salvos em: {caminho_json}")
        except Exception as e:
            logger.error(f"Erro ao salvar resultados em JSON: {str(e)}")
        
        return resultados


# Função para uso direto do script
def main():
    """
    Função principal para execução direta do script.
    """
    # Diretório base do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    
    # Carregar dados processados
    with open(os.path.join(base_dir, 'output', 'metricas_processadas.json'), 'r', encoding='utf-8') as f:
        metricas = json.load(f)
    
    # Criar analisador
    analyzer = DataAnalyzer(metricas.get('dataframes', {}), metricas)
    
    # Executar análise
    resultados = analyzer.executar_analise_completa()
    
    if resultados:
        print("Análise de dados concluída com sucesso!")
    else:
        print("Falha na análise de dados.")

if __name__ == "__main__":
    main()