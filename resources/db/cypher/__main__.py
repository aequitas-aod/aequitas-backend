import sys
from . import overwrite_actual_general_context


if len(sys.argv) < 2 or sys.argv[1] != "regenerate" or sys.argv[2] != "general_context":
    print(f"Usage: python -m resources.db.cypher regenerate general_context")
    exit(1)

overwrite_actual_general_context()
