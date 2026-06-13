"""
main.py
UI-AIAS — Universal IT Admin AI Suite v2.0
Punto de entrada principal de la aplicación.
"""

import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from modules.ai_engine import AIEngine, OllamaConnectionError
from modules.sys_manager import SysManager
from modules.database import DatabaseManager
from modules.report_gen import generate_pdf

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ══════════════════════════════════════════════════════
#  APP PRINCIPAL
# ══════════════════════════════════════════════════════
class UIAIASApp(ctk.CTk):
    APP_TITLE   = "UI-AIAS — Universal IT Admin AI Suite"
    APP_VERSION = "2.0.0"

    def __init__(self):
        super().__init__()
        self.ai      = AIEngine()
        self.sys_mgr = SysManager()
        self.db      = DatabaseManager()
        self._theme  = "dark"

        self.title(self.APP_TITLE)
        self.geometry("1280x800")
        self.minsize(960, 620)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_frames()
        self._show_frame("dashboard")

    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=215, corner_radius=0)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_rowconfigure(10, weight=1)
        self.sidebar = sb

        ctk.CTkLabel(sb, text="⚙ UI-AIAS",
                     font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(20, 2))

        ctk.CTkLabel(sb, text=f"v{self.APP_VERSION}",
                     font=ctk.CTkFont(size=11), text_color="gray",
        ).grid(row=1, column=0, padx=20, pady=(0, 10))

        self.btn_theme = ctk.CTkButton(
            sb, text="☀ Tema claro",
            command=self._toggle_theme,
            fg_color="transparent",
            hover_color=("#2d2c2a", "#3a3936"),
            font=ctk.CTkFont(size=12), width=185,
        )
        self.btn_theme.grid(row=2, column=0, padx=10, pady=(0, 6))

        nav_items = [
            ("🏠  Dashboard",        "dashboard"),
            ("🔍  Análisis de Logs",  "log_analyzer"),
            ("🖥  Diagnóstico",       "diagnostics"),
            ("🤖  Generador Scripts", "script_gen"),
            ("💬  Chat con IA",       "chat"),
            ("📋  Historial",         "history"),
        ]
        for i, (label, key) in enumerate(nav_items, start=3):
            ctk.CTkButton(
                sb, text=label, anchor="w",
                command=lambda k=key: self._show_frame(k),
                fg_color="transparent",
                hover_color=("#2d2c2a", "#3a3936"),
                font=ctk.CTkFont(size=13),
            ).grid(row=i, column=0, padx=10, pady=2, sticky="ew")

        ctk.CTkLabel(sb, text="Modelo IA:",
                     font=ctk.CTkFont(size=11), text_color="gray",
        ).grid(row=9, column=0, padx=14, pady=(10, 0), sticky="w")

        self.var_model  = ctk.StringVar(value="llama3.2")
        self.model_menu = ctk.CTkOptionMenu(
            sb, values=["llama3.2"],
            variable=self.var_model, width=185,
            command=self._on_model_change,
        )
        self.model_menu.grid(row=10, column=0, padx=10, pady=(2, 6), sticky="ew")

        self.lbl_ollama = ctk.CTkLabel(
            sb, text="● Ollama: comprobando…",
            font=ctk.CTkFont(size=11), text_color="gray",
        )
        self.lbl_ollama.grid(row=11, column=0, padx=14, pady=(0, 14), sticky="sw")
        threading.Thread(target=self._check_ollama, daemon=True).start()

    def _check_ollama(self):
        ok = self.ai.check_connection()
        self.lbl_ollama.configure(
            text="● Ollama: activo" if ok else "● Ollama: inactivo",
            text_color="#6daa45" if ok else "#a13544",
        )
        if ok:
            models = self.ai.list_models()
            if models:
                self.model_menu.configure(values=models)
                self.var_model.set(models[0])
                self.ai.model = models[0]

    def _on_model_change(self, selected: str):
        self.ai.model = selected
        self.lbl_ollama.configure(
            text=f"● Modelo: {selected.split(':')[0]}",
            text_color="#4f98a3",
        )

    def _toggle_theme(self):
        self._theme = "light" if self._theme == "dark" else "dark"
        ctk.set_appearance_mode(self._theme)
        self.btn_theme.configure(
            text="🌙 Tema oscuro" if self._theme == "light" else "☀ Tema claro"
        )

    def _build_frames(self):
        self.frames = {}
        panels = {
            "dashboard":    DashboardFrame,
            "log_analyzer": LogAnalyzerFrame,
            "diagnostics":  DiagnosticsFrame,
            "script_gen":   ScriptGenFrame,
            "chat":         ChatFrame,
            "history":      HistoryFrame,
        }
        for key, Cls in panels.items():
            f = Cls(self, self.ai, self.sys_mgr, self.db)
            f.grid(row=0, column=1, sticky="nsew")
            self.frames[key] = f

    def _show_frame(self, key: str):
        self.frames[key].tkraise()
        if key == "history" and hasattr(self.frames[key], "refresh"):
            self.frames[key].refresh()


