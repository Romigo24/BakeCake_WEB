COSTS = {
    "Levels":   [0, 400, 750, 1100],
    "Forms":    [0, 600, 400, 1000],
    "Toppings": [0, 0, 200, 180, 200, 300, 350, 200],
    "Berries":  [0, 400, 300, 450, 500],
    "Decors":   [0, 300, 400, 350, 300, 200, 280],
    "Words":    500,
}

def _as_i(x):
    try:
        return int(x)
    except Exception:
        return 0

def _safe_pick(arr, idx):
    if not isinstance(idx, int) or idx < 0 or idx >= len(arr):
        return 0
    return arr[idx]

def calc_total(details: dict) -> int:
    """details: dict со строковыми значениями из формы.
       Ключи: Levels, Form, Topping, Berries, Decor, Words (строка)."""
    lvl   = _as_i(details.get("Levels"))
    form  = _as_i(details.get("Form"))
    top   = _as_i(details.get("Topping"))
    berr  = _as_i(details.get("Berries"))
    decor = _as_i(details.get("Decor"))
    has_words = bool(details.get("Words"))

    return (
        _safe_pick(COSTS["Levels"],   lvl)  +
        _safe_pick(COSTS["Forms"],    form) +
        _safe_pick(COSTS["Toppings"], top)  +
        _safe_pick(COSTS["Berries"],  berr) +
        _safe_pick(COSTS["Decors"],   decor)+
        (COSTS["Words"] if has_words else 0)
    )
