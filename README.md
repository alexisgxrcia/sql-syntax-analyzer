# SQL Syntax Analyzer
## *Advanced SQL Parser with Lexical, Syntactic, and Semantic Analysis*

A comprehensive SQL compiler front-end implementing classical compiler construction phases, designed as an educational framework for understanding formal language processing and database query analysis.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

## 🎯 Project Overview

This project implements a complete **SQL compiler front-end** demonstrating fundamental principles of compiler construction applied to SQL query processing. It serves as an educational tool for understanding:

- **Lexical Analysis**: Token recognition and symbol table management
- **Syntax Analysis**: Grammar validation and parse tree construction  
- **Semantic Analysis**: Type checking and contextual validation
- **Error Handling**: Comprehensive error detection and recovery
- **Database Integration**: Real-time query execution and schema validation

## 🏗️ System Architecture

The system follows the **classical compiler pipeline** architecture:

```
SQL Input → Lexical Analysis → Syntax Analysis → Semantic Analysis → Code Generation → Execution
     ↓              ↓               ↓                ↓                ↓             ↓
 Raw SQL      →   Tokens      →   Parse Tree   →  Symbol Table  →   Validated  →  Results
                                                                      Query
```

### 📁 Component Structure

```
sql-syntax-analyzer/
├── app.py                          # Main GUI Application & Controller
├── core/
│   ├── scanner_dml.py              # Lexical Analyzer (Tokenizer)
│   ├── analyzer_syntax.py          # Syntax Analyzer (Parser)
│   ├── analyzer_semantic.py        # Semantic Analyzer
│   ├── syntax_errors.py            # Error Handler & Recovery System
│   └── db_connector.py             # Database Abstraction Layer
└── README.md
```

## 🚀 Installation & Setup

### Prerequisites
```bash
# Python 3.7 or higher
python --version

# MySQL 8.0 or higher
mysql --version
```

### Dependency Installation
```bash
pip install mysql-connector-python
pip install customtkinter
pip install Pillow
```

### Database Configuration
**Configure Connection** in `core/db_connector.py`:
```python
DB_CONFIG = {
    "db_name": "inscritos",
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "your_password"
}
```

### Execution
```bash
cd sql-syntax-analyzer
python app.py
```

### Token Classification System

| Type | Code Range | Description | Examples |
|------|------------|-------------|----------|
| Reserved Words | 10-30 | SQL keywords | SELECT, FROM, WHERE |
| Identifiers | 401+ | User-defined names | table_name, column_name |
| Constants | 600+ | Literal values | 'string', 123, 45.67 |
| Delimiters | 50-55 | Syntax separators | ( ) , ; ' |
| Operators | 70-73 | Arithmetic operators | + - * / |
| Relational | 81-86 | Comparison operators | = < > <= >= <> |

### Error Classification

The system implements a hierarchical error classification scheme:

- **Level 1**: Lexical Errors (invalid characters, malformed tokens)
- **Level 2**: Syntax Errors (grammar violations, missing tokens)
- **Level 3**: Semantic Errors (type mismatches, undefined references)
- **Level 4**: Runtime Errors (constraint violations, execution failures)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Developed as an educational framework for demonstrating compiler construction principles applied to SQL query processing and database system integration.**