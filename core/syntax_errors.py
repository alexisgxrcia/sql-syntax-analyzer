from core.scanner_dml import reserved_words, delimiters, operators, relational_operators, constants

ERROR_CODES = {
    101: "Símbolo desconocido.",
    
    200: "Sin error.",
    201: "Se esperaba Palabra Reservada.",
    204: "Se esperaba Identificador.",
    205: "Se esperaba Delimitador.",
    206: "Se esperaba Constante.",
    207: "Se esperaba Operador.",
    208: "Se esperaba Operador Relacional.",
    
    311: "Columna no encontrada.",
    312: "Atributo ambiguo.",
    313: "Tipo de conversión de datos no válido.",
    314: "Tabla no encontrada.",
    315: "Nombre de restricción duplicado.",
    316: "Tipo de datos no válido.",
    317: "Atributo duplicado en la tabla.",
    318: "Atributo con nombre no válido.",
    319: "Tabla no existe en condición WHERE."
}

class SyntaxErrorHandler:
    def __init__(self):
        self.forbidden_chars = ['&', '@', '$', '!', '^', '%', '?', '~', '|', '\\', '`', '"']
        
        self.valid_data_types = [
            "NUMERIC", "INT", "INTEGER", "SMALLINT", "BIGINT", "DECIMAL", "FLOAT", 
            "REAL", "CHAR", "VARCHAR", "TEXT", "DATE", "TIME", "TIMESTAMP", 
            "BOOLEAN", "BLOB", "DOUBLE"
        ]
        
        self.palabras_reservadas = set()
        for _, (_, word_code) in reserved_words.items():
            self.palabras_reservadas.add(word_code)
        
        self.delimitadores = set()
        for _, delim_code in delimiters.items():
            self.delimitadores.add(delim_code)
        
        self.operadores = set()
        for _, op_code in operators.items():
            self.operadores.add(op_code)
        
        self.operadores_relacionales = set()
        for _, rel_op_code in relational_operators.items():
            self.operadores_relacionales.add(rel_op_code)
        
        self.constantes_codes = set()
        for _, const_code in constants.items():
            self.constantes_codes.add(const_code)
        
        self.context_to_error = {
            (312, None): 201,
            (317, None): 201,
            (314, None): 208,
            (315, None): 208,
            (311, 4): 204,
            (316, 4): 204,
            (316, 61): 206,
            (316, 62): 206,
            (306, None): 204,
            (308, None): 204,
            (309, 4): 204,
            (301, None): 204,
            (302, None): 204,
            (301, 199): 204,
            (302, 199): 204,
            (311, None): 204,
            (311, 199): 204,
            (314, 52): 201,
            
            (200, None): 201,
            (202, None): 204,
            (203, None): 201,
            (204, None): 201,
            (207, None): 201,
            (208, None): 201,
            
            (211, None): 201,
            (212, None): 206,
            (213, None): 206
        }
        
        self.nonterminal_names = {
            200: "CREATE_TABLE_STMT",
            201: "MORE_STATEMENTS",
            202: "COLUMN_DEF",
            203: "DATA_TYPE",
            204: "NULLABILITY",
            205: "MORE_COLUMNS",
            206: "NEXT_COLUMN",
            207: "CONSTRAINT_DEF",
            208: "KEY_TYPE",
            209: "MORE_CONSTRAINTS",
            210: "NEXT_CONSTRAINT",
            211: "INSERT_STMT",
            212: "VALUES_LIST",
            213: "VALUE_ITEM",
            214: "MORE_VALUES",
            215: "MORE_INSERTS",
            216: "SIZE_SPEC",
            217: "KEY_CONSTRAINT",
            218: "ID_LIST",
            219: "MORE_IDS",
            300: "CONSULTA_SQL",
            301: "LISTA_ATRIBUTOS",
            302: "ATRIBUTO",
            303: "MAS_ATRIBUTOS",
            304: "IDENTIFICADOR_COMPUESTO",
            305: "REFERENCIA",
            306: "LISTA_TABLAS",
            307: "MAS_TABLAS",
            308: "TABLA",
            309: "ALIAS",
            310: "CONDICION",
            311: "EXPRESION",
            312: "OPERACION_LOGICA",
            313: "OPERANDO_IZQUIERDO",
            314: "OPERANDO_DERECHO",
            315: "OPERADOR",
            316: "VALOR",
            317: "CONECTOR_LOGICO",
            318: "CONSTANTE",
            319: "VALOR_NUMERICO",
            320: "DISTINCT_OPT"
        }
        
        self.and_code = None
        self.or_code = None
        self.where_code = None
        self.select_code = None
        self.from_code = None
        self.create_code = None
        self.table_code = None
        self.insert_code = None
        self.into_code = None
        self.values_code = None
        
        for word, (_, code) in reserved_words.items():
            word_lower = word.lower()
            if word_lower == "and":
                self.and_code = code
            elif word_lower == "or":
                self.or_code = code
            elif word_lower == "where":
                self.where_code = code
            elif word_lower == "select":
                self.select_code = code
            elif word_lower == "from":
                self.from_code = code
            elif word_lower == "create":
                self.create_code = code
            elif word_lower == "table":
                self.table_code = code
            elif word_lower == "insert":
                self.insert_code = code
            elif word_lower == "into":
                self.into_code = code
            elif word_lower == "values":
                self.values_code = code
        
        self.critical_states = {
            306: 204,
            308: 204,
            304: 204,
            312: 201,
            314: 208,
            315: 208,
            202: 204,
            203: 201,
            207: 201,
            212: 206,
            213: 206
        }

    def get_token_type(self, token_info):
        code = token_info[1][2]
        
        if (code >= 400 and code < 500):
            return 4
        
        if (code >= 600 and code < 750):
            token_value = token_info[1][1]
            if token_value.startswith("'") and token_value.endswith("'"):
                return 62
            else:
                try:
                    float(token_value)
                    return 61
                except:
                    return 62
            
        return code
    
    def is_terminal(self, symbol):
        return (symbol < 200 and symbol != 99) or symbol == 199
    
    def get_symbol_name(self, code):
        if code in self.nonterminal_names:
            return self.nonterminal_names[code]
        
        for word, (_, word_code) in reserved_words.items():
            if word_code == code:
                return word
                
        for delim, delim_code in delimiters.items():
            if delim_code == code:
                return f"'{delim}'"
                
        for op, op_code in operators.items():
            if op_code == code:
                return f"'{op}'"
                
        for rel_op, rel_op_code in relational_operators.items():
            if rel_op_code == code:
                return f"'{rel_op}'"
                
        if code == 4:
            return "IDENTIFICADOR"
        elif code == 61 or code == 62:
            return "CONSTANTE"
        elif code == 99:
            return "EPSILON"
        elif code == 199:
            return "FIN_DE_ENTRADA"
            
        return str(code)
    
    def array_to_string(self, arr):
        return " ".join([self.get_symbol_name(x) for x in arr])
    
    def format_error_message(self, error_code, line, custom_message=None):
        if error_code == 101:
            error_type = "1"
        elif error_code >= 300 and error_code < 400:
            error_type = "3"
        else:
            error_type = "2"
        
        line_formatted = f"{line:02d}"
        
        message = custom_message if custom_message else ERROR_CODES[error_code]
        
        return f"{error_type}:{error_code} Línea {line_formatted}. {message}"

    def get_error_code_by_context(self, symbol, K=None, current_context=None, prev_token_type=None, 
                                  prev_token=None, last_id_token=None, tokens=None, current_token_index=None):
        if current_context == 'IN_SUBQUERY' and K == 53:
            return 99
            
        if current_context == 'MISSING_IN' or (prev_token_type == 4 and K == 52):
            return 201
        
        if current_context == 'CREATE_TABLE':
            if prev_token == self.create_code:
                return 201
            elif prev_token == self.table_code:
                return 204
            elif symbol == 202 or symbol == 203:
                return 204
        
        if current_context == 'CONSTRAINT' and symbol == 209 and K == 55:
            return 205
        
        if current_context == 'INSERT_INTO' or prev_token == self.insert_code:
            if prev_token == self.insert_code:
                return 201
            elif prev_token == self.into_code:
                return 204
            elif symbol == 212 or symbol == 213:
                return 201
        
        if current_context == 'INSERT_VALUES':
            if prev_token == self.values_code:
                return 205
            elif symbol == 213:
                return 206
        
        if prev_token_type == 4 and K == 52:
            return 201
        
        if prev_token == self.select_code:
            return 204
        
        if prev_token == self.where_code:
            return 204
            
        if (prev_token_type == 4 or last_id_token is not None) and K in [61, 62] and current_context in ['WHERE_CONDITION', 'COMPARISON', 'COMPARISON_LEFT']:
            return 208
            
        if symbol in self.critical_states:
            return self.critical_states[symbol]
            
        if (symbol, K) in self.context_to_error:
            return self.context_to_error[(symbol, K)]
        elif (symbol, None) in self.context_to_error:
            return self.context_to_error[(symbol, None)]
            
        if current_context:
            if current_context == 'FROM' and (symbol == 306 or symbol == 308):
                return 204
                
            if current_context == 'WHERE_CONDITION' and symbol == 312:
                return 201
            
            if current_context == 'COMPARISON' and symbol in [314, 315]:
                return 208
                
            if (current_context == 'COMPARISON_LEFT' or current_context == 'WHERE_CONDITION') and K in [61, 62]:
                return 208
            
            if current_context == 'SELECT_LIST' or symbol == 301 or symbol == 302:
                return 204
            
            if current_context == 'CREATE_TABLE' and symbol >= 200 and symbol <= 210:
                if symbol in [202, 206, 207]:
                    return 204
                elif symbol == 203:
                    return 201
                elif symbol == 204:
                    return 201
                elif symbol == 208:
                    return 201
            
            if current_context == 'INSERT_INTO' and symbol >= 211 and symbol <= 215:
                if symbol in [211]:
                    return 201
                elif symbol in [212, 213, 214]:
                    return 206
        
        if prev_token == self.from_code and (symbol == 306 or symbol == 308):
            return 204
            
        if prev_token_type == 4 and K in [61, 62] and not current_context == 'COMPARISON':
            return 208
            
        if self.and_code == symbol or self.or_code == symbol:
            return 201
        elif symbol == 13:
            return 201
        elif symbol in self.operadores_relacionales:
            return 208
        elif symbol == 4:
            return 204
        elif symbol in self.delimitadores:
            return 205
        elif symbol in [61, 62] or symbol in self.constantes_codes:
            return 206
        elif symbol in self.operadores:
            return 207
        elif symbol in self.palabras_reservadas:
            return 201
        
        if symbol >= 200 and symbol <= 210:
            if symbol in [202, 206]:
                return 204
            else:
                return 201
        elif symbol >= 211 and symbol <= 215:
            if symbol in [212, 213, 214]:
                return 206
            else:
                return 201
        elif symbol >= 300:
            if symbol == 312 or symbol == 317:
                return 201
            elif symbol >= 314 and symbol <= 315:
                return 208
            elif symbol >= 316 and symbol <= 319:
                return 206
            elif symbol == 312 or symbol == 317:
                return 201
            elif symbol == 301 or symbol == 302:
                return 204
        
        return 201
    
    def classify_terminal_error(self, X, K, line, tokens, current_token_index, prev_token_type=None, current_context=None, last_id_token=None, prev_token=None):
        if X == 17 and K == 4:
            return self.format_error_message(201, line)
            
        if X == 4 and K == 52 and current_context == 'CREATE_TABLE':
            return self.format_error_message(204, line)
            
        if X == 17 and prev_token == self.create_code:
            return self.format_error_message(201, line)
            
        if X == 28 and prev_token == self.insert_code:
            return self.format_error_message(201, line)
            
        if X == 28:
            return self.format_error_message(201, line)
            
        if prev_token_type == 4 and K == 52:
            return self.format_error_message(201, line)
        
        if prev_token_type in [61, 62] and K in [61, 62] and current_context == 'INSERT_VALUES':
            return self.format_error_message(205, line)

        if X == 55 and K == 53 and current_context in ['IN_SUBQUERY', 'WHERE_CONDITION']:
            return self.format_error_message(205, line)
            
        if K in [61, 62] and prev_token_type == 4:
            error_code = 208
        else:
            error_code = self.get_error_code_by_context(X, K, current_context, prev_token_type, 
                                                        prev_token, last_id_token, tokens, current_token_index)
        
        return self.format_error_message(error_code, line)
    
    def classify_nonterminal_error(self, X, K, line, tokens, current_token_index, prev_token_type=None, current_context=None, last_id_token=None, prev_token=None):
        if current_context == 'CONSTRAINT' and X == 218 and K == 53 and prev_token == 52:
            return self.format_error_message(204, line)
            
        if current_context == 'CONSTRAINT' and X == 209 and (K == 199 or K not in [50, 53]):
            return self.format_error_message(205, line)
        
        if X in [205, 206, 217] and K == 199 and prev_token in [20, 21, 23, 24, 25]:
            return self.format_error_message(205, line)
            
        if current_context == 'CONSTRAINT' and X == 209 and K == 55:
            return self.format_error_message(205, line)
            
        if prev_token_type == 4 and K == 52:
            return self.format_error_message(201, line)
            
        if K in [61, 62] and prev_token_type == 4:
            error_code = 208
        else:
            error_code = self.get_error_code_by_context(X, K, current_context, prev_token_type, 
                                                        prev_token, last_id_token, tokens, current_token_index)
        
        return self.format_error_message(error_code, line)
    
    def check_malformed_strings(self, tokens):
        for idx, token_info in enumerate(tokens):
            line = token_info[0]
            token_data = token_info[1]
            token_text = token_data[1]
            
            if token_text == "$" or token_text == "EOF" or token_data[2] == 199:
                continue
            
            if token_text == "''":
                continue
                
            if token_text == "'":
                return self.format_error_message(205, line)
                
            if token_text.startswith("'") and not token_text.endswith("'"):
                return self.format_error_message(205, line)
                
            if token_text.endswith("'") and not token_text.startswith("'"):
                return self.format_error_message(205, line)
                
            if token_text.startswith("'") and token_text.endswith("'") and len(token_text) > 2:
                content = token_text[1:-1]
                i = 0
                while i < len(content):
                    if i < len(content) - 1 and content[i:i+2] == "''":
                        i += 2
                    else:
                        if content[i] == "'":
                            return self.format_error_message(205, line)
                        i += 1
                        
            if token_text.count("'") > 2 and token_text.startswith("'") and token_text.endswith("'"):
                inner_content = token_text[1:-1]
                if inner_content.count("'") % 2 != 0:
                    return self.format_error_message(205, line)
        
        return None

    def check_insert_into_sequence(self, tokens):
        if len(tokens) > 1:
            first_token_value = tokens[0][1][1].upper()
            second_token_value = tokens[1][1][1].upper()
            
            if first_token_value == "INSERT" and second_token_value != "INTO":
                line = tokens[1][0]
                return self.format_error_message(201, line)
        
        return None
    
    def check_consecutive_constants(self, tokens, get_token_type_fn):
        for i in range(len(tokens) - 1):
            current_token = tokens[i]
            next_token = tokens[i+1]
            
            current_type = get_token_type_fn(current_token)
            next_type = get_token_type_fn(next_token)
            
            if (current_type in [61, 62] and next_type in [61, 62]):
                line = next_token[0]
                return self.format_error_message(205, line)
        
        return None
        
    def check_forbidden_characters(self, sql_query):
        lines = sql_query.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            inside_quotes = False
            i = 0
            
            while i < len(line):
                char = line[i]
                
                if char == "'":
                    inside_quotes = not inside_quotes
                
                if not inside_quotes and char in self.forbidden_chars:
                    return self.format_error_message(101, line_num)
                
                i += 1
            
            if inside_quotes:
                pass
                
        return None
        
    def validate_select_tables(self, tokens, tables_info):
        if not tables_info:
            return None
        
        from_index = -1
        tables = []
        
        for i in range(len(tokens)):
            token_info = tokens[i]
            token_value = token_info[1][1].upper()
            token_type = self.get_token_type(token_info)
            
            if token_type == 11:
                from_index = i
                break
        
        if from_index >= 0 and from_index + 1 < len(tokens):
            i = from_index + 1
            while i < len(tokens):
                token_info = tokens[i]
                token_value = token_info[1][1]
                token_type = self.get_token_type(token_info)
                
                if token_type == 12:
                    break
                
                if token_type == 4:
                    tables.append(token_value)
                    i += 1
                    
                    if i < len(tokens) and self.get_token_type(tokens[i]) == 4:
                        i += 1
                    
                    if i < len(tokens) and tokens[i][1][1] == ',':
                        i += 1
                        continue
                    elif i < len(tokens) and self.get_token_type(tokens[i]) != 12:
                        break
                else:  
                    break
            
            for table_name in tables:
                table_exists = False
                for table_info in tables_info:
                    if table_info['name'].upper() == table_name.upper():
                        table_exists = True
                        break
                
                if not table_exists:
                    line = tokens[from_index + 1][0]
                    error_msg = self.format_error_message(314, line, f"La tabla '{table_name}' no existe en la base de datos.")
                    return {
                        "status": "error", 
                        "message": "Se encontraron errores semánticos en SELECT", 
                        "errors": [error_msg]
                    }
        
        return None
    
    def validate_select_columns(self, tokens, tables_info):
        if not tables_info:
            return None
        
        from_index = -1
        tables = []
        table_aliases = {}
        
        for i in range(len(tokens)):
            token_info = tokens[i]
            token_value = token_info[1][1].upper()
            token_type = self.get_token_type(token_info)
            
            if token_type == 11:
                from_index = i
                break
        
        if from_index >= 0 and from_index + 1 < len(tokens):
            i = from_index + 1
            while i < len(tokens):
                token_info = tokens[i]
                token_value = token_info[1][1]
                token_type = self.get_token_type(token_info)
                
                if token_type == 12:
                    break
                
                if token_type == 4:
                    table_name = token_value
                    tables.append(table_name)
                    i += 1
                    
                    if i < len(tokens) and self.get_token_type(tokens[i]) == 4:
                        alias = tokens[i][1][1]
                        table_aliases[alias.upper()] = table_name.upper()
                        i += 1
                    
                    if i < len(tokens) and tokens[i][1][1] == ',':
                        i += 1
                        continue
                    elif i < len(tokens) and self.get_token_type(tokens[i]) != 12:
                        break
                else:  
                    break
        
        columns = []
        select_index = -1
        
        for i in range(len(tokens)):
            token_info = tokens[i]
            token_value = token_info[1][1].upper()
            token_type = self.get_token_type(token_info)
            
            if token_type == 10:
                select_index = i
                break
        
        if select_index >= 0 and select_index + 1 < len(tokens) and from_index > select_index:
            i = select_index + 1
            
            if i < len(tokens) and self.get_token_type(tokens[i]) == 30:
                i += 1
            
            while i < from_index:
                token_info = tokens[i]
                token_value = token_info[1][1]
                token_type = self.get_token_type(token_info)
                
                if token_type == 4 or token_value == '*':
                    column = token_value
                    
                    if i + 2 < from_index and tokens[i+1][1][1] == '.' and self.get_token_type(tokens[i+2]) == 4:
                        table_name = token_value
                        column = tokens[i+2][1][1]
                        columns.append((table_name, column))
                        i += 3
                    else:
                        columns.append((None, column))
                        i += 1
                    
                    if i < from_index and tokens[i][1][1] == ',':
                        i += 1
                        continue
                else:
                    i += 1
        
        for table_name, column_name in columns:
            if column_name == '*':
                continue
            
            if table_name:
                if table_name.upper() in table_aliases:
                    table_name = table_aliases[table_name.upper()]
                
                table_found = False
                for table_info in tables_info:
                    if table_info['name'].upper() == table_name.upper():
                        table_found = True
                        column_found = False
                        for attr in table_info['attributes']:
                            if attr['name'].upper() == column_name.upper():
                                column_found = True
                                break
                        
                        if not column_found:
                            line = tokens[select_index + 1][0]
                            error_msg = self.format_error_message(311, line, f"La columna '{column_name}' no existe en la tabla '{table_name}'.")
                            return {
                                "status": "error", 
                                "message": "Se encontraron errores semánticos en SELECT", 
                                "errors": [error_msg]
                            }
                        break
                
                if not table_found:
                    line = tokens[select_index + 1][0]
                    error_msg = self.format_error_message(314, line, f"La tabla '{table_name}' no existe en la base de datos.")
                    return {
                        "status": "error", 
                        "message": "Se encontraron errores semánticos en SELECT", 
                        "errors": [error_msg]
                    }
            else:
                column_found = False
                tables_with_column = []
                
                for table_name in tables:
                    for table_info in tables_info:
                        if table_info['name'].upper() == table_name.upper():
                            for attr in table_info['attributes']:
                                if attr['name'].upper() == column_name.upper():
                                    column_found = True
                                    tables_with_column.append(table_info['name'])
                                    break
                                    
                if len(tables_with_column) > 1:
                    line = tokens[select_index + 1][0]
                    error_msg = self.format_error_message(312, line, f"La columna '{column_name}' es ambigua. Existe en las tablas: {', '.join(tables_with_column)}.")
                    return {
                        "status": "error", 
                        "message": "Se encontraron errores semánticos en SELECT", 
                        "errors": [error_msg]
                    }
        
        return None
    
    def validate_type_conversions(self, tokens, tables_info):
        if not tables_info:
            return None
            
        is_select_query = False
        for token_info in tokens:
            token_type = self.get_token_type(token_info)
            if token_type == 10:
                is_select_query = True
                break
                
        if not is_select_query:
            return None
        
        numeric_types = ['INTEGER', 'INT', 'SMALLINT', 'TINYINT', 'BIGINT', 'DECIMAL', 'NUMERIC',
                        'FLOAT', 'REAL', 'DOUBLE']
        string_types = ['VARCHAR', 'CHAR', 'TEXT']
        date_types = ['DATE', 'DATETIME', 'TIMESTAMP', 'TIME']
        
        type_compatibility = {
            'numeric': {
                'numeric': True,
                'string': False,
                'date': False,
                'boolean': True
            },
            'string': {
                'numeric': False,
                'string': True,
                'date': False,
                'boolean': False
            },
            'date': {
                'numeric': False,
                'string': False,
                'date': True,
                'boolean': False
            },
            'boolean': {
                'numeric': True,
                'string': False,
                'date': False,
                'boolean': True
            }
        }
        
        column_types = {}
        
        for table_info in tables_info:
            table_name = table_info.get('name', '').upper()
            attributes = table_info.get('attributes', [])
            
            for attr in attributes:
                column_name = attr.get('name', '').upper()
                column_type = attr.get('type', '').upper()
                
                column_key = f"{table_name}.{column_name}"
                column_types[column_key] = column_type
                column_types[column_name] = column_type
        
        where_index = -1
        for i in range(len(tokens)):
            if self.get_token_type(tokens[i]) == 12:
                where_index = i
                break
                
        if where_index < 0:
            return None
            
        i = where_index + 1
        
        while i < len(tokens) - 2:
            if self.get_token_type(tokens[i]) == 4:
                left_operand = tokens[i][1][1].upper()
                left_type_category = None
                
                if i + 2 < len(tokens) and tokens[i+1][1][1] == '.' and self.get_token_type(tokens[i+2]) == 4:
                    table_name = left_operand
                    column_name = tokens[i+2][1][1].upper()
                    left_operand = f"{table_name}.{column_name}"
                    i += 2
                
                left_data_type = column_types.get(left_operand)
                
                if left_data_type:
                    if left_data_type in numeric_types:
                        left_type_category = 'numeric'
                    elif left_data_type in string_types:
                        left_type_category = 'string'
                    elif left_data_type in date_types:
                        left_type_category = 'date'
                    elif left_data_type == 'BOOLEAN':
                        left_type_category = 'boolean'
                else:
                    i += 1
                    continue
                
                if i + 1 < len(tokens) and self.get_token_type(tokens[i+1]) in self.operadores_relacionales:
                    operator = tokens[i+1][1][1]
                    i += 1
                    
                    if i + 1 < len(tokens):
                        i += 1
                        right_token = tokens[i]
                        right_token_type = self.get_token_type(right_token)
                        right_operand = right_token[1][1]
                        right_type_category = None
                        
                        if right_token_type == 61:
                            right_type_category = 'numeric'
                        elif right_token_type == 62:
                            right_type_category = 'string'
                        elif right_token_type == 4:
                            if i + 2 < len(tokens) and tokens[i+1][1][1] == '.' and self.get_token_type(tokens[i+2]) == 4:
                                right_table = right_operand
                                right_column = tokens[i+2][1][1].upper()
                                right_operand = f"{right_table}.{right_column}"
                                i += 2
                            
                            right_data_type = column_types.get(right_operand.upper())
                            
                            if right_data_type:
                                if right_data_type in numeric_types:
                                    right_type_category = 'numeric'
                                elif right_data_type in string_types:
                                    right_type_category = 'string'
                                elif right_data_type in date_types:
                                    right_type_category = 'date'
                                elif right_data_type == 'BOOLEAN':
                                    right_type_category = 'boolean'
                            else:
                                right_type_category = 'string'
                        
                        if left_type_category and right_type_category and left_type_category != right_type_category:
                            if not type_compatibility.get(left_type_category, {}).get(right_type_category, False):
                                line = right_token[0]
                                error_msg = self.format_error_message(313, line, 
                                    f"Error de conversión al convertir el valor del atributo '{left_operand}' del tipo {left_type_category} a tipo de dato {right_type_category}.")
                                
                                return {
                                    "status": "error", 
                                    "message": "Se encontraron errores semánticos en la conversión de tipos", 
                                    "errors": [error_msg]
                                }
                    i += 1
                else:
                    i += 1
            else:
                i += 1
        
        return None

    def validate_create_table_constraints(self, tokens):
        constraint_names = []
        
        for i in range(len(tokens) - 1):
            token_info = tokens[i]
            token_value = token_info[1][1].upper()
            
            if token_value == 'CONSTRAINT' and i + 1 < len(tokens):
                constraint_name = tokens[i+1][1][1]
                
                if constraint_name in constraint_names:
                    line = tokens[i+1][0]
                    error_msg = self.format_error_message(315, line, 
                                f"El nombre de restricción '{constraint_name}' está duplicado.")
                    return {
                        "status": "error", 
                        "message": "Se encontraron errores semánticos en CREATE TABLE", 
                        "errors": [error_msg]
                    }
                    
                constraint_names.append(constraint_name)
        
        return None
        
    def validate_where_conditions(self, tokens, tables_info):
        if not tables_info:
            return None
            
        where_index = -1
        for i in range(len(tokens)):
            token_info = tokens[i]
            token_value = token_info[1][1].upper()
            token_type = self.get_token_type(token_info)
            
            if token_type == 12:
                where_index = i
                break
                
        if where_index < 0 or where_index + 1 >= len(tokens):
            return None
            
        i = where_index + 1
        while i < len(tokens):
            token_info = tokens[i]
            token_value = token_info[1][1]
            token_type = self.get_token_type(token_info)
            
            if token_type == 4:
                if i + 2 < len(tokens) and tokens[i+1][1][1] == '.' and self.get_token_type(tokens[i+2]) == 4:
                    table_name = token_value
                    column_name = tokens[i+2][1][1]
                    
                    table_exists = False
                    for table_info in tables_info:
                        if table_info['name'].upper() == table_name.upper():
                            table_exists = True
                            break
                    
                    if not table_exists:
                        line = token_info[0]
                        error_msg = self.format_error_message(319, line, 
                                    f"El identificador \"{table_name}.{column_name}\" no es válido. Tabla no encontrada.")
                        return {
                            "status": "error", 
                            "message": "Se encontraron errores semánticos en la cláusula WHERE", 
                            "errors": [error_msg]
                        }
                    
                    column_exists = False
                    for table_info in tables_info:
                        if table_info['name'].upper() == table_name.upper():
                            for attr in table_info['attributes']:
                                if attr['name'].upper() == column_name.upper():
                                    column_exists = True
                                    break
                            break
                    
                    if not column_exists:
                        line = token_info[0]
                        error_msg = self.format_error_message(311, line, 
                                    f"La columna '{column_name}' no existe en la tabla '{table_name}'.")
                        return {
                            "status": "error", 
                            "message": "Se encontraron errores semánticos en la cláusula WHERE", 
                            "errors": [error_msg]
                        }
                    
                    if '#' in column_name:
                        line = token_info[0]
                        error_msg = self.format_error_message(318, line, 
                                    f"El nombre del atributo \"{column_name}\" no es válido.")
                        return {
                            "status": "error", 
                            "message": "Se encontraron errores semánticos en la cláusula WHERE", 
                            "errors": [error_msg]
                        }
                    
                    i += 3
                    
                    if i < len(tokens) and self.get_token_type(tokens[i]) in self.operadores_relacionales:
                        operator = tokens[i][1][1]
                        i += 1
                        
                        if i < len(tokens):
                            right_token = tokens[i]
                            right_type = self.get_token_type(right_token)
                            right_value = right_token[1][1]
                            
                            if right_type == 4:
                                if i + 2 < len(tokens) and tokens[i+1][1][1] == '.' and self.get_token_type(tokens[i+2]) == 4:
                                    right_table = right_value
                                    right_column = tokens[i+2][1][1]
                                    
                                    table_exists = False
                                    for table_info in tables_info:
                                        if table_info['name'].upper() == right_table.upper():
                                            table_exists = True
                                            break
                                    
                                    if not table_exists:
                                        line = right_token[0]
                                        error_msg = self.format_error_message(319, line, 
                                                    f"El identificador \"{right_table}.{right_column}\" no es válido. Tabla no encontrada.")
                                        return {
                                            "status": "error", 
                                            "message": "Se encontraron errores semánticos en la cláusula WHERE", 
                                            "errors": [error_msg]
                                        }
                                    
                                    column_exists = False
                                    for table_info in tables_info:
                                        if table_info['name'].upper() == right_table.upper():
                                            for attr in table_info['attributes']:
                                                if attr['name'].upper() == right_column.upper():
                                                    column_exists = True
                                                    break
                                            break
                                    
                                    if not column_exists:
                                        line = right_token[0]
                                        error_msg = self.format_error_message(311, line, 
                                                    f"La columna '{right_column}' no existe en la tabla '{right_table}'.")
                                        return {
                                            "status": "error", 
                                            "message": "Se encontraron errores semánticos en la cláusula WHERE", 
                                            "errors": [error_msg]
                                        }
                                    
                                    i += 3
                                else:
                                    is_valid_column = False
                                    
                                    for table_info in tables_info:
                                        for attr in table_info['attributes']:
                                            if attr['name'].upper() == right_value.upper():
                                                is_valid_column = True
                                                break
                                        if is_valid_column:
                                            break
                                    
                                    if not is_valid_column:
                                        line = right_token[0]
                                        error_msg = self.format_error_message(312, line, 
                                                    f"El nombre del atributo \"{right_value}\" no es válido.")
                                        return {
                                            "status": "error", 
                                            "message": "Se encontraron errores semánticos en la cláusula WHERE", 
                                            "errors": [error_msg]
                                        }
                                    
                                    i += 1
                            elif right_type == 62:
                                if not (right_value.startswith("'") and right_value.endswith("'")):
                                    line = right_token[0]
                                    error_msg = self.format_error_message(205, line, 
                                                f"Error de sintaxis: el literal de texto '{right_value}' debe estar entre comillas simples.")
                                    return {
                                        "status": "error", 
                                        "message": "Se encontraron errores de sintaxis en la cláusula WHERE", 
                                        "errors": [error_msg]
                                    }
                                i += 1
                            else:
                                i += 1
                        else:
                            break
                    
                else:
                    column_name = token_value
                    
                    if '#' in column_name:
                        line = token_info[0]
                        error_msg = self.format_error_message(318, line, 
                                    f"El nombre del atributo \"{column_name}\" no es válido.")
                        return {
                            "status": "error", 
                            "message": "Se encontraron errores semánticos en la cláusula WHERE", 
                            "errors": [error_msg]
                        }
                    
                    i += 1
            else:
                i += 1
                
        return None
    
    def validate_unquoted_literal(self, value):
        if not isinstance(value, str):
            return False
            
        if value.startswith("'") and value.endswith("'"):
            return False
            
        if value.isdigit():
            return False
            
        if not value.isalpha() and not value.isdigit():
            return True
            
        return False
    
    def validate_attribute_names(self, tokens):
        is_select_query = False
        for token_info in tokens:
            token_type = self.get_token_type(token_info)
            if token_type == 10:
                is_select_query = True
                break
                
        if not is_select_query:
            return None
            
        for i in range(len(tokens)):
            token_info = tokens[i]
            token_value = token_info[1][1]
            token_type = self.get_token_type(token_info)
            
            if token_type == 4:
                if '#' in token_value:
                    is_attribute = False
                    
                    if i > 0:
                        prev_token_type = self.get_token_type(tokens[i-1])
                        prev_token_value = tokens[i-1][1][1]
                        if prev_token_type == 10 or prev_token_value == ',':
                            is_attribute = True
                    
                    if i > 0 and tokens[i-1][1][1] == '.':
                        is_attribute = True
                    elif i + 1 < len(tokens) and self.get_token_type(tokens[i+1]) in self.operadores_relacionales:
                        is_attribute = True
                    elif i + 1 < len(tokens) and tokens[i+1][1][1] == '.':
                        is_attribute = True
                    elif i + 1 < len(tokens):
                        next_token_value = tokens[i+1][1][1]
                        next_token_type = self.get_token_type(tokens[i+1])
                        if next_token_value == ',' or next_token_type == 11:
                            is_attribute = True
                    elif i > 1 and (self.get_token_type(tokens[i-1]) == 14 or self.get_token_type(tokens[i-1]) == 15):
                        is_attribute = True
                    elif i > 2 and tokens[i-2][1][1] == '(' and self.get_token_type(tokens[i-1]) == 10:
                        is_attribute = True
                    elif i > 1 and self.get_token_type(tokens[i-1]) == 13:
                        is_attribute = True
                        
                    if is_attribute:
                        line = token_info[0]
                        error_msg = self.format_error_message(318, line, f"El nombre del atributo \"{token_value}\" no es válido.")
                        return {
                            "status": "error", 
                            "message": "Se encontraron errores semánticos en nombres de atributos", 
                            "errors": [error_msg]
                        }
        
        return None