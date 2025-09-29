from PySide6.QtWidgets import QApplication, QMainWindow
from form_ui import Ui_MathRoots
from logic.mathroots_controller import MathRootsController
from logic.graphic import Graphic
from logic.table_styles import TableStyleManager

class MathRoots(QMainWindow):
    """Ventana principal de MathRoots"""
    def __init__(self):
        super().__init__()
        self.ui = Ui_MathRoots()
        self.ui.setupUi(self)

        # Inicializa el objeto de gráficas
        self.graphics = Graphic(self.ui)
        
        # Inicializa el controlador y le pasa la UI
        self.controller = MathRootsController(self.ui)
        
        # Conectar el graphics con el controller
        self.controller.set_graphics(self.graphics)

        # Ajustes iniciales
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.HomeStackedWidgets.setCurrentIndex(0)
        
        # Aplica el estilo minimalista a las tablas
        self.apply_table_styles()

    def apply_table_styles(self):
        """
        Aplica los estilos minimalistas a todas las tablas de la aplicación
        """
        TableStyleManager.apply_to_ui(self.ui)

def main():
    app = QApplication([])
    
    # Opcional: Aplicar qt-material a toda la aplicación
    # import qt_material
    # qt_material.apply_stylesheet(app, theme='light_red.xml')
    
    window = MathRoots()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()