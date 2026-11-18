import io
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

class FileTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "data.txt"

    def test_roundtrip(self):
        self.path.write_text("ready", encoding="ascii")
        self.assertEqual(self.path.read_text(encoding="ascii"), "ready")

suite = unittest.defaultTestLoader.loadTestsFromTestCase(FileTests)
result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
print(result.wasSuccessful())
