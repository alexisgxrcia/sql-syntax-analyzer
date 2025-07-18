import tkinter as tk
from tkinter import ttk, scrolledtext
import customtkinter as ctk
from core.scanner_dml import DMLScanner
from core.analyzer_syntax import SyntaxAnalyzer

ctk.deactivate_automatic_dpi_awareness()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

default_query = """SELECT ANOMBRE
FROM ALUMNOS,INSCRITOS,CARRERAS
WHERE INSCRITOS.SEMESTRE='2010I'
AND CARRERAS.CNOMBRE='ISC'
AND ALUMNOS.GENERACION='2010';"""

class ModernTooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, "bbox") else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = ctk.CTkToplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(
            self.tooltip,
            text=self.text,
            corner_radius=6,
            fg_color="#313244",
            text_color="#cdd6f4",
            padx=10,
            pady=6
        )
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class SQLAnalyzerApp(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("dark")

        super().__init__()
        self.title("SQL Analyzer")
        self.geometry("1100x850")

        self._apply_theme_settings()

        self.scanner = DMLScanner()
        self.analyzer = SyntaxAnalyzer()

        self.setup_colors()
        self.create_ui()

        self.after(100, self.adjust_panel_sizes)
        self.bind("<Configure>", self.on_window_resize)

        self.load_tables_info()

    def _apply_theme_settings(self):
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#1e1e2e")

    def setup_colors(self):
        self.colors = {
            "bg": "#1e1e2e",
            "surface": "#313244",
            "overlay": "#45475a",
            "accent": "#89b4fa",
            "text": "#cdd6f4",
            "subtext": "#a6adc8",
            "error": "#f38ba8",
            "success": "#a6e3a1"
        }

    def create_ui(self):
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(
            main_container,
            text="Analizador SQL",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            text_color=self.colors["accent"]
        )
        title.pack(anchor=tk.W, pady=(0, 15))

        buttons_panel = ctk.CTkFrame(main_container, fg_color=self.colors["surface"], corner_radius=10, height=60)
        buttons_panel.pack(fill=tk.X, pady=(0, 15), side=tk.BOTTOM)
        buttons_panel.pack_propagate(False)

        buttons_layout = ctk.CTkFrame(buttons_panel, fg_color="transparent")
        buttons_layout.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self.analyze_btn = ctk.CTkButton(
            buttons_layout,
            text="Analizar y Ejecutar",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color=self.colors["accent"],
            text_color=self.colors["bg"],
            hover_color="#74c7ec",
            corner_radius=8,
            width=120,
            height=35,
            command=self.analyze_sql
        )
        self.analyze_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_btn = ctk.CTkButton(
            buttons_layout,
            text="Limpiar",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color=self.colors["error"],
            text_color=self.colors["bg"],
            hover_color="#eb6f92",
            corner_radius=8,
            width=120,
            height=35,
            command=self.clear_input
        )
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.status_var = tk.StringVar(value="Listo para analizar")
        self.status = ctk.CTkLabel(
            buttons_layout,
            textvariable=self.status_var,
            font=ctk.CTkFont(family="Inter", size=13)
        )
        self.status.pack(side=tk.RIGHT)

        panels_container = ctk.CTkFrame(main_container, fg_color="transparent")
        panels_container.pack(fill=tk.BOTH, expand=True)

        panels_container.columnconfigure(0, weight=1, minsize=350, uniform="column")
        panels_container.columnconfigure(1, weight=1, minsize=350, uniform="column")
        panels_container.rowconfigure(0, weight=1)
        panels_container.rowconfigure(1, weight=1)

        sql_panel = ctk.CTkFrame(panels_container, fg_color=self.colors["surface"], corner_radius=10)
        sql_panel.grid(row=0, column=0, padx=(0, 10), pady=(0, 10), sticky="nsew")

        sql_inner = ctk.CTkFrame(sql_panel, fg_color="transparent")
        sql_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        sql_title = ctk.CTkLabel(
            sql_inner,
            text="Consulta SQL",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold")
        )
        sql_title.pack(anchor=tk.W, pady=(0, 10))

        editor_container = ctk.CTkFrame(sql_inner, fg_color="transparent")
        editor_container.pack(fill=tk.BOTH, expand=True)

        self.line_numbers = tk.Text(
            editor_container,
            width=3,
            padx=5,
            pady=8,
            takefocus=0,
            border=0,
            background=self.colors["overlay"],
            foreground=self.colors["subtext"],
            font=("JetBrains Mono", 13),
            cursor='arrow',
            relief=tk.FLAT,
            highlightthickness=0
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.line_numbers.tag_configure("right", justify='right')
        self.line_numbers.config(state='disabled')

        self.sql_input = scrolledtext.ScrolledText(
            editor_container,
            height=7,
            font=("JetBrains Mono", 13),
            background=self.colors["overlay"],
            foreground=self.colors["text"],
            insertbackground=self.colors["accent"],
            borderwidth=0,
            relief=tk.FLAT,
            selectbackground=self.colors["accent"],
            selectforeground=self.colors["bg"],
            padx=10,
            pady=8,
            undo=True
        )
        self.sql_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.sql_scrollbar = self.sql_input.vbar
        self.sql_scrollbar.config(command=self.on_scroll)

        self.sql_input.bind('<KeyRelease>', self.update_line_numbers)
        self.sql_input.bind('<FocusIn>', self.update_line_numbers)
        self.sql_input.bind('<MouseWheel>', self.update_line_numbers)
        self.sql_input.bind('<Configure>', self.update_line_numbers)

        self.sql_input.tag_configure("error_line", background=self.colors["error"], foreground=self.colors["bg"])
        self.sql_input.bind("<Key>", self.clear_error_highlighting)

        self.sql_input.insert(tk.END, default_query)
        self.after(100, self.update_line_numbers)

        errors_panel = ctk.CTkFrame(panels_container, fg_color=self.colors["surface"], corner_radius=10)
        errors_panel.grid(row=0, column=1, padx=(10, 0), pady=(0, 10), sticky="nsew")

        errors_inner = ctk.CTkFrame(errors_panel, fg_color="transparent")
        errors_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        errors_title = ctk.CTkLabel(
            errors_inner,
            text="Errores",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold")
        )
        errors_title.pack(anchor=tk.W, pady=(0, 10))

        self.errors_text = scrolledtext.ScrolledText(
            errors_inner,
            font=("JetBrains Mono", 12),
            background=self.colors["overlay"],
            foreground=self.colors["text"],
            borderwidth=0,
            relief=tk.FLAT,
            padx=10,
            pady=8,
            state='disabled'  # Widget en modo solo lectura
        )
        self.errors_text.pack(fill=tk.BOTH, expand=True)

        results_panel = ctk.CTkFrame(panels_container, fg_color=self.colors["surface"], corner_radius=10)
        results_panel.grid(row=1, column=0, padx=(0, 10), pady=(10, 0), sticky="nsew")

        results_panel.grid_propagate(False)
        panels_container.update_idletasks()
        panel_width = panels_container.winfo_width() // 2 - 15
        results_panel.configure(width=panel_width)

        results_inner = ctk.CTkFrame(results_panel, fg_color="transparent")
        results_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        results_title = ctk.CTkLabel(
            results_inner,
            text="Resultados",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold")
        )
        results_title.pack(anchor=tk.W, pady=(0, 10))

        results_container = ctk.CTkFrame(results_inner, fg_color="transparent")
        results_container.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure(
            "Results.Treeview",
            background=self.colors["overlay"],
            fieldbackground=self.colors["overlay"],
            foreground=self.colors["text"],
            rowheight=25,
            borderwidth=0
        )
        style.configure(
            "Results.Treeview.Heading",
            background=self.colors["surface"],
            foreground=self.colors["text"],
            relief="flat",
            borderwidth=0,
            padding=5
        )
        style.map(
            "Results.Treeview.Heading",
            background=[("active", self.colors["accent"])],
            foreground=[("active", self.colors["bg"])]
        )
        style.map(
            "Results.Treeview",
            background=[("selected", self.colors["accent"])],
            foreground=[("selected", self.colors["bg"])]
        )

        treeview_frame = ctk.CTkFrame(results_container, fg_color="transparent")
        treeview_frame.pack(fill=tk.BOTH, expand=True)
        treeview_frame.pack_propagate(False)

        treeview_frame.columnconfigure(0, weight=1)
        treeview_frame.columnconfigure(1, weight=0)
        treeview_frame.rowconfigure(0, weight=1)
        treeview_frame.rowconfigure(1, weight=0)

        results_vsb = ttk.Scrollbar(treeview_frame, orient="vertical")
        results_hsb = ttk.Scrollbar(treeview_frame, orient="horizontal")

        self.results_tree = ttk.Treeview(
            treeview_frame,
            show="headings",
            style="Results.Treeview",
            yscrollcommand=results_vsb.set,
            xscrollcommand=results_hsb.set
        )

        results_vsb.configure(command=self.results_tree.yview)
        results_hsb.configure(command=self.results_tree.xview)

        self.results_tree.grid(row=0, column=0, sticky='nsew')
        results_vsb.grid(row=0, column=1, sticky='ns')
        results_hsb.grid(row=1, column=0, sticky='ew')

        tables_panel = ctk.CTkFrame(panels_container, fg_color=self.colors["surface"], corner_radius=10)
        tables_panel.grid(row=1, column=1, padx=(10, 0), pady=(10, 0), sticky="nsew")

        tables_inner = ctk.CTkFrame(tables_panel, fg_color="transparent")
        tables_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        tables_title = ctk.CTkLabel(
            tables_inner,
            text="Tablas en la Base de Datos",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold")
        )
        tables_title.pack(anchor=tk.W, pady=(0, 10))

        style.configure(
            "TNotebook",
            background=self.colors["surface"],
            tabmargins=[2, 5, 2, 0],
            borderwidth=0
        )
        style.configure(
            "TNotebook.Tab",
            background=self.colors["surface"],
            foreground=self.colors["text"],
            padding=[10, 5],
            borderwidth=0
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", self.colors["accent"])],
            foreground=[("selected", self.colors["bg"])],
            expand=[("selected", [1, 1, 1, 0])]
        )

        self.tables_notebook = ttk.Notebook(tables_inner, style="TNotebook")
        self.tables_notebook.pack(fill=tk.BOTH, expand=True)

        self.general_tab = ctk.CTkFrame(self.tables_notebook, fg_color=self.colors["overlay"])
        self.tables_notebook.add(self.general_tab, text="General")

        self.tables_info_text = scrolledtext.ScrolledText(
            self.general_tab,
            font=("JetBrains Mono", 12),
            background=self.colors["overlay"],
            foreground=self.colors["text"],
            borderwidth=0,
            relief=tk.FLAT,
            padx=10,
            pady=8,
            state='disabled'
        )
        self.tables_info_text.pack(fill=tk.BOTH, expand=True)

    def on_scroll(self, *args):
        self.sql_input.yview(*args)
        self.line_numbers.yview(*args)

    def update_line_numbers(self, event=None):
        final_index = self.sql_input.index("end-1c")
        num_of_lines = int(final_index.split('.')[0])

        line_numbers_text = '\n'.join(str(i) for i in range(1, num_of_lines + 1))

        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_numbers_text)
        self.line_numbers.tag_add("right", "1.0", "end")
        self.line_numbers.config(state='disabled')

        self.line_numbers.yview_moveto(self.sql_input.yview()[0])

    def clear_error_highlighting(self, event=None):
        if event and event.keysym not in ('Left', 'Right', 'Up', 'Down', 'Home', 'End', 'Prior', 'Next'):
            self.sql_input.tag_remove("error_line", "1.0", "end")

    def clear_input(self):
        self.sql_input.delete("1.0", tk.END)
        self.update_line_numbers()

        self.errors_text.config(state='normal')
        self.errors_text.delete("1.0", tk.END)
        self.errors_text.config(state='disabled')

        self.clear_results_view()

        self.status_var.set("Entrada limpiada")
        self.configure_status()
        self.sql_input.tag_remove("error_line", "1.0", "end")

    def analyze_sql(self):
        self.errors_text.config(state='normal')
        self.errors_text.delete("1.0", tk.END)
        self.errors_text.config(state='disabled')

        self.clear_error_highlighting()

        self.clear_results_view()

        sql_query = self.sql_input.get("1.0", tk.END)

        if not sql_query.strip():
            self.status_var.set("Error: No hay una consulta SQL para analizar")
            self.configure_status("error")
            return

        self.status_var.set("Analizando...")
        self.configure_status()
        self.update_idletasks()

        try:
            result = self.analyzer.parse(sql_query)

            if result["status"] == "success":
                self.status_var.set("✅ Análisis completado. Ejecutando consulta...")
                self.configure_status("success")

                self.execute_sql(sql_query)
            else:
                self.status_var.set("❌ " + result["message"])
                self.configure_status("error")

                self.errors_text.config(state='normal')
                for error in result.get("errors", []):
                    self.errors_text.insert(tk.END, f"{error}\n")
                    self.highlight_error_line(error)
                self.errors_text.config(state='disabled')

        except Exception as e:
            self.status_var.set(f"Error durante el análisis: {str(e)}")
            self.configure_status("error")
            self.errors_text.config(state='normal')
            self.errors_text.insert(tk.END, f"Error inesperado: {str(e)}")
            self.errors_text.config(state='disabled')

    def execute_sql(self, sql_query=None):
        if not sql_query:
            sql_query = self.sql_input.get("1.0", tk.END).strip()

        if not sql_query:
            return

        self.status_var.set("Ejecutando consulta...")
        self.configure_status()
        self.update_idletasks()

        try:
            result = self.analyzer.execute_sql_query(sql_query)

            if result["status"] == "error":
                self.clear_results_view()

                self.status_var.set("❌ Error en la consulta")
                self.configure_status("error")

                self.errors_text.config(state='normal')
                for error in result.get("errors", []):
                    self.errors_text.insert(tk.END, f"{error}\n")
                    self.highlight_error_line(error)
                self.errors_text.config(state='disabled')
            else:
                if "execution" in result:
                    execution = result["execution"]

                    if execution["status"] == "success":
                        self.status_var.set("✅ " + execution["message"])
                        self.configure_status("success")

                        if "data" in execution and execution["data"]:
                            self.display_query_results(execution["data"], execution["column_names"])
                        else:
                            self.status_var.set(f"✅ Consulta ejecutada: {execution.get('rows_affected', 0)} filas afectadas")

                        if sql_query.strip().upper().startswith(("CREATE", "ALTER", "DROP")):
                            self.update_tables_display()
                    else:
                        self.status_var.set(f"❌ Error al ejecutar: {execution['message']}")
                        self.configure_status("error")
                        self.errors_text.config(state='normal')
                        self.errors_text.insert(tk.END, f"Error de ejecución: {execution['message']}")
                        self.errors_text.config(state='disabled')

        except Exception as e:
            self.status_var.set(f"Error durante la ejecución: {str(e)}")
            self.configure_status("error")
            self.errors_text.config(state='normal')
            self.errors_text.insert(tk.END, f"Error inesperado: {str(e)}")
            self.errors_text.config(state='disabled')

    def load_tables_info(self):
        self.update_tables_display()

    def update_tables_display(self):
        for tab in self.tables_notebook.tabs():
            tab_id = self.tables_notebook.index(tab)
            if tab_id > 0:
                self.tables_notebook.forget(tab_id)

        self.tables_info_text.config(state='normal')
        self.tables_info_text.delete("1.0", tk.END)

        try:
            tables = self.analyzer.tables_info
            if tables:
                self.tables_info_text.insert(tk.END, "TABLAS CARGADAS:\n\n")
                for table in tables:
                    self.tables_info_text.insert(tk.END, f"- {table['name']}\n")

                    tab = ctk.CTkFrame(self.tables_notebook, fg_color=self.colors["overlay"])
                    self.tables_notebook.add(tab, text=table['name'])

                    tab_frame = ctk.CTkFrame(tab, fg_color="transparent")
                    tab_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                    tab_text = scrolledtext.ScrolledText(
                        tab_frame,
                        font=("JetBrains Mono", 12),
                        background=self.colors["overlay"],
                        foreground=self.colors["text"],
                        borderwidth=0,
                        relief=tk.FLAT,
                        padx=10,
                        pady=8,
                        state='normal'
                    )
                    tab_text.pack(fill=tk.BOTH, expand=True)

                    tab_text.insert(tk.END, f"Tabla: {table['name']}\n", "title")
                    tab_text.insert(tk.END, f"{'-'*40}\n\n")

                    if 'attributes' in table and table['attributes']:
                        max_name_width = max(len(col['name']) for col in table['attributes'])

                        tab_text.insert(tk.END, "ATRIBUTOS:\n\n", "subtitle")
                        for col in table['attributes']:
                            name_padded = col['name'].ljust(max_name_width)
                            tab_text.insert(tk.END, f"• {name_padded}  |  ", "attr_name")
                            tab_text.insert(tk.END, f"{col['type']}\n", "attr_type")

                        if 'primary_key' in table and table['primary_key']:
                            tab_text.insert(tk.END, f"\nCLAVE PRIMARIA:\n", "subtitle")
                            tab_text.insert(tk.END, f"• {', '.join(table['primary_key'])}\n", "key")

                        if 'foreign_keys' in table and table['foreign_keys']:
                            tab_text.insert(tk.END, f"\nCLAVES FORÁNEAS:\n", "subtitle")
                            for fk in table['foreign_keys']:
                                if isinstance(fk, dict) and 'columns' in fk and 'referenced_table' in fk:
                                    tab_text.insert(tk.END, f"• {', '.join(fk['columns'])} → {fk['referenced_table']}", "key")
                                    if 'referenced_columns' in fk:
                                        tab_text.insert(tk.END, f".{', '.join(fk['referenced_columns'])}", "key")
                                    tab_text.insert(tk.END, "\n")
                    else:
                        tab_text.insert(tk.END, "No hay información de columnas disponible\n")

                    tab_text.tag_configure("title", font=("JetBrains Mono", 14, "bold"), foreground=self.colors["accent"])
                    tab_text.tag_configure("subtitle", font=("JetBrains Mono", 12, "bold"), foreground=self.colors["subtext"])
                    tab_text.tag_configure("attr_name", foreground=self.colors["accent"])
                    tab_text.tag_configure("attr_type", foreground=self.colors["subtext"])
                    tab_text.tag_configure("key", foreground="#a6e3a1")

                    tab_text.config(state='disabled')
            else:
                self.tables_info_text.insert(tk.END, "No hay tablas disponibles en la base de datos.\n")
        except Exception as e:
            self.tables_info_text.insert(tk.END, f"Error al cargar información de tablas: {str(e)}\n")

        self.tables_info_text.config(state='disabled')

    def update_semantic_tables(self):
        self.status_var.set("Actualizando tablas semánticas...")
        self.configure_status()
        self.update_idletasks()

        try:
            result = self.analyzer.update_semantic_tables()

            if result["status"] == "success":
                self.status_var.set("✅ " + result["message"])
                self.configure_status("success")

                self.update_tables_display()
            else:
                self.status_var.set("❌ Error al actualizar tablas semánticas")
                self.configure_status("error")

                self.errors_text.config(state='normal')
                self.errors_text.insert(tk.END, "ERROR AL CARGAR TABLAS:\n\n")
                for error in result.get("errors", []):
                    self.errors_text.insert(tk.END, f"{error}\n")
                self.errors_text.config(state='disabled')

        except Exception as e:
            self.status_var.set(f"Error al actualizar tablas: {str(e)}")
            self.configure_status("error")
            self.errors_text.config(state='normal')
            self.errors_text.insert(tk.END, f"Error inesperado: {str(e)}")
            self.errors_text.config(state='disabled')

    def display_query_results(self, data, columns):
        self.results_tree["columns"] = columns

        num_columns = len(columns)

        stretch = num_columns <= 3

        if num_columns <= 3:
            col_width = 150
        else:
            col_width = 90

        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=col_width, minwidth=80, stretch=stretch)

        for i, row in enumerate(data):
            tag = "even" if i % 2 == 0 else "odd"
            self.results_tree.insert("", tk.END, values=row, tags=(tag,))

        self.results_tree.tag_configure("even", background=self.colors["overlay"])
        self.results_tree.tag_configure("odd", background=self.colors["surface"])

        self.after(100, self.adjust_panel_sizes)

    def highlight_error_line(self, error_message):
        try:
            if "Línea" in error_message:
                line_str = error_message.split("Línea")[1].split(".")[0].strip()
                line_num = int(line_str)
                start_index = f"{line_num}.0"
                self.sql_input.see(start_index)
                self.sql_input.tag_add("error_line", start_index, f"{line_num}.end lineend")
        except:
            pass

    def configure_status(self, state="normal"):
        if state == "success":
            self.status.configure(text_color=self.colors["success"])
        elif state == "error":
            self.status.configure(text_color=self.colors["error"])
        else:
            self.status.configure(text_color=self.colors["text"])

    def on_window_resize(self, event=None):
        if event and event.widget == self:
            self.after(100, self.adjust_panel_sizes)

    def adjust_panel_sizes(self):
        try:
            total_width = self.winfo_width()
            if total_width <= 1:
                return

            panel_width = (total_width - 60) // 2

            results_slaves = self.grid_slaves(row=1, column=0)
            tables_slaves = self.grid_slaves(row=1, column=1)

            if results_slaves and len(results_slaves) > 0:
                results_panel = results_slaves[0]
                results_panel.configure(width=panel_width)

            if tables_slaves and len(tables_slaves) > 0:
                tables_panel = tables_slaves[0]
                tables_panel.configure(width=panel_width)

            if hasattr(self, 'results_tree') and self.results_tree["columns"]:
                columns = self.results_tree["columns"]
                num_columns = len(columns)

                if num_columns > 0:
                    if num_columns <= 3:
                        col_width = (panel_width - 30) // num_columns
                        stretch = True
                    else:
                        col_width = min(100, (panel_width - 30) // num_columns)
                        stretch = False

                    for col in columns:
                        self.results_tree.column(col, width=col_width, stretch=stretch)

        except Exception:
            pass

    def clear_results_view(self):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        self.results_tree["columns"] = ()

        self.results_tree.update_idletasks()

if __name__ == "__main__":
    app = SQLAnalyzerApp()
    app.mainloop()
