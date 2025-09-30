# MathRoots - Proyecto para metodos numericos

"MathRoots" es una aplicación diseñada para encontrar las raíces de ecuaciones. En lugar de hacer los cálculos a mano, el programa te permite resolver estos problemas complejos de manera eficiente y visual.

---

## Características Principales

- **Python**: 
    - Métodos Numéricos: Utiliza los métodos de bisección y Newton-Raphson para una resolución precisa y eficiente.

    - Visualización de Gráficas: Genera una gráfica de la función para mostrar visualmente las raíces.

    - Tabla de Iteraciones: Presenta una tabla detallada de cada paso del cálculo para seguir el proceso de forma transparente.

    - Entrada Inteligente: Permite al usuario ingresar ecuaciones a través de reconocimiento de imágenes o comandos de voz.
 

---

## Tecnologías utilizadas

Desarrollado en Python e integra varias librerías y frameworks clave para manejar la interfaz de usuario, el procesamiento de imágenes, el reconocimiento de voz y la visualización de datos.

- **PySide6 & qt-material**: Para la interfaz gráfica de usuario (GUI).

- **Pillow**: Para el procesamiento de imágenes.

- **pix2tex & pytesseract**: Para el reconocimiento de texto y ecuaciones (OCR).

- **SpeechRecognition & PyAudio**: Para la función de reconocimiento de voz.

- **pyqtgraph**: Para la visualización y graficación de datos.

---

# Sobre el entorno vitual
Es necesario crear un entorno virtual de la siguiente forma:
``` sh
python -m venv <nombre-del-entorno>
```
por ejemplo:
``` sh
python -m venv env
```

# Instalación de librerías y framworks

**Librerías para GUI y manejo de imágenes:**

- **PySide6**: Framework para la interfaz gráfica

``` sh
pip install PySide6 
```

- **Qt materia**: Temas y personalización
``` sh
pip install qt-material
```

- **Pillow (PIL)**: Abrir y manipular impagenes
``` sh
pip install Pillow
```

**Librerías para GUI y manejo de imágenes:**

- **pix2tex**: OCR especializado en ecuaciones matemáticas

``` sh
pip install pix2tex
```

- **pytesseract**: OCR general (como fallback)

``` sh
pip install pytesseract
```
**Librerías reconocimiento de voz:**

- **SpeechRecognition**: Reconocimiento de voz

``` sh
pip install SpeechRecognition
```

- **PyAudio**: Captura de audio desde micrófono

``` sh
pip install PyAudio
```
**Visualización y Cálculo:**

- **pyqtgraph, PyQt6 y NumPy**:  Para la generación de gráficas de alto rendimiento y dependencias para el funcionamiento.

``` sh
pip install pyqtgraph PyQt6 numpy
pip install pyqtgraph[all] PyQt6 numpy
```

- **Pillow**: Procesamiento y exportación de imágenes.

``` sh
pip install pillow
```

- **lxml**: Para trabajar con archivos XML y HTML.

``` sh
pip install lxml
```
