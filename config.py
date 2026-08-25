import os
from dotenv import load_dotenv

load_dotenv()

# Configurações do Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8709655947:AAHN2jUZ9C_XJH4My6ajUqImrNA4ySoP5tU")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "237735366")

# Intervalo em segundos entre cada checagem de ofertas
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "45"))

# Domínio da Amazon Brasil = 12
AMAZON_DOMAIN_ID = int(os.getenv("AMAZON_DOMAIN_ID", "12"))

# Desconto percentual mínimo padrão
MIN_DISCOUNT_PERCENT = int(os.getenv("MIN_DISCOUNT_PERCENT", "20"))

# URL EXATA DO KEEPA DEALS COM FILTROS DE CATEGORIAS EXCLUÍDAS E INCLUÍDAS
# Exclui: Pet Shop, Construção, Livros, Jardim/Piscina, Papelaria, Bebês, etc.
# Inclui e prioriza: Informática, Eletrônicos, Games, Moda, Instrumentos Musicais.
KEEPA_DEALS_TARGET_URL = (
    "https://keepa.com/#!deals/"
    "%7B%22page%22%3A0%2C%22domainId%22%3A%2212%22%2C"
    "%22excludeCategories%22%3A%5B%5B%5D%2C%5B%5D%2C%5B%5D%2C%5B%5D%2C%5B%5D%2C%5B%5D%2C%5B%5D%2C%5B%5D%2C%5B%5D%2C%5B%5D%2C%5B%5D%2C%5B%5D%2C"
    "%5B6740748011%2C18991195011%2C18991136011%2C18991021011%2C16957182011%2C16957239011%2C7791937011%2C17242603011%5D%2C"
    "%5B%5D%2C%5B%5D%5D%2C"
    "%22includeCategories%22%3A%5B%5B%5D%2C%5B%5D%2C%5B%5D%2C%5B%5D%2C%5B%5D%2C%5B%5D%2C%5B%5D%2C%5B%5D%2C%5B%5D%2C%5B%5D%2C%5B%5D%2C%5B%5D%2C"
    "%5B16339926011%5D%2C"
    "%5B%5D%2C%5B%5D%5D%2C"
    "%22priceTypes%22%3A%5B18%5D%2C%22deltaRange%22%3A%5B0%2C2147483647%5D%2C%22deltaPercentRange%22%3A%5B20%2C100%5D%2C"
    "%22salesRankRange%22%3A%5B-1%2C-1%5D%2C%22currentRange%22%3A%5B0%2C400000%5D%2C%22minRating%22%3A-1%2C"
    "%22isLowest%22%3Afalse%2C%22isLowest90%22%3Afalse%2C%22isLowestOffer%22%3Afalse%2C%22isOutOfStock%22%3Afalse%2C"
    "%22titleSearch%22%3A%22%22%2C%22isRangeEnabled%22%3Atrue%2C%22isFilterEnabled%22%3Afalse%2C%22filterErotic%22%3Atrue%2C"
    "%22singleVariation%22%3Atrue%2C%22hasReviews%22%3Afalse%2C%22isPrimeExclusive%22%3Afalse%2C%22mustHaveAmazonOffer%22%3Afalse%2C"
    "%22mustNotHaveAmazonOffer%22%3Afalse%2C%22sortType%22%3A1%2C%22dateRange%22%3A%220%22%2C%22warehouseConditions%22%3A%5B1%2C2%2C3%2C4%2C5%5D%2C"
    "%22settings%22%3A%7B%22viewTyp%22%3A0%7D%2C%22perPage%22%3A150%7D"
)