# ══════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════
class DashboardFrame(ctk.CTkFrame):

    def __init__(self, master, ai, sys_mgr, db):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.sys_mgr  = sys_mgr
        self._running = True
        self.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(self, text="Panel de Control",
                     font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, padx=30, pady=(24, 4), sticky="w")

        ctk.CTkLabel(self, text="Métricas del sistema en tiempo real.",
                     font=ctk.CTkFont(size=13), text_color="gray",
        ).grid(row=1, column=0, columnspan=3, padx=30, pady=(0, 16), sticky="w")

        os_card = ctk.CTkFrame(self)
        os_card.grid(row=2, column=0, columnspan=3, padx=30, pady=(0, 16), sticky="ew")
        os_card.grid_columnconfigure(1, weight=1)
        for i, (k, v) in enumerate(sys_mgr.get_os_info().items()):
            ctk.CTkLabel(os_card, text=f"{k}:",
                         font=ctk.CTkFont(weight="bold"), text_color="#4f98a3",
            ).grid(row=i, column=0, padx=(16, 8), pady=3, sticky="w")
            ctk.CTkLabel(os_card, text=str(v),
            ).grid(row=i, column=1, padx=(0, 16), pady=3, sticky="w")

        self._cards = {}
        for col, (key, title) in enumerate([
            ("cpu",   "🔲 CPU"),
            ("ram",   "🧠 RAM"),
            ("disco", "💾 Disco"),
        ]):
            card = ctk.CTkFrame(self)
            card.grid(row=3, column=col,
                      padx=(30 if col == 0 else 8, 8 if col < 2 else 30),
                      pady=8, sticky="ew")
            ctk.CTkLabel(card, text=title,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color="#4f98a3",
            ).pack(padx=14, pady=(12, 2), anchor="w")
            lbl = ctk.CTkLabel(card, text="Calculando…",
                               font=ctk.CTkFont(size=20, weight="bold"))
            lbl.pack(padx=14, pady=(0, 12))
            self._cards[key] = lbl

        self._update_metrics()

    def _update_metrics(self):
        if not self._running:
            return

        def _fetch():
            try:
                import psutil
                cpu    = f"{psutil.cpu_percent(interval=1):.1f}%"
                ram    = psutil.virtual_memory()
                ram_s  = f"{ram.used/1e9:.1f} / {ram.total/1e9:.1f} GB"
                disk   = psutil.disk_usage("C:\\" if self.sys_mgr.is_windows() else "/")
                disk_s = f"{disk.used/1e9:.1f} / {disk.total/1e9:.1f} GB"
            except ImportError:
                cpu = ram_s = disk_s = "pip install psutil"
            self._cards["cpu"].configure(text=cpu)
            self._cards["ram"].configure(text=ram_s)
            self._cards["disco"].configure(text=disk_s)
            if self._running:
                self.after(3000, self._update_metrics)

        threading.Thread(target=_fetch, daemon=True).start()

    def destroy(self):
        self._running = False
        super().destroy()


