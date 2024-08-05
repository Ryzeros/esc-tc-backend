from utils.promotion_misc import validate_promotions

from hypothesis import given, strategies as st
import pytest


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
        print(f"Testing with rules: {rules} and data: {data}")
        try:
            result = validate_promotions(rules, data)
            print(f"Result: {result}")
            assert isinstance(result, bool)
        except Exception as e:
            print(f"Exception occurred: {e}")
            assert False, f"Exception occurred: {e}"

    inner_test()


if __name__ == "__main__":
    pytest.main()
