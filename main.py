import time
import logging
import sys
from config import CHECK_INTERVAL_SECONDS
from database import Database
from hardware_parser import HardwareParser
from telegram_notifier import TelegramNotifier
from amazon_scraper import AmazonDealScraper

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

        eval_result = HardwareParser.evaluate_deal(title, price, drop_percent)
        if not eval_result["is_deal"]:
            return

        if self.db.is_already_notified(asin, price):
            return

        logger.info(f"🔥 OFERTA ENCONTRADA: {title[:50]}... | R$ {price:.2f} (Tier: {eval_result['tier']})")
        
        sent = self.notifier.send_deal_alert(
            title=title,
            asin=asin,
            current_price=price,
            drop_percent=drop_percent,
            tier=eval_result["tier"],
            cpu=eval_result.get("cpu", "N/A"),
            ram=eval_result.get("ram", "N/A"),
            storage=eval_result.get("storage", "N/A"),
            image_url=image_url
        )

        if sent:
            self.db.save_deal(asin, title, price, drop_percent, eval_result["tier"])
            logger.info(f"✅ Alerta enviado para o Telegram com sucesso! (ASIN: {asin})")

    def run(self):
        logger.info("==================================================")
        logger.info("🚀 MONITORADOR AMAZON BR (ALTA VELOCIDADE 24/7)")
        logger.info(f"⏱️ Intervalo de Checagem: {CHECK_INTERVAL_SECONDS} segundos")
        logger.info("==================================================")

        if self.notifier.send_test_message():
            logger.info("📱 Notificação de teste enviada ao Telegram com sucesso!")
        else:
            logger.warning("⚠️ Não foi possível enviar teste ao Telegram. Verifique o arquivo .env!")

        cycle = 1
        while self.running:
            try:
                logger.info(f"\n--- [Ciclo #{cycle}] Varrendo ofertas na Amazon Brasil... ---")
                
                deals = self.amazon_direct.search_deals()
                logger.info(f"Amazon retornou {len(deals)} produtos para análise.")
                
                processed_count = 0
                for deal in deals:
                    self.process_deal(deal)
                    processed_count += 1

                cycle += 1
                time.sleep(CHECK_INTERVAL_SECONDS)

            except KeyboardInterrupt:
                logger.info("Parando o monitorador...")
                self.running = False
            except Exception as e:
                logger.error(f"Erro durante o ciclo de monitoramento: {e}", exc_info=True)
                time.sleep(15)

        logger.info("Monitorador encerrado.")

if __name__ == "__main__":
    monitor = DealMonitor()
    monitor.run()
