from PySide6.QtWidgets import QApplication, QMainWindow
from form_ui import Ui_MathRoots
from logic.mathroots_controller import MathRootsController
from logic.graphic import Graphic
from logic.table_styles import TableStyleManager  # Importar el gestor de estilos

class MathRoots(QMainWindow):
    """Ventana principal de MathRoots"""
    def __init__(self):
        super().__init__()
        self.ui = Ui_MathRoots()
        self.ui.setupUi(self)

        # Inicializa el controlador y le pasa la UI
        self.controller = MathRootsController(self.ui)
        self.graphics = Graphic(self.ui)    ## pretendo usarlo para crear la grafica dentro de mis elementos ya creados

        # Ajustes iniciales
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.HomeStackedWidgets.setCurrentIndex(0)
        
        # --- Aplica el estilo minimalista a las tablas ---
        self.apply_table_styles()

    def apply_table_styles(self):
        """
        Aplica los estilos minimalistas a todas las tablas de la aplicación
        """
        # Opción 1: Aplicar automáticamente a tablas comunes
        TableStyleManager.apply_to_ui(self.ui)
        
        # Opción 2: Aplicar a tablas específicas (descomenta si necesitas control específico)
        # table_names = ['tabla_iteraciones', 'tabla_resultados', 'tabla_historial']
        # TableStyleManager.apply_to_multiple_tables(self.ui, table_names)
        
        # Opción 3: Aplicar a una tabla específica (descomenta si necesitas una sola)
        # TableStyleManager.apply_minimal_style_to_table(self.ui.tabla_iteraciones)

def main():
    app = QApplication([])
    
    # Opcional: Aplicar qt-material a toda la aplicación excepto las tablas
    # import qt_material
    # qt_material.apply_stylesheet(app, theme='light_red.xml')
    
    window = MathRoots()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()