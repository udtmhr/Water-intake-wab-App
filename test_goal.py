import unittest
from utils import calculate_daily_goal

class TestGoalCalculation(unittest.TestCase):
    def test_young_age(self):
        # Age < 30: weight * 40
        self.assertEqual(calculate_daily_goal(60, 25), 2400)

    def test_middle_age(self):
        # Age 30-55: weight * 35
        self.assertEqual(calculate_daily_goal(60, 40), 2100)

    def test_senior_age(self):
        # Age > 55: weight * 30
        self.assertEqual(calculate_daily_goal(60, 60), 1800)

if __name__ == '__main__':
    unittest.main()
