import unittest

from workforce.utils import group_by


class TestGroupBy(unittest.TestCase):
    def test_base_case(self):
        key = 'a'
        case = [{key: 1}, {key: 3}, {key: 2}]
        self.assertDictEqual(group_by(case, key), {
            1: [{key: 1}],
            2: [{key: 2}],
            3: [{key: 3}],
        })

    def test_it_groups_duplicated_keys_preserving_order(self):
        key = 'a'
        case = [{key: 1, 'b': 3}, {key: 2}, {key: 1}, {key: 3}, {key: 2}]
        self.assertDictEqual(group_by(case, key), {
            1: [{key: 1, 'b': 3}, {key: 1}],
            2: [{key: 2}, {key: 2}],
            3: [{key: 3}],
        })

    def test_it_does_not_throw_if_key_does_not_exists(self):
        key = 'a'
        case = [{}, {'b': 3}, {key: 2}]

        self.assertDictEqual(group_by(case, key), {
            None: [{}, {'b': 3}],
            2: [{key: 2}],
        })

    def test_appends_with_function_applied(self):
        key = 'a'
        case = [{key: 30}]

        def fn(x): return {
            **x,
            key: x[key] * 2
        }

        self.assertDictEqual(group_by(case, key, fn=fn), {
            30: [{key: 60}]
        })

    def test_works_with_objects(self):
        key = 'a'

        class Obj():
            a = 10

        instance = Obj()
        case = [instance]

        self.assertDictEqual(group_by(case, key), {
            10: [instance],
        })
