import argparse, csv
from math import ceil

SAFETY_DAYS, COVER_DAYS = 7, 30

def make_demo(path):
    rows = [("SKU-001", "Cotton T-Shirt", 14, 90, 10), ("SKU-002", "Steel Bottle", 120, 60, 14),
            ("SKU-003", "Phone Case", 8, 150, 7), ("SKU-004", "Yoga Mat", 40, 20, 21),
            ("SKU-005", "Desk Lamp", 0, 45, 12), ("SKU-006", "Notebook Pack", 35, 70, 9)]
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sku", "name", "on_hand", "sold_last_30d", "lead_time_days"])
        w.writerows(rows)

def main():
    p = argparse.ArgumentParser(description="Inventory reorder alerts")
    p.add_argument("file", nargs="?", default="stock.csv")
    p.add_argument("--demo", action="store_true")
    args = p.parse_args()
    if args.demo:
        make_demo(args.file)

    results = []
    with open(args.file, newline="") as f:
        for r in csv.DictReader(f):
            on_hand, sold, lead = int(r["on_hand"]), int(r["sold_last_30d"]), int(r["lead_time_days"])
            daily = sold / 30
            left = on_hand / daily if daily else 9999
            qty = max(0, ceil(daily * (lead + COVER_DAYS) - on_hand))
            status = ("ORDER NOW" if left <= lead
                      else "ORDER SOON" if left <= lead + SAFETY_DAYS else "OK")
            results.append((left, r["sku"], r["name"], on_hand, round(daily, 1), lead, status, qty))
    results.sort()

    print(f"\n{'SKU':<9}{'Item':<16}{'Stock':>6}{'Per day':>8}{'Days left':>10}  {'Status':<11}{'Order qty':>9}")
    for left, sku, name, oh, daily, lead, status, qty in results:
        days = "-" if left == 9999 else f"{left:.1f}"
        print(f"{sku:<9}{name:<16}{oh:>6}{daily:>8}{days:>10}  {status:<11}{qty if status != 'OK' else '':>9}")

    with open("reorder_list.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sku", "name", "status", "order_qty"])
        w.writerows((s, n, st, q) for _, s, n, _, _, _, st, q in results if st != "OK")
    print("\nSaved reorder_list.csv\n")

if __name__ == "__main__":
    main()