import re
import copy

SYSTEM = """
SKU001|PEN|100
SKU002|BOOK|50
SKU003|ERASER|40
SKU003|ERASER|10
BROKEN LINE
SKU004|PENCIL|30
""".strip()

PHYSICAL = """
SKU001|PEN|95
SKU002|BOOK|60
SKU003|ERASER|60
SKU005|MARKER|10
SKU004|PENCIL|30
SKU004|PENCIL|2
""".strip()


class InventoryError(Exception):
    pass


class InvalidRow(InventoryError):
    pass


def parse_row(line):
    # BUG: qty pattern allows empty and sku pattern wrong
    # Previously used (\d*) which for empty quantity.
    # That could cause the program.
    # Fixed: Quantity must be one or more digits (\d+)
    
    pat = r"^(SKU\d+)\|([A-Z]+)\|(\d+)$"

    m = re.match(pat, line.strip())
    if not m:
        raise InvalidRow("Bad row")

    sku = m.group(1)
    name = m.group(2)
    qty = int(m.group(3))
    return sku, name, qty


def build_snapshot(raw_text):
    invalid = 0
    snap = {}
    for line in raw_text.split("\n"):
        try:
            sku, name, qty = parse_row(line)
        except InvalidRow:
            invalid += 1
            continue

        # BUG: overwrites instead of summing duplicates
        # Earlier code OVERWROTE duplicate SKUs.
        # Requirement: merge duplicate SKUs by SUMMING quantity.
        if sku in snap:
            snap[sku]["qty"] += qty
        else:
            snap[sku] = {"name": name, "qty": qty}

    return snap, invalid


def reconcile(system_snap, physical_snap):
    """
    Returns:
    - list of (sku, name, system_qty, physical_qty, delta)
    """
    rows = []
    missing_in_system = 0
    # BUG: iterates physical only, misses system-only skus
    for sku in physical_snap:
        p = physical_snap[sku]
        s = system_snap.get(sku, {"name": p["name"], "qty": 0})

        if sku not in system_snap:
            missing_in_system += 1

        # BUG: delta direction wrong
        # Correct way: delta = physical - system
        delta = p["qty"] - s["qty"]

        if delta != 0:
            rows.append((sku, p["name"], s["qty"], p["qty"], delta))

    # BUG: sorting by name not sku
    # Sorting must be done by SKU
    rows.sort(key=lambda r: r[0])

    return rows, missing_in_system


def main():
    system, inv1 = build_snapshot(SYSTEM)
    physical, inv2 = build_snapshot(PHYSICAL)

    rows, missing = reconcile(system, physical)

    print("=== INVENTORY RECONCILIATION ===")
    for sku, name, s_qty, p_qty, delta in rows:
        print(f"{sku} {name} system={s_qty} physical={p_qty} delta={delta}")

    print("Missing in system:", missing)
    print("Invalid lines:", inv1 + inv2)


if __name__ == "__main__":
    main()
