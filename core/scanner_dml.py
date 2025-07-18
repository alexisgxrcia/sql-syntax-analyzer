import re

reserved_words = {
    'SELECT': ('s', 10),
    'FROM': ('f', 11),
    'WHERE': ('w', 12),
    'IN': ('n', 13),
    'AND': ('y', 14),
    'OR': ('o', 15),
    'CREATE': ('c', 16),
    'TABLE': ('t', 17),
    'CHAR': ('h', 18),
    'NUMERIC': ('u', 19),
    'NOT': ('e', 20),
    'NULL': ('g', 21),
    'CONSTRAINT': ('b', 22),
    'KEY': ('k', 23),
    'PRIMARY': ('p', 24),
    'FOREIGN': ('j', 25),
    'REFERENCES': ('l', 26),
    'INSERT': ('m', 27),
    'INTO': ('q', 28),
    'VALUES': ('v', 29),
    'DISTINCT': ('d', 30)
}

delimiters = {
    ',': 50,
    '.': 51,
    '(': 52,
    ')': 53,
    "'": 54,
    ';': 55
}

operators = {
    '+': 70,
    '-': 71,
    '*': 72,
    '/': 73
}

constants = {
    'd': 61,
    'a': 62
}

relational_operators = {
    '>': 81,
    '<': 82,
    '=': 83,
    '>=': 84,
    '<=': 85,
    '<>': 86
}

class DMLScanner:
    def __init__(self):
        self.tokens = []
        self.line_number = 1
        self.current_tokens = []
        self.identifier_counter = 401
        self.constant_counter = 600
        self.identifiers = {}
        self.constants = {}
        self.last_operator = None
    
    def reset(self):
        self.tokens = []
        self.line_number = 1
        self.current_tokens = []
        self.identifier_counter = 401
        self.constant_counter = 600
        self.identifiers = {}
        self.constants = {}
        self.last_operator = None
    
    def analyze_sql(self, sql_query):
        self.reset()
        
        self.input_module(sql_query)
        
        return {
            'tokens': self.tokens,
            'identifiers': self.identifiers,
            'constants': self.constants,
        }
    
    def get_token_type_text(self, type_code):
        type_map = {
            1: "Palabra Reservada",
            4: "Identificador",
            5: "Delimitador",
            6: "Constante",
            7: "Operador",
            8: "Operador Relacional"
        }
        return type_map.get(type_code, "Desconocido")
    
    def input_module(self, sql_query):
        lines = sql_query.strip().split('\n')
        self.line_number = 1
        
        for line in lines:
            line = line.replace("'", "'")
            line = line.replace("'", "'")
            
            tokens = []
            i = 0
            while i < len(line):
                if line[i] == "'":
                    start = i
                    i += 1
                    while i < len(line) and line[i] != "'":
                        i += 1
                    if i < len(line):
                        i += 1
                        tokens.append(line[start:i])
                    else:
                        tokens.append(line[start:])
                
                elif line[i] in ',;()':
                    tokens.append(line[i])
                    i += 1
                
                elif line[i] == '.':
                    tokens.append(line[i])
                    i += 1
                
                elif line[i] in '<>=':
                    start = i
                    i += 1
                    if i < len(line) and ((line[i-1] == '<' and line[i] in '>=') or 
                                         (line[i-1] == '>' and line[i] == '=') or
                                         (line[i-1] == '=' and line[i] == '>')):
                        i += 1
                    tokens.append(line[start:i])
                    self.last_operator = line[start:i]
                
                elif line[i] in '+-*/':
                    tokens.append(line[i])
                    i += 1
                
                elif line[i].isalnum() or line[i] == '#' or line[i] == '_':
                    start = i
                    i += 1
                    while i < len(line) and (line[i].isalnum() or line[i] == '#' or line[i] == '_' or line[i] == '.'):
                        i += 1
                    tokens.append(line[start:i])
                
                elif line[i].isspace():
                    i += 1
                
                else:
                    tokens.append(line[i])
                    i += 1
            
            self.analyze_tokens(tokens)
            self.line_number += 1
    
    def is_constant(self, token, prev_tokens=None):
        if token.startswith("'") and token.endswith("'"):
            return True
        
        if token.isdigit():
            return True
        
        if '.' in token or '#' in token:
            return False
        
        if self.last_operator in relational_operators:
            if re.match(r'^[A-Za-z]', token) and token.isalnum():
                return False
            if not (token.startswith("'") and token.endswith("'")):
                return True
        
        if self.current_tokens and self.current_tokens[-1] == '=':
            if re.match(r'^[A-Za-z]', token) and token.isalnum():
                return False
            if not (token.startswith("'") and token.endswith("'")):
                return True
            
        return False

    def is_identifier(self, token):
        if token.upper() in reserved_words:
            return False
            
        if token in operators or token in delimiters or token in relational_operators:
            return False
            
        if self.is_constant(token):
            return False
            
        if '.' in token:
            parts = token.split('.')
            if len(parts) == 2 and all(part.isalnum() or '#' in part or '_' in part for part in parts):
                return True
            
        return token.isalnum() or '#' in token or '_' in token
            
    def analyze_module(self, token):
        token_upper = token.upper()
        
        if token_upper in reserved_words:
            symbol, id_ = reserved_words[token_upper]
            self.current_tokens.append(token)
            return (1, token_upper, id_, symbol)
        
        if token in delimiters:
            self.current_tokens.append(token)
            return (5, token, delimiters[token], None)
        
        if token in relational_operators:
            self.current_tokens.append(token)
            self.last_operator = token
            return (8, token, relational_operators[token], None)
        
        if token in operators:
            self.current_tokens.append(token)
            return (7, token, operators[token], None)
        
        if self.is_constant(token):
            clean_token = token
            if token.startswith("'") and token.endswith("'"):
                clean_token = token[1:-1]
                
            if clean_token not in self.constants:
                self.constants[clean_token] = (self.constant_counter, [self.line_number])
                self.constant_counter += 1
            else:
                if self.line_number not in self.constants[clean_token][1]:
                    self.constants[clean_token] = (self.constants[clean_token][0], self.constants[clean_token][1] + [self.line_number])
            
            self.current_tokens.append(token)
            self.last_operator = None
            return (6, token, self.constants[clean_token][0], self.constants[clean_token][1])
        
        if self.is_identifier(token):
            if token not in self.identifiers:
                self.identifiers[token] = (self.identifier_counter, [self.line_number])
                self.identifier_counter += 1
            else:
                if self.line_number not in self.identifiers[token][1]:
                    self.identifiers[token] = (self.identifiers[token][0], self.identifiers[token][1] + [self.line_number])
            
            self.current_tokens.append(token)
            return (4, token, self.identifiers[token][0], self.identifiers[token][1])
        
        return None
    
    def analyze_tokens(self, words):
        for word in words:
            token_info = self.analyze_module(word)
            if token_info:
                self.tokens.append((self.line_number, token_info))
                
                if token_info[0] == 8:
                    self.last_operator = word

def format_tokens(tokens):
    result = []
    for token in tokens:
        if len(token) < 2 or not isinstance(token[1], tuple) or len(token[1]) < 4:
            continue
            
        line_number = token[0]
        token_value = token[1][1]
        token_type = token[1][0]
        token_code = token[1][2]
        
        token_type_text = ""
        if token_type == 1:
            token_type_text = "Palabra Reservada"
        elif token_type == 4:
            token_type_text = "Identificador"
        elif token_type == 5:
            token_type_text = "Delimitador"
        elif token_type == 6:
            token_type_text = "Constante"
        elif token_type == 7:
            token_type_text = "Operador"
        elif token_type == 8:
            token_type_text = "Operador Relacional"
        elif token_type == "EOF":
            token_type_text = "Fin de Entrada"
        else:
            token_type_text = str(token_type)
        
        result.append({
            "Línea": line_number,
            "Token": token_value,
            "Tipo": token_type_text,
            "Código": token_code
        })
    
    return result