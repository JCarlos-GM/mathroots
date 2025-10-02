from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt
import sys
from form_ui import Ui_MathRoots
from logic.mathroots_controller import MathRootsController
from logic.graphic import Graphic
from logic.table_styles import TableStyleManager


class MathRoots(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MathRoots()
        self.ui.setupUi(self)
        self.controller = MathRootsController(self.ui, self) 

        # Pasa 'self' (la instancia de la ventana MathRoots) al controlador
        self.controller = MathRootsController(self.ui, self) 
        self.graphics = Graphic(self.ui)

        # Ajustes iniciales de las ventanas
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.HomeStackedWidgets.setCurrentIndex(0)

        # Conecta el controller con graphics
        self.controller.set_graphics(self.graphics)
        
        # Aplica estilos a las tablas
        self.apply_table_styles()
        
        print("MathRoots iniciado correctamente")
        print("Widget de configuraciones integrado en el stackedWidget 'resultados'")

    def apply_table_styles(self):
        """Aplica estilos personalizados a las tablas de la interfaz"""
        TableStyleManager.apply_to_ui(self.ui)

    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana"""
        print("Cerrando aplicación...")
        # Limpiar recursos del controller (workers de OCR y voz)
        self.controller.cleanup()
        event.accept()


def main():
    """Función principal que ejecuta la aplicación"""
    app = QApplication(sys.argv)
    
    # Configuración opcional de la aplicación
    app.setApplicationName("MathRoots")
    app.setOrganizationName("MathRoots")
    app.setApplicationVersion("1.0.0")
    
    # Crear y mostrar la ventana principal
    window = MathRoots()
    window.show()
    
    # Ejecutar el loop de eventos
    sys.exit(app.exec())


if __name__ == "__main__":
    main()