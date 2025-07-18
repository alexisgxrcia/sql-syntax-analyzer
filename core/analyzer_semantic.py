import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

class DDLSemanticAnalyzer:
    def __init__(self):
        self.tables = []
        self.current_table = None
        self.current_attribute = None
        self.in_constraint = False
        self.constraint_type = None
        self.constraint_name = None
        self.references_table = None
        self.references_column = None
        
    def analyze_ddl(self, tokens):
        self.tables = []
        self.current_table = None
        self.current_attribute = None
        self.in_constraint = False
        self.constraint_type = None
        self.constraint_name = None
        self.references_table = None
        self.references_column = None
        
        i = 0
        while i < len(tokens):
            line_num, (type_code, token, code, _) = tokens[i]
            
            if type_code == 1 and token == "CREATE":
                i = self._process_create_statement(tokens, i)
            else:
                i += 1
                
        return self.tables
    
    def _process_create_statement(self, tokens, start_idx):
        i = start_idx
        
        i += 1
        
        if i < len(tokens) and tokens[i][1][1] == "TABLE":
            i += 1
            
            if i < len(tokens) and tokens[i][1][0] == 4:
                table_name = tokens[i][1][1]
                self.current_table = {
                    'name': table_name,
                    'attributes': [],
                    'constraints': []
                }
                self.tables.append(self.current_table)
                i += 1
                
                if i < len(tokens) and tokens[i][1][1] == "(":
                    i += 1
                    
                    i = self._process_table_definition(tokens, i)
                    
        return i
    
    def _process_table_definition(self, tokens, start_idx):
        i = start_idx
        
        while i < len(tokens):
            line_num, (type_code, token, code, _) = tokens[i]
            
            if token == ")":
                return i + 1
            
            if type_code == 1 and token == "CONSTRAINT":
                i = self._process_constraint(tokens, i)
                continue
            
            if type_code == 1 and (token == "PRIMARY" or token == "FOREIGN"):
                i = self._process_key_constraint(tokens, i)
                continue
            
            if type_code == 4:
                i = self._process_attribute(tokens, i)
                continue
                
            i += 1
            
        return i
    
    def _process_attribute(self, tokens, start_idx):
        i = start_idx
        
        attr_name = tokens[i][1][1]
        i += 1
        
        attribute = {
            'name': attr_name,
            'type': None,
            'size': None,
            'not_null': False
        }
        
        if i < len(tokens) and tokens[i][1][0] == 1:
            attribute['type'] = tokens[i][1][1]
            i += 1
            
            if i < len(tokens) and tokens[i][1][1] == "(":
                i += 1
                if i < len(tokens) and (tokens[i][1][0] == 6 or tokens[i][1][0] == 4):
                    attribute['size'] = tokens[i][1][1]
                    i += 1
                    
                    if i < len(tokens) and tokens[i][1][1] == ")":
                        i += 1
            
            if i < len(tokens) and tokens[i][1][0] == 1 and tokens[i][1][1] == "NOT":
                i += 1
                if i < len(tokens) and tokens[i][1][0] == 1 and tokens[i][1][1] == "NULL":
                    attribute['not_null'] = True
                    i += 1
        
        if self.current_table:
            self.current_table['attributes'].append(attribute)
            
        if i < len(tokens) and tokens[i][1][1] == ",":
            i += 1
            
        return i
    
    def _process_constraint(self, tokens, start_idx):
        i = start_idx
        
        i += 1
        
        constraint_name = None
        if i < len(tokens) and tokens[i][1][0] == 4:
            constraint_name = tokens[i][1][1]
            i += 1
        
        if i < len(tokens) and tokens[i][1][0] == 1:
            constraint_type = tokens[i][1][1]
            
            if constraint_type == "PRIMARY" and i+1 < len(tokens) and tokens[i+1][1][1] == "KEY":
                i = self._process_primary_key(tokens, i, constraint_name)
            elif constraint_type == "FOREIGN" and i+1 < len(tokens) and tokens[i+1][1][1] == "KEY":
                i = self._process_foreign_key(tokens, i, constraint_name)
            else:
                i += 1
        else:
            i += 1
            
        if i < len(tokens) and tokens[i][1][1] == ",":
            i += 1
            
        return i
    
    def _process_key_constraint(self, tokens, start_idx):
        i = start_idx
        constraint_type = tokens[i][1][1]
        
        if constraint_type == "PRIMARY" and i+1 < len(tokens) and tokens[i+1][1][1] == "KEY":
            i = self._process_primary_key(tokens, i, None)
        elif constraint_type == "FOREIGN" and i+1 < len(tokens) and tokens[i+1][1][1] == "KEY":
            i = self._process_foreign_key(tokens, i, None)
        else:
            i += 1
            
        if i < len(tokens) and tokens[i][1][1] == ",":
            i += 1
            
        return i
    
    def _process_primary_key(self, tokens, start_idx, constraint_name):
        i = start_idx
        
        i += 1
        
        i += 1
        
        constraint = {
            'name': constraint_name,
            'type': 'PRIMARY KEY',
            'columns': []
        }
        
        if i < len(tokens) and tokens[i][1][1] == "(":
            i += 1
            
            while i < len(tokens) and tokens[i][1][1] != ")":
                if tokens[i][1][0] == 4:
                    constraint['columns'].append(tokens[i][1][1])
                    
                i += 1
                
                if i < len(tokens) and tokens[i][1][1] == ",":
                    i += 1
            
            if i < len(tokens) and tokens[i][1][1] == ")":
                i += 1
        
        if self.current_table:
            self.current_table['constraints'].append(constraint)
            
        return i
    
    def _process_foreign_key(self, tokens, start_idx, constraint_name):
        i = start_idx
        
        i += 1
        
        i += 1
        
        constraint = {
            'name': constraint_name,
            'type': 'FOREIGN KEY',
            'columns': [],
            'references_table': None,
            'references_columns': []
        }
        
        if i < len(tokens) and tokens[i][1][1] == "(":
            i += 1
            
            while i < len(tokens) and tokens[i][1][1] != ")":
                if tokens[i][1][0] == 4:
                    constraint['columns'].append(tokens[i][1][1])
                    
                i += 1
                
                if i < len(tokens) and tokens[i][1][1] == ",":
                    i += 1
            
            if i < len(tokens) and tokens[i][1][1] == ")":
                i += 1
        
        if i < len(tokens) and tokens[i][1][0] == 1 and tokens[i][1][1] == "REFERENCES":
            i += 1
            
            if i < len(tokens) and tokens[i][1][0] == 4:
                constraint['references_table'] = tokens[i][1][1]
                i += 1
                
                if i < len(tokens) and tokens[i][1][1] == "(":
                    i += 1
                    
                    while i < len(tokens) and tokens[i][1][1] != ")":
                        if tokens[i][1][0] == 4:
                            constraint['references_columns'].append(tokens[i][1][1])
                            
                        i += 1
                        
                        if i < len(tokens) and tokens[i][1][1] == ",":
                            i += 1
                    
                    if i < len(tokens) and tokens[i][1][1] == ")":
                        i += 1
        
        if self.current_table:
            self.current_table['constraints'].append(constraint)
            
        return i