#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de instalação para o sistema de automação de análise de dados imobiliários
Este script verifica e instala todas as dependências necessárias
"""

import sys
import subprocess
import os
import platform
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instalacao.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('setup')

def verificar_python():
    """
    Verifica se a versão do Python é compatível.
    
    Returns:
        bool: True se a versão é compatível, False caso contrário
    """
    versao_atual = sys.version_info
    versao_minima = (3, 10)
    
    if versao_atual >= versao_minima:
        logger.info(f"Versão do Python compatível: {sys.version}")
        return True
    else:
        logger.error(f"Versão do Python incompatível: {sys.version}")
        logger.error(f"É necessário Python {versao_minima[0]}.{versao_minima[1]} ou superior")
        return False

def instalar_dependencias():
    """
    Instala as dependências necessárias.
    
    Returns:
        bool: True se todas as dependências foram instaladas com sucesso, False caso contrário
    """
    dependencias = [
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'scikit-learn',
        'statsmodels',
        'reportlab',
        'openpyxl',
        'jinja2',
        'weasyprint'
    ]
    
    logger.info("Instalando dependências...")
    
    for dep in dependencias:
        logger.info(f"Instalando {dep}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            logger.info(f"{dep} instalado com sucesso")
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao instalar {dep}: {str(e)}")
            return False
    
    logger.info("Todas as dependências foram instaladas com sucesso")
    return True

def verificar_estrutura_diretorios():
    """
    Verifica e cria a estrutura de diretórios necessária.
    
    Returns:
        bool: True se a estrutura foi verificada/criada com sucesso, False caso contrário
    """
    diretorios = ['data', 'output', 'templates']
    
    logger.info("Verificando estrutura de diretórios...")
    
    try:
        for dir in diretorios:
            if not os.path.exists(dir):
                os.makedirs(dir)
                logger.info(f"Diretório '{dir}' criado")
            else:
                logger.info(f"Diretório '{dir}' já existe")
        
        logger.info("Estrutura de diretórios verificada com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao verificar/criar estrutura de diretórios: {str(e)}")
        return False

def main():
    """
    Função principal de instalação.
    """
    logger.info("Iniciando instalação do sistema de automação de análise de dados imobiliários")
    
    # Verificar versão do Python
    if not verificar_python():
        logger.error("Instalação abortada devido a versão incompatível do Python")
        return False
    
    # Instalar dependências
    if not instalar_dependencias():
        logger.error("Instalação abortada devido a falha na instalação de dependências")
        return False
    
    # Verificar estrutura de diretórios
    if not verificar_estrutura_diretorios():
        logger.error("Instalação abortada devido a falha na verificação/criação de diretórios")
        return False
    
    logger.info("Instalação concluída com sucesso!")
    
    # Instruções finais
    print("\n" + "="*80)
    print("INSTALAÇÃO CONCLUÍDA COM SUCESSO")
    print("="*80)
    print("Para executar o sistema, use o comando:")
    print("python scripts/main.py")
    print("\nPara gerar dados de exemplo para testes:")
    print("python scripts/main.py --gerar-dados")
    print("\nPara mais informações, consulte a documentação (documentacao.md)")
    print("="*80)
    
    return True

if __name__ == "__main__":
    main()
