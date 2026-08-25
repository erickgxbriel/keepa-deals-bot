import re
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from curl_cffi import requests

logger = logging.getLogger(__name__)

class AmazonDealScraper:
    """
    Monitorador de alta precisão e velocidade para Amazon Brasil usando TLS Impersonate e BeautifulSoup.
    """
    def __init__(self):
        self.session = requests.Session(impersonate="chrome120")
        self.headers = {
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Referer": "https://www.google.com.br/"
        }

    def search_deals(self) -> List[Dict[str, Any]]:
        deals = []
        
        # Categorias de busca na Amazon Brasil
        queries = [
            # Mini PCs
            "mini+pc+ryzen", "mini+pc+intel+n100", "mini+pc+32gb", "beelink+mini+pc", "acemagician+mini+pc", "gmktec+mini+pc",
            # Hardware & SSD
            "ssd+nvme+1tb", "ssd+nvme+2tb", "monitor+gamer+144hz", "placa+de+video+rtx",
            # Games & Controles
            "controle+xbox+series", "dualsense+ps5", "nintendo+switch+oled", "headset+hyperx", "mouse+logitech+g502",
            # Instrumentos
            "violao+yamaha", "guitarra+tagima", "ukulele+tagima", "bateria+eletronica",
            # Moda / Marcas
            "camiseta+aeropostale+masculina", "jaqueta+columbia+fleece", "calca+levis+511", "moletom+hanes", "camiseta+calvin+klein"
        ]

        for q in queries:
            try:
                url = f"https://www.amazon.com.br/s?k={q}&s=exact-aware-popularity-rank"
                res = self.session.get(url, headers=self.headers, timeout=12)
                if res.status_code != 200:
                    continue

                soup = BeautifulSoup(res.text, "html.parser")
                items = soup.select("div[data-asin]")

                for div in items:
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

                    # Queda / Preço Riscado
                    drop_percent = 0.0
                    old_p_el = div.select_one("span.a-price.a-text-price span.a-offscreen")
                    if old_p_el:
                        try:
                            old_num = float(re.sub(r"[^0-9]", "", old_p_el.get_text(strip=True))) / 100.0
                            if old_num > current_price:
                                drop_percent = ((old_num - current_price) / old_num) * 100.0
                        except Exception:
                            pass

                    # Imagem do produto
                    img_el = div.select_one("img.s-image")
                    image_url = img_el.get("src") if img_el else None

                    deals.append({
                        "asin": asin,
                        "title": title,
                        "price": current_price,
                        "drop_percent": drop_percent,
                        "image_url": image_url,
                        "link": f"https://www.amazon.com.br/dp/{asin}"
                    })

            except Exception as e:
                logger.warning(f"Erro ao buscar termo '{q}': {e}")

        return deals
