"""
logic/graphic.py
Clase para manejar gráficas con PyQtGraph en MathRoots
Instalación requerida: pip install pyqtgraph numpy
"""

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QVBoxLayout, QWidget, QMessageBox
from PySide6.QtCore import Qt
import pyqtgraph as pg
import numpy as np


class Graphic(QObject):
    """Controlador para las gráficas de funciones matemáticas"""

    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.plot_widget = None
        self.funciones_graficadas = []
        self.colores = [
            (46, 134, 222),  # Azul
            (231, 76, 60),  # Rojo
            (46, 204, 113),  # Verde
            (155, 89, 182),  # Morado
            (241, 196, 15),  # Amarillo
            (230, 126, 34),  # Naranja
        ]
        self.indice_color = 0

        # Inicializar la gráfica en el contenedor de tu UI
        self.init_plot()

    def init_plot(self):
        """
        Inicializa el PlotWidget de PyQtGraph en tu UI.
        Asume que tienes un QWidget o QFrame en tu UI llamado 'grafica_container'
        o similar donde quieres mostrar la gráfica.

        IMPORTANTE: En Qt Designer, crea un QWidget/QFrame vacío donde quieras
        la gráfica y nómbralo (por ejemplo: 'grafica_container')
        """
        # Buscar el contenedor en tu UI
        # Ajusta el nombre según tu UI (puede ser grafica_container, plot_frame, etc.)
        container = getattr(self.ui, "grafica_container", None)

        if container is None:
            print("No se encontró 'grafica_container' en la UI")
            print("Crea un QWidget en Qt Designer y nómbralo 'grafica_container'")
            return

        # Crear el PlotWidget de PyQtGraph
        self.plot_widget = pg.PlotWidget()

        # Configurar apariencia
        self.configurar_grafica()

        # Crear layout en el contenedor y agregar el plot
        if container.layout() is None:
            layout = QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(layout)
        else:
            layout = container.layout()

        # Limpiar layout si tiene widgets previos
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Agregar el plot widget
        layout.addWidget(self.plot_widget)

        print("Gráfica PyQtGraph inicializada correctamente")

    def configurar_grafica(self):
        """Configura la apariencia inicial de la gráfica"""
        if self.plot_widget is None:
            return

        # Fondo blanco
        self.plot_widget.setBackground("w")

        # Mostrar rejilla
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

        # Etiquetas de ejes
        self.plot_widget.setLabel("left", "y", color="black", size="12pt")
        self.plot_widget.setLabel("bottom", "x", color="black", size="12pt")

        # Título
        self.plot_widget.setTitle("Gráfica de Funciones", color="black", size="14pt")

        # Agregar leyenda
        self.plot_widget.addLegend(offset=(10, 10))

        # Líneas de referencia (ejes X e Y)
        linea_h = pg.InfiniteLine(
            pos=0, angle=0, pen=pg.mkPen("k", width=1, style=Qt.PenStyle.DashLine)
        )
        linea_v = pg.InfiniteLine(
            pos=0, angle=90, pen=pg.mkPen("k", width=1, style=Qt.PenStyle.DashLine)
        )
        self.plot_widget.addItem(linea_h)
        self.plot_widget.addItem(linea_v)

        # Habilitar antialiasing para líneas suaves
        pg.setConfigOptions(antialias=True)

    def parsear_funcion(self, expresion):
        """
        Convierte una expresión matemática en texto a una función evaluable.

        Args:
            expresion (str): Expresión matemática como texto (ej: "x**2 - 3*x + 2")

        Returns:
            function: Función lambda evaluable

        Raises:
            ValueError: Si la expresión no es válida
        """
        # Reemplazar ^ por ** para potencias
        expresion = expresion.replace("^", "**")

        # Funciones matemáticas permitidas (seguras)
        funciones_permitidas = {
            "sin": np.sin,
            "cos": np.cos,
            "tan": np.tan,
            "exp": np.exp,
            "log": np.log,
            "ln": np.log,
            "sqrt": np.sqrt,
            "abs": np.abs,
            "arcsin": np.arcsin,
            "arccos": np.arccos,
            "arctan": np.arctan,
            "sinh": np.sinh,
            "cosh": np.cosh,
            "tanh": np.tanh,
            "pi": np.pi,
            "e": np.e,
        }

        try:
            # Crear función lambda segura
            func = lambda x: eval(
                expresion, {"__builtins__": {}}, {**funciones_permitidas, "x": x}
            )
            return func
        except Exception as e:
            raise ValueError(f"Error al parsear la función: {str(e)}")

    def graficar_funcion(self, expresion, x_min=-10, x_max=10, limpiar=False):
        """
        Grafica una función matemática.
        
        Args:
            expresion (str): Expresión matemática (ej: "x**2", "sin(x)")
            x_min (float): Valor mínimo de x
            x_max (float): Valor máximo de x
            limpiar (bool): Si True, limpia las gráficas anteriores
        
        Returns:
            bool: True si se graficó correctamente, False en caso contrario
        """
        if self.plot_widget is None:
            QMessageBox.warning(
                None, 
                "Error", 
                "La gráfica no está inicializada. Verifica que 'grafica_container' exista en tu UI."
            )
            return False
        
        try:
            # Limpiar si es necesario
            if limpiar:
                self.limpiar_grafica()
            
            # Parsear la función
            func = self.parsear_funcion(expresion)
            
            # Generar datos
            # Aumentamos el número de puntos a 10000 para una mejor resolución
            x = np.linspace(x_min, x_max, 10000)
            
            # Manejar posibles errores en la evaluación
            try:
                y = func(x)
            except:
                # Si falla con array, intentar elemento por elemento
                y = np.array([func(xi) if not np.isnan(func(xi)) else np.nan for xi in x])
            
            # Verificar valores válidos
            if np.all(np.isnan(y)) or np.all(np.isinf(y)):
                QMessageBox.warning(
                    None, 
                    "Error", 
                    "La función produce valores inválidos en el rango especificado"
                )
                return False
            
            # Obtener color
            color = self.colores[self.indice_color % len(self.colores)]
            pen = pg.mkPen(color=color, width=2)
            
            # Graficar
            curva = self.plot_widget.plot(x, y, pen=pen, name=expresion)
            
            # Guardar referencia
            self.funciones_graficadas.append({
                'expresion': expresion,
                'curva': curva,
                'color': color
            })
            
            # Incrementar índice de color
            self.indice_color += 1
            
            print(f"Función graficada: {expresion}")
            return True
            
        except ValueError as e:
            QMessageBox.critical(None, "Error de Expresión", str(e))
            return False
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error al graficar: {str(e)}")
            return False
    

    def limpiar_grafica(self):
        """Limpia todas las gráficas y reinicia la configuración"""
        if self.plot_widget is None:
            return

        self.plot_widget.clear()
        self.funciones_graficadas = []
        self.indice_color = 0
        self.configurar_grafica()
        print("Gráfica limpiada")

    def eliminar_funcion(self, indice):
        """
        Elimina una función específica de la gráfica.

        Args:
            indice (int): Índice de la función a eliminar
        """
        if (
            self.plot_widget is None
            or indice < 0
            or indice >= len(self.funciones_graficadas)
        ):
            return

        # Eliminar de la gráfica
        self.plot_widget.removeItem(self.funciones_graficadas[indice]["curva"])

        # Eliminar de la lista
        self.funciones_graficadas.pop(indice)

    def exportar_imagen(self, ruta=None):
        """
        Exporta la gráfica como imagen PNG.

        Args:
            ruta (str): Ruta donde guardar la imagen. Si es None, abre diálogo.

        Returns:
            bool: True si se exportó correctamente
        """
        if self.plot_widget is None:
            return False

        try:
            if ruta is None:
                from PySide6.QtWidgets import QFileDialog

                ruta, _ = QFileDialog.getSaveFileName(
                    None,
                    "Guardar gráfica",
                    "grafica.png",
                    "PNG (*.png);;SVG (*.svg);;Todos los archivos (*.*)",
                )

            if ruta:
                exporter = pg.exporters.ImageExporter(self.plot_widget.plotItem)
                exporter.parameters()["width"] = 1920
                exporter.export(ruta)
                print(f"Gráfica exportada: {ruta}")
                return True

            return False

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error al exportar: {str(e)}")
            return False

    def set_rango(self, x_min, x_max, y_min=None, y_max=None):
        """
        Establece el rango visible de la gráfica.

        Args:
            x_min (float): Valor mínimo de x
            x_max (float): Valor máximo de x
            y_min (float, optional): Valor mínimo de y
            y_max (float, optional): Valor máximo de y
        """
        if self.plot_widget is None:
            return

        self.plot_widget.setXRange(x_min, x_max, padding=0)

        if y_min is not None and y_max is not None:
            self.plot_widget.setYRange(y_min, y_max, padding=0)

    def auto_rango(self):
        """Ajusta automáticamente el rango de la gráfica"""
        if self.plot_widget is None:
            return

        self.plot_widget.autoRange()

    def get_funciones_graficadas(self):
        """
        Retorna la lista de funciones actualmente graficadas.

        Returns:
            list: Lista de diccionarios con información de las funciones
        """
        return [
            {"expresion": f["expresion"], "color": f["color"]}
            for f in self.funciones_graficadas
        ]