# ══════════════════════════════════════════════════════
#  ANÁLISIS DE LOGS
# ══════════════════════════════════════════════════════
class LogAnalyzerFrame(ctk.CTkFrame):

    PROMPT = (
        "Eres un experto en análisis forense de logs. "
        "Analiza el siguiente log, identifica errores críticos, "
        "advertencias y patrones sospechosos. Da recomendaciones concretas:\n\n{}"
    )

    def __init__(self, master, ai, sys_mgr, db):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.ai       = ai
        self.db       = db
        self._content = ""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self, text="Análisis de Logs con IA",
                     font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=0, padx=30, pady=(24, 4), sticky="w")

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=1, column=0, padx=30, pady=(0, 10), sticky="ew")
        ctk.CTkButton(bar, text="📂 Abrir archivo",
                      command=self._open, width=170,
        ).pack(side="left", padx=(0, 8))
        self.lbl_file = ctk.CTkLabel(bar, text="Ningún archivo cargado",
                                     text_color="gray", font=ctk.CTkFont(size=12))
        self.lbl_file.pack(side="left", padx=8)
        ctk.CTkButton(bar, text="🔍 Analizar con IA",
                      command=self._analyze, width=160,
                      fg_color="#01696f", hover_color="#0c4e54",
        ).pack(side="right")

        self.txt = ctk.CTkTextbox(
            self, font=ctk.CTkFont(family="Courier", size=12), wrap="word")
        self.txt.grid(row=2, column=0, padx=30, pady=(0, 10), sticky="nsew")
        self._set("Carga un archivo de log y pulsa 'Analizar con IA'.")

        ctk.CTkButton(self, text="📄 Exportar PDF",
                      command=self._export, width=160,
        ).grid(row=3, column=0, padx=30, pady=(0, 20), sticky="e")

    def _open(self):
        path = filedialog.askopenfilename(
            filetypes=[("Log/Texto", "*.log *.txt *.csv"), ("Todos", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                self._content = f.read(20_000)
            self.lbl_file.configure(text=Path(path).name, text_color="white")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _analyze(self):
        if not self._content:
            messagebox.showwarning("Aviso", "Primero carga un archivo.")
            return
        self._set("⏳ Analizando…\n")

        def _run():
            try:
                def tok(t):
                    self.txt.configure(state="normal")
                    self.txt.insert("end", t)
                    self.txt.see("end")
                    self.txt.configure(state="disabled")
                def done(full):
                    self.db.save_log_analysis(self.lbl_file.cget("text"), full)
                self._set("")
                self.ai.stream_query(self.PROMPT.format(self._content), tok, done)
            except OllamaConnectionError as e:
                self._set(f"[ERROR]\n{e}")

        threading.Thread(target=_run, daemon=True).start()

    def _export(self):
        try:
            path = generate_pdf({"analisis_ia": self.txt.get("0.0", "end"),
                                  "os_info": {"Módulo": "Análisis de Logs"}})
            messagebox.showinfo("PDF generado", f"Guardado en:\n{path}")
        except Exception as e:
            messagebox.showerror("Error PDF", str(e))

    def _set(self, text):
        self.txt.configure(state="normal")
        self.txt.delete("0.0", "end")
        self.txt.insert("0.0", text)
        self.txt.configure(state="disabled")


# ══════════════════════════════════════════════════════
#  DIAGNÓSTICO
# ══════════════════════════════════════════════════════
class DiagnosticsFrame(ctk.CTkFrame):

    def __init__(self, master, ai, sys_mgr, db):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.ai      = ai
        self.sys_mgr = sys_mgr
        self.db      = db
        self._diag   = {}
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self, text="Diagnóstico del Sistema",
                     font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=0, padx=30, pady=(24, 4), sticky="w")

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=1, column=0, padx=30, pady=(0, 10), sticky="ew")
        ctk.CTkButton(bar, text="▶ Ejecutar diagnóstico",
                      command=self._run, width=200,
                      fg_color="#01696f", hover_color="#0c4e54",
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(bar, text="🤖 Resumen IA",
                      command=self._ai_summary, width=130,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(bar, text="📄 Exportar PDF",
                      command=self._export, width=130,
        ).pack(side="left")

        self.txt = ctk.CTkTextbox(
            self, font=ctk.CTkFont(family="Courier", size=11), wrap="word")
        self.txt.grid(row=2, column=0, padx=30, pady=(0, 20), sticky="nsew")
        self._set("Pulsa 'Ejecutar diagnóstico' para comenzar.")

    def _run(self):
        self._set("⏳ Ejecutando diagnósticos…\n")
        def _go():
            self._diag = self.sys_mgr.get_full_diagnostics()
            lines = []
            for k, v in self._diag.items():
                lines.append(f"\n{'='*40}\n{k.upper()}\n{'='*40}")
                if isinstance(v, dict):
                    for dk, dv in v.items():
                        lines.append(f"  {dk}: {dv}")
                else:
                    lines.append(str(v))
            self._set("\n".join(lines))
            self.db.save_diagnostic(
                self.sys_mgr.os_name, "Diagnóstico completo",
                "\n".join(lines)[:1000])
        threading.Thread(target=_go, daemon=True).start()

    def _ai_summary(self):
        if not self._diag:
            messagebox.showwarning("Aviso", "Ejecuta primero el diagnóstico.")
            return
        summary = "\n".join(f"{k}: {str(v)[:300]}" for k, v in self._diag.items())
        prompt  = ("Eres un sysadmin experto. Analiza estos datos, detecta problemas "
                   "y da recomendaciones de seguridad y rendimiento:\n\n" + summary)
        self._set("⏳ Generando resumen IA…\n")
        def _go():
            try:
                def tok(t):
                    self.txt.configure(state="normal")
                    self.txt.insert("end", t)
                    self.txt.see("end")
                    self.txt.configure(state="disabled")
                self._set("")
                self.ai.stream_query(prompt, tok)
            except OllamaConnectionError as e:
                self._set(f"[ERROR]\n{e}")
        threading.Thread(target=_go, daemon=True).start()

    def _export(self):
        if not self._diag:
            messagebox.showwarning("Aviso", "Ejecuta primero el diagnóstico.")
            return
        try:
            path = generate_pdf(self._diag)
            messagebox.showinfo("PDF generado", f"Guardado en:\n{path}")
        except Exception as e:
            messagebox.showerror("Error PDF", str(e))

    def _set(self, text):
        self.txt.configure(state="normal")
        self.txt.delete("0.0", "end")
        self.txt.insert("0.0", text)
        self.txt.configure(state="disabled")


# ══════════════════════════════════════════════════════
#  GENERADOR DE SCRIPTS
# ══════════════════════════════════════════════════════
class ScriptGenFrame(ctk.CTkFrame):

    PROMPT = (
        "Eres experto en scripting. Crea un script de {tipo} en {os} para:\n\n"
        "{desc}\n\n"
        "Requisitos: comentarios en cada sección, manejo de errores robusto. "
        "Devuelve SOLO el código dentro de un bloque ```{tipo}\n...\n```."
    )
    EXTENSIONS = {
        "bash": ".sh", "powershell": ".ps1",
        "python": ".py", "batch": ".bat",
    }

    def __init__(self, master, ai, sys_mgr, db):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.ai = ai
        self.db = db
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(self, text="Generador de Scripts con IA",
                     font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=0, padx=30, pady=(24, 4), sticky="w")

        opts = ctk.CTkFrame(self)
        opts.grid(row=1, column=0, padx=30, pady=(0, 10), sticky="ew")
        ctk.CTkLabel(opts, text="Tipo:").grid(row=0, column=0, padx=(12, 4), pady=10)
        self.var_tipo = ctk.StringVar(value="bash")
        ctk.CTkOptionMenu(opts, values=["bash", "powershell", "python", "batch"],
                          variable=self.var_tipo, width=130,
        ).grid(row=0, column=1, padx=4, pady=10)
        ctk.CTkLabel(opts, text="OS:").grid(row=0, column=2, padx=(16, 4), pady=10)
        self.var_os = ctk.StringVar(value=sys_mgr.os_name)
        ctk.CTkOptionMenu(opts, values=["Linux", "Windows", "macOS"],
                          variable=self.var_os, width=130,
        ).grid(row=0, column=3, padx=4, pady=10, sticky="w")

        ctk.CTkLabel(self, text="Describe el problema o tarea:",
                     font=ctk.CTkFont(size=13),
        ).grid(row=2, column=0, padx=30, pady=(4, 0), sticky="w")

        self.txt_in = ctk.CTkTextbox(self, height=90)
        self.txt_in.grid(row=2, column=0, padx=30, pady=(28, 4), sticky="ew")

        ctk.CTkButton(self, text="⚡ Generar Script",
                      command=self._generate, width=160,
                      fg_color="#01696f", hover_color="#0c4e54",
        ).grid(row=2, column=0, padx=30, pady=(128, 0), sticky="e")

        self.txt_out = ctk.CTkTextbox(
            self, font=ctk.CTkFont(family="Courier", size=12), wrap="word")
        self.txt_out.grid(row=3, column=0, padx=30, pady=(8, 8), sticky="nsew")
        self.txt_out.insert("0.0", "El script generado aparecerá aquí.")
        self.txt_out.configure(state="disabled")

        btn_bar = ctk.CTkFrame(self, fg_color="transparent")
        btn_bar.grid(row=4, column=0, padx=30, pady=(0, 20), sticky="e")
        ctk.CTkButton(btn_bar, text="📋 Copiar",
                      command=self._copy, width=120,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_bar, text="💾 Guardar archivo",
                      command=self._save_file, width=150,
                      fg_color="#437a22", hover_color="#2e5c10",
        ).pack(side="left")

    def _generate(self):
        desc = self.txt_in.get("0.0", "end").strip()
        if not desc:
            messagebox.showwarning("Aviso", "Escribe una descripción.")
            return
        prompt = self.PROMPT.format(
            tipo=self.var_tipo.get(), os=self.var_os.get(), desc=desc)
        self._set_out("⏳ Generando script…\n")
        def _go():
            try:
                def tok(t):
                    self.txt_out.configure(state="normal")
                    self.txt_out.insert("end", t)
                    self.txt_out.see("end")
                    self.txt_out.configure(state="disabled")
                def done(full):
                    self.db.save_query("ScriptGen", prompt[:500], full[:500])
                self._set_out("")
                self.ai.stream_query(prompt, tok, done)
            except OllamaConnectionError as e:
                self._set_out(f"[ERROR]\n{e}")
        threading.Thread(target=_go, daemon=True).start()

    def _set_out(self, text):
        self.txt_out.configure(state="normal")
        self.txt_out.delete("0.0", "end")
        self.txt_out.insert("0.0", text)
        self.txt_out.configure(state="disabled")

    def _copy(self):
        content = self.txt_out.get("0.0", "end").strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            messagebox.showinfo("Copiado", "Script copiado al portapapeles.")

    def _save_file(self):
        content = self.txt_out.get("0.0", "end").strip()
        if not content:
            messagebox.showwarning("Aviso", "Genera un script primero.")
            return
        lines = content.split("\n")
        code_lines, inside = [], False
        for line in lines:
            if line.startswith("```") and not inside:
                inside = True
                continue
            if line.startswith("```") and inside:
                inside = False
                continue
            if inside:
                code_lines.append(line)
        code = "\n".join(code_lines) if code_lines else content
        ext  = self.EXTENSIONS.get(self.var_tipo.get(), ".txt")
        path = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[(f"Script {self.var_tipo.get()}", f"*{ext}"),
                       ("Todos", "*.*")],
            initialfile=f"script_generado{ext}",
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
            messagebox.showinfo("Guardado", f"Script guardado en:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ══════════════════════════════════════════════════════
#  CHAT CONVERSACIONAL
# ══════════════════════════════════════════════════════
class ChatFrame(ctk.CTkFrame):

    SYSTEM_PROMPT = (
        "Eres UI-AIAS, un asistente experto en administración de sistemas IT, "
        "ciberseguridad y scripting. Responde en español de forma precisa y concisa. "
        "Cuando des comandos o código usa bloques de código."
    )

    def __init__(self, master, ai, sys_mgr, db):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.ai       = ai
        self.db       = db
        self._history = []
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, padx=30, pady=(24, 4), sticky="ew")
        ctk.CTkLabel(top, text="💬 Chat con IA",
                     font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(side="left")
        ctk.CTkButton(top, text="🗑 Limpiar",
                      command=self._clear, width=110,
        ).pack(side="right")

        self.txt = ctk.CTkTextbox(
            self, font=ctk.CTkFont(size=13), wrap="word")
        self.txt.grid(row=1, column=0, padx=30, pady=(0, 8), sticky="nsew")
        self.txt.configure(state="disabled")
        self._append("Sistema", "Chat listo. Pregunta sobre IT, sysadmin o ciberseguridad.\n")

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=2, column=0, padx=30, pady=(0, 20), sticky="ew")
        bar.grid_columnconfigure(0, weight=1)
        self.entry = ctk.CTkEntry(
            bar, placeholder_text="Escribe tu pregunta…",
            font=ctk.CTkFont(size=13))
        self.entry.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        self.entry.bind("<Return>", lambda e: self._send())
        ctk.CTkButton(bar, text="Enviar ➤",
                      command=self._send, width=100,
                      fg_color="#01696f", hover_color="#0c4e54",
        ).grid(row=0, column=1)

    def _build_prompt(self, user_msg: str) -> str:
        parts = [self.SYSTEM_PROMPT, "\n\n"]
        for turn in self._history[-10:]:
            role = "Usuario" if turn["role"] == "user" else "Asistente"
            parts.append(f"{role}: {turn['content']}\n")
        parts.append(f"Usuario: {user_msg}\nAsistente:")
        return "".join(parts)

    def _send(self):
        msg = self.entry.get().strip()
        if not msg:
            return
        self.entry.delete(0, "end")
        self._append("Tú", msg)
        self._history.append({"role": "user", "content": msg})
        self._append("UI-AIAS", "")
        def _run():
            try:
                def tok(t):
                    self.txt.configure(state="normal")
                    self.txt.insert("end", t)
                    self.txt.see("end")
                    self.txt.configure(state="disabled")
                def done(full):
                    self._history.append({"role": "assistant", "content": full})
                    self.db.save_query("Chat", msg[:500], full[:500])
                    self.txt.configure(state="normal")
                    self.txt.insert("end", "\n\n")
                    self.txt.configure(state="disabled")
                self.ai.stream_query(self._build_prompt(msg), tok, done)
            except OllamaConnectionError as e:
                self._append("Error", str(e))
        threading.Thread(target=_run, daemon=True).start()

    def _append(self, role: str, text: str):
        self.txt.configure(state="normal")
        if role == "Tú":
            self.txt.insert("end", f"\n👤 Tú:\n{text}\n\n")
        elif role == "UI-AIAS":
            self.txt.insert("end", f"🤖 UI-AIAS:\n{text}")
        elif role == "Sistema":
            self.txt.insert("end", f"ℹ {text}\n")
        else:
            self.txt.insert("end", f"⚠ {role}: {text}\n")
        self.txt.see("end")
        self.txt.configure(state="disabled")

    def _clear(self):
        self._history.clear()
        self.txt.configure(state="normal")
        self.txt.delete("0.0", "end")
        self.txt.configure(state="disabled")
        self._append("Sistema", "Chat reiniciado.\n")


# ══════════════════════════════════════════════════════
#  HISTORIAL
# ══════════════════════════════════════════════════════
class HistoryFrame(ctk.CTkFrame):

    def __init__(self, master, ai, sys_mgr, db):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.db = db
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, padx=30, pady=(24, 10), sticky="ew")
        ctk.CTkLabel(top, text="Historial de Actividad",
                     font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(side="left")
        ctk.CTkButton(top, text="🔄 Actualizar",
                      command=self.refresh, width=110,
        ).pack(side="right")

        self.txt = ctk.CTkTextbox(
            self, font=ctk.CTkFont(family="Courier", size=11), wrap="word")
        self.txt.grid(row=1, column=0, padx=30, pady=(0, 20), sticky="nsew")
        self.refresh()

    def refresh(self):
        lines = ["="*60, "  CONSULTAS (últimas 20)", "="*60]
        try:
            for r in self.db.get_queries(20):
                lines.append(
                    f"[{r['fecha'][:19]}] [{r['modulo']}]\n  {r['prompt'][:80]}…\n")
            lines += ["", "="*60, "  DIAGNÓSTICOS (últimos 10)", "="*60]
            for r in self.db.get_diagnostics(10):
                lines.append(
                    f"[{r['fecha'][:19]}] {r['sistema_os']} — {r['titulo']}\n")
            lines += ["", "="*60, "  LOGS ANALIZADOS (últimos 10)", "="*60]
            for r in self.db.get_log_analyses(10):
                lines.append(
                    f"[{r['fecha'][:19]}] {r['nombre_archivo']}\n"
                    f"  {r['resumen_ia'][:80]}…\n")
        except Exception as e:
            lines.append(f"Error cargando historial: {e}")

        self.txt.configure(state="normal")
        self.txt.delete("0.0", "end")
        self.txt.insert("0.0", "\n".join(lines))
        self.txt.configure(state="disabled")


# ══════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════
if __name__ == "__main__":
    app = UIAIASApp()
    app.mainloop()