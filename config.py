"""設定ファイル - 会社情報、税率、掛率"""

# 会社情報
COMPANY_INFO = {
    "name": "橋本総業株式会社",
    "postal_code": "〒103-0016",
    "address": "東京都中央区日本橋小網町6-7",
    "tel": "03-3666-3481",
    "fax": "03-3666-3499",
}

# 消費税率
TAX_RATE = 0.10

# 見積番号プレフィックス
ESTIMATE_PREFIX = "EST"

# 掛率（卸値率）定義
WHOLESALE_RATES = {
    "パッケージエアコン": 0.35,
    "ルームエアコン": 0.40,
    "ロスナイ・換気扇": 0.45,
    "住設機器_TOTO": 0.40,
    "住設機器_LIXIL": 0.42,
    "管材": 0.55,
    "バルブ・継手": 0.50,
}

# カテゴリ別掛率マッピング
def get_wholesale_rate(category, maker, product_name=""):
    """カテゴリ・メーカー・品名から掛率を取得"""
    if category == "空調":
        if "ロスナイ" in product_name or "換気扇" in product_name:
            return WHOLESALE_RATES["ロスナイ・換気扇"]
        if "壁掛" in product_name:
            return WHOLESALE_RATES["ルームエアコン"]
        return WHOLESALE_RATES["パッケージエアコン"]
    elif category == "住設":
        if maker == "TOTO":
            return WHOLESALE_RATES["住設機器_TOTO"]
        elif maker == "LIXIL":
            return WHOLESALE_RATES["住設機器_LIXIL"]
        return WHOLESALE_RATES["住設機器_TOTO"]
    elif category == "管材":
        if "バルブ" in product_name or "継手" in product_name or "エルボ" in product_name or "チーズ" in product_name:
            return WHOLESALE_RATES["バルブ・継手"]
        return WHOLESALE_RATES["管材"]
    return 0.50  # デフォルト


# アップロード設定
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"xlsx", "xls"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
