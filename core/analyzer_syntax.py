from core.scanner_dml import DMLScanner;
from core.syntax_errors import SyntaxErrorHandler;
from core.analyzer_semantic import DDLSemanticAnalyzer;
from core.db_connector import DBConnector;

class SyntaxAnalyzer:
    def __init__(self):
        self.error_handler = SyntaxErrorHandler()

        self.syntax_table = {
            200: {16: [16,17,4,52,202,53,55,201]},
            201: {16: [200], 27: [211], 10: [300], 199: [99]},
            202: {4: [4,203,216,204,217,205]},
            203: {18: [18], 19: [19], 4: [4]},
            204: {20: [20, 21], 50: [99], 24: [99], 53: [99]},
            205: {50: [50, 206], 53: [99]},
            206: {4: [202], 22: [207]},
            207: {22: [22,4,208,52,218,53,209]},
            208: {24: [24, 23], 25: [25, 23]},
            209: {26: [26,4,52,4,53,210], 50: [50, 207], 53: [99]},
            210: {50: [50, 207], 53: [99]},
            211: {27: [27,28,4,29,52,212,53,55,215]},
            212: {54: [213,214], 61: [213, 214], 62: [213, 214]},
            213: {54: [54,62,54], 61: [61], 62: [62]},
            214: {50: [50, 212], 53: [99]},
            215: {27: [211], 16: [200], 10: [300], 199: [99]},
            216: {52: [52,61,53], 24: [99], 50: [99], 53: [99]},
            217: {24: [24, 23], 50: [99], 53: [99]},
            218: {4: [4,219]},
            219: {50: [50,4,219], 53: [99]},
            300: {10: [10, 320, 301, 11, 306, 310, 55, 201]},
            320: {30: [30], 4: [99], 72: [99]},
            301: {4: [302], 72: [72, 303]},
            302: {4: [304, 303]},
            303: {11: [99], 12: [99], 50: [50, 302], 53: [99], 199: [99]},
            304: {4: [4, 305]},
            305: {8: [99], 11: [99], 12: [99], 13: [99], 14: [99], 15: [99],
                 50: [99], 51: [51, 4], 53: [99], 54: [99],
                 81: [99], 82: [99], 83: [99], 84: [99], 85: [99], 86: [99], 199: [99]},
            306: {4: [308, 307]},
            307: {12: [99], 50: [50, 306], 53: [99], 199: [99]},
            308: {4: [4, 309]},
            309: {4: [4], 12: [99], 50: [99], 53: [99], 199: [99]},
            310: {12: [12, 311], 53: [99], 199: [99]},
            311: {4: [313, 312], 61: [319, 312], 62: [318, 312], 14: [14, 311], 15: [15, 311]},
            312: {14: [317, 311], 15: [317, 311], 53: [99], 199: [99], 4: [99]},
            313: {4: [304, 314]},
            314: {13: [13, 52, 300, 53],
                  81: [315, 316],
                  82: [315, 316],
                  83: [315, 316],
                  84: [315, 316],
                  85: [315, 316],
                  86: [315, 316],
                  53: [99],
                  14: [99],
                  15: [99]
                 },
            315: {81: [81], 82: [82], 83: [83], 84: [84], 85: [85], 86: [86]},
            316: {4: [304], 54: [54, 318, 54], 61: [319], 62: [318], 6: [319], 53: [99], 14: [99], 15: [99]},
            317: {14: [14], 15: [15]},
            318: {61: [319], 62: [62], 53: [99], 14: [99], 15: [99]},
            319: {61: [61], 53: [99], 14: [99], 15: [99]}
        }

        self.scanner = DMLScanner()
        self.semantic_analyzer = DDLSemanticAnalyzer()

        self.stack = []
        self.errors = []
        self.tokens = []
        self.current_token_index = 0

        self.current_context = None
        self.analysis_path = []
        self.prev_token = None
        self.prev_token_type = None
        self.last_id_token = None

        self.tables_info = []

        self.db_connector = DBConnector()

        self.update_semantic_tables()

    def reset(self):
        self.stack = []
        self.errors = []
        self.tokens = []
        self.current_token_index = 0
        self.current_context = None
        self.analysis_path = []
        self.prev_token = None
        self.prev_token_type = None
        self.last_id_token = None

    def update_context(self, X, K=None):
        self.analysis_path.append((X, K))

        if self.error_handler.is_terminal(X) and X != 99 and X != 199:
            self.prev_token = X
            self.prev_token_type = X

            if X == 4:
                self.last_id_token = self.current_token_index

            if X == 13:
                self.current_context = 'IN_SUBQUERY'
            elif X == 52:
                if self.current_context == 'IN_SUBQUERY':
                    pass
                elif self.prev_token_type == 4 and self.current_context != 'IN_SUBQUERY':
                    self.current_context = 'MISSING_IN'
            elif X == 53:
                if self.current_context == 'IN_SUBQUERY':
                    self.current_context = 'WHERE_CONDITION'
            elif X == 14 or X == 15:
                if self.current_context == 'IN_SUBQUERY':
                    self.current_context = 'WHERE_CONDITION'

        if X == 16:
            self.current_context = 'CREATE_TABLE'
        elif X == 17:
            self.current_context = 'CREATE_TABLE'
        elif X == 200 or X == 202:
            self.current_context = 'CREATE_TABLE'
        elif X == 203:
            self.current_context = 'DATA_TYPE'
        elif X == 204:
            self.current_context = 'COLUMN_NULL'
        elif X == 207 or X == 208:
            self.current_context = 'CONSTRAINT'

        elif X == 27:
            self.current_context = 'INSERT_INTO'
        elif X == 28:
            self.current_context = 'INSERT_INTO'
        elif X == 211:
            self.current_context = 'INSERT_INTO'
        elif X == 212 or X == 213:
            self.current_context = 'INSERT_VALUES'

        elif X == self.error_handler.select_code or X == 10:
            self.current_context = 'SELECT_LIST'
        elif X == 301 or X == 302:
            self.current_context = 'SELECT_LIST'
        elif X == self.error_handler.from_code or X == 11:
            self.current_context = 'FROM'
        elif X == 306 or X == 308:
            self.current_context = 'TABLE_LIST'
        elif X == 310 and K == self.error_handler.where_code:
            self.current_context = 'WHERE_CONDITION'
        elif X == self.error_handler.where_code or X == 12:
            self.current_context = 'WHERE_CONDITION'
        elif X == 312 and (K == self.error_handler.and_code or K == self.error_handler.or_code):
            self.current_context = 'WHERE_CONDITION'
        elif X == 314 or X == 315:
            self.current_context = 'COMPARISON'
        elif X == 304 and self.current_context == 'WHERE_CONDITION':
            self.current_context = 'COMPARISON_LEFT'
        elif X in self.error_handler.operadores_relacionales:
            self.last_id_token = None

    def parse(self, sql_query):

        forbidden_error = self.error_handler.check_forbidden_characters(sql_query)
        if forbidden_error:
            return {
                "status": "error",
                "message": "Se encontraron caracteres no permitidos",
                "errors": [forbidden_error],
                "steps": []
            }

        scan_result = self.scanner.analyze_sql(sql_query)
        tokens = scan_result['tokens']

        if not tokens:
            return {"status": "error", "message": "No hay tokens para analizar", "errors": [], "steps": []}

        current_statement_tokens = []
        statement_count = 0
        results = []

        i = 0
        while i < len(tokens):
            token_info = tokens[i]
            token_type = self.error_handler.get_token_type(token_info)
            token_value = token_info[1][1].upper() if token_info[1][1] else ""

            is_new_statement = False

            if token_type == 55 and current_statement_tokens:
                current_statement_tokens.append(token_info)
                statement_count += 1

                first_token = current_statement_tokens[0]
                first_token_value = first_token[1][1].upper()

                statement_type = "SELECT"
                if first_token_value == "CREATE":
                    statement_type = "CREATE"
                elif first_token_value == "INSERT":
                    statement_type = "INSERT"

                result = self._parse_statement(current_statement_tokens, statement_type)
                result['statement_number'] = statement_count
                results.append(result)

                if result['status'] == 'success':
                    semantic_result = None

                    attribute_validation = self.error_handler.validate_attribute_names(current_statement_tokens)
                    if attribute_validation:
                        semantic_result = attribute_validation

                    elif statement_type == "CREATE":
                        constraint_validation = self.error_handler.validate_create_table_constraints(current_statement_tokens)
                        if constraint_validation:
                            semantic_result = constraint_validation
                        else:
                            table_analysis_result = self._analyze_create_table(current_statement_tokens)
                            if table_analysis_result:
                                semantic_result = table_analysis_result
                    elif statement_type == "SELECT":
                        if self.tables_info:
                            validations = [
                                lambda: self.error_handler.validate_where_conditions(current_statement_tokens, self.tables_info),
                                lambda: self.error_handler.validate_type_conversions(current_statement_tokens, self.tables_info),
                                lambda: self.error_handler.validate_select_tables(current_statement_tokens, self.tables_info),
                                lambda: self.error_handler.validate_select_columns(current_statement_tokens, self.tables_info)
                            ]

                            for validate_fn in validations:
                                validation_result = validate_fn()
                                if validation_result:
                                    semantic_result = validation_result
                                    break

                    if semantic_result:
                        semantic_result['steps'] = result['steps']
                        semantic_result['statement_number'] = statement_count
                        semantic_result['statement_tokens'] = current_statement_tokens
                        results[-1] = semantic_result

                        error_msgs = [f"Sentencia {statement_count}: {error}" for error in semantic_result['errors']]
                        return {
                            "status": "error",
                            "message": "Se encontró un error semántico",
                            "errors": error_msgs,
                            "results": results
                        }

                elif result['status'] == 'error':
                    error_msgs = [f"Sentencia {statement_count}: {error}" for error in result['errors']]
                    return {
                        "status": "error",
                        "message": "Se encontró un error sintáctico",
                        "errors": error_msgs,
                        "results": results
                    }

                current_statement_tokens = []
                is_new_statement = True

            if not is_new_statement:
                current_statement_tokens.append(token_info)

            i += 1

        if current_statement_tokens:
            statement_count += 1

            first_token = current_statement_tokens[0]
            first_token_value = first_token[1][1].upper()

            statement_type = "SELECT"
            if first_token_value == "CREATE":
                statement_type = "CREATE"
            elif first_token_value == "INSERT":
                statement_type = "INSERT"

            result = self._parse_statement(current_statement_tokens, statement_type)
            result['statement_number'] = statement_count
            results.append(result)

            if result['status'] == 'success':
                semantic_result = None

                attribute_validation = self.error_handler.validate_attribute_names(current_statement_tokens)
                if attribute_validation:
                    semantic_result = attribute_validation

                elif statement_type == "CREATE":
                    constraint_validation = self.error_handler.validate_create_table_constraints(current_statement_tokens)
                    if constraint_validation:
                        semantic_result = constraint_validation
                    else:
                        table_analysis_result = self._analyze_create_table(current_statement_tokens)
                        if table_analysis_result:
                            semantic_result = table_analysis_result
                elif statement_type == "SELECT":
                    if self.tables_info:
                        validations = [
                            lambda: self.error_handler.validate_where_conditions(current_statement_tokens, self.tables_info),
                            lambda: self.error_handler.validate_type_conversions(current_statement_tokens, self.tables_info),
                            lambda: self.error_handler.validate_select_tables(current_statement_tokens, self.tables_info),
                            lambda: self.error_handler.validate_select_columns(current_statement_tokens, self.tables_info)
                        ]

                        for validate_fn in validations:
                            validation_result = validate_fn()
                            if validation_result:
                                semantic_result = validation_result
                                break

                if semantic_result:
                    semantic_result['steps'] = result['steps']
                    semantic_result['statement_number'] = statement_count
                    semantic_result['statement_tokens'] = current_statement_tokens
                    results[-1] = semantic_result

                    error_msgs = [f"Sentencia {statement_count}: {error}" for error in semantic_result['errors']]
                    return {
                        "status": "error",
                        "message": "Se encontró un error semántico",
                        "errors": error_msgs,
                        "results": results
                    }

            elif result['status'] == 'error':
                error_msgs = [f"Sentencia {statement_count}: {error}" for error in result['errors']]
                return {
                    "status": "error",
                    "message": "Se encontró un error sintáctico",
                    "errors": error_msgs,
                    "results": results
                }

        return {
            'status': 'success',
            'message': 'Análisis de SQL completado exitosamente',
            'errors': [],
            'results': results
        }

    def _parse_statement(self, tokens, statement_type):
        self.reset()
        self.tokens = tokens

        if not tokens:
            return {"status": "error", "message": "No hay tokens para analizar", "errors": [], "steps": []}

        error_msg = self.error_handler.check_malformed_strings(tokens)
        if error_msg:
            return {"status": "error", "message": "Se encontraron errores sintácticos",
                    "errors": [error_msg], "steps": []}

        error_msg = self.error_handler.check_consecutive_constants(tokens, self.error_handler.get_token_type)
        if error_msg:
            return {"status": "error", "message": "Se encontraron errores sintácticos",
                    "errors": [error_msg], "steps": []}

        if statement_type == "INSERT":
            error_msg = self.error_handler.check_insert_into_sequence(tokens)
            if error_msg:
                return {"status": "error", "message": "Se encontraron errores sintácticos",
                        "errors": [error_msg], "steps": []}

        self.stack = [199]

        if statement_type == "CREATE":
            self.stack.append(201)
        elif statement_type == "INSERT":
            self.stack.append(211)
        else:
            self.stack.append(300)

        self.current_token_index = 0
        steps = []
        error = False
        subquery_level = 0
        in_subquery_stack = []
        parenthesis_stack = []

        has_artificial_eof = False
        if self.current_token_index >= len(self.tokens) or self.error_handler.get_token_type(self.tokens[-1]) != 199:
            eof_token = (tokens[-1][0] if tokens else 1, ("EOF", "$", 199, None))
            self.tokens.append(eof_token)
            has_artificial_eof = True

        while self.stack and self.current_token_index < len(self.tokens) and not error:
            X = self.stack.pop()

            token_info = self.tokens[self.current_token_index]
            line = token_info[0]
            K = self.error_handler.get_token_type(token_info)

            if X == 199 and K == 53 and len(parenthesis_stack) > 0:
                self.stack.append(X)
                X = 53

            if (K == 14 or K == 15) and self.current_context == 'WHERE_CONDITION' and subquery_level == 0:
                if X != K and X != 317 and X != 312 and X != 311:
                    self.stack.append(X)
                    X = 311

            if K == 53 and self.current_context == 'IN_SUBQUERY' and X != 53:
                self.stack.append(X)
                self.stack.append(53)
                X = 53

            if statement_type == "SELECT" and X == 199 and K == 55:
                if self.current_token_index == len(self.tokens) - (2 if has_artificial_eof else 1):
                    self.current_token_index += 1
                    self.stack.append(X)
                    continue

            if self.current_token_index == len(self.tokens) - 1 and K == 199:
                if not self.error_handler.is_terminal(X) and X != 199:
                    if X in self.syntax_table and 199 in self.syntax_table[X]:
                        production = self.syntax_table[X][199]
                        for symbol in reversed(production):
                            if symbol != 99:
                                self.stack.append(symbol)
                        continue

            self.update_context(X, K)

            step_info = {
                "X": X,
                "K": K,
                "stack": self.stack.copy(),
                "X_name": self.error_handler.get_symbol_name(X),
                "K_name": self.error_handler.get_symbol_name(K),
                "context": self.current_context
            }

            if self.error_handler.is_terminal(X):
                if X == K:
                    step_info["action"] = f"Emparejado: {self.error_handler.get_symbol_name(X)}"

                    if X == 13:
                        in_subquery_stack.append(True)

                    if X == 52:
                        parenthesis_stack.append(52)
                        if self.current_context == 'IN_SUBQUERY':
                            subquery_level += 1

                    if X == 53 and parenthesis_stack:
                        parenthesis_stack.pop()
                        if subquery_level > 0:
                            subquery_level -= 1
                            if subquery_level == 0 and in_subquery_stack:
                                in_subquery_stack.pop()
                                self.current_context = 'WHERE_CONDITION'

                    if X != 199:
                        self.current_token_index += 1
                elif X == 99:
                    step_info["action"] = "Epsilon: No acción"
                    continue
                else:
                    if X == 55 and K == 53 and (self.current_context == 'IN_SUBQUERY' or subquery_level > 0 or parenthesis_stack):
                        self.stack.append(X)
                        X = 53
                        step_info["X"] = X
                        step_info["X_name"] = self.error_handler.get_symbol_name(X)
                        step_info["action"] = f"Emparejado: {self.error_handler.get_symbol_name(X)}"
                        self.current_token_index += 1

                        if parenthesis_stack:
                            parenthesis_stack.pop()

                        if subquery_level > 0:
                            subquery_level -= 1

                        if subquery_level == 0 and in_subquery_stack:
                            in_subquery_stack.pop()
                            self.current_context = 'WHERE_CONDITION'

                        steps.append(step_info)
                        continue
                    elif X == 53 and K == 199 and len(parenthesis_stack) == 0:
                        self.stack.append(199)
                        continue
                    else:
                        error = True
                        error_message = self.error_handler.classify_terminal_error(
                            X, K, line, self.tokens, self.current_token_index,
                            self.prev_token_type, self.current_context,
                            self.last_id_token, self.prev_token
                        )

                        step_info["action"] = f"ERROR: {error_message}"
                        self.errors.append(error_message)

            else:
                if X in self.syntax_table and K in self.syntax_table[X]:
                    production = self.syntax_table[X][K]
                    step_info["action"] = f"Producción: {self.error_handler.get_symbol_name(X)} -> {self.error_handler.array_to_string(production)}"

                    for symbol in reversed(production):
                        if symbol != 99:
                            self.stack.append(symbol)
                else:
                    epsilon_found = False

                    for possible_K in [99, 199]:
                        if X in self.syntax_table and possible_K in self.syntax_table[X]:
                            production = self.syntax_table[X][possible_K]
                            step_info["action"] = f"Producción (epsilon): {self.error_handler.get_symbol_name(X)} -> {self.error_handler.array_to_string(production)}"

                            for symbol in reversed(production):
                                if symbol != 99:
                                    self.stack.append(symbol)

                            epsilon_found = True
                            break

                    if not epsilon_found:
                        error = True
                        error_message = self.error_handler.classify_nonterminal_error(
                            X, K, line, self.tokens, self.current_token_index,
                            self.prev_token_type, self.current_context,
                            self.last_id_token, self.prev_token
                        )
                        step_info["action"] = f"ERROR: {error_message}"
                        self.errors.append(error_message)

            steps.append(step_info)

            if X == 199 and K == 199:
                break

        if self.stack and self.stack != [199] and not error:
            if statement_type == "SELECT":
                special_stack_patterns = [
                    [199],
                    [199, 201],
                    [199, 312],
                    [199, 201, 55],
                    [199, 201, 55, 312]
                ]

                stack_without_redundant = self._simplify_stack(self.stack)
                stack_valid = False

                for pattern in special_stack_patterns:
                    if self._match_stack_pattern(stack_without_redundant, pattern):
                        stack_valid = True
                        break

                if stack_valid:
                    self.stack = []

            if len(self.stack) == 1 and self.stack[0] == 199:
                self.stack = []
            elif has_artificial_eof and self.current_token_index == len(self.tokens) - 1:
                has_all_epsilon = True
                for symbol in self.stack:
                    if symbol != 199 and (symbol not in self.syntax_table or 199 not in self.syntax_table[symbol]):
                        has_all_epsilon = False
                        break

                if has_all_epsilon:
                    self.stack = []
                else:
                    error_code = 204

                    incomplete_msg = f"Sentencia {statement_type} incompleta."

                    if statement_type == "SELECT":
                        if self.prev_token == self.error_handler.where_code or self.current_context == 'WHERE_CONDITION':
                            error_code = 204
                        elif self.prev_token == self.error_handler.select_code or self.current_context == 'SELECT_LIST':
                            error_code = 204

                    error_msg = self.error_handler.format_error_message(error_code, self.tokens[-1][0], incomplete_msg)
                    self.errors.append(error_msg)
                    error = True
            else:
                expected_symbol = None
                for s in self.stack:
                    if s != 199:
                        expected_symbol = s
                        break

                if expected_symbol:
                    error_code = self.error_handler.get_error_code_by_context(
                        expected_symbol, current_context=self.current_context,
                        prev_token_type=self.prev_token_type, prev_token=self.prev_token,
                        last_id_token=self.last_id_token, tokens=self.tokens,
                        current_token_index=self.current_token_index
                    )
                    error_msg = self.error_handler.format_error_message(error_code, self.tokens[-1][0])
                else:
                    error_msg = self.error_handler.format_error_message(201, self.tokens[-1][0])

                self.errors.append(error_msg)
                error = True

        if self.current_token_index < len(self.tokens) - (1 if has_artificial_eof else 0) and not error:
            token_linea = self.tokens[self.current_token_index][0]

            if statement_type == "SELECT":
                token_type = self.error_handler.get_token_type(self.tokens[self.current_token_index])
                if token_type in [61, 62] and self.prev_token_type == 4:
                    error_msg = self.error_handler.format_error_message(208, token_linea)
                    self.errors.append(error_msg)
                    error = True
                    return self._format_result(statement_type, error, steps)

            error_msg = self.error_handler.format_error_message(201, token_linea)
            self.errors.append(error_msg)
            error = True

        elif statement_type == "SELECT" and not error and has_artificial_eof:
            last_real_token_index = len(self.tokens) - 2
            if last_real_token_index >= 0:
                last_token_type = self.error_handler.get_token_type(self.tokens[last_real_token_index])
                if last_token_type != 55:
                    token_linea = self.tokens[last_real_token_index][0]
                    error_msg = self.error_handler.format_error_message(205, token_linea)
                    self.errors.append(error_msg)
                    error = True

        return self._format_result(statement_type, error, steps)

    def _simplify_stack(self, stack):
        if not stack:
            return stack

        simplified = stack.copy()

        i = 0
        while i < len(simplified) - 3:
            if (simplified[i:i+4] == [53, 201, 55, 312] or
                simplified[i:i+3] == [53, 201, 55] or
                simplified[i:i+2] == [53, 201]):
                simplified = simplified[:i] + simplified[i+4:]
                i = 0
            else:
                i += 1

        return simplified

    def _match_stack_pattern(self, stack, pattern):
        if len(stack) < len(pattern):
            return False

        for i, symbol in enumerate(pattern):
            if i >= len(stack) or stack[i] != symbol:
                return False

        return True

    def _format_result(self, statement_type, error, steps):
        if not error:
            return {
                "status": "success",
                "message": f"Análisis sintáctico de {statement_type} completado con éxito",
                "errors": [],
                "steps": steps
            }
        else:
            return {
                "status": "error",
                "message": f"Se encontraron errores sintácticos en {statement_type}",
                "errors": self.errors,
                "steps": steps
            }

    def update_semantic_tables(self):
        try:
            db_tables_info = self.db_connector.get_db_metadata()

            if not db_tables_info:
                return {
                    "status": "error",
                    "message": "No se pudo obtener información de la base de datos",
                    "errors": [self.db_connector.error if hasattr(self.db_connector, 'error') else "Error desconocido"]
                }

            for db_table in db_tables_info:
                exists = False
                for i, existing_table in enumerate(self.tables_info):
                    if existing_table['name'].upper() == db_table['name'].upper():
                        self.tables_info[i] = db_table
                        exists = True
                        break

                if not exists:
                    self.tables_info.append(db_table)

            return {
                "status": "success",
                "message": f"Tablas semánticas actualizadas exitosamente. {len(db_tables_info)} tablas cargadas.",
                "tables": [table['name'] for table in self.tables_info]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": "Error al actualizar tablas semánticas",
                "errors": [str(e)]
            }

    def execute_sql_query(self, sql_query):
        parse_result = self.parse(sql_query)

        if parse_result.get("status") == "error":
            return parse_result

        statement_type = None
        for result in parse_result.get("results", []):
            statement_tokens = result.get("statement_tokens", [])
            if statement_tokens:
                statement_type = statement_tokens[0][1][1].upper()
                break

        execution_result = self.db_connector.execute_query(sql_query)

        if execution_result["status"] == "success":
            parse_result["execution"] = {
                "status": "success",
                "message": execution_result["message"],
                "data": execution_result.get("data"),
                "column_names": execution_result.get("column_names"),
                "rows_affected": execution_result.get("rows_affected")
            }

            if statement_type in ["CREATE", "INSERT"]:
                if statement_type == "INSERT":
                    self.update_semantic_tables()
                elif statement_type == "CREATE" and not any(table['name'].upper() == sql_query.split()[2].upper() for table in self.tables_info):
                    self.update_semantic_tables()
        else:
            parse_result["execution"] = {
                "status": "error",
                "message": execution_result["message"]
            }

        return parse_result

    def _find_attribute_line(self, tokens, attr_name):
        for token_info in tokens:
            line_num, (type_code, token, code, _) = token_info

            if type_code == 4 and token.upper() == attr_name.upper():
                return line_num

        return 1

    def _analyze_create_table(self, tokens):
        tables = self.semantic_analyzer.analyze_ddl(tokens)

        for table in tables:
            attr_names = []
            for attr in table['attributes']:
                if attr['name'] in attr_names:
                    line_num = self._find_attribute_line(tokens, attr['name'])
                    error_msg = self.error_handler.format_error_message(
                        317, line_num,
                        f"El atributo '{attr['name']}' está duplicado en la tabla '{table['name']}'."
                    )
                    return {
                        "status": "error",
                        "message": "Se encontraron errores semánticos en CREATE TABLE",
                        "errors": [error_msg],
                        "steps": []
                    }
                attr_names.append(attr['name'])

            exists = False
            for existing_table in self.tables_info:
                if existing_table['name'].upper() == table['name'].upper():
                    existing_table.update(table)
                    exists = True
                    break

            if not exists:
                self.tables_info.append(table)

        return None
