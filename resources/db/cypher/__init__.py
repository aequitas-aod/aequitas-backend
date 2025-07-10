from pathlib import Path

from application.automation.parsing import _pythonize

DIR = Path(__file__).parent

PATH_GENERAL_CONTEXT_CYPHER = DIR / "general-context.cypher"


_MAX_LINE_LENGTH = 2**64


def _generate_kv_pair(key, value, indent=2, chunk_size=_MAX_LINE_LENGTH):
    def _indent(s, level=1):
        return " " * indent * level + s

    def _wrap(s, delimiter="'"):
        s = s.replace(delimiter, f"\\{delimiter}")
        return f"{delimiter}{s}{delimiter}"

    result = f"{_indent(f'`{key}`', level=1)}:"
    for i in range(0, len(value), chunk_size):
        if i > 0:
            result += " +"
        result += f"\n{_indent(_wrap(value[i:i + chunk_size]), level=2)}"
    return result


def generate_general_context(**kwargs):
    result = "CREATE (pc: PublicContext {"
    for i, (k, v) in enumerate(kwargs.items()):
        if i > 0:
            result += ","
        result += "\n"
        result += _generate_kv_pair(k, v)
    result += "\n});"
    return result


def generate_actual_general_context():
    from resources.db import PATH_DATASETS
    from resources.db.context import context_data, DIR as CONTEXT_DIR
    from resources.db.datasets import dataset_path, DIR as DATASETS_DIR
    from application.automation.scripts.on_dataset_created import get_stats, get_heads
    from application.automation.parsing import read_csv, to_csv
    from utils.encodings import encode as base64encode
    import json

    data = dict()

    data["datasets"] = PATH_DATASETS.read_text()

    for dataset_name in DATASETS_DIR.glob("*.csv"):
        dataset_name = dataset_name.stem
        key_name = dataset_name.title().replace("_", "")
        if "Test-" not in key_name:
            key_name += "-1"
        path = dataset_path(dataset_name)
        csv = path.read_text()
        data[f"dataset__{key_name}"] = csv
        df = read_csv(path)
        stats = _pythonize(get_stats(df))
        heads = get_heads(df)
        data[f"stats__{key_name}"] = to_csv(stats)
        data[f"dataset_head__{key_name}"] = to_csv(heads)

    for context_file in CONTEXT_DIR.glob("*.yml"):
        key_name = context_file.stem
        value = context_data(key_name)
        data[key_name] = json.dumps(value, indent=4)
        for algo in value:
            data[f"{key_name}__{algo}"] = json.dumps(value[algo], indent=4)

    for k in sorted(data.keys()):
        print("Add key", k, "to general context")

    data = {k: base64encode(v) for k, v in data.items()}
    return generate_general_context(**data)


def overwrite_actual_general_context():
    PATH_GENERAL_CONTEXT_CYPHER.write_text(generate_actual_general_context())
    print(f"Regenerated {PATH_GENERAL_CONTEXT_CYPHER}")
