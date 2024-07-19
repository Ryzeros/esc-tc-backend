from sympy import sympify, symbols


def eval_points_conditions(string: str, x: int):
    """
    Evaluate the condition for x
    """
    parts = string.split()

    if len(parts) == 3:
        operator = parts[1].strip()
        right = float(parts[2].strip())
        x = float(x)

        if operator == "<":
            return x < right
        elif operator == "<=":
            return x <= right
        elif operator == ">":
            return x > right
        elif operator == ">=":
            return x >= right
        elif operator == "==":
            return x == right

    return False


def calculate_points(x_val: int, formula: str):
    x = symbols('x')
    formula = sympify(formula)
    result = formula.subs(x, x_val)
    return result


def validate_promotions(rule: dict, data: dict):
    operator_map = {
        "eq": lambda a, b: a == b,
        "gt": lambda a, b: a > b,
        "gte": lambda a, b: a >= b,
        "lt": lambda a, b: a < b,
        "lte": lambda a, b: a <= b,
        "in": lambda a, b: a in b
    }

    if len(data) == 0:
        return False

    for key, condition in rule.items():
        if key not in data:
            return False

        operation = condition.get('op', 'eq')
        value = condition['value']
        if isinstance(value, list):
            operation = 'in'

        if not operator_map[operation](data[key], value):
            return False
    return True
