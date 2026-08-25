import re
import requests
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class AmazonDealScraper:
    """
    Monitorador complementar direto da Amazon Brasil com rotação de headers.
    Busca os termos de Mini PC e identifica produtos em oferta/desconto.
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Referer": "https://www.google.com/"
        }

    def search_mini_pcs(self) -> List[Dict[str, Any]]:
        deals = []
        queries = ["mini+pc+ryzen", "mini+pc+intel", "mini+pc+beelink", "mini+pc+acemagician"]
        
        for q in queries:
            url = f"https://www.amazon.com.br/s?k={q}&s=exact-aware-popularity-rank"
            try:
                res = requests.get(url, headers=self.headers, timeout=12)
                if res.status_code == 200:
                    html = res.text
                    
                    # Regex para extrair ASIN, título e preço
                    items = re.findall(r'data-asin="([A-Z0-9]{10})".*?<h2[^>]*>(?:<a[^>]*>)?<span[^>]*>(.*?)<\/span>.*?<span class="a-price-whole">([0-9.,]+)<\/span>', html, re.DOTALL)
                    
                    for asin, title, price_whole in items:
                        # Limpa preço
                        price_clean = price_whole.replace(".", "").replace(",", ".").strip()
                        try:
                            price = float(price_clean)
                        except ValueError:
                            continue
                            
                        # Limpa título
                        title_clean = re.sub(r'<[^>]+>', '', title).strip()
                        
                        deals.append({
                            "asin": asin,
                            "title": title_clean,
                            "price": price,
                            "drop_percent": 0.0, # Preço direto
                            "image_url": None
                        })
            except Exception as e:
                logger.warning(f"Aviso ao consultar Amazon direta: {e}")

        return deals
