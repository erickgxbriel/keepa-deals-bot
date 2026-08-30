import os
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ==============================================================================
# TRAVA DE SEGURANÇA GLOBAL (WHITELIST RÍGIDA)
# Somente este ID tem permissão de receber alertas ou interagir com o bot.
# ==============================================================================
AUTHORIZED_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "237735366"))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8709655947:AAHN2jUZ9C_XJH4My6ajUqImrNA4ySoP5tU")

class TelegramNotifier:
    def __init__(self, token: str = TELEGRAM_BOT_TOKEN, chat_id: int = AUTHORIZED_CHAT_ID):
        self.token = token
        self.chat_id = AUTHORIZED_CHAT_ID  # Sempre força o ID autorizado
        self.api_url = f"https://api.telegram.org/bot{self.token}"

    def is_authorized(self, incoming_id: int) -> bool:
        """Verifica se o remetente ou destinatário é estritamente o seu usuário."""
        try:
            return int(incoming_id) == AUTHORIZED_CHAT_ID
        except (ValueError, TypeError):
            return False

    def send_deal_alert(self, 
                        title: str, 
                        asin: str, 
                        current_price: float, 
                        drop_percent: float, 
                        tier: str, 
                        cpu: str = "N/A", 
                        ram: str = "N/A", 
                        storage: str = "N/A", 
                        image_url: Optional[str] = None) -> bool:
        """
        Envia alerta formatado garantindo entrega EXCLUSIVA no seu Chat ID.
        """
        if not self.token:
            logger.warning("TELEGRAM_BOT_TOKEN não configurado!")
            return False

        # TRAVA DE SEGURANÇA: Bloqueio contra spammers ou IDs não autorizados
        if not self.is_authorized(self.chat_id):
            logger.error(f"⛔ Tentativa de envio bloqueada! ID não autorizado: {self.chat_id}")
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

        if cpu != "N/A" and ram != "N/A":
            specs_text = (
                f"🧠 **Processador:** `{cpu}`\n"
                f"💾 **Memória RAM:** `{ram}`\n"
                f"💽 **Armazenamento:** `{storage}`\n\n"
            )
        else:
            specs_text = ""

        message = (
            f"🛒 **[OFERTAS AMAZON]** ⚡\n\n"
            f"🏷️ **{title}**\n\n"
            f"📊 **Categoria:** {tier_label}\n"
            f"{specs_text}"
            f"💰 **Preço Atual:** `R$ {current_price:,.2f}`\n"
            f"📉 **Queda de Preço:** `-{drop_percent:.0f}%`\n\n"
            f"🔗 **Link:** [Ver na Amazon Brasil]({amazon_url})"
        )

        inline_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🛒 Comprar na Amazon", "url": amazon_url}
                ]
            ]
        }

        try:
            if image_url:
                payload = {
                    "chat_id": AUTHORIZED_CHAT_ID,
                    "caption": message,
                    "parse_mode": "Markdown",
                    "photo": image_url,
                    "reply_markup": inline_keyboard
                }
                res = requests.post(f"{self.api_url}/sendPhoto", json=payload, timeout=10)
                if res.status_code == 200:
                    return True

            # Fallback para mensagem de texto se foto falhar
            payload = {
                "chat_id": AUTHORIZED_CHAT_ID,
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
        """Envia mensagem de validação da trava de segurança."""
        if not self.token:
            return False
        try:
            payload = {
                "chat_id": AUTHORIZED_CHAT_ID,
                "text": (
                    "🔒 **TRAVA DE SEGURANÇA ATIVADA** 🔒\n\n"
                    f"✅ Bot configurado com Whitelist exclusiva para o ID: `{AUTHORIZED_CHAT_ID}`.\n"
                    "⛔ Qualquer mensagem, comando ou tentativa de spam externo será ignorada e bloqueada."
                ),
                "parse_mode": "Markdown"
            }
            res = requests.post(f"{self.api_url}/sendMessage", json=payload, timeout=10)
            return res.status_code == 200
        except Exception as e:
            logger.error(f"Erro de conexão com Telegram: {e}")
            return False

if __name__ == "__main__":
    notifier = TelegramNotifier()
    print("Enviando teste de segurança...")
    ok = notifier.send_test_message()
    print(f"Status do teste: {'SUCESSO ✅' if ok else 'FALHA ❌'}")
