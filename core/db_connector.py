import mysql.connector
import os

DB_CONFIG = {
    #"db_name": "b9ypce7rqqi8mykx8czk",
    #"host": "b9ypce7rqqi8mykx8czk-mysql.services.clever-cloud.com",
    #"port": 3306,
    #"user": "uhvtvrr8d9tobfkz",
    #"password": "VCW3xvGipBSlYFmTLfxA"
    "db_name": "inscritos",
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": ""
}

class DBConnector:    
    def __init__(self, config=None):
        self.config = config or DB_CONFIG
        self.connection = None
        self.cursor = None
        self.error = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.config["host"],
                port=self.config["port"],
                user=self.config["user"],
                password=self.config["password"],
                database=self.config["db_name"]
            )
            self.cursor = self.connection.cursor()
            return True
        except Exception as e:
            self.error = f"Error al conectar a la base de datos MySQL: {str(e)}"
            return False
    
    def disconnect(self):
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                self.cursor = None
                return True
            except Exception as e:
                self.error = f"Error al cerrar la conexión: {str(e)}"
                return False
        return True
    
    def execute_query(self, query):
        result = {
            "status": "error",
            "message": "",
            "data": None,
            "rows_affected": 0,
            "column_names": []
        }
        
        if not self.connection:
            if not self.connect():
                result["message"] = self.error
                return result
        
        try:
            self.cursor.execute(query)
            
            if query.strip().upper().startswith("SELECT"):
                rows = self.cursor.fetchall()
                column_names = [column[0] for column in self.cursor.description]
                
                result["status"] = "success"
                result["message"] = f"Consulta ejecutada con éxito. {len(rows)} filas recuperadas."
                result["data"] = rows
                result["column_names"] = column_names
            
            else:
                self.connection.commit()
                rows_affected = self.cursor.rowcount
                
                result["status"] = "success"
                result["message"] = f"Consulta ejecutada con éxito. {rows_affected} filas afectadas."
                result["rows_affected"] = rows_affected
            
            return result
            
        except Exception as e:
            result["message"] = f"Error al ejecutar la consulta: {str(e)}"
            return result
    
    def get_db_metadata(self):
        tables_info = []
        
        if not self.connection:
            if not self.connect():
                return tables_info
        
        try:
            self.cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s
            """, (self.config["db_name"],))
            
            tables = self.cursor.fetchall()
            
            for table_row in tables:
                table_name = table_row[0]
                table_info = {
                    'name': table_name,
                    'attributes': [],
                    'constraints': []
                }
                
                self.cursor.execute("""
                    SELECT column_name, data_type, character_maximum_length, 
                           numeric_precision, is_nullable, column_key
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position
                """, (self.config["db_name"], table_name))
                
                columns = self.cursor.fetchall()
                
                for column in columns:
                    column_name, data_type, char_max_length, num_precision, is_nullable, column_key = column
                    
                    size = None
                    if char_max_length is not None:
                        size = char_max_length
                    elif num_precision is not None:
                        size = num_precision
                    
                    column_info = {
                        'name': column_name,
                        'type': data_type.upper(),
                        'size': size,
                        'not_null': is_nullable == 'NO'
                    }
                    
                    table_info['attributes'].append(column_info)
                
                self.cursor.execute("""
                    SELECT kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                      ON tc.constraint_name = kcu.constraint_name
                     AND tc.table_schema = kcu.table_schema
                     AND tc.table_name = kcu.table_name
                    WHERE tc.constraint_type = 'PRIMARY KEY'
                      AND tc.table_schema = %s
                      AND tc.table_name = %s
                """, (self.config["db_name"], table_name))
                
                primary_keys = [row[0] for row in self.cursor.fetchall()]
                
                if primary_keys:
                    constraint = {
                        'name': f'PK_{table_name}',
                        'type': 'PRIMARY KEY',
                        'columns': primary_keys
                    }
                    table_info['constraints'].append(constraint)
                
                self.cursor.execute("""
                    SELECT kcu.constraint_name,
                           kcu.column_name,
                           kcu.referenced_table_name,
                           kcu.referenced_column_name
                    FROM information_schema.key_column_usage kcu
                    JOIN information_schema.table_constraints tc
                      ON tc.constraint_name = kcu.constraint_name
                     AND tc.table_schema = kcu.table_schema
                     AND tc.table_name = kcu.table_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                      AND tc.table_schema = %s
                      AND tc.table_name = %s
                """, (self.config["db_name"], table_name))
                
                fk_results = self.cursor.fetchall()
                
                fk_groups = {}
                for fk in fk_results:
                    constraint_name, column_name, ref_table, ref_column = fk
                    
                    if constraint_name not in fk_groups:
                        fk_groups[constraint_name] = {
                            'ref_table': ref_table,
                            'columns': [],
                            'ref_columns': []
                        }
                    
                    fk_groups[constraint_name]['columns'].append(column_name)
                    fk_groups[constraint_name]['ref_columns'].append(ref_column)
                
                for constraint_name, fk_info in fk_groups.items():
                    constraint = {
                        'name': constraint_name,
                        'type': 'FOREIGN KEY',
                        'columns': fk_info['columns'],
                        'references_table': fk_info['ref_table'],
                        'references_columns': fk_info['ref_columns']
                    }
                    table_info['constraints'].append(constraint)
                
                tables_info.append(table_info)
            
            return tables_info
            
        except Exception as e:
            print(f"Error al obtener metadatos de MySQL: {str(e)}")
            return [] 