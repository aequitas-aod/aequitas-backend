import sys
from . import PATH_INIT_CYPHER
from .cypher import (
    overwrite_actual_general_context,
    PATH_GENERAL_CONTEXT_CYPHER,
)


if len(sys.argv) < 2 or sys.argv[1] != "regenerate" or sys.argv[2] != "init":
    print(f"Usage: python -m resources.db regenerate init")
    exit(1)

overwrite_actual_general_context()

with PATH_INIT_CYPHER.open("w") as f:
    f.write(PATH_GENERAL_CONTEXT_CYPHER.read_text())

print(f"Regenerated {PATH_INIT_CYPHER}")
