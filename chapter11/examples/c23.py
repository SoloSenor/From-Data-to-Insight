import io
import unittest

def check_function(function):
    class RegressionTest(unittest.TestCase):
        def test_partial_return(self):
            self.assertEqual(function(3, 100, 1), 200)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(RegressionTest)
    result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
    return result.wasSuccessful()

print(check_function(lambda q, p, r: q * p - r))
print(check_function(lambda q, p, r: (q - r) * p))
