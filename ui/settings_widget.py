from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QCheckBox, QPushButton,
                               QGroupBox, QFormLayout, QLineEdit, QScrollArea)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QDoubleValidator, QIntValidator

class SettingsWidget(QWidget):
    """
    Widget de configuración para ajustar parámetros de resolución.
    Versión no modal que se integra en el stackedWidget.
    """
    
    # Señal que se emite cuando se guardan las configuraciones
    settings_saved = Signal(dict)
    
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        
        # Configuraciones por defecto
        self.default_settings = {
            'method': 'biseccion',
            'tolerance': 1e-6,
            'max_iterations': 100,
            'auto_interval': True,
            'interval_start': -100,
            'interval_end': 100,
            'interval_step': 0.1,
        }
        
        # Usar configuraciones actuales o las por defecto
        self.settings = current_settings if current_settings else self.default_settings.copy()
        
        self._setup_ui()
        self._load_settings()
        self._connect_signals()
        self._apply_styles()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario con un QScrollArea."""
        
        # Layout principal del widget
        main_layout = QVBoxLayout(self)
        
        # Crear un QScrollArea que contendrá todo el contenido desplazable
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Crear un widget interno para contener todo el contenido de la UI
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título del widget
        title_label = QLabel("Configuraciones de resolución")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18pt; 
                font-weight: bold;
                color: #CD1C18;
                padding: 1px;
            }
        """)
        content_layout.addWidget(title_label)
        
        # Grupo: Método de resolución
        method_group = QGroupBox("Método de resolución")
        method_layout = QFormLayout()
        
        self.method_combo = QComboBox()
        self.method_combo.addItem("Bisección", "biseccion")
        self.method_combo.addItem("Newton-Raphson", "newton")
        method_layout.addRow("Método:", self.method_combo)
        
        method_group.setLayout(method_layout)
        content_layout.addWidget(method_group)
        
        # Grupo: Parámetros de convergencia
        convergence_group = QGroupBox("Parámetros de Convergencia")
        convergence_layout = QFormLayout()
        
        self.tolerance_input = QLineEdit()
        tolerance_validator = QDoubleValidator(1e-12, 1.0, 10, self.tolerance_input)
        tolerance_validator.setNotation(QDoubleValidator.ScientificNotation)
        self.tolerance_input.setValidator(tolerance_validator)
        convergence_layout.addRow("Tolerancia (Error):", self.tolerance_input)
        
        self.max_iter_input = QLineEdit()
        self.max_iter_input.setValidator(QIntValidator(1, 1000, self.max_iter_input))
        convergence_layout.addRow("Máx. Iteraciones:", self.max_iter_input)
        
        convergence_group.setLayout(convergence_layout)
        content_layout.addWidget(convergence_group)
        
        # Grupo: Intervalo de búsqueda
        interval_group = QGroupBox()
        interval_layout_main = QVBoxLayout(interval_group)

        interval_title_layout = QHBoxLayout()
        interval_title_label = QLabel("Intervalo de Búsqueda")
        interval_title_label.setStyleSheet("font-weight: bold; font-size: 18pt; color: #CD1C18;") 
        interval_title_layout.addWidget(interval_title_label)
        
        self.auto_interval_check = QCheckBox()
        self.auto_interval_check.setChecked(True)
        self.auto_interval_check.setText("Automático")
        self.auto_interval_check.setFixedSize(QSize(80, 25))
        interval_title_layout.addStretch()
        interval_title_layout.addWidget(self.auto_interval_check)

        interval_layout_main.addLayout(interval_title_layout)

        self.manual_interval_widget = QGroupBox("Intervalo Personalizado")
        manual_layout = QFormLayout()
        
        self.interval_start_input = QLineEdit()
        self.interval_start_input.setValidator(QDoubleValidator(-10000, 10000, 2))
        manual_layout.addRow("Inicio:", self.interval_start_input)
        
        self.interval_end_input = QLineEdit()
        self.interval_end_input.setValidator(QDoubleValidator(-10000, 10000, 2))
        manual_layout.addRow("Fin:", self.interval_end_input)

        self.interval_step_input = QLineEdit()
        self.interval_step_input.setValidator(QDoubleValidator(0.01, 10, 2))
        manual_layout.addRow("Paso:", self.interval_step_input)
        
        self.manual_interval_widget.setLayout(manual_layout)
        self.manual_interval_widget.setEnabled(False)
        interval_layout_main.addWidget(self.manual_interval_widget)
        
        content_layout.addWidget(interval_group)
        
        # Agregar espacio flexible para empujar los botones hacia abajo
        content_layout.addStretch()
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.restore_button = QPushButton("Restaurar por Defecto")
        self.restore_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12pt; /* Aumentado 1pt */
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        self.save_button = QPushButton("Guardar Configuraciones")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #CD1C18;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12pt; /* Aumentado 1pt */
            }
            QPushButton:hover {
                background-color: #a81614;
            }
        """)
        
        buttons_layout.addWidget(self.restore_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        
        # Añadir el widget de contenido al QScrollArea
        self.scroll_area.setWidget(content_widget)
        
        # Añadir el QScrollArea y el layout de botones al layout principal
        main_layout.addWidget(self.scroll_area)
        main_layout.addLayout(buttons_layout)
    
    def _connect_signals(self):
        """Conecta las señales de los widgets"""
        self.auto_interval_check.toggled.connect(self._on_auto_interval_toggled)
        self.save_button.clicked.connect(self._on_save)
        self.restore_button.clicked.connect(self._restore_defaults)
        
    def _on_auto_interval_toggled(self, checked):
        """Habilita/deshabilita el intervalo manual y establece el foco."""
        self.manual_interval_widget.setEnabled(not checked)
        if not checked:
            self.auto_interval_check.setText("Manual")
            self.interval_start_input.setFocus()
        else:
            self.auto_interval_check.setText("Automático")
    
    def _load_settings(self):
        """Carga las configuraciones actuales en la interfaz"""
        index = self.method_combo.findData(self.settings['method'])
        if index >= 0:
            self.method_combo.setCurrentIndex(index)
        
        self.tolerance_input.setText(str(self.settings['tolerance']))
        self.max_iter_input.setText(str(self.settings['max_iterations']))
        
        self.auto_interval_check.setChecked(self.settings['auto_interval'])
        self.interval_start_input.setText(str(self.settings['interval_start']))
        self.interval_end_input.setText(str(self.settings['interval_end']))
        self.interval_step_input.setText(str(self.settings['interval_step']))
        
        self._on_auto_interval_toggled(self.settings['auto_interval']) 
    
    def _restore_defaults(self):
        """Restaura los valores por defecto"""
        self.settings = self.default_settings.copy()
        self._load_settings()
        print("Configuraciones restauradas a valores por defecto")
    
    def _on_save(self):
        """Guarda las configuraciones"""
        try:
            tolerance_val = float(self.tolerance_input.text())
            max_iter_val = int(self.max_iter_input.text())
            
            if not self.auto_interval_check.isChecked():
                interval_start_val = float(self.interval_start_input.text())
                interval_end_val = float(self.interval_end_input.text())
                interval_step_val = float(self.interval_step_input.text())
            else:
                interval_start_val = self.default_settings['interval_start']
                interval_end_val = self.default_settings['interval_end']
                interval_step_val = self.default_settings['interval_step']
            
            self.settings = {
                'method': self.method_combo.currentData(),
                'tolerance': tolerance_val,
                'max_iterations': max_iter_val,
                'auto_interval': self.auto_interval_check.isChecked(),
                'interval_start': interval_start_val,
                'interval_end': interval_end_val,
                'interval_step': interval_step_val,
            }
            
            self.settings_saved.emit(self.settings)
            
            print("Configuraciones guardadas:")
            print(f"   - Método: {self.settings['method']}")
            print(f"   - Tolerancia: {self.settings['tolerance']}")
            print(f"   - Max Iteraciones: {self.settings['max_iterations']}")
            print(f"   - Intervalo automático: {self.settings['auto_interval']}")
            if not self.settings['auto_interval']:
                print(f"   - Rango: [{self.settings['interval_start']}, {self.settings['interval_end']}]")
                print(f"   - Paso: {self.settings['interval_step']}")
            
        except ValueError:
            print("Error: Por favor, ingrese valores numéricos válidos en los campos de intervalo.")

    def get_settings(self):
        """Retorna las configuraciones actuales"""
        return self.settings.copy()
    
    def update_settings(self, new_settings):
        """Actualiza las configuraciones desde el exterior"""
        self.settings = new_settings.copy()
        self._load_settings()
    
    def _apply_styles(self):
        """Aplica estilos personalizados al widget, incluyendo el scrollbar."""
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
            }
            
            /* Estilo para la barra de desplazamiento vertical */
            QScrollArea {
                border: none;
            }
            
            QScrollArea QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0;
            }
            
            /* Estilo para el "handle" (el pulgar de la barra) */
            QScrollArea QScrollBar::handle:vertical {
                background-color: #CD1C18;
                border-radius: 5px;
                min-height: 20px;
            }

            QScrollArea QScrollBar::handle:vertical:hover {
                background-color: #a81614;
            }

            /* Estilo para los botones de la barra de desplazamiento (flechas) */
            QScrollArea QScrollBar::add-line:vertical,
            QScrollArea QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0;
                width: 0;
            }
            
            /* Estilo para la zona de la barra de desplazamiento antes y después del handle */
            QScrollArea QScrollBar::add-page:vertical,
            QScrollArea QScrollBar::sub-page:vertical {
                background: none;
            }
            
            QGroupBox {
                font-weight: bold;
                border: none;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                font-size: 14pt; 
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                color: #828282;
                font-weight: bold;
                background-color: none;
                font-size: 14pt; 
            }
            
            QLabel {
                color: #333;
                font-size: 13pt; /* Aumentado 1pt */
            }
            
            QComboBox {
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                background-color: white; 
                color: black;
                min-width: 200px;
                font-size: 12pt; /* Aumentado 1pt */
            }
            
            QComboBox QAbstractItemView {
                background-color: white; 
                color: black;
                border: 1px solid #ddd;
                font-size: 12pt; /* Aumentado 1pt */
            }
            
            QComboBox:hover {
                border: 2px solid #CD1C18;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
            
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                background-color: white; 
                color: black;
                min-width: 150px;
                font-size: 12pt; /* Aumentado 1pt */
            }
            
            QLineEdit:hover {
                border: 2px solid #CD1C18;
            }
            
            QLineEdit:focus {
                border: 2px solid #CD1C18;
            }
            
            QCheckBox {
                font-size: 13pt; /* Aumentado 1pt */
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            
            QCheckBox::indicator:hover {
                border: 2px solid #CD1C18;
            }
            
            QCheckBox::indicator:checked {
                background-color: #CD1C18;
                border: 2px solid #CD1C18;
            }
            
            QPushButton {
                font-size: 12pt; /* Aumentado 1pt */
            }
        """)