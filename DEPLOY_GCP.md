# 🚀 Guia de Implantação: Google Cloud Compute Engine (e2-micro Always Free)

Instruções passo a passo para rodar o **Deal Tracker Bot** 24/7 na sua VM do Google Cloud.

---

## 1. Subir o Projeto para o GitHub (na sua máquina local)

Na sua máquina local, abra o terminal na pasta do projeto:

```bash
cd "/home/gabriel/Downloads/Automação Keepa Amazon"
git init
git add .
git commit -m "Initial commit - Mini PC Deal Tracker"
```

Crie um repositório **Privado** no seu GitHub (ex: `keepa-deals-bot`) e envie o código:
```bash
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/keepa-deals-bot.git
git push -u origin main
```

*(O arquivo `.gitignore` já garante que seu `.env` com suas senhas e o banco de dados local não serão enviados publicamente).*

---

## 2. Acessar a VM do Google Cloud e Preparar o Ambiente

Conecte na sua VM via SSH (pelo console do GCP ou pelo seu terminal `gcloud compute ssh SUA_INSTANCIA`):

### 2.1 Criar Swap Memory (Crucial para a VM `e2-micro` com 1GB RAM)
A VM `e2-micro` tem 1GB de RAM. Para o Playwright/Chromium rodar com folga sem travar por falta de memória, crie 2GB de Swap:
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 2.2 Instalar Pacotes do Sistema e Dependências do Playwright
```bash
sudo apt update && sudo apt install -y python3-venv python3-pip git
```

### 2.3 Clonar o Repositório na VM
```bash
cd ~
git clone https://github.com/SEU_USUARIO/keepa-deals-bot.git
cd keepa-deals-bot
```

### 2.4 Criar o Ambiente Virtual e Instalar o Chromium
```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/playwright install chromium
./venv/bin/playwright install-deps chromium
```

---

## 3. Criar o Arquivo `.env` na VM

Crie o arquivo `.env` com suas credenciais:
```bash
nano .env
```
Cole o conteúdo:
```env
TELEGRAM_BOT_TOKEN="8709655947:AAHN2jUZ9C_XJH4My6ajUqImrNA4ySoP5tU"
TELEGRAM_CHAT_ID="237735366"
CHECK_INTERVAL_SECONDS=45
AMAZON_DOMAIN_ID=12
MIN_DISCOUNT_PERCENT=20
```
Pressione `Ctrl + O`, `Enter` e depois `Ctrl + X` para salvar e sair.

---

## 4. Configurar como Serviço `systemd` (Rodar 24h em Segundo Plano)

Para garantir que o bot nunca pare e religue sozinho se a VM reiniciar:

1. Crie o arquivo de serviço:
```bash
sudo nano /etc/systemd/system/keepa-bot.service
```

2. Cole o conteúdo abaixo (assumindo que seu usuário é o padrão da VM):
```ini
[Unit]
Description=Keepa Amazon Deals Telegram Bot
After=network.target

[Service]
Type=simple
User=SEU_USUARIO_LINUX
WorkingDirectory=/home/SEU_USUARIO_LINUX/keepa-deals-bot
ExecStart=/home/SEU_USUARIO_LINUX/keepa-deals-bot/venv/bin/python main.py
Restart=always
RestartSec=15

[Install]
WantedBy=multi-user.target
```
*(Dica: descubra seu usuário digitando `whoami` no terminal da VM e substitua `SEU_USUARIO_LINUX`)*.

3. Ative e inicie o serviço:
```bash
sudo systemctl daemon-reload
sudo systemctl enable keepa-bot
sudo systemctl start keepa-bot
```

---

## 5. Comandos Úteis de Manutenção na VM

- **Ver o status do bot:**
  ```bash
  sudo systemctl status keepa-bot
  ```
- **Acompanhar os logs em tempo real:**
  ```bash
  journalctl -u keepa-bot -f
  ```
- **Reiniciar o bot após alterar configurações:**
  ```bash
  sudo systemctl restart keepa-bot
  ```
- **Parar o bot:**
  ```bash
  sudo systemctl stop keepa-bot
  ```
