from sympy import sympify, symbols
import re


def eval_points_conditions(condition: str, x: float):
    """
    Evaluate the condition for x.
    Supports operators: <, <=, >, >=, ==, !=
    Supports range comparisons like 600 < x < 1000
    """
    # Regular expression to match range comparisons like 600 < x < 1000
    range_pattern = re.compile(r'^\s*(-?\d+(\.\d+)?)\s*([<>]=?)\s*x\s*([<>]=?)\s*(-?\d+(\.\d+)?)\s*$')
    single_pattern = re.compile(r'^\s*x\s*([<>]=?|==|!=)\s*(-?\d+(\.\d+)?)\s*$')

    range_match = range_pattern.match(condition)
    single_match = single_pattern.match(condition)

    if range_match:
        left_value = float(range_match.group(1))
        left_operator = range_match.group(3)
        right_operator = range_match.group(4)
        right_value = float(range_match.group(5))

        if left_operator == "<":
            left_result = left_value < x
        elif left_operator == "<=":
            left_result = left_value <= x
        elif left_operator == ">":
            left_result = left_value > x
        elif left_operator == ">=":
            left_result = left_value >= x
        else:
            raise ValueError(f"Unsupported operator: {left_operator}")

        if right_operator == "<":
            right_result = x < right_value
        elif right_operator == "<=":
            right_result = x <= right_value
        elif right_operator == ">":
            right_result = x > right_value
        elif right_operator == ">=":
            right_result = x >= right_value
        else:
            raise ValueError(f"Unsupported operator: {right_operator}")

        return left_result and right_result

    elif single_match:
        operator = single_match.group(1)
        right = float(single_match.group(2))

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
        elif operator == "!=":
            return x != right

    else:
        raise ValueError(f"Invalid condition format: {condition}")

    return False


def calculate_points(x_val: int, formula: str):
    x = symbols('x')
    formula = sympify(formula)
    result = formula.subs(x, x_val)
    return int(result)


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
        print(key, condition)
        if key not in data:
            return False

        operation = condition.get('op', 'eq')
        value = condition['value']
        print(value)
        if isinstance(value, list):
            operation = 'in'
        if not operator_map[operation](data[key], value):
            return False
    return True
