"""
Widget de historial para mostrar ecuaciones resueltas previamente
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QScrollArea, QFrame, QMessageBox)
from PySide6.QtCore import Qt, Signal, QDateTime
from PySide6.QtGui import QFont
import json
import os


class HistoryItemWidget(QFrame):
    """Widget individual para cada entrada del historial"""
    
    load_clicked = Signal(dict)  
    delete_clicked = Signal(int)  
    
    def __init__(self, history_data: dict, index: int, parent=None):
        super().__init__(parent)
        self.history_data = history_data
        self.index = index
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz del item"""
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            HistoryItemWidget {
                background-color: #FFFFFF;
                border: 2px solid #E0E0E0;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }
            HistoryItemWidget:hover {
                border: 2px solid #CD1C18;
                background-color: #FFF5F5;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Fecha y hora
        datetime_label = QLabel(self.history_data.get('datetime', 'Fecha desconocida'))
        datetime_label.setStyleSheet("color: #666666; font-size: 14px;")
        layout.addWidget(datetime_label)
        
        # Ecuación
        equation_label = QLabel(f"<b>Ecuación:</b> {self.history_data.get('equation', 'N/A')}")
        equation_label.setWordWrap(True)
        equation_label.setStyleSheet("font-size: 20px; color: #333333;")
        layout.addWidget(equation_label)
        
        # Método usado
        method_label = QLabel(f"<b>Método:</b> {self.history_data.get('method', 'N/A')}")
        method_label.setStyleSheet("font-size: 18px; color: #555555;")
        layout.addWidget(method_label)
        
        # Resultados (raíces encontradas)
        roots = self.history_data.get('roots', [])
        if roots:
            roots_text = ", ".join([f"{root:.6f}" for root in roots[:3]])  # Mostrar máximo 3
            if len(roots) > 3:
                roots_text += f" (+{len(roots)-3} más)"
            roots_label = QLabel(f"<b>Raíces:</b> {roots_text}")
            roots_label.setStyleSheet("font-size: 18px; color: #555555;")
            layout.addWidget(roots_label)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        load_btn = QPushButton("Cargar")
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #CD1C18;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #a81614;
            }
        """)
        load_btn.clicked.connect(lambda: self.load_clicked.emit(self.history_data))
        
        delete_btn = QPushButton("Eliminar")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5F5F5;
                color: #333333;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.index))
        
        buttons_layout.addWidget(load_btn)
        buttons_layout.addWidget(delete_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)


class HistoryWidget(QWidget):
    """Widget principal para mostrar el historial de ecuaciones"""
    
    equation_loaded = Signal(dict)  # Señal cuando se carga una ecuación del historial
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history_file = "mathroots_history.json"
        self.history_data = []
        self.setup_ui()
        self.load_history()
        
    def setup_ui(self):
        """Configura la interfaz del widget"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        title_label = QLabel("Historial:")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #CD1C18;")
        main_layout.addWidget(title_label)
        
        # Botones de acción superiores
        top_buttons_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Actualizar")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5F5F5;
                color: #333333;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_history)
        
        clear_all_btn = QPushButton("Limpiar Todo")
        clear_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5F5F5;
                color: #D32F2F;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #FFEBEE;
            }
        """)
        clear_all_btn.clicked.connect(self.clear_all_history)
        
        top_buttons_layout.addWidget(refresh_btn)
        top_buttons_layout.addWidget(clear_all_btn)
        top_buttons_layout.addStretch()
        
        main_layout.addLayout(top_buttons_layout)
        
        # Área de scroll para los items del historial
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #F9F9F9;
            }
            QScrollBar:vertical {
                border: none;
                background: #F0F0F0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #CD1C18;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a81614;
            }
        """)
        
        # Contenedor para los items
        self.history_container = QWidget()
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setAlignment(Qt.AlignTop)
        self.history_layout.setSpacing(10)
        
        scroll_area.setWidget(self.history_container)
        main_layout.addWidget(scroll_area)
        
    def load_history(self):
        """Carga el historial desde el archivo JSON"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history_data = json.load(f)
            else:
                self.history_data = []
            
            self.populate_history()
            
        except Exception as e:
            print(f"Error al cargar historial: {e}")
            self.history_data = []
            self.show_empty_message()
    
    def save_history(self):
        """Guarda el historial en el archivo JSON"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error al guardar historial: {e}")
    
    def add_history_entry(self, equation: str, method: str, roots: list, 
                         iterations: int, settings: dict):
        """
        Añade una nueva entrada al historial
        
        Args:
            equation: Ecuación resuelta
            method: Método utilizado
            roots: Lista de raíces encontradas
            iterations: Número de iteraciones
            settings: Configuración utilizada
        """
        entry = {
            'datetime': QDateTime.currentDateTime().toString("dd/MM/yyyy hh:mm:ss"),
            'equation': equation,
            'method': method,
            'roots': roots,
            'total_iterations': iterations,
            'settings': settings
        }
        
        # Añadir al inicio de la lista (más reciente primero)
        self.history_data.insert(0, entry)
        
        # Limitar a 50 entradas
        if len(self.history_data) > 50:
            self.history_data = self.history_data[:50]
        
        self.save_history()
        self.populate_history()
    
    def populate_history(self):
        """Llena el widget con los items del historial"""
        # Limpiar items existentes
        while self.history_layout.count():
            item = self.history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.history_data:
            self.show_empty_message()
            return
        
        # Añadir items del historial
        for index, history_item in enumerate(self.history_data):
            item_widget = HistoryItemWidget(history_item, index)
            item_widget.load_clicked.connect(self._on_load_clicked)
            item_widget.delete_clicked.connect(self._on_delete_clicked)
            self.history_layout.addWidget(item_widget)
    
    def show_empty_message(self):
        """Muestra mensaje cuando no hay historial"""
        empty_label = QLabel("📝 No hay ecuaciones en el historial.\n\n"
                           "Resuelve algunas ecuaciones y aparecerán aquí.")
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setStyleSheet("""
            color: #999999;
            font-size: 17px;
            padding: 50px;
        """)
        self.history_layout.addWidget(empty_label)
    
    def _on_load_clicked(self, history_data: dict):
        """Maneja el clic en cargar una ecuación"""
        self.equation_loaded.emit(history_data)
        print(f"Cargando ecuación del historial: {history_data.get('equation')}")
    
    def _on_delete_clicked(self, index: int):
        """Maneja el clic en eliminar una entrada"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Estás seguro de que deseas eliminar esta entrada del historial?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if 0 <= index < len(self.history_data):
                del self.history_data[index]
                self.save_history()
                self.populate_history()
                print(f"Entrada {index} eliminada del historial")
    
    def refresh_history(self):
        """Recarga el historial desde el archivo"""
        self.load_history()
        print("Historial actualizado")
    
    def clear_all_history(self):
        """Limpia todo el historial sin confirmación"""
        self.history_data = []
        self.save_history()
        self.populate_history()
        print("Historial completamente limpiado")