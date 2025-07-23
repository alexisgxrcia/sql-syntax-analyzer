# SQL Syntax Analyzer

This project was developed as an educational framework for demonstrating core compiler construction principles through the implementation of a complete SQL compiler front-end. It focuses on SQL query processing and database system integration, serving as a learning tool for understanding how compilers analyze and transform SQL code.

- **Lexical Analysis**: Token recognition and symbol table management
- **Syntax Analysis**: Grammar validation and parse tree construction  
- **Semantic Analysis**: Type checking and contextual validation
- **Error Handling**: Comprehensive error detection and recovery
- **Database Integration**: Real-time query execution and schema validation

## System Architecture

The system follows the **classical compiler pipeline** architecture:

```
SQL Input → Lexical Analysis → Syntax Analysis → Semantic Analysis → Code Generation → Execution
     ↓              ↓               ↓                ↓                ↓             ↓
 Raw SQL      →   Tokens      →   Parse Tree   →  Symbol Table  →   Validated  →  Results
                                                                      Query
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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.