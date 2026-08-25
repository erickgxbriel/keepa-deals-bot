import requests
import logging
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self, token: str = TELEGRAM_BOT_TOKEN, chat_id: str = TELEGRAM_CHAT_ID):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{self.token}"

    def send_deal_alert(self, title: str, asin: str, current_price: float, drop_percent: float, tier: str, cpu: str = "N/A", ram: str = "N/A", storage: str = "N/A", image_url: str = None) -> bool:
        if not self.token or not self.chat_id:
            logger.warning("Telegram Bot Token ou Chat ID não configurados!")
            return False

        amazon_url = f"https://www.amazon.com.br/dp/{asin}"
        
        tier_icons = {
            "ENTRY": "🟢 Mini PC Básico / Escritório",
            "MID": "🟡 Mini PC Intermediário",
            "HIGH": "🔥 Mini PC Alto Desempenho (Sweet Spot)",
            "ULTRA": "🚀 Mini PC Gamer / Top de Linha",
            "STORAGE": "💾 Armazenamento / SSD NVMe",
            "MONITOR": "🖥️ Monitor Gamer / Produtividade",
            "GPU": "🎮 Placa de Vídeo / GPU",
            "MEGA_DEAL": "⚡ MEGA OFERTA (Bug / Queima de Estoque)"
        }
        tier_label = tier_icons.get(tier, tier)

        # Monta a mensagem dependendo se tem detalhes de PC ou é geral
        if cpu != "N/A" and ram != "N/A":
            specs_text = (
                f"🧠 **Processador:** `{cpu}`\n"
                f"💾 **Memória RAM:** `{ram}`\n"
                f"💽 **Armazenamento:** `{storage}`\n\n"
            )
        else:
            specs_text = ""

        message = (
            f"⚡ **OPORTUNIDADE DETECTADA!** ⚡\n\n"
            f"🏷️ **{title}**\n\n"
            f"📊 **Categoria:** {tier_label}\n"
            f"{specs_text}"
            f"💰 **Preço Atual:** `R$ {current_price:,.2f}`\n"
            f"📉 **Queda de Preço:** `-{drop_percent:.0f}%`\n\n"
            f"🛒 **Link Amazon:** [Clique aqui para comprar na Amazon]({amazon_url})"
        )

        inline_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🛒 Comprar Agora na Amazon", "url": amazon_url}
                ]
            ]
        }

        try:
            if image_url:
                payload = {
                    "chat_id": self.chat_id,
                    "caption": message,
                    "parse_mode": "Markdown",
                    "photo": image_url,
                    "reply_markup": inline_keyboard
                }
                res = requests.post(f"{self.api_url}/sendPhoto", json=payload, timeout=10)
                if res.status_code == 200:
                    return True

            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False,
                "reply_markup": inline_keyboard
            }
            res = requests.post(f"{self.api_url}/sendMessage", json=payload, timeout=10)
            return res.status_code == 200
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem no Telegram: {e}")
            return False

    def send_test_message(self) -> bool:
        if not self.token or not self.chat_id:
            return False
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": "🤖 **Bot de Alertas Amazon inicializado com sucesso!**\nMonitorando todas as categorias no Keepa...",
                "parse_mode": "Markdown"
            }
            res = requests.post(f"{self.api_url}/sendMessage", json=payload, timeout=10)
            return res.status_code == 200
        except Exception as e:
            logger.error(f"Erro de conexão com Telegram: {e}")
            return False
