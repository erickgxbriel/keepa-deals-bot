import re
from typing import Dict, Any, Optional, Tuple
from config import HARDWARE_TIERS, CURATED_BRANDS

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
        if candidates:
            return candidates[0]
        return None

    @staticmethod
    def extract_storage(text: str) -> Optional[str]:
        text_lower = text.lower()
        tb_match = re.search(r'(\d+)\s*(?:tb|t)\s*(?:ssd|nvme|m\.2|rom)?', text_lower)
        if tb_match:
            return f"{tb_match.group(1)}TB"
        
        gb_match = re.search(r'(\d{3,4})\s*(?:gb|g)\s*(?:ssd|nvme|m\.2|rom|emmc)?', text_lower)
        if gb_match:
            val = int(gb_match.group(1))
            if val in [128, 256, 512, 1000, 1024, 2000, 2048]:
                return f"{val}GB" if val < 1000 else f"{val//1000}TB"
        return None

    @staticmethod
    def extract_cpu(text: str) -> Tuple[Optional[str], Optional[str]]:
        text_lower = text.lower()
        for tier_name, tier_info in [("ULTRA", HARDWARE_TIERS["ULTRA"]), 
                                     ("HIGH", HARDWARE_TIERS["HIGH"]), 
                                     ("MID", HARDWARE_TIERS["MID"]), 
                                     ("ENTRY", HARDWARE_TIERS["ENTRY"])]:
            for pattern in tier_info["patterns"]:
                match = re.search(pattern, text_lower)
                if match:
                    matched_str = match.group(0).strip()
                    return tier_name, matched_str.upper()
        return None, None

    @classmethod
    def evaluate_deal(cls, title: str, current_price: float, drop_percent: float = 0.0) -> Dict[str, Any]:
        title_lower = title.lower()

        # -------------------------------------------------------------
        # 1. MINI PC
        # -------------------------------------------------------------
        minipc_rule = CURATED_BRANDS["MINI_PC"]
        is_minipc = any(re.search(kw, title_lower) for kw in minipc_rule["brands"])
        is_minipc_accessory = any(re.search(kw, title_lower) for kw in minipc_rule["negative_keywords"])

        if is_minipc and not is_minipc_accessory:
            tier_name, cpu_name = cls.extract_cpu(title)
            ram_gb = cls.extract_ram(title)
            storage_str = cls.extract_storage(title)
            
            if tier_name:
                tier_config = HARDWARE_TIERS[tier_name]
                if ram_gb and ram_gb in tier_config["max_prices"]:
                    max_allowed_price = tier_config["max_prices"][ram_gb]
                else:
                    max_allowed_price = tier_config["default_max_price"]

                is_good_price = current_price <= max_allowed_price
                is_deal = is_good_price and (drop_percent >= 15.0 if drop_percent > 0 else True)

                if is_deal:
                    return {
                        "is_deal": True,
                        "category": "MINI_PC",
                        "tier": tier_name,
                        "cpu": cpu_name,
                        "ram": f"{ram_gb}GB" if ram_gb else "N/I",
                        "storage": storage_str or "N/I",
                        "current_price": current_price,
                        "max_allowed_price": max_allowed_price,
                        "drop_percent": drop_percent,
                        "reason": f"Mini PC Tier {tier_name} aprovado! R$ {current_price:.2f} <= Teto R$ {max_allowed_price:.2f}"
                    }

        # -------------------------------------------------------------
        # 2. PEÇAS DE COMPUTADOR (SSD NVMe, RAM, Monitores, GPUs)
        # -------------------------------------------------------------
        pc_cfg = CURATED_BRANDS["PC_PARTS"]
        is_pc_neg = any(re.search(kw, title_lower) for kw in pc_cfg["negative_keywords"])
        if not is_pc_neg:
            for item_key, item_info in pc_cfg["items"].items():
                if any(re.search(p, title_lower) for p in item_info["patterns"]):
                    if current_price <= item_info["max_price"] and drop_percent >= item_info["min_discount"]:
                        return {
                            "is_deal": True,
                            "category": "PC_PARTS",
                            "tier": f"💾 PEÇA DE PC ({item_key})",
                            "cpu": "N/A", "ram": "N/A", "storage": cls.extract_storage(title) or "N/A",
                            "current_price": current_price,
                            "max_allowed_price": item_info["max_price"],
                            "drop_percent": drop_percent,
                            "reason": f"Achado de Peça de PC ({item_key}): R$ {current_price:.2f} <= Teto R$ {item_info['max_price']:.2f} (-{drop_percent:.0f}%)"
                        }

        # -------------------------------------------------------------
        # 3. GAMES E CONSOLES (Consoles, Joysticks e Periféricos)
        # -------------------------------------------------------------
        games_cfg = CURATED_BRANDS["GAMES_CONSOLES"]
        is_game_neg = any(re.search(kw, title_lower) for kw in games_cfg["negative_keywords"])
        if not is_game_neg:
            for item_key, item_info in games_cfg["items"].items():
                if any(re.search(p, title_lower) for p in item_info["patterns"]):
                    if current_price <= item_info["max_price"] and drop_percent >= item_info["min_discount"]:
                        return {
                            "is_deal": True,
                            "category": "GAMES",
                            "tier": f"🎮 GAMES ({item_key})",
                            "cpu": "N/A", "ram": "N/A", "storage": "N/A",
                            "current_price": current_price,
                            "max_allowed_price": item_info["max_price"],
                            "drop_percent": drop_percent,
                            "reason": f"Achado Gamer ({item_key}): R$ {current_price:.2f} <= Teto R$ {item_info['max_price']:.2f} (-{drop_percent:.0f}%)"
                        }

        # -------------------------------------------------------------
        # 4. INSTRUMENTOS MUSICAIS (Violão, guitarra, baixo, bateria, percussão)
        # -------------------------------------------------------------
        music_cfg = CURATED_BRANDS["MUSICAL_INSTRUMENTS"]
        is_music_neg = any(re.search(kw, title_lower) for kw in music_cfg["negative_keywords"])
        if not is_music_neg:
            for item_key, item_info in music_cfg["items"].items():
                if any(re.search(p, title_lower) for p in item_info["patterns"]):
                    if current_price <= item_info["max_price"] and drop_percent >= item_info["min_discount"]:
                        return {
                            "is_deal": True,
                            "category": "MUSIC",
                            "tier": f"🎸 INSTRUMENTO MUSICAL",
                            "cpu": "N/A", "ram": "N/A", "storage": "N/A",
                            "current_price": current_price,
                            "max_allowed_price": item_info["max_price"],
                            "drop_percent": drop_percent,
                            "reason": f"Instrumento Musical em Oferta: R$ {current_price:.2f} <= Teto R$ {item_info['max_price']:.2f} (-{drop_percent:.0f}%)"
                        }

        # -------------------------------------------------------------
        # 5. MODA & MARCAS AMERICANAS (Aeropostale, Columbia, Levi's, Hanes, etc)
        # -------------------------------------------------------------
        fashion_cfg = CURATED_BRANDS["FASHION"]
        matched_fashion_brand = None
        for b_pat in fashion_cfg["brands"]:
            m = re.search(b_pat, title_lower)
            if m:
                matched_fashion_brand = m.group(0).upper()
                break

        is_fashion_neg = any(re.search(kw, title_lower) for kw in fashion_cfg["negative_keywords"])

        if matched_fashion_brand and not is_fashion_neg:
            target_max_price = fashion_cfg["default_max_price"]
            target_min_discount = fashion_cfg["default_min_discount"]
            item_type_label = "Vestuário"

            for type_name, type_info in fashion_cfg["item_types"].items():
                if any(re.search(p, title_lower) for p in type_info["patterns"]):
                    target_max_price = type_info["max_price"]
                    target_min_discount = type_info["min_discount"]
                    item_type_label = type_name.replace("_", " ")
                    break

            if current_price <= target_max_price and drop_percent >= target_min_discount:
                return {
                    "is_deal": True,
                    "category": "FASHION",
                    "tier": f"👕 MODA ({matched_fashion_brand})",
                    "cpu": "N/A", "ram": "N/A", "storage": "N/A",
                    "current_price": current_price,
                    "max_allowed_price": target_max_price,
                    "drop_percent": drop_percent,
                    "reason": f"Achado {matched_fashion_brand} ({item_type_label}): R$ {current_price:.2f} <= Teto R$ {target_max_price:.2f} (-{drop_percent:.0f}%)"
                }

        # -------------------------------------------------------------
        # 6. AUTOMOTIVO (Lavadoras Wap/Karcher, Som, Pneus)
        # -------------------------------------------------------------
        auto_cfg = CURATED_BRANDS["AUTOMOTIVE"]
        if any(re.search(p, title_lower) for p in auto_cfg["patterns"]) and not any(re.search(n, title_lower) for n in auto_cfg["negative_keywords"]):
            if current_price <= auto_cfg["max_price"] and drop_percent >= auto_cfg["min_discount"]:
                return {
                    "is_deal": True,
                    "category": "AUTOMOTIVE",
                    "tier": "🚗 AUTOMOTIVO / EQUIPAMENTO",
                    "cpu": "N/A", "ram": "N/A", "storage": "N/A",
                    "current_price": current_price,
                    "max_allowed_price": auto_cfg["max_price"],
                    "drop_percent": drop_percent,
                    "reason": f"Achado Automotivo: R$ {current_price:.2f} (-{drop_percent:.0f}%)"
                }

        return {
            "is_deal": False,
            "reason": "Fora dos critérios de achados reais ou categoria desativada",
            "tier": None,
            "cpu": None,
            "ram": None,
            "storage": None
        }
