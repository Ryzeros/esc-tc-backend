from utils.promotion_misc import eval_points_conditions, validate_promotions, calculate_points

from hypothesis import given, strategies as st
import pytest
import sys


def test_validate_promotions():
    @given(
        rules=st.dictionaries(
            keys=st.text(),
            values=st.fixed_dictionaries({
                'op': st.one_of(st.just('eq'), st.just('gt'), st.just('gte'), st.just('lt'), st.just('lte'), st.just('in')),
                'value': st.one_of(st.integers(), st.lists(st.integers(), min_size=1))
            })
        ),
        data=st.dictionaries(keys=st.text(), values=st.integers())
    )
    def inner_test(rules, data):
        print(f"Testing with rules: {rules} and data: {data}", file=sys.stdout)
        try:
            result = validate_promotions(rules, data)
            print(f"Result: {result}", file=sys.stdout)
            assert isinstance(result, bool)
        except Exception as e:
            print(f"Exception occurred: {e}", file=sys.stdout)
            assert False, f"Exception occurred: {e}"

    inner_test()


if __name__ == "__main__":
    pytest.main()

