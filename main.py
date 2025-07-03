import argparse
import difflib
import json
import logging
import os
import sys
import yaml

try:
    from jsonschema import validate, ValidationError
except ImportError:
    print("jsonschema library not found. Please install it: pip install jsonschema")
    sys.exit(1)


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.

    Returns:
        argparse.ArgumentParser: The configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Compares two configuration files and highlights the differences."
    )
    parser.add_argument("file1", help="Path to the first configuration file.")
    parser.add_argument("file2", help="Path to the second configuration file.")
    parser.add_argument(
        "--type",
        choices=["json", "yaml", "ini"],
        default="yaml",
        help="Type of configuration files (default: yaml).",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file to write the diff to.",
    )
    parser.add_argument(
        "--schema",
        help="Path to JSON schema file for validating config files.",
    )
    return parser


def load_config(file_path, config_type):
    """
    Loads a configuration file based on its type.

    Args:
        file_path (str): The path to the configuration file.
        config_type (str): The type of the configuration file (json, yaml, ini).

    Returns:
        dict: The loaded configuration as a dictionary.
        None: If the file doesn't exist or the type is unsupported

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not valid
    """
    try:
        with open(file_path, "r") as f:
            if config_type == "json":
                try:
                    return json.load(f)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON file: {e}") from e
            elif config_type == "yaml":
                try:
                    return yaml.safe_load(f)
                except yaml.YAMLError as e:
                    raise ValueError(f"Invalid YAML file: {e}") from e
            elif config_type == "ini":
                # Implement INI parsing if needed. For now, raise an exception
                raise ValueError("INI format is not yet supported.")
            else:
                logging.error(f"Unsupported configuration type: {config_type}")
                return None
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {file_path}") from e
    except Exception as e:
        logging.error(f"Error loading config file: {e}")
        return None


def validate_config(config_data, schema_path):
    """Validates a configuration dictionary against a JSON schema.

    Args:
        config_data (dict): The configuration data to validate.
        schema_path (str): The path to the JSON schema file.

    Returns:
        bool: True if the configuration is valid, False otherwise.
    """
    if not schema_path:
        return True # Validation skipped as no schema path specified

    try:
        with open(schema_path, "r") as f:
            schema = json.load(f)

        validate(instance=config_data, schema=schema)
        logging.info("Configuration file is valid against the schema.")
        return True
    except FileNotFoundError:
        logging.error(f"Schema file not found: {schema_path}")
        return False
    except ValidationError as e:
        logging.error(f"Configuration validation failed: {e}")
        return False
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON schema file: {e}")
        return False
    except Exception as e:
        logging.error(f"Error validating configuration: {e}")
        return False


def diff_configs(config1, config2):
    """
    Compares two configuration dictionaries and returns a diff.

    Args:
        config1 (dict): The first configuration dictionary.
        config2 (dict): The second configuration dictionary.

    Returns:
        list: A list of strings representing the diff.
    """
    config1_str = json.dumps(config1, indent=4, sort_keys=True).splitlines()
    config2_str = json.dumps(config2, indent=4, sort_keys=True).splitlines()

    diff = difflib.unified_diff(config1_str, config2_str, fromfile="file1", tofile="file2")
    return list(diff)


def write_diff(diff, output_file):
    """
    Writes the diff to the specified output file.

    Args:
        diff (list): The list of diff lines.
        output_file (str): The path to the output file.
    """
    try:
        with open(output_file, "w") as f:
            for line in diff:
                f.write(line + "\n")
        logging.info(f"Diff written to: {output_file}")
    except Exception as e:
        logging.error(f"Error writing diff to file: {e}")


def main():
    """
    Main function to execute the configuration comparison.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    # Input validation: check that both files exist
    if not os.path.exists(args.file1):
        logging.error(f"File not found: {args.file1}")
        sys.exit(1)
    if not os.path.exists(args.file2):
        logging.error(f"File not found: {args.file2}")
        sys.exit(1)

    try:
        config1 = load_config(args.file1, args.type)
        config2 = load_config(args.file2, args.type)
    except ValueError as e:
        logging.error(e)
        sys.exit(1)
    except FileNotFoundError as e:
        logging.error(e)
        sys.exit(1)

    if config1 is None or config2 is None:
        sys.exit(1)

    # Validate config files against schema if provided
    if args.schema:
        if not validate_config(config1, args.schema) or not validate_config(config2, args.schema):
            sys.exit(1)

    diff = diff_configs(config1, config2)

    if diff:
        if args.output:
            write_diff(diff, args.output)
        else:
            for line in diff:
                print(line)
    else:
        logging.info("Configurations are identical.")

    logging.info("Configuration comparison completed.")


if __name__ == "__main__":
    main()