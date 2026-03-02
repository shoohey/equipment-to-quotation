"""機器データモデル・パーサー"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


class EquipmentItem:
    """機器1品目を表すクラス"""

    def __init__(self, category, maker, model, name, quantity, unit, list_price, location=""):
        self.category = category
        self.maker = maker
        self.model = model
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.list_price = list_price
        self.location = location

    def to_dict(self):
        return {
            "category": self.category,
            "maker": self.maker,
            "model": self.model,
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "list_price": self.list_price,
            "location": self.location,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            category=data.get("category", ""),
            maker=data.get("maker", ""),
            model=data.get("model", ""),
            name=data.get("name", ""),
            quantity=data.get("quantity", 0),
            unit=data.get("unit", "台"),
            list_price=data.get("list_price", 0),
            location=data.get("location", ""),
        )


class EquipmentList:
    """機器表全体を表すクラス"""

    def __init__(self, project_name="", client_name="", items=None):
        self.project_name = project_name
        self.client_name = client_name
        self.items = items or []

    def add_item(self, item):
        self.items.append(item)

    def get_by_category(self, category):
        return [item for item in self.items if item.category == category]

    def get_categories(self):
        return sorted(set(item.category for item in self.items))

    def get_summary(self):
        """カテゴリ別集計サマリーを返す"""
        summary = {}
        for item in self.items:
            cat = item.category
            if cat not in summary:
                summary[cat] = {"count": 0, "total_list_price": 0}
            summary[cat]["count"] += item.quantity
            summary[cat]["total_list_price"] += item.list_price * item.quantity
        return summary

    def to_dict(self):
        return {
            "project_name": self.project_name,
            "client_name": self.client_name,
            "items": [item.to_dict() for item in self.items],
        }

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data):
        items = [EquipmentItem.from_dict(item) for item in data.get("items", [])]
        return cls(
            project_name=data.get("project_name", ""),
            client_name=data.get("client_name", ""),
            items=items,
        )

    @classmethod
    def from_json(cls, json_str):
        return cls.from_dict(json.loads(json_str))


def load_demo_data():
    """デモ用機器表データを読み込む"""
    path = os.path.join(DATA_DIR, "demo_equipment.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return EquipmentList.from_dict(data)


def load_product_catalog():
    """商品マスタを読み込む"""
    path = os.path.join(DATA_DIR, "product_catalog.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def lookup_product(model, catalog=None):
    """型番から商品マスタを検索"""
    if catalog is None:
        catalog = load_product_catalog()
    for category, products in catalog.items():
        for product in products:
            if product["model"] == model:
                return {**product, "category": category}
    return None
