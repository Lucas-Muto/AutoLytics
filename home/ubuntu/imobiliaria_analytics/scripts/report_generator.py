#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de geração de relatório PDF para análise imobiliária
Este script gera um relatório PDF com insights estratégicos baseados nas análises realizadas
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import logging
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.platypus import PageBreak, ListFlowable, ListItem
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output', 'relatorio.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('report_generator')

class ReportGenerator:
    """
    Classe para geração de relatório PDF com insights estratégicos.
    """
    
    def __init__(self, resultados_analise, output_dir):
        """
        Inicializa o gerador de relatório.
        
        Args:
            resultados_analise (dict): Resultados da análise de dados
            output_dir (str): Diretório onde o relatório PDF será salvo
        """
        self.resultados = resultados_analise
        self.output_dir = output_dir
        self.styles = getSampleStyleSheet()
        self._configurar_estilos()
        logger.info(f"Gerador de relatório inicializado. Diretório de saída: {output_dir}")
    
    def _configurar_estilos(self):
        """
        Configura estilos personalizados para o relatório.
        """
        # Estilo para título principal
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            textColor=colors.darkblue
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            textColor=colors.darkblue
        ))
        
        # Estilo para seções
        self.styles.add(ParagraphStyle(
            name='Secao',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            textColor=colors.darkblue
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leading=14
        ))
        
        # Estilo para insights
        self.styles.add(ParagraphStyle(
            name='Insight',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leading=14,
            leftIndent=20,
            borderWidth=1,
            borderColor=colors.lightblue,
            borderPadding=5,
            borderRadius=5,
            backColor=colors.lightblue.clone(alpha=0.2)
        ))
        
        # Estilo para recomendações
        self.styles.add(ParagraphStyle(
            name='Recomendacao',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leading=14,
            leftIndent=20,
            borderWidth=1,
            borderColor=colors.green,
            borderPadding=5,
            borderRadius=5,
            backColor=colors.green.clone(alpha=0.2)
        ))
        
        # Estilo para alertas
        self.styles.add(ParagraphStyle(
            name='Alerta',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leading=14,
            leftIndent=20,
            borderWidth=1,
            borderColor=colors.red,
            borderPadding=5,
            borderRadius=5,
            backColor=colors.red.clone(alpha=0.2)
        ))
        
        # Estilo para rodapé
        self.styles.add(ParagraphStyle(
            name='Rodape',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey
        ))
        
        logger.info("Estilos personalizados configurados")
    
    def _criar_cabecalho(self):
        """
        Cria o cabeçalho do relatório.
        
        Returns:
            list: Lista de elementos para o cabeçalho
        """
        elementos = []
        
        # Título principal
        titulo = Paragraph("Relatório Estratégico de Análise Imobiliária", self.styles['TituloPrincipal'])
        elementos.append(titulo)
        
        # Data do relatório
        data_atual = datetime.now().strftime("%d/%m/%Y")
        data_texto = Paragraph(f"Data: {data_atual}", self.styles['TextoNormal'])
        elementos.append(data_texto)
        
        # Descrição do relatório
        descricao = Paragraph(
            "Este relatório apresenta uma análise estratégica dos dados imobiliários, "
            "incluindo tendências de vendas, desempenho de corretores, conversão de leads "
            "e oportunidades de mercado. As recomendações são baseadas em análises estatísticas "
            "e visam auxiliar na tomada de decisões para maximizar os resultados da empresa.",
            self.styles['TextoNormal']
        )
        elementos.append(descricao)
        
        elementos.append(Spacer(1, 0.5*cm))
        
        return elementos
    
    def _criar_resumo_executivo(self):
        """
        Cria a seção de resumo executivo.
        
        Returns:
            list: Lista de elementos para o resumo executivo
        """
        elementos = []
        
        # Título da seção
        titulo = Paragraph("1. Resumo Executivo", self.styles['Subtitulo'])
        elementos.append(titulo)
        
        # Principais métricas
        metricas = self.resultados.get('metricas', {})
        
        # Métricas de produção
        producao = metricas.get('producao', {})
        if producao:
            total_vendas = producao.get('total_vendas', 0)
            vgv_total = producao.get('vgv_total', 0)
            vgv_medio = producao.get('vgv_medio', 0)
            
            texto_producao = Paragraph(
                f"<b>Produção:</b> Total de {total_vendas} vendas realizadas, "
                f"com VGV total de R$ {vgv_total:,.2f} e valor médio de R$ {vgv_medio:,.2f} por transação.",
                self.styles['TextoNormal']
            )
            elementos.append(texto_producao)
        
        # Métricas de ganhos
        ganhos = metricas.get('ganhos', {})
        if ganhos:
            total_comissoes = ganhos.get('total_comissoes', 0)
            comissao_media = ganhos.get('comissao_media', 0)
            
            texto_ganhos = Paragraph(
                f"<b>Ganhos:</b> Total de R$ {total_comissoes:,.2f} em comissões, "
                f"com média de R$ {comissao_media:,.2f} por transação.",
                self.styles['TextoNormal']
            )
            elementos.append(texto_ganhos)
        
        # Métricas de leads
        leads = metricas.get('leads', {})
        if leads:
            total_leads = leads.get('total_leads', 0)
            leads_convertidos = leads.get('leads_convertidos', 0)
            taxa_conversao = leads.get('taxa_conversao', 0) * 100
            
            texto_leads = Paragraph(
                f"<b>Leads:</b> Total de {total_leads} leads captados, "
                f"com {leads_convertidos} conversões ({taxa_conversao:.2f}% de taxa de conversão).",
                self.styles['TextoNormal']
            )
            elementos.append(texto_leads)
        
        elementos.append(Spacer(1, 0.3*cm))
        
        # Principais insights
        insights = self.resultados.get('insights', [])
        if insights:
            texto_insights = Paragraph("<b>Principais Insights:</b>", self.styles['TextoNormal'])
            elementos.append(texto_insights)
            
            # Filtrar insights de alto impacto
            insights_alto_impacto = [i for i in insights if i.get('impacto') == 'alto']
            
            # Se não houver insights de alto impacto, usar todos
            if not insights_alto_impacto:
                insights_alto_impacto = insights[:3]
            else:
                insights_alto_impacto = insights_alto_impacto[:3]
            
            for insight in insights_alto_impacto:
                texto = Paragraph(insight.get('descricao', ''), self.styles['Insight'])
                elementos.append(texto)
        
        elementos.append(Spacer(1, 0.3*cm))
        
        # Principais recomendações
        recomendacoes = self.resultados.get('recomendacoes', [])
        if recomendacoes:
            texto_recomendacoes = Paragraph("<b>Principais Recomendações:</b>", self.styles['TextoNormal'])
            elementos.append(texto_recomendacoes)
            
            # Filtrar recomendações de alta prioridade
            recomendacoes_alta = [r for r in recomendacoes if r.get('prioridade') == 'alta']
            
            # Se não houver recomendações de alta prioridade, usar todas
            if not recomendacoes_alta:
                recomendacoes_alta = recomendacoes[:3]
            else:
                recomendacoes_alta = recomendacoes_alta[:3]
            
            for recomendacao in recomendacoes_alta:
                texto = Paragraph(recomendacao.get('descricao', ''), self.styles['Recomendacao'])
                elementos.append(texto)
        
        elementos.append(PageBreak())
        
        return elementos
    
    def _criar_secao_producao(self):
        """
        Cria a seção de análise de produção.
        
        Returns:
            list: Lista de elementos para a seção de produção
        """
        elementos = []
        
        # Título da seção
        titulo = Paragraph("2. Análise de Produção", self.styles['Subtitulo'])
        elementos.append(titulo)
        
        # Descrição da seção
        descricao = Paragraph(
            "Esta seção apresenta a análise das vendas realizadas, incluindo tendências temporais, "
            "desempenho por tipo de imóvel e análise dos corretores mais produtivos.",
            self.styles['TextoNormal']
        )
        elementos.append(descricao)
        
        elementos.append(Spacer(1, 0.3*cm))
        
        # Tendências de vendas
        subtitulo = Paragraph("2.1. Tendências de Vendas", self.styles['Secao'])
        elementos.append(subtitulo)
        
        # Adicionar gráfico de tendências se disponível
        figuras = self.resultados.get('figuras', [])
        figura_tendencia = next((f for f in figuras if 'tendencia_vendas' in f.get('arquivo', '')), None)
        
        if figura_tendencia:
            caminho_figura = os.path.join(self.output_dir, figura_tendencia.get('arquivo', ''))
            if os.path.exists(caminho_figura):
                img = Image(caminho_figura, width=6*inch, height=3*inch)
                elementos.append(img)
                elementos.append(Spacer(1, 0.2*cm))
                
                # Legenda da figura
                legenda = Paragraph(
                    f"<i>{figura_tendencia.get('descricao', 'Tendências de vendas ao longo do tempo')}</i>",
                    self.styles['TextoNormal']
                )
                elementos.append(legenda)
        
        # Análise de tendências
        resultados_analise = self.resultados.get('resultados_analise', {})
        tendencias = resultados_analise.get('tendencias_vendas', {})
        
        if tendencias:
            tendencia_valor = tendencias.get('tendencia_valor', {})
            tendencia_qtd = tendencias.get('tendencia_quantidade', {})
            
            if tendencia_valor and tendencia_qtd:
                direcao_valor = tendencia_valor.get('direcao', 'estável')
                direcao_qtd = tendencia_qtd.get('direcao', 'estável')
                
                texto_tendencia = Paragraph(
                    f"A análise de tendências mostra que o valor total de vendas está em direção <b>{direcao_valor}</b>, "
                    f"enquanto a quantidade de vendas está em direção <b>{direcao_qtd}</b>.",
                    self.styles['TextoNormal']
                )
                elementos.append(texto_tendencia)
        
        # Insights relacionados a tendências
        insights = [i for i in self.resultados.get('insights', []) if i.get('categoria') == 'tendencia_vendas']
        if insights:
            for insight in insights:
                texto = Paragraph(insight.get('descricao', ''), self.styles['Insight'])
                elementos.append(texto)
        
        elementos.append(Spacer(1, 0.3*cm))
        
        # Desempenho de corretores
        subtitulo = Paragraph("2.2. Desempenho de Corretores", self.styles['Secao'])
        elementos.append(subtitulo)
        
        # Adicionar gráfico de desempenho se disponível
        figura_corretores = next((f for f in figuras if 'desempenho_corretores' in f.get('arquivo', '')), None)
        
        if figura_corretores:
            caminho_figura = os.path.join(self.output_dir, figura_corretores.get('arquivo', ''))
            if os.path.exists(caminho_figura):
                img = Image(caminho_figura, width=6*inch, height=3*inch)
                elementos.append(img)
                elementos.append(Spacer(1, 0.2*cm))
                
                # Legenda da figura
                legenda = Paragraph(
                    f"<i>{figura_corretores.get('descricao', 'Desempenho dos corretores em valor e quantidade de vendas')}</i>",
                    self.styles['TextoNormal']
                )
                elementos.append(legenda)
        
        # Análise de corretores
        desempenho_corretores = resultados_analise.get('desempenho_corretores', {})
        
        if desempenho_corretores:
            top_corretores = desempenho_corretores.get('top_corretores', [])
            
            if top_corretores and len(top_corretores) > 0:
                # Criar tabela com top corretores
                dados_tabela = [['Corretor', 'Valor Total (R$)', 'Valor Médio (R$)', 'Quantidade']]
                
                for corretor in top_corretores[:5]:  # Limitar a 5 corretores
                    dados_tabela.append([
                        corretor.get('corretor', ''),
                        f"{corretor.get('valor_total', 0):,.2f}",
                        f"{corretor.get('valor_medio', 0):,.2f}",
                        corretor.get('quantidade', 0)
                    ])
                
                tabela = Table(dados_tabela, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
                tabela.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                elementos.append(tabela)
                elementos.append(Spacer(1, 0.3*cm))
        
        # Insights relacionados a corretores
        insights = [i for i in self.resultados.get('insights', []) if i.get('categoria') == 'desempenho_corretores']
        if insights:
            for insight in insights:
                texto = Paragraph(insight.get('descricao', ''), self.styles['Insight'])
                elementos.append(texto)
        
        elementos.append(PageBreak())
        
        return elementos

    def gerar_relatorio(self, nome_arquivo):
        """
        Gera o relatório PDF completo.
        
        Args:
            nome_arquivo (str): Nome do arquivo PDF a ser gerado
            
        Returns:
            str: Caminho do arquivo PDF gerado ou None em caso de erro
        """
        try:
            # Criar caminho completo do arquivo
            caminho_pdf = os.path.join(self.output_dir, nome_arquivo)
            
            # Criar documento
            doc = SimpleDocTemplate(
                caminho_pdf,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Lista de elementos do relatório
            elementos = []
            
            # Adicionar seções
            elementos.extend(self._criar_cabecalho())
            elementos.extend(self._criar_resumo_executivo())
            
            # Gerar PDF
            doc.build(elementos)
            
            logger.info(f"Relatório PDF gerado com sucesso: {caminho_pdf}")
            return caminho_pdf
        except Exception as e:
            logger.error(f"Erro ao gerar relatório PDF: {str(e)}")
            return None


# Função para uso direto do script
def main():
    """
    Função principal para execução direta do script.
    """
    # Diretório base do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, 'output')
    
    # Carregar resultados da análise
    with open(os.path.join(output_dir, 'resultados_analise.json'), 'r', encoding='utf-8') as f:
        resultados = json.load(f)
    
    # Criar gerador de relatório
    generator = ReportGenerator(resultados, output_dir)
    
    # Gerar relatório
    data_atual = datetime.now().strftime("%Y%m%d")
    nome_arquivo = f"relatorio_estrategico_{data_atual}.pdf"
    
    caminho_relatorio = generator.gerar_relatorio(nome_arquivo)
    
    if caminho_relatorio:
        print(f"Relatório gerado com sucesso: {caminho_relatorio}")
    else:
        print("Falha na geração do relatório.")

if __name__ == "__main__":
    main()