import time
import logging
from typing import List, Dict, Any
from playwright.sync_api import sync_playwright
from playwright_stealth.stealth import Stealth
from config import KEEPA_DEALS_TARGET_URL

logger = logging.getLogger(__name__)

class KeepaScraper:
    def __init__(self, user_data_dir: str = "./browser_session"):
        self.user_data_dir = user_data_dir
        self.playwright = None
        self.browser_context = None
        self.page = None
        self.deals_url = KEEPA_DEALS_TARGET_URL

    def start(self, headless: bool = True):
        self.playwright = sync_playwright().start()
        self.browser_context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=headless,
            viewport={'width': 1366, 'height': 768},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        self.page = self.browser_context.new_page()
        Stealth().apply_stealth_sync(self.page)
        logger.info("Navegador Keepa inicializado com sucesso.")

    def fetch_deals(self) -> List[Dict[str, Any]]:
        deals = []
        if not self.page:
            return deals

        try:
            # Navega para a URL com as categorias filtradas
            if self.page.url != self.deals_url:
                logger.info("Navegando para o feed filtrado de Deals no Keepa...")
                self.page.goto(self.deals_url, timeout=60000, wait_until="domcontentloaded")
                time.sleep(6)
            else:
                self.page.keyboard.press("F5")
                time.sleep(4)

            self.page.wait_for_timeout(3000)

            extracted_items = self.page.evaluate(r'''() => {
                const results = [];
                const rows = document.querySelectorAll('tr[id^="deal_"], .dealRow, #dealTable tbody tr, table tbody tr');
                
                rows.forEach(row => {
                    try {
                        const titleEl = row.querySelector('.dealTitle, a[title], td a, a.deal-title');
                        const priceEl = row.querySelector('.dealPrice, .currentPrice, td:nth-child(5), td[class*="price"]');
                        const dropEl = row.querySelector('.dealDrop, .percentDrop, td:nth-child(6), td[class*="drop"]');
                        const imgEl = row.querySelector('img');
                        const linkEl = row.querySelector('a[href*="/dp/"], a[href*="amazon."]');
                        
                        let asin = "";
                        let link = linkEl ? linkEl.getAttribute('href') : "";
                        if (link) {
                            const match = link.match(/\/dp\/([A-Z0-9]{10})/i);
                            if (match) asin = match[1];
                        }
                        
                        const title = titleEl ? (titleEl.innerText || titleEl.getAttribute('title') || "") : "";
                        
                        if (title && (priceEl || asin)) {
                            results.push({
                                title: title,
                                priceText: priceEl ? priceEl.innerText : "",
                                dropText: dropEl ? dropEl.innerText : "",
                                asin: asin,
                                imageUrl: imgEl ? imgEl.getAttribute('src') : "",
                                link: link
                            });
                        }
                    } catch (e) {}
                });
                return results;
            }''')

            for item in extracted_items:
                title = item.get("title", "").strip()
                asin = item.get("asin", "").strip()
                if not title:
                    continue
                
                price_str = item.get("priceText", "").replace("R$", "").replace(".", "").replace(",", ".").strip()
                try:
                    price = float(price_str)
                except ValueError:
                    price = 0.0

                drop_str = item.get("dropText", "").replace("%", "").replace("-", "").strip()
                try:
                    drop_percent = float(drop_str)
                except ValueError:
                    drop_percent = 0.0

                deals.append({
                    "title": title,
                    "asin": asin,
                    "price": price,
                    "drop_percent": drop_percent,
                    "image_url": item.get("imageUrl"),
                    "link": item.get("link")
                })

        except Exception as e:
            logger.error(f"Erro ao buscar deals no Keepa: {e}")

        return deals

    def stop(self):
        if self.browser_context:
            self.browser_context.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Navegador finalizado.")
