import time
import logging
import signal
import sys
from config import CHECK_INTERVAL_SECONDS
from database import Database
from hardware_parser import HardwareParser
from telegram_notifier import TelegramNotifier
from keepa_scraper import KeepaScraper
from amazon_scraper import AmazonDealScraper

# Configuração de Logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

class DealMonitor:
    def __init__(self):
        self.db = Database()
        self.notifier = TelegramNotifier()
        self.keepa = KeepaScraper()
        self.amazon_direct = AmazonDealScraper()
        self.running = True

    def process_deal(self, deal: dict):
        asin = deal.get("asin")
        title = deal.get("title")
        price = deal.get("price")
        drop_percent = deal.get("drop_percent", 0.0)
        image_url = deal.get("image_url")

        if not asin or not title or price <= 0:
            return

        # 1. Avalia hardware e custo-benefício
        eval_result = HardwareParser.evaluate_deal(title, price, drop_percent)
        
        if not eval_result["is_deal"]:
            return

        # 2. Verifica se já notificamos esse produto por preço igual/menor
        if self.db.is_already_notified(asin, price):
            return

        # 3. Dispara alerta urgente no Telegram
        logger.info(f"🔥 OFERTA ENCONTRADA: {title[:50]}... | R$ {price:.2f} (Tier: {eval_result['tier']})")
        
        sent = self.notifier.send_deal_alert(
            title=title,
            asin=asin,
            current_price=price,
            drop_percent=drop_percent,
            tier=eval_result["tier"],
            cpu=eval_result["cpu"],
            ram=eval_result["ram"],
            storage=eval_result["storage"],
            image_url=image_url
        )

        # 4. Registra no banco de dados local
        if sent:
            self.db.save_deal(
                asin=asin,
                title=title,
                price=price,
                drop_percent=drop_percent,
                tier=eval_result["tier"]
            )
            logger.info(f"✅ Alerta enviado para o Telegram com sucesso! (ASIN: {asin})")

    def run(self):
        logger.info("==================================================")
        logger.info("🚀 INICIANDO MONITORADOR DE PROMOÇÕES DE MINI PC")
        logger.info(f"⏱️ Intervalo de Checagem: {CHECK_INTERVAL_SECONDS} segundos")
        logger.info("==================================================")

        # Testa conexão do bot no Telegram
        if self.notifier.send_test_message():
            logger.info("📱 Notificação de teste enviada ao Telegram com sucesso!")
        else:
            logger.warning("⚠️ Não foi possível enviar teste ao Telegram. Verifique seu arquivo .env!")

        # Inicializa o navegador Playwright
        try:
            self.keepa.start(headless=True)
        except Exception as e:
            logger.error(f"Erro ao inicializar Playwright: {e}")

        cycle = 1
        while self.running:
            try:
                logger.info(f"\n--- [Ciclo #{cycle}] Buscando novas ofertas... ---")
                
                # 1. Busca ofertas no Keepa Deals
                keepa_deals = self.keepa.fetch_deals()
                logger.info(f"Keepa retornou {len(keepa_deals)} itens.")
                for deal in keepa_deals:
                    self.process_deal(deal)

                # 2. Busca ofertas diretas na Amazon
                amazon_deals = self.amazon_direct.search_mini_pcs()
                logger.info(f"Amazon direta retornou {len(amazon_deals)} itens.")
                for deal in amazon_deals:
                    self.process_deal(deal)

                cycle += 1
                time.sleep(CHECK_INTERVAL_SECONDS)

            except KeyboardInterrupt:
                logger.info("Parando o monitorador...")
                self.running = False
            except Exception as e:
                logger.error(f"Erro durante o ciclo de monitoramento: {e}", exc_info=True)
                time.sleep(15)

        self.keepa.stop()
        logger.info("Monitorador encerrado.")

if __name__ == "__main__":
    monitor = DealMonitor()
    monitor.run()
