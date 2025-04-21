# AnansiCore

AnansiCore is a symbolic, structured, and deterministic intermediate language designed to represent the syntax and control flow of high-level code in a linear token format. It is both human-readable and machine-parseable, optimized for program analysis, transformation, and intelligent patching workflows.

## ✨ Features

- Fully deterministic structure: `Etiqueta.ID:Payload`
- Clean separation of syntax and payload content
- Hierarchical token IDs allow reconstructing AST
- Validated using strict rules from v0.7 grammar specification
- Supports conversion between `.txt` and `.json` formats
- Includes a Python-based CLI to parse, validate, edit and export files
- Ready for integration with code generators, linters or AI tools

## 📁 Project Structure

```
anansicore/
├── grammar.lark         # Lark grammar for parsing tokens
├── requeriments.txt     # Requeriments
├── parser.py            # CLI parser for txt/json input
├── validator.py         # Structural and semantic validation rules
├── test/                # Unit tests for validation engine
├── examples/            # Sample .txt and .json test cases
├── data/                # Your custom .txt / .json AnansiCore files
├── docs/                # For full grammar specification and encoding rules
└── README.md
```

## 🛠️ Requirements

- Python ≥ 3.8
- [lark-parser](https://github.com/lark-parser/lark) ≥ 1.1

Install dependencies:

```bash
pip install -r requirements.txt
```

## 🚀 Quickstart

```bash
# Validate a .txt file and export to json
python parser.py examples/sample.txt -o output.json

# Edit a token's payload in-place
python parser.py output.json --edit r.1.2 '[[new_value]]'

# Convert JSON back to txt
python parser.py output.json --txt regenerated.txt
```

## 🧪 Run tests

```bash
python test_validator.py
```

## 🔍 License

MIT License. Created by Manuel Barros and contributors.
