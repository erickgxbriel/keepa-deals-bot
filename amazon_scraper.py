import re
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from curl_cffi import requests

logger = logging.getLogger(__name__)

class AmazonDealScraper:
    """
    Monitorador de alta precisão e velocidade para Amazon Brasil.
    Captura tanto novidades quanto variações bruscas de preço em tempo real.
    """
    def __init__(self):
        self.session = requests.Session(impersonate="chrome120")
        self.headers = {
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Referer": "https://www.google.com.br/"
        }

    def fetch_url_items(self, url: str) -> List[Dict[str, Any]]:
        items_found = []
        try:
            res = self.session.get(url, headers=self.headers, timeout=12)
            if res.status_code != 200:
                return items_found

            soup = BeautifulSoup(res.text, "html.parser")
            divs = soup.select("div[data-asin]")

            for div in divs:
                asin = div.get("data-asin", "").strip()
                if not asin or len(asin) != 10:
                    continue

                title_el = div.select_one("h2 span")
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)

                price_whole = div.select_one("span.a-price-whole")
                if not price_whole:
                    continue

                raw_whole = re.sub(r"[^0-9]", "", price_whole.get_text(strip=True))
                price_frac = div.select_one("span.a-price-fraction")
                frac_str = re.sub(r"[^0-9]", "", price_frac.get_text(strip=True)) if price_frac else "00"

                try:
                    current_price = float(f"{raw_whole}.{frac_str}")
                except ValueError:
                    continue

                # Identifica desconto se houver preço riscado ("De R$ ...")
                drop_percent = 0.0
                old_p_el = div.select_one("span.a-price.a-text-price span.a-offscreen")
                if old_p_el:
                    try:
                        old_num = float(re.sub(r"[^0-9]", "", old_p_el.get_text(strip=True))) / 100.0
                        if old_num > current_price:
                            drop_percent = ((old_num - current_price) / old_num) * 100.0
                    except Exception:
                        pass

                # Imagem
                img_el = div.select_one("img.s-image")
                image_url = img_el.get("src") if img_el else None

                items_found.append({
                    "asin": asin,
                    "title": title,
                    "price": current_price,
                    "drop_percent": drop_percent,
                    "image_url": image_url,
                    "link": f"https://www.amazon.com.br/dp/{asin}"
                })
        except Exception as e:
            logger.warning(f"Erro ao acessar {url}: {e}")

        return items_found

    def search_deals(self) -> List[Dict[str, Any]]:
        deals = []
        
        # Estratégia de busca com filtros de ordenação da Amazon:
        # 1. date-desc-rank: Itens recém-cadastrados / atualizados recentemente
        # 2. price-asc-rank: Menor preço
        # 3. exact-aware-popularity-rank: Mais relevantes / ofertas
        terms = [
            # Mini PCs (alta prioridade)
            ("mini+pc+ryzen", "date-desc-rank"),
            ("mini+pc+ryzen", "price-asc-rank"),
            ("mini+pc+intel+n100", "price-asc-rank"),
            ("acemagician+mini+pc", "date-desc-rank"),
            ("beelink+mini+pc", "date-desc-rank"),
            ("gmktec+mini+pc", "date-desc-rank"),
            
            # Peças de PC & SSD
            ("ssd+nvme+1tb", "price-asc-rank"),
            ("ssd+nvme+2tb", "price-asc-rank"),
            ("monitor+gamer+144hz", "price-asc-rank"),
            ("placa+de+video+rtx", "price-asc-rank"),
            
            # Games
            ("controle+xbox+series", "price-asc-rank"),
            ("dualsense+ps5", "price-asc-rank"),
            ("nintendo+switch+oled", "price-asc-rank"),
            ("mouse+logitech+g502", "price-asc-rank"),
            
            # Instrumentos
            ("violao+yamaha", "price-asc-rank"),
            ("guitarra+tagima", "price-asc-rank"),
            ("ukulele+tagima", "price-asc-rank"),
            
            # Moda / Marcas
            ("camiseta+aeropostale+masculina", "price-asc-rank"),
            ("jaqueta+columbia+fleece", "price-asc-rank"),
            ("calca+levis+masculina", "price-asc-rank"),
            ("moletom+hanes", "price-asc-rank"),
            ("camiseta+calvin+klein", "price-asc-rank")
        ]

        seen_asins = set()
        for q, sort_order in terms:
            url = f"https://www.amazon.com.br/s?k={q}&s={sort_order}"
            page_items = self.fetch_url_items(url)
            for item in page_items:
                if item["asin"] not in seen_asins:
                    seen_asins.add(item["asin"])
                    deals.append(item)

        return deals
