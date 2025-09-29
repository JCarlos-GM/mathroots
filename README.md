Métodos Numéricos 

Repositorio de Métodos Numéricos que contiene scripts, algoritmos y proyectos enfocados en la resolución de problemas matemáticos, ingeniería y análisis de ecuaciones mediante OCR y herramientas de visualización interactiva. Incluye implementaciones en Python con aplicaciones gráficas, reconocimiento de texto y voz, así como proyectos para explorar y experimentar con métodos numéricos y ecuaciones matemáticas.

🔹 Contenido del Repositorio
Python

Scripts y funciones para métodos numéricos clásicos, incluyendo:

Resolución de ecuaciones no lineales

Sistemas de ecuaciones lineales

Interpolación y aproximación

Integración y derivación numérica

Métodos iterativos y de optimización

Métodos para ecuaciones diferenciales ordinarias (EDO)

Proyectos con interfaz / visualización

Aplicaciones gráficas para explorar métodos numéricos y ecuaciones

Gráficas interactivas para analizar convergencia, error y comportamiento de los algoritmos

OCR especializado en ecuaciones matemáticas para extraer expresiones desde imágenes

Funcionalidad de reconocimiento de voz para entrada de ecuaciones o comandos

⚙️ Tecnologías y Librerías Utilizadas
GUI y manejo de imágenes

PySide6 – Framework para interfaz gráfica

Qt Material – Temas y estilos modernos

Pillow (PIL) – Abrir y manipular imágenes

OCR (Reconocimiento de texto)

pix2tex – OCR especializado en ecuaciones matemáticas

pytesseract – OCR general como alternativa

Reconocimiento de voz

SpeechRecognition – Reconocimiento de voz

PyAudio – Captura de audio desde micrófono

Otras librerías útiles

pyqtgraph / PyQt6 / numpy – Visualización interactiva y cálculos

lxml – Procesamiento de XML y documentos

pillow – Exportación de imágenes PNG con mejor calidad

📦 Instalación y Entorno Virtual

Se recomienda crear un entorno virtual para mantener las dependencias aisladas:

python -m venv env


Activar el entorno virtual:

UNIX / Linux / macOS

source env/bin/activate


Windows

env\Scripts\activate


Instalar todas las dependencias:

pip install PySide6 qt-material Pillow
pip install pix2tex pytesseract
pip install SpeechRecognition PyAudio
pip install pyqtgraph PyQt6 numpy
pip install lxml


Nota: Algunas librerías, como PyAudio, pueden requerir compiladores adicionales en Windows.

🚀 Ejecución de la Aplicación

Una vez instaladas todas las dependencias, se puede ejecutar cualquier script principal de Python directamente:

python main.py


Para compilar un ejecutable standalone (opcional), se puede usar PyInstaller:

pyinstaller --onefile --windowed --name="SolverOne" main.py
