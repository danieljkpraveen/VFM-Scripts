import ast
import sys


def clean_and_parse(value):
    value = value.strip()
    if value.startswith('[') and value.endswith(']'):
        value = value.replace('\\"', '"')
        try:
            return ast.literal_eval(value)
        except Exception:
            return value
    return value


def process_inputs(lines):
    outputs = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Split by the first comma
        if ',' in line:
            key, val = line.split(',', 1)
        else:
            key, val = line, ""
        value = clean_and_parse(val)
        # Always convert value to string for the second column
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value)
        outputs.append([key.strip(), str(value)])
    return outputs


def read_stdin():
    return sys.stdin.read()


if __name__ == "__main__":
    input_str = read_stdin().strip().splitlines()
    result = process_inputs(input_str)
    print(len(result))
    print(str(result))
