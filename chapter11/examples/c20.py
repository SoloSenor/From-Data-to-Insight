import io
import unittest

def require_positive(value):
    if value <= 0:
        raise ValueError("quantity must be positive")
    return value

class ValidationTests(unittest.TestCase):
    def test_zero_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "positive"):
            require_positive(0)

suite = unittest.defaultTestLoader.loadTestsFromTestCase(ValidationTests)
result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
print(result.wasSuccessful())
