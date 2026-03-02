"""見積書計算ロジック"""

import datetime
from config import TAX_RATE, ESTIMATE_PREFIX, COMPANY_INFO, get_wholesale_rate


class QuotationItem:
    """見積書の1明細行"""

    def __init__(self, no, name, model, maker, quantity, unit, list_price, wholesale_rate):
        self.no = no
        self.name = name
        self.model = model
        self.maker = maker
        self.quantity = quantity
        self.unit = unit
        self.list_price = list_price
        self.wholesale_rate = wholesale_rate
        self.unit_price = int(list_price * wholesale_rate)
        self.amount = self.unit_price * quantity

    def to_dict(self):
        return {
            "no": self.no,
            "name": self.name,
            "model": self.model,
            "maker": self.maker,
            "quantity": self.quantity,
            "unit": self.unit,
            "list_price": self.list_price,
            "wholesale_rate": self.wholesale_rate,
            "unit_price": self.unit_price,
            "amount": self.amount,
        }


class Quotation:
    """見積書全体"""

    def __init__(self, project_name, client_name, items=None):
        self.estimate_number = self._generate_estimate_number()
        self.estimate_date = datetime.date.today()
        self.project_name = project_name
        self.client_name = client_name
        self.company_info = COMPANY_INFO
        self.items = items or []

    def _generate_estimate_number(self):
        now = datetime.datetime.now()
        return f"{ESTIMATE_PREFIX}-{now.year}-{now.strftime('%m%d%H%M')}"

    @classmethod
    def from_equipment_list(cls, equipment_list):
        """機器表から見積書を生成"""
        quotation = cls(
            project_name=equipment_list.project_name,
            client_name=equipment_list.client_name,
        )

        for i, eq_item in enumerate(equipment_list.items, 1):
            rate = get_wholesale_rate(eq_item.category, eq_item.maker, eq_item.name)
            q_item = QuotationItem(
                no=i,
                name=eq_item.name,
                model=eq_item.model,
                maker=eq_item.maker,
                quantity=eq_item.quantity,
                unit=eq_item.unit,
                list_price=eq_item.list_price,
                wholesale_rate=rate,
            )
            quotation.items.append(q_item)

        return quotation

    @property
    def subtotal(self):
        return sum(item.amount for item in self.items)

    @property
    def tax(self):
        return int(self.subtotal * TAX_RATE)

    @property
    def total(self):
        return self.subtotal + self.tax

    def get_estimate_date_jp(self):
        """和暦の日付文字列を返す"""
        d = self.estimate_date
        year = d.year - 2018  # 令和換算
        return f"令和{year}年{d.month}月{d.day}日"

    def to_dict(self):
        return {
            "estimate_number": self.estimate_number,
            "estimate_date": self.estimate_date.isoformat(),
            "estimate_date_jp": self.get_estimate_date_jp(),
            "project_name": self.project_name,
            "client_name": self.client_name,
            "company_info": self.company_info,
            "items": [item.to_dict() for item in self.items],
            "subtotal": self.subtotal,
            "tax": self.tax,
            "total": self.total,
        }
