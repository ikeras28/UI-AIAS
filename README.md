⚙️ UI-AIAS — Universal IT Admin AI Suite
Aplicación de escritorio multiplataforma para administración IT con IA local integrada. Sin APIs externas, sin costes, todo corre en tu máquina.

📸 Vista previa
<img width="1358" height="717" alt="image" src="https://github.com/user-attachments/assets/4414d6b4-2541-4dfe-989a-a8e7cc7c81aa" />
<img width="1359" height="715" alt="image" src="https://github.com/user-attachments/assets/0b0c8de9-7f73-4ca6-93bb-4e0320275e89" />



✨ Funcionalidades
Módulo	Descripción
🏠 Dashboard	Métricas de CPU, RAM y Disco en tiempo real (actualización cada 3s)
🔍 Análisis de Logs	Carga archivos .log/.txt y los analiza con IA forense
🖥 Diagnóstico	Auditoría completa: procesos, red, servicios y logs del SO
🤖 Generador de Scripts	Genera Bash, PowerShell, Python y Batch con IA
💬 Chat con IA	Asistente conversacional especializado en IT y ciberseguridad
📋 Historial	Registro persistente en SQLite de todas las operaciones
📄 Exportar PDF	Genera reportes profesionales con un clic
🛠️ Stack Tecnológico
Lenguaje: Python 3.12+

GUI: CustomTkinter (arquitectura orientada a objetos)

IA Local: Ollama + Llama 3.2 (http://localhost:11434)

Base de datos: SQLite3

PDF: ReportLab

Métricas: psutil

Compatibilidad: Windows 10/11 y Linux (sin librerías propietarias)

📁 Estructura del Proyecto
text
UI-AIAS/
├── main.py                 # Punto de entrada y GUI principal
├── requirements.txt        # Dependencias del proyecto
├── modules/
│   ├── ai_engine.py        # Conexión con Ollama, streaming de tokens
│   ├── sys_manager.py      # Auditoría multiplataforma del SO
│   ├── database.py         # ORM ligero SQLite3
│   └── report_gen.py       # Generación de PDFs con ReportLab
└── reports/                # PDFs generados (creado automáticamente)
🚀 Instalación y Uso
1. Requisitos previos
Python 3.12+ — marcar ✅ Add Python to PATH

Ollama — backend de IA local

Git

2. Clonar el repositorio
bash
git clone https://github.com/TU_USUARIO/UI-AIAS.git
cd UI-AIAS
3. Crear entorno virtual
bash
# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
4. Instalar dependencias
bash
pip install -r requirements.txt
5. Descargar el modelo de IA
bash
ollama pull llama3.2
6. Ejecutar la aplicación
bash
python main.py
⚙️ Configuración
Por defecto la app se conecta a Ollama en http://localhost:11434.

El selector de modelos del sidebar carga automáticamente todos los modelos que tengas instalados en Ollama. Puedes cambiar el modelo activo en cualquier momento sin reiniciar.

🗄️ Base de Datos
La base de datos admin_suite.db se crea automáticamente en la raíz del proyecto con tres tablas:

Tabla	Contenido
historial_consultas	Todas las consultas realizadas a la IA
diagnosticos_guardados	Diagnósticos completos del sistema
logs_analizados	Resultados de análisis forense de logs
🔧 Troubleshooting
ModuleNotFoundError: No module named 'customtkinter'
→ Asegúrate de tener el venv activo antes de ejecutar: .venv\Scripts\Activate.ps1

● Ollama: inactivo en el sidebar
→ Abre Ollama desde el menú de inicio o ejecuta ollama serve en otra terminal.

Python was not found
→ Reinstala Python marcando la casilla Add Python to PATH.

El PDF tiene caracteres rotos (■)
→ Asegúrate de tener arial.ttf en C:\Windows\Fonts\ (Windows) o dejavu fonts en Linux.

🔒 Seguridad
✅ Toda la comunicación es 100% local

✅ No se realizan llamadas a APIs externas de pago

✅ Los datos nunca salen de tu máquina

✅ La base de datos se almacena localmente en admin_suite.db

📄 Licencia
Este proyecto está bajo la licencia MIT — puedes usarlo, modificarlo y distribuirlo libremente.
