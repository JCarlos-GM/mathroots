from PySide6.QtWidgets import QApplication, QMainWindow
from form_ui import Ui_MathRoots
from logic.mathroots_controller import MathRootsController
from logic.graphic import Graphic
from logic.table_styles import TableStyleManager  

class MathRoots(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MathRoots()
        self.ui.setupUi(self)

        # Inicializa las clases de control, metodos y utilidades
        self.controller = MathRootsController(self.ui)
        self.graphics = Graphic(self.ui)   

        # Ajustes iniciales de las ventanas
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.HomeStackedWidgets.setCurrentIndex(0)

        self.controller.set_graphics(self.graphics)
        
        self.apply_table_styles()

    def apply_table_styles(self):
        TableStyleManager.apply_to_ui(self.ui)

def main():
    app = QApplication([])
    window = MathRoots()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()