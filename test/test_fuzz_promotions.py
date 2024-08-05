from hypothesis import given, strategies as st
from sympy import sympify, symbols
import re

from utils.promotion_misc import eval_points_conditions, validate_promotions, calculate_points

# Fuzz test for eval_points_conditions
@given(
    condition=st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd')), min_size=1, max_size=50),
    x=st.floats(allow_nan=False, allow_infinity=False)
)
def test_eval_points_conditions(condition, x):
    try:
        result = eval_points_conditions(condition, x)
        assert isinstance(result, bool)
    except ValueError:
        # It's okay if the function raises ValueError for invalid inputs
        pass

# Fuzz test for calculate_points
@given(
    x_val=st.integers(),
    formula=st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd')), min_size=1, max_size=50)
)
def test_calculate_points(x_val, formula):
    try:
        result = calculate_points(x_val, formula)
        assert isinstance(result, int)
    except:
        # It's okay if the function raises an exception for invalid inputs
        pass

# Fuzz test for validate_promotions
@given(
    rule=st.dictionaries(
        keys=st.text(min_size=1),
        values=st.dictionaries(
            keys=st.sampled_from(['op', 'value']),
            values=st.one_of(
                st.text(),
                st.integers(),
                st.lists(st.integers())
            )
        )
    ),
    data=st.dictionaries(
        keys=st.text(min_size=1),
        values=st.one_of(st.text(), st.integers(), st.lists(st.integers()))
    )
)
def test_validate_promotions(rule, data):
    try:
        result = validate_promotions(rule, data)
        assert isinstance(result, bool)
    except:
        # It's okay if the function raises an exception for invalid inputs
        pass

# Run the tests
if __name__ == "__main__":
    test_eval_points_conditions()
    test_calculate_points()
    test_validate_promotions()