""" sample test"""


from django.test import SimpleTestCase
from app import calc


class CalcTests(SimpleTestCase):
    """Test cal module"""

    def test_add(self):
        res = calc.add(5, 6)
        self.assertEqual(res, 11)

    def test_substract(self):
        res = calc.subtract(1, 6)
        self.assertEqual(res, 5)
