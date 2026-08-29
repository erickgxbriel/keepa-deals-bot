import re
from typing import Dict, Any, Optional, Tuple

class HardwareParser:
    @staticmethod
    def extract_ram(text: str) -> Optional[int]:
        text_lower = text.lower()
        ram_matches = re.findall(r'(\d+)\s*(?:gb|g)\s*(?:ddr\d|ram|lpddr\d)?', text_lower)
        candidates = []
        for m in ram_matches:
            val = int(m)
            if val in [4, 8, 12, 16, 24, 32, 64, 128]:
                candidates.append(val)
        return candidates[0] if candidates else None

    @staticmethod
    def extract_storage(text: str) -> Optional[str]:
        text_lower = text.lower()
        tb_match = re.search(r'(\d+)\s*(?:tb|t)\s*(?:ssd|nvme|m\.2|rom)?', text_lower)
        if tb_match:
            return f"{tb_match.group(1)}TB"
        
        gb_match = re.search(r'(\d{3,4})\s*(?:gb|g)\s*(?:ssd|nvme|m\.2|rom|emmc)?', text_lower)
        if gb_match:
            val = int(gb_match.group(1))
            if val in [128, 240, 256, 480, 500, 512, 1000, 1024, 2000, 2048]:
                return f"{val}GB" if val < 1000 else f"{val//1000}TB"
        return None

    @classmethod
    def evaluate_deal(cls, title: str, current_price: float, drop_percent: float = 0.0, badge: str = "") -> Dict[str, Any]:
        title_lower = title.lower()

        # -------------------------------------------------------------
        # 1. LISTA DE BLOQUEIO DE LIXO / ACESSÓRIOS / BUGIGANGAS
        # -------------------------------------------------------------
        junk_patterns = [
            r"suporte", r"mount\b", r"montagem", r"cabo", r"adaptador", r"carregador", 
            r"cooler", r"ventilador", r"gabinete", r"capa", r"estojo", r"case\b", 
            r"dock", r"placa\s*de\s*rede", r"antena", r"caixa\s*de\s*som", r"caixinha", 
            r"soundbar", r"alto\s*falante", r"webcam", r"tela\s*ips", r"touchpad", 
            r"mini\s*teclado", r"adesivo", r"skin", r"palheta", r"encordoamento", 
            r"afinador", r"correia", r"meia\b", r"cueca", r"cadarço"
        ]
        if any(re.search(p, title_lower) for p in junk_patterns):
            return {"is_deal": False, "reason": "Acessório / Periférico descartado"}

        # -------------------------------------------------------------
        # 2. MINI PCS (Foco Cirúrgico em Computadores Reais)
        # -------------------------------------------------------------
        is_pc = bool(re.search(r"mini\s*pc|mini\s*computador|mini\s*desktop|beelink|minisforum|acemagician|kamrui|gmktec|geekom|bosgame|trycoo|morefine|mele", title_lower))
        
        if is_pc:
            ram = cls.extract_ram(title)
            ssd = cls.extract_storage(title)

            # RYZEN 7 / RYZEN 9 / I7 / I9 (Topo / Sweet Spot - Ex: seu AceMagician R$ 1.900)
            if re.search(r"ryzen\s*7|r7|ryzen\s*9|r9|core\s*i7|i7-|core\s*i9|5700u|5800h|5825u|7730u|7735hs|7840hs|8845hs", title_lower):
                max_price = 2150.0 if (ram and ram >= 32) else 1750.0
                if current_price <= max_price:
                    return {
                        "is_deal": True,
                        "category": "MINI_PC",
                        "tier": "🔥 MINI PC RYZEN 7 / I7 (ALTO DESEMPENHO)",
                        "cpu": "Ryzen 7 / i7",
                        "ram": f"{ram}GB" if ram else "N/I",
                        "storage": ssd or "N/I",
                        "current_price": current_price,
                        "reason": f"Mini PC Potente por R$ {current_price:.2f} <= Teto R$ {max_price:.2f}"
                    }

            # RYZEN 5 / I5 (Intermediário Custo-Benefício)
            elif re.search(r"ryzen\s*5|r5|5500u|5600h|5600u|5625u|core\s*i5|i5-", title_lower):
                max_price = 1450.0
                if current_price <= max_price:
                    return {
                        "is_deal": True,
                        "category": "MINI_PC",
                        "tier": "🟡 MINI PC RYZEN 5 / I5 (INTERMEDIÁRIO)",
                        "cpu": "Ryzen 5 / i5",
                        "ram": f"{ram}GB" if ram else "N/I",
                        "storage": ssd or "N/I",
                        "current_price": current_price,
                        "reason": f"Mini PC Ryzen 5/i5 por R$ {current_price:.2f} <= Teto R$ {max_price:.2f}"
                    }

            # N95 / N100 / N200 / RYZEN 3 / CELERON (Básico / Entrada)
            elif re.search(r"n95|n97|n100|n150|n200|n5095|n5105|ryzen\s*3|r3|3200u|3250u|3500u|celeron", title_lower):
                max_price = 980.0
                if current_price <= max_price:
                    return {
                        "is_deal": True,
                        "category": "MINI_PC",
                        "tier": "🟢 MINI PC BÁSICO (N100 / RYZEN 3)",
                        "cpu": "Básico",
                        "ram": f"{ram}GB" if ram else "N/I",
                        "storage": ssd or "N/I",
                        "current_price": current_price,
                        "reason": f"Mini PC Básico por R$ {current_price:.2f} <= Teto R$ {max_price:.2f}"
                    }

            # Qualquer outro PC completo super barato (< R$ 750)
            elif current_price <= 750.0:
                return {
                    "is_deal": True,
                    "category": "MINI_PC",
                    "tier": "🟢 MINI PC ECONÔMICO",
                    "cpu": "Econômico",
                    "ram": f"{ram}GB" if ram else "N/I",
                    "storage": ssd or "N/I",
                    "current_price": current_price,
                    "reason": f"PC Completo super barato por R$ {current_price:.2f}"
                }

        # -------------------------------------------------------------
        # 3. MODA DE MARCA AMERICANA (Apenas Camiseta/Calça/Jaqueta com preço de Outlet)
        # -------------------------------------------------------------
        brands_fashion = [r"aeropostale", r"columbia", r"lee\b", r"levi'?s", r"tommy\s*hilfiger", r"calvin\s*klein", r"hanes\b", r"lacoste"]
        for b in brands_fashion:
            if re.search(b, title_lower):
                if re.search(r"camiseta|t-shirt|polo", title_lower) and current_price <= 85.0:
                    return {"is_deal": True, "category": "FASHION", "tier": f"👕 MODA ({b.upper()})", "current_price": current_price, "reason": f"Camiseta de Marca por R$ {current_price:.2f}"}
                elif re.search(r"calca|calça|jeans", title_lower) and current_price <= 140.0:
                    return {"is_deal": True, "category": "FASHION", "tier": f"👖 JEANS ({b.upper()})", "current_price": current_price, "reason": f"Calça de Marca por R$ {current_price:.2f}"}
                elif re.search(r"jaqueta|moletom|fleece|corta\s*vento", title_lower) and current_price <= 170.0:
                    return {"is_deal": True, "category": "FASHION", "tier": f"🧥 JAQUETA/MOLETOM ({b.upper()})", "current_price": current_price, "reason": f"Jaqueta de Marca por R$ {current_price:.2f}"}

        # -------------------------------------------------------------
        # 4. CONSOLES / GAMES / INSTRUMENTOS
        # -------------------------------------------------------------
        if re.search(r"console.*playstation\s*5|console.*ps5|ps5\s*slim\s*edicao", title_lower) and current_price <= 3100.0:
            return {"is_deal": True, "category": "GAMES", "tier": "🎮 CONSOLE PS5", "current_price": current_price, "reason": f"PS5 por R$ {current_price:.2f}"}
        
        if re.search(r"nintendo\s*switch\s*oled", title_lower) and not re.search(r"jogo|mídia|case", title_lower) and current_price <= 1900.0:
            return {"is_deal": True, "category": "GAMES", "tier": "🎮 NINTENDO SWITCH OLED", "current_price": current_price, "reason": f"Switch OLED por R$ {current_price:.2f}"}

        if re.search(r"controle.*(dualsense|xbox)", title_lower) and current_price <= 310.0:
            return {"is_deal": True, "category": "GAMES", "tier": "🎮 CONTROLE ORIGINAL", "current_price": current_price, "reason": f"Controle por R$ {current_price:.2f}"}

        if re.search(r"violao|violão|guitarra", title_lower) and re.search(r"yamaha|tagima|fender|squier", title_lower) and current_price <= 800.0:
            return {"is_deal": True, "category": "MUSIC", "tier": "🎸 INSTRUMENTO DE MARCA", "current_price": current_price, "reason": f"Instrumento por R$ {current_price:.2f}"}

        return {"is_deal": False, "reason": "Preço fora da oportunidade real"}
