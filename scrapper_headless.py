#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json

class CEBASScraper:
    def __init__(self):
        self.webhook_url = os.getenv('WEBHOOK_URL', '')
        self.base_url = 'https://www.gov.br/pt-br/noticias'
        self.search_term = 'CEBAS'
        
    def scrape(self):
        """Executa o scraping das notícias CEBAS"""
        try:
            print(f"🚀 Iniciando scraper - {datetime.now().isoformat()}")
            
            # Opções do Chrome headless
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            
            # Inicializar driver
            driver = webdriver.Chrome(options=options)
            
            # Acessar URL de busca
            search_url = f"{self.base_url}?SearchableText={self.search_term}"
            print(f"📡 Acessando: {search_url}")
            driver.get(search_url)
            
            # Aguardar carregamento do conteúdo
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "article")))
            
            # Extrair HTML
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Processar notícias
            noticias = self._processar_noticias(soup)
            
            # Fechar driver
            driver.quit()
            
            print(f"✅ Encontradas {len(noticias)} notícias")
            
            # Enviar para webhook
            if noticias:
                self._enviar_webhook(noticias)
            
            return noticias
            
        except Exception as e:
            print(f"❌ Erro no scraper: {str(e)}")
            return []
    
    def _processar_noticias(self, soup):
        """Processa HTML e extrai notícias"""
        noticias = []
        articles = soup.find_all('article', class_='tileItem')
        
        for article in articles:
            try:
                titulo = article.find('h2')
                titulo_text = titulo.get_text(strip=True) if titulo else 'Sem título'
                
                link_elem = article.find('a', href=True)
                link = link_elem['href'] if link_elem else 'https://www.gov.br/'
                if not link.startswith('http'):
                    link = f"https://www.gov.br{link}"
                
                descricao_elem = article.find('p', class_='description')
                descricao = descricao_elem.get_text(strip=True) if descricao_elem else ''
                
                noticias.append({
                    'titulo': titulo_text,
                    'link': link,
                    'descricao': descricao,
                    'data_coleta': datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"Erro ao processar article: {e}")
                continue
        
        return noticias
    
    def _enviar_webhook(self, dados):
        """Envia dados para webhook do n8n"""
        if not self.webhook_url:
            print("⚠️  WEBHOOK_URL não configurada")
            return
        
        try:
            payload = {
                'noticias': dados,
                'timestamp': datetime.now().isoformat(),
                'fonte': 'Railway CEBAS Scraper'
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ Dados enviados para n8n com sucesso!")
            else:
                print(f"⚠️  Status {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao enviar webhook: {str(e)}")

if __name__ == '__main__':
    scraper = CEBASScraper()
    scraper.scrape()
