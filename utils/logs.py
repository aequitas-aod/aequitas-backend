import logging
from utils.env import ENV


if any(s in ENV for s in ["dev", "test"]):
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.ERROR)

logger = logging.getLogger("aequitas-backend")
