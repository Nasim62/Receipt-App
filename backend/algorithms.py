from typing import List
from statistics import mean, median, mode
from .models import Receipt

# ---------- searching ----------
def linear_search(receipts: List[Receipt], keyword: str) -> List[Receipt]:
    return [r for r in receipts if keyword.lower() in r.vendor.lower()]

def range_search(receipts: List[Receipt], min_amt: float, max_amt: float) -> List[Receipt]:
    return [r for r in receipts if min_amt <= r.amount <= max_amt]

# ---------- sorting (custom mergesort for O(n log n)) ----------
def merge_sort(receipts: List[Receipt], key=lambda r: r.amount):
    if len(receipts) <= 1:
        return receipts
    mid = len(receipts) // 2
    left  = merge_sort(receipts[:mid], key)
    right = merge_sort(receipts[mid:], key)
    return _merge(left, right, key)

def _merge(a, b, key):
    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        if key(a[i]) <= key(b[j]):
            result.append(a[i]); i += 1
        else:
            result.append(b[j]); j += 1
    result.extend(a[i:]); result.extend(b[j:])
    return result

# ---------- aggregation ----------
def stats(receipts: List[Receipt]):
    amounts = [r.amount for r in receipts]
    return {
        "sum": sum(amounts),
        "mean": mean(amounts) if amounts else 0,
        "median": median(amounts) if amounts else 0,
        "mode": mode(amounts) if len(set(amounts)) > 1 else amounts[0] if amounts else 0
    }
