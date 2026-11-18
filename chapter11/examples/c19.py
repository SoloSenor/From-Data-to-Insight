import io
import unittest

def retained(quantity, price, returned):
    return (quantity - returned) * price

class RetainedTests(unittest.TestCase):
    def test_partial_return(self):
        self.assertEqual(retained(3, 100, 1), 200)

suite = unittest.defaultTestLoader.loadTestsFromTestCase(RetainedTests)
result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
print(result.testsRun)
print(result.wasSuccessful())
