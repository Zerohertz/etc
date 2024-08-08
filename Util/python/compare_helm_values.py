from collections import OrderedDict

import yaml


def ordered_load(stream, Loader=yaml.SafeLoader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping
    )
    return yaml.load(stream, OrderedLoader)


def compare_yaml(yaml1, yaml2, prefix=""):
    differences = OrderedDict()

    for key in yaml1.keys():
        old_value = yaml1[key]
        new_value = yaml2.get(key, None)

        if isinstance(old_value, dict) and isinstance(new_value, dict):
            # Recursively compare nested dictionaries
            nested_diff = compare_yaml(old_value, new_value, prefix + key + ".")
            if nested_diff:
                differences[key] = nested_diff
        elif old_value != new_value:
            # If values differ, create a difference entry
            differences[key] = {"old": old_value, "new": new_value}

    return differences


def format_value(value):
    """Format the value for printing."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


def print_differences(differences, level=0):
    indent = "  " * level
    for key, value in differences.items():
        if isinstance(value, dict) and "old" in value and "new" in value:
            # Print old value as a comment
            old_formatted = format_value(value["old"])
            new_formatted = format_value(value["new"])
            print(f"{indent}# {key}: {old_formatted}")
            # Print new value
            print(f"{indent}{key}: {new_formatted}")
        elif isinstance(value, dict):
            # Only print key if there are nested changes
            print(f"{indent}{key}:")
            print_differences(value, level + 1)


def main(yaml_file1, yaml_file2):
    # Load the YAML files with order preservation
    with open(yaml_file1, "r") as file1:
        yaml1 = ordered_load(file1)
    with open(yaml_file2, "r") as file2:
        yaml2 = ordered_load(file2)

    # Compare the YAML files
    differences = compare_yaml(yaml1, yaml2)

    # Print the differences
    print_differences(differences)


# Usage
yaml_file1 = "tmp.yaml"
yaml_file2 = "values.yaml"

main(yaml_file1, yaml_file2)
