#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de geração de dados de exemplo para testes
Este script gera dados simulados para testar o sistema de análise imobiliária
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
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output', 'geracao_dados.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('data_generator')

class DataGenerator:
    """
    Classe para geração de dados de exemplo para testes.
    """
    
    def __init__(self, output_dir):
        """
        Inicializa o gerador de dados.
        
        Args:
            output_dir (str): Diretório onde os arquivos Excel serão salvos
        """
        self.output_dir = output_dir
        logger.info(f"Gerador de dados inicializado. Diretório de saída: {output_dir}")
    
    def gerar_dados_producao(self, num_registros=200, periodo_dias=100):
        """
        Gera dados simulados de produção (vendas).
        
        Args:
            num_registros (int): Número de registros a serem gerados
            periodo_dias (int): Período em dias para distribuição das datas
            
        Returns:
            pandas.DataFrame: DataFrame com dados simulados de produção
        """
        try:
            # Definir dados base
            datas = [datetime.now() - timedelta(days=i) for i in range(periodo_dias)]
            corretores = [f"Corretor {i}" for i in range(1, 11)]
            tipos_imovel = ['Apartamento', 'Casa', 'Terreno', 'Comercial', 'Rural']
            bairros = ['Centro', 'Jardins', 'Vila Nova', 'Beira Mar', 'Parque Industrial', 'Zona Sul', 'Zona Norte']
            
            # Definir distribuição de valores por tipo de imóvel
            valores_medios = {
                'Apartamento': 450000,
                'Casa': 650000,
                'Terreno': 300000,
                'Comercial': 800000,
                'Rural': 550000
            }
            
            # Gerar dados aleatórios
            np.random.seed(42)  # Para reprodutibilidade
            
            # Gerar tipos de imóveis com distribuição não uniforme
            probabilidades_tipos = [0.4, 0.3, 0.15, 0.1, 0.05]  # Mais apartamentos e casas
            tipos = np.random.choice(tipos_imovel, num_registros, p=probabilidades_tipos)
            
            # Gerar valores de venda baseados no tipo de imóvel
            valores_venda = []
            for tipo in tipos:
                valor_medio = valores_medios[tipo]
                # Adicionar variação de 30% para mais ou para menos
                valores_venda.append(np.random.normal(valor_medio, valor_medio * 0.15))
            
            # Gerar datas com tendência (mais vendas recentes)
            pesos_datas = np.linspace(1, 3, periodo_dias)  # Mais peso para datas recentes
            pesos_datas = pesos_datas / sum(pesos_datas)
            datas_venda = np.random.choice(datas, num_registros, p=pesos_datas)
            
            # Gerar corretores com desempenho variado
            # Alguns corretores têm mais vendas que outros
            pesos_corretores = np.array([3, 2.5, 2, 1.5, 1, 1, 0.8, 0.8, 0.7, 0.7])
            pesos_corretores = pesos_corretores / sum(pesos_corretores)
            corretores_venda = np.random.choice(corretores, num_registros, p=pesos_corretores)
            
            # Criar DataFrame
            df = pd.DataFrame({
                'data_venda': datas_venda,
                'corretor': corretores_venda,
                'tipo_imovel': tipos,
                'bairro': np.random.choice(bairros, num_registros),
                'valor_venda': valores_venda,
                'area_m2': np.random.normal(120, 40, num_registros),
                'comissao_percentual': np.random.uniform(2, 6, num_registros)
            })
            
            # Adicionar algumas tendências
            # Corretores mais experientes vendem imóveis mais caros
            for i, corretor in enumerate(corretores[:3]):
                idx = df[df['corretor'] == corretor].index
                df.loc[idx, 'valor_venda'] *= (1.1 - i * 0.03)  # Aumento de 10%, 7%, 4% para os top 3
            
            # Adicionar coluna de VGV (Volume Geral de Vendas)
            df['vgv'] = df['valor_venda']
            
            # Arredondar valores numéricos
            df['valor_venda'] = df['valor_venda'].round(2)
            df['area_m2'] = df['area_m2'].round(2)
            df['comissao_percentual'] = df['comissao_percentual'].round(2)
            df['vgv'] = df['vgv'].round(2)
            
            logger.info(f"Gerados {len(df)} registros de dados de produção")
            return df
        except Exception as e:
            logger.error(f"Erro ao gerar dados de produção: {str(e)}")
            return pd.DataFrame()
    
    def gerar_dados_ganhos(self, df_producao):
        """
        Gera dados simulados de ganhos (comissões) com base nos dados de produção.
        
        Args:
            df_producao (pandas.DataFrame): DataFrame com dados de produção
            
        Returns:
            pandas.DataFrame: DataFrame com dados simulados de ganhos
        """
        try:
            if df_producao.empty:
                logger.error("DataFrame de produção vazio. Impossível gerar dados de ganhos.")
                return pd.DataFrame()
            
            # Criar cópia dos dados relevantes
            df = df_producao[['data_venda', 'corretor', 'valor_venda', 'comissao_percentual']].copy()
            
            # Renomear colunas
            df = df.rename(columns={'data_venda': 'data_venda_original'})
            
            # Calcular valor da comissão
            df['valor_comissao'] = (df['valor_venda'] * df['comissao_percentual'] / 100).round(2)
            
            # Adicionar data de pagamento (alguns dias após a venda)
            df['data_pagamento'] = df['data_venda_original'] + pd.to_timedelta(np.random.randint(5, 30, len(df)), unit='d')
            
            # Adicionar status de pagamento
            df['status_pagamento'] = np.random.choice(['Pago', 'Pendente', 'Em processamento'], len(df), p=[0.8, 0.15, 0.05])
            
            # Adicionar informações de equipe
            equipes = ['Equipe A', 'Equipe B', 'Equipe C']
            
            # Distribuir corretores em equipes
            mapeamento_equipes = {}
            corretores = df['corretor'].unique()
            for i, corretor in enumerate(corretores):
                mapeamento_equipes[corretor] = equipes[i % len(equipes)]
            
            df['equipe'] = df['corretor'].map(mapeamento_equipes)
            
            # Selecionar colunas finais
            df_final = df[['data_pagamento', 'data_venda_original', 'corretor', 'equipe', 'valor_venda', 'comissao_percentual', 'valor_comissao', 'status_pagamento']]
            
            logger.info(f"Gerados {len(df_final)} registros de dados de ganhos")
            return df_final
        except Exception as e:
            logger.error(f"Erro ao gerar dados de ganhos: {str(e)}")
            return pd.DataFrame()
    
    def gerar_dados_leads(self, num_registros=500, periodo_dias=120):
        """
        Gera dados simulados de leads.
        
        Args:
            num_registros (int): Número de registros a serem gerados
            periodo_dias (int): Período em dias para distribuição das datas
            
        Returns:
            pandas.DataFrame: DataFrame com dados simulados de leads
        """
        try:
            # Definir dados base
            datas = [datetime.now() - timedelta(days=i) for i in range(periodo_dias)]
            origens = ['Site', 'Indicação', 'Portais', 'Redes Sociais', 'Anúncios', 'Eventos', 'Outros']
            tipos_interesse = ['Apartamento', 'Casa', 'Terreno', 'Comercial', 'Rural']
            corretores = [f"Corretor {i}" for i in range(1, 11)]
            
            # Definir taxas de conversão por origem
            taxas_conversao = {
                'Site': 0.25,
                'Indicação': 0.45,
                'Portais': 0.20,
                'Redes Sociais': 0.15,
                'Anúncios': 0.18,
                'Eventos': 0.30,
                'Outros': 0.10
            }
            
            # Gerar dados aleatórios
            np.random.seed(43)  # Semente diferente da produção
            
            # Gerar origens com distribuição não uniforme
            probabilidades_origens = [0.3, 0.15, 0.25, 0.15, 0.1, 0.03, 0.02]
            origens_lead = np.random.choice(origens, num_registros, p=probabilidades_origens)
            
            # Gerar datas de captação
            pesos_datas = np.linspace(1, 2, periodo_dias)  # Mais peso para datas recentes
            pesos_datas = pesos_datas / sum(pesos_datas)
            datas_captacao = np.random.choice(datas, num_registros, p=pesos_datas)
            
            # Gerar status de conversão baseado na origem
            convertidos = []
            for origem in origens_lead:
                taxa = taxas_conversao[origem]
                convertidos.append(np.random.choice([True, False], p=[taxa, 1-taxa]))
            
            # Criar DataFrame
            df = pd.DataFrame({
                'data_captacao': datas_captacao,
                'origem': origens_lead,
                'tipo_interesse': np.random.choice(tipos_interesse, num_registros),
                'valor_estimado': np.random.normal(500000, 200000, num_registros).round(2),
                'convertido': convertidos,
                'corretor_responsavel': np.random.choice(corretores, num_registros)
            })
            
            # Adicionar data de conversão para leads convertidos
            df['data_conversao'] = None
            for i in range(len(df)):
                if df.iloc[i]['convertido']:
                    # Tempo até conversão varia de 1 a 30 dias
                    dias_ate_conversao = np.random.randint(1, 30)
                    df.loc[i, 'data_conversao'] = df.iloc[i]['data_captacao'] + timedelta(days=dias_ate_conversao)
            
            # Adicionar status do lead
            df['status'] = 'Não contatado'
            for i in range(len(df)):
                if df.iloc[i]['convertido']:
                    df.loc[i, 'status'] = 'Convertido'
                else:
                    # Distribuir status para não convertidos
                    df.loc[i, 'status'] = np.random.choice(
                        ['Em negociação', 'Contatado', 'Não interessado', 'Não contatado'],
                        p=[0.3, 0.4, 0.2, 0.1]
                    )
            
            # Adicionar tendência temporal na taxa de conversão
            # Melhoria gradual nos últimos 30 dias
            for i in range(len(df)):
                data = df.iloc[i]['data_captacao']
                if (datetime.now() - data).days <= 30:
                    # Aumentar chance de conversão em 20% para leads recentes
                    if not df.iloc[i]['convertido'] and np.random.random() < 0.2:
                        df.loc[i, 'convertido'] = True
                        dias_ate_conversao = np.random.randint(1, 15)
                        df.loc[i, 'data_conversao'] = data + timedelta(days=dias_ate_conversao)
                        df.loc[i, 'status'] = 'Convertido'
            
            logger.info(f"Gerados {len(df)} registros de dados de leads")
            return df
        except Exception as e:
            logger.error(f"Erro ao gerar dados de leads: {str(e)}")
            return pd.DataFrame()
    
    def salvar_dados(self, df_producao, df_ganhos, df_leads):
        """
        Salva os DataFrames gerados em arquivos Excel.
        
        Args:
            df_producao (pandas.DataFrame): DataFrame de produção
            df_ganhos (pandas.DataFrame): DataFrame de ganhos
            df_leads (pandas.DataFrame): DataFrame de leads
            
        Returns:
            bool: True se os dados foram salvos com sucesso, False caso contrário
        """
        try:
            # Verificar se o diretório existe
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            
            # Salvar arquivos
            arquivo_producao = os.path.join(self.output_dir, 'dados_producao.xlsx')
            arquivo_ganhos = os.path.join(self.output_dir, 'dados_ganhos.xlsx')
            arquivo_leads = os.path.join(self.output_dir, 'dados_leads.xlsx')
            
            df_producao.to_excel(arquivo_producao, index=False)
            df_ganhos.to_excel(arquivo_ganhos, index=False)
            df_leads.to_excel(arquivo_leads, index=False)
            
            logger.info(f"Dados de produção salvos em: {arquivo_producao}")
            logger.info(f"Dados de ganhos salvos em: {arquivo_ganhos}")
            logger.info(f"Dados de leads salvos em: {arquivo_leads}")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar dados: {str(e)}")
            return False
    
    def gerar_todos_dados(self, num_producao=200, num_leads=500, periodo_dias=100):
        """
        Gera e salva todos os dados de exemplo.
        
        Args:
            num_producao (int): Número de registros de produção
            num_leads (int): Número de registros de leads
            periodo_dias (int): Período em dias para distribuição das datas
            
        Returns:
            bool: True se os dados foram gerados e salvos com sucesso, False caso contrário
        """
        try:
            # Gerar dados
            df_producao = self.gerar_dados_producao(num_producao, periodo_dias)
            df_ganhos = self.gerar_dados_ganhos(df_producao)
            df_leads = self.gerar_dados_leads(num_leads, periodo_dias)
            
            # Salvar dados
            sucesso = self.salvar_dados(df_producao, df_ganhos, df_leads)
            
            if sucesso:
                logger.info("Todos os dados foram gerados e salvos com sucesso")
            else:
                logger.error("Falha ao salvar os dados gerados")
            
            return sucesso
        except Exception as e:
            logger.error(f"Erro ao gerar todos os dados: {str(e)}")
            return False


# Função para uso direto do script
def main():
    """
    Função principal para execução direta do script.
    """
    # Diretório base do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    
    # Criar diretório de saída se não existir
    output_dir = os.path.join(base_dir, 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Gerar dados
    generator = DataGenerator(data_dir)
    sucesso = generator.gerar_todos_dados(num_producao=200, num_leads=500, periodo_dias=100)
    
    if sucesso:
        print("Dados de exemplo gerados com sucesso!")
    else:
        print("Falha ao gerar dados de exemplo.")


if __name__ == "__main__":
    main()