# -------------------------------------------------------------
# CURADORIA DE ACHADOS E TETOS DE PREÇO POR CATEGORIA
# -------------------------------------------------------------
CURATED_BRANDS = {
    # 1. MINI PCS (Foco total em Hardware vs Preço)
    "MINI_PC": {
        "brands": [r"mini\s*pc", r"micro\s*pc", r"mini\s*computador", r"beelink", r"minisforum", r"acemagician", r"kamrui", r"gmktec", r"geekom", r"firebat", r"chatreey"],
        "negative_keywords": [r"suporte", r"cabo\s*hdmi", r"case\s*para", r"adaptador", r"carregador", r"cooler\s*para", r"somente\s*gabinete"],
    },

    # 2. PEÇAS DE COMPUTADOR & PERIFÉRICOS (SSD NVMe, RAM, Monitores, GPUs)
    "PC_PARTS": {
        "items": {
            "SSD_NVME": {
                "patterns": [r"nvme", r"ssd\s*1tb", r"ssd\s*2tb", r"ssd\s*4tb", r"m\.2\s*pcie", r"samsung\s*990", r"samsung\s*980", r"crucial\s*p3", r"kingston\s*nv2", r"wd\s*black", r"sn850"],
                "max_price": 750.0,
                "min_discount": 30.0
            },
            "MEMORIA_RAM": {
                "patterns": [r"memoria\s*ddr4", r"memoria\s*ddr5", r"corsair\s*vengeance", r"fury\s*beast", r"xpg", r"g\.skill"],
                "max_price": 400.0,
                "min_discount": 30.0
            },
            "MONITOR_GAMER": {
                "patterns": [r"monitor\s*gamer", r"monitor\s*144hz", r"monitor\s*165hz", r"monitor\s*240hz", r"monitor\s*ips", r"monitor\s*4k", r"monitor\s*ultrawide"],
                "max_price": 1400.0,
                "min_discount": 25.0
            },
            "GPU_PLACA_VIDEO": {
                "patterns": [r"rtx\s*4060", r"rtx\s*4070", r"rtx\s*4080", r"rx\s*6750", r"rx\s*7600", r"rx\s*7700", r"rx\s*7800"],
                "max_price": 3800.0,
                "min_discount": 20.0
            }
        },
        "negative_keywords": [r"case\s*para", r"adaptador", r"dissipador\s*avulso", r"suporte\s*de\s*placa", r"cabo\s*riser", r"suporte\s*para\s*monitor"]
    },

    # 3. GAMES E CONSOLES (Foco em consoles, controles originais e periféricos gamer a preço baixo)
    "GAMES_CONSOLES": {
        "items": {
            "CONSOLES": {
                "patterns": [r"playstation\s*5", r"ps5\b", r"nintendo\s*switch", r"switch\s*oled", r"xbox\s*series\s*s", r"xbox\s*series\s*x", r"steam\s*deck", r"rog\s*ally", r"anbernic", r"miyoo"],
                "max_price": 3600.0,
                "min_discount": 15.0 # Consoles raramente caem mais de 15%
            },
            "CONTROLES_JOYSTICKS": {
                "patterns": [r"dualsense", r"controle\s*ps5", r"controle\s*xbox", r"8bitdo", r"pro\s*controller\s*switch", r"gamesir", r"flydigi"],
                "max_price": 350.0,
                "min_discount": 25.0
            },
            "HEADSETS_MOUSES_TECLADOS_GAMER": {
                "patterns": [
                    r"headset\s*gamer", r"mouse\s*gamer", r"teclado\s*mecanico", 
                    r"hyperx\s*cloud", r"logitech\s*g", r"razer\s*deathadder", 
                    r"razer\s*blackwidow", r"redragon", r"steelseries"
                ],
                "max_price": 280.0,    # Periféricos a preço realmente muito baixo
                "min_discount": 35.0
            }
        },
        "negative_keywords": [r"adesivo", r"skin\s*para", r"capa\s*de\s*silicone", r"grip\s*para", r"suporte\s*para\s*controle"]
    },

    # 4. INSTRUMENTOS MUSICAIS (Violão, guitarra, baixo, bateria, ukulele, percussão)
    "MUSICAL_INSTRUMENTS": {
        "items": {
            "CORDAS_TECLAS_PERCUSSAO": {
                "patterns": [
                    r"violao", r"violão", r"guitarra", r"contrabaixo", r"baixo\s*elétrico", 
                    r"ukulele", r"bateria\s*eletronica", r"bateria\s*acustica", 
                    r"pandeiro", r"cajon", r"cajón", r"teclado\s*musical", r"piano\s*digital"
                ],
                "brands": [r"yamaha", r"tagima", r"fender", r"squier", r"ibanez", r"epiphone", r"roland", r"korg", r"alesis", r"giannini", r"strinberg", r"luthier"],
                "max_price": 1800.0,
                "min_discount": 30.0
            },
            "EQUIPAMENTOS_AUDIO_ESTUDIO": {
                "patterns": [r"interface\s*de\s*audio", r"focusrite\s*scarlett", r"microfone\s*shure", r"microfone\s*condensador", r"pedaleira", r"amplificador"],
                "max_price": 950.0,
                "min_discount": 30.0
            }
        },
        "negative_keywords": [r"palheta\s*avulsa", r"cabo\s*p10\s*avulso", r"afinador", r"suporte\s*de\s*chao", r"correia", r"capotraste", r"encordoamento"]
    },

    # 5. MODA & MARCAS AMERICANAS / ESPORTIVAS
    "FASHION": {
        "brands": [
            r"aeropostale", r"columbia", r"lee\b", r"levi'?s", r"tommy\s*hilfiger", 
            r"calvin\s*klein", r"hanes\b", r"nautica", r"lacoste", r"ralph\s*lauren", 
            r"adidas", r"nike", r"under\s*armour", r"puma", r"the\s*north\s*face", 
            r"timberland", r"oakley", r"gap\b", r"quiksilver", r"billabong"
        ],
        "item_types": {
            "CAMISETA_POLO": {
                "patterns": [r"camiseta", r"t-shirt", r"polo", r"regata"],
                "max_price": 95.0,
                "min_discount": 35.0
            },
            "CAMISA_SOCIAL": {
                "patterns": [r"camisa\s*manga", r"camisa\s*social", r"camisa\s*jeans", r"camisa\s*xadrez", r"button\s*down"],
                "max_price": 135.0,
                "min_discount": 40.0
            },
            "CALCA_JEANS_CHINO": {
                "patterns": [r"calca", r"calça", r"jeans", r"chino"],
                "max_price": 150.0,
                "min_discount": 40.0
            },
            "BERMUDA_SHORT": {
                "patterns": [r"bermuda", r"short", r"boardshort"],
                "max_price": 95.0,
                "min_discount": 35.0
            },
            "MOLETON_JAQUETA_CORTAVENTO": {
                "patterns": [r"moletom", r"hoodie", r"jaqueta", r"corta\s*vento", r"fleece", r"anorak"],
                "max_price": 190.0,
                "min_discount": 40.0
            },
            "TENIS_CALCADOS": {
                "patterns": [r"tenis", r"tênis", r"sneaker", r"bota", r"sapatenis"],
                "max_price": 230.0,
                "min_discount": 35.0
            }
        },
        "default_max_price": 120.0,
        "default_min_discount": 35.0,
        "negative_keywords": [r"meia\b", r"cueca", r"cadarço", r"chaveiro", r"adesivo"]
    },

    # 6. AUTOMOTIVO (Apenas itens de alto valor com desconto agressivo)
    "AUTOMOTIVE": {
        "patterns": [r"lavadora\s*de\s*alta\s*pressao", r"karcher", r"wap", r"som\s*automotivo", r"multimidia\s*carplay", r"pneu\s*pirelli", r"pneu\s*michelin", r"bateria\s*heliar", r"bateria\s*moura"],
        "negative_keywords": [r"cheirinho", r"adesivo", r"capa\s*volante", r"palheta\s*parabrisa"],
        "max_price": 1200.0,
        "min_discount": 40.0
    }
}

