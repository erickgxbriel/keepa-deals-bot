# 🚀 Mini PC Deal Tracker (Amazon BR + Keepa)

Sistema automatizado de alta velocidade para monitorar promoções relâmpago de Mini PCs na **Amazon Brasil** com filtro de custo-benefício por Hardware e alertas em tempo real no **Telegram**.

---

## 🛠️ 1. Como Configurar o Telegram

1. Abra o Telegram e procure pelo bot **`@BotFather`**.
2. Digite `/newbot` e siga as instruções para criar um bot e copiar o **`TELEGRAM_BOT_TOKEN`**.
3. Procure pelo bot **`@userinfobot`** no Telegram e envie qualquer mensagem para descobrir o seu **`TELEGRAM_CHAT_ID`**.
4. Crie o arquivo `.env` baseado no `.env.example`:
   ```bash
   cp .env.example .env
   ```
5. Abra o `.env` e preencha suas chaves:
   ```env
   TELEGRAM_BOT_TOKEN="seu_token_aqui"
   TELEGRAM_CHAT_ID="seu_chat_id_aqui"
   ```

---

## 💻 2. Como Rodar Localmente (Linux / WSL / Mac)

```bash
# 1. Ativar o ambiente virtual
source venv/bin/activate

# 2. Iniciar o monitorador
python main.py
```

---

## ☁️ 3. Como Rodar 24h Grátis em uma VPS (Oracle Cloud / GCP / Ubuntu Server)

### Passo a Passo no Servidor Linux:
1. Clone seu repositório no servidor:
   ```bash
   git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
   cd "SEU_REPOSITORIO"
   ```

2. Instale as dependências e o Playwright:
   ```bash
   sudo apt update && sudo apt install -y python3-venv python3-pip
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   playwright install chromium
   playwright install-deps chromium
   ```

3. Crie o serviço no Linux (`systemd`) para rodar em background e reiniciar se cair ou se o servidor reiniciar:
   ```bash
   sudo nano /etc/systemd/system/minipc-bot.service
   ```
   Cole o seguinte conteúdo (ajustando o caminho da sua pasta):
   ```ini
   [Unit]
   Description=Mini PC Deal Tracker Bot
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/minipc-bot
   ExecStart=/home/ubuntu/minipc-bot/venv/bin/python main.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

4. Ative e inicie o serviço:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable minipc-bot
   sudo systemctl start minipc-bot
   ```

5. Para ver os logs em tempo real na VPS:
   ```bash
   journalctl -u minipc-bot -f
   ```

---

## ⚙️ 4. Como Customizar os Tiers e Preços de Corte
No arquivo `config.py`, você pode ajustar o teto de preço para cada processador e quantidade de RAM/SSD conforme as suas preferências.
