import io
import logging
buffer = io.StringIO()
logger = logging.Logger("chapter11.example")
handler = logging.StreamHandler(buffer)
handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
logger.addHandler(handler)
try:
    logger.warning("invalid record=%s field=%s", 2, "quantity")
finally:
    logger.removeHandler(handler)
    handler.close()
print(buffer.getvalue(), end="")
