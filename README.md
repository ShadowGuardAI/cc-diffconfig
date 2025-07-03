# cc-DiffConfig
Compares two configuration files (e.g., JSON, YAML, INI) and highlights the differences, showing additions, deletions, and modifications using difflib. Can be used to track config drift. - Focused on Tools that audit system or application configurations against predefined security benchmarks (e.g., CIS benchmarks, custom policies). These tools parse configuration files and compare them to a set of rules or schemas to identify deviations and potential security misconfigurations.

## Install
`git clone https://github.com/ShadowGuardAI/cc-diffconfig`

## Usage
`./cc-diffconfig [params]`

## Parameters
- `-h`: Show help message and exit
- `--type`: No description provided
- `--output`: Output file to write the diff to.
- `--schema`: Path to JSON schema file for validating config files.

## License
Copyright (c) ShadowGuardAI