# Critérios detalhados de Hardware para Mini PC
HARDWARE_TIERS = {
    "ENTRY": {
        "patterns": [r"n95", r"n97", r"n100", r"n150", r"n200", r"n5095", r"n5105", r"celeron", r"j4125", r"j4105", r"intel n"],
        "max_prices": {8: 750.0, 16: 1050.0, 32: 1250.0},
        "default_max_price": 950.0
    },
    "MID": {
        "patterns": [r"ryzen\s*5", r"r5\s*\d{4}", r"5500u", r"5560u", r"5600h", r"5600u", r"5625u", r"4500u", r"4600h", r"4700u", r"core\s*i5", r"i5-\d{4,5}"],
        "max_prices": {8: 1100.0, 16: 1450.0, 32: 1700.0},
        "default_max_price": 1450.0
    },
    "HIGH": {
        "patterns": [r"ryzen\s*7\s*5700u", r"ryzen\s*7\s*5800h", r"ryzen\s*7\s*5800u", r"ryzen\s*7\s*5825u", r"ryzen\s*7\s*7730u", r"ryzen\s*7\s*4800u", r"ryzen\s*7\s*4800h", r"r7\s*5700u", r"r7\s*5800h", r"core\s*i7", r"i7-\d{4,5}", r"ryzen\s*7"],
        "max_prices": {16: 1650.0, 32: 1950.0, 64: 2400.0},
        "default_max_price": 1850.0
    },
    "ULTRA": {
        "patterns": [r"7735hs", r"7840hs", r"7940hs", r"8845hs", r"8945hs", r"ryzen\s*9", r"core\s*i9", r"core\s*ultra", r"radeon\s*780m", r"radeon\s*680m"],
        "max_prices": {16: 2500.0, 32: 3100.0, 64: 3800.0},
        "default_max_price": 2900.0
    }
}
