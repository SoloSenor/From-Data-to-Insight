import io
import unittest

class BoundaryTests(unittest.TestCase):
    def test_cases(self):
        cases = [(3, 100, 0, 300), (3, 100, 1, 200),
                 (3, 100, 3, 0), (3, 0, 1, 0)]
        for quantity, price, returned, expected in cases:
            with self.subTest(quantity=quantity, returned=returned):
                self.assertEqual((quantity - returned) * price, expected)

suite = unittest.defaultTestLoader.loadTestsFromTestCase(BoundaryTests)
result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
print(result.testsRun)
print(result.wasSuccessful())
