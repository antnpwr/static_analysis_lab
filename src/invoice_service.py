from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple

@dataclass
class LineItem:
    sku: str
    category: str
    unit_price: float
    qty: int
    fragile: bool = False

@dataclass
class Invoice:
    invoice_id: str
    customer_id: str
    country: str
    membership: str
    coupon: Optional[str]
    items: List[LineItem]

class InvoiceService:
    def __init__(self) -> None:
        self._coupon_rate: Dict[str, float] = {
            "WELCOME10": 0.10,
            "VIP20": 0.20,
            "STUDENT5": 0.05
        }

    def _validate(self, inv: Invoice) -> List[str]:
        problems: List[str] = []
        if inv is None:
            problems.append("Invoice is missing")
            return problems
        if not inv.invoice_id:
            problems.append("Missing invoice_id")
        if not inv.customer_id:
            problems.append("Missing customer_id")
        if not inv.items:
            problems.append("Invoice must contain items")
        for it in inv.items:
            if not it.sku:
                problems.append("Item sku is missing")
            if it.qty <= 0:
                problems.append(f"Invalid qty for {it.sku}")
            if it.unit_price < 0:
                problems.append(f"Invalid price for {it.sku}")
            if it.category not in ("book", "food", "electronics", "other"):
                problems.append(f"Unknown category for {it.sku}")
        return problems

    def _calculate_subtotal_and_fragile_fee(inv):
    subtotal = 0.0
    fragile_fee = 0.0

    for it in inv.items:
        line = it.unit_price * it.qty
        subtotal += line
        if it.fragile:
            fragile_fee += 5.0 * it.qty

    return subtotal, fragile_fee

    def _calculate_shipping(inv, subtotal):
    if inv.country == "TH":
        return 60 if subtotal < 500 else 0

    if inv.country == "JP":
        return 600 if subtotal < 4000 else 0

    if inv.country == "US":
        if subtotal < 100:
            return 15
        elif subtotal < 300:
            return 8
        return 0

    return 25 if subtotal < 200 else 0

    def _calculate_discount(inv, subtotal, warnings):
    discount = 0.0

    if inv.membership == "gold":
        discount = subtotal * 0.03
    elif inv.membership == "platinum":
        discount = subtotal * 0.05
    elif subtotal > 3000:
        discount = 20

    if inv.coupon is not None and inv.coupon.strip() != "":
        code = inv.coupon.strip()
        if code in self._coupon_rate:
            discount += subtotal * self._coupon_rate[code]
        else:
            warnings.append("Unknown coupon")

    return discount

    def _calculate_tax(inv, subtotal, discount):
    taxable = subtotal - discount

    if inv.country == "TH":
        return taxable * 0.07
    if inv.country == "JP":
        return taxable * 0.10
    if inv.country == "US":
        return taxable * 0.08

    return taxable * 0.05


    def compute_total(self, inv: Invoice) -> Tuple[float, List[str]]:
    warnings: List[str] = []

    problems = self._validate(inv)
    if problems:
        raise ValueError(": ".join(problems))

    subtotal, fragile_fee = _calculate_subtotal_and_fragile_fee(inv)
    shipping = _calculate_shipping(inv, subtotal)
    discount = _calculate_discount(inv, subtotal, warnings)
    tax = _calculate_tax(inv, subtotal, discount)

    total = subtotal + shipping + fragile_fee + tax - discount
    total = max(total, 0)

    if subtotal > 10000 and inv.membership not in ("gold", "platinum"):
        warnings.append("Consider membership upgrade")

    return total, warnings

