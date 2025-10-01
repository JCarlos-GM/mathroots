from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QCheckBox, QPushButton,
                               QGroupBox, QFormLayout, QFrame, QLineEdit)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDoubleValidator, QIntValidator

class SettingsDialog(QDialog):
    """
    Ventana de configuración para ajustar parámetros de resolución.
    """
    
    # Señal que se emite cuando se guardan las configuraciones
    settings_saved = Signal(dict)
    
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self._apply_styles()
        
        # Configuraciones por defecto
        self.default_settings = {
            'method': 'biseccion',  # 'biseccion' o 'newton'
            'tolerance': 1e-6,
            'max_iterations': 100,
            'auto_interval': True,
            'interval_start': -100,
            'interval_end': 100,
            'interval_step': 0.1,
        }
        
        # Usar configuraciones actuales o las por defecto
        self.settings = current_settings if current_settings else self.default_settings.copy()
        
        self.setWindowTitle("Configuraciones de Resolución")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        self._setup_ui()
        self._load_settings()
        self._connect_signals()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Grupo: Método de resolución
        method_group = QGroupBox("Método de Resolución")
        method_layout = QFormLayout()
        
        self.method_combo = QComboBox()
        self.method_combo.addItem("Bisección", "biseccion")
        self.method_combo.addItem("Newton-Raphson", "newton")
        method_layout.addRow("Método:", self.method_combo)
        
        method_group.setLayout(method_layout)
        layout.addWidget(method_group)
        
        # Grupo: Parámetros de convergencia
        convergence_group = QGroupBox("Parámetros de Convergencia")
        convergence_layout = QFormLayout()
        
        # QLineEdit para la tolerancia con validador QDoubleValidator
        self.tolerance_input = QLineEdit()
        tolerance_validator = QDoubleValidator(1e-12, 1.0, 10, self.tolerance_input)
        tolerance_validator.setNotation(QDoubleValidator.ScientificNotation)
        self.tolerance_input.setValidator(tolerance_validator)
        convergence_layout.addRow("Tolerancia (Error):", self.tolerance_input)
        
        # QLineEdit para las iteraciones con validador QIntValidator
        self.max_iter_input = QLineEdit()
        self.max_iter_input.setValidator(QIntValidator(1, 100, self.max_iter_input))
        convergence_layout.addRow("Máx. Iteraciones:", self.max_iter_input)
        
        convergence_group.setLayout(convergence_layout)
        layout.addWidget(convergence_group)
        
        # Grupo: Intervalo de búsqueda
        interval_group = QGroupBox("Intervalo de Búsqueda")
        interval_layout = QVBoxLayout()
        
        # Checkbox para automático
        self.auto_interval_check = QCheckBox("Búsqueda automática de intervalo")
        self.auto_interval_check.setChecked(True)
        interval_layout.addWidget(self.auto_interval_check)
        
        # Formulario para intervalo manual
        self.manual_interval_widget = QGroupBox("Intervalo Personalizado")
        manual_layout = QFormLayout()
        
        # Usar QLineEdit con validador para el inicio del intervalo
        self.interval_start_input = QLineEdit()
        self.interval_start_input.setValidator(QDoubleValidator(-10000, 10000, 2))
        manual_layout.addRow("Inicio:", self.interval_start_input)
        
        # Usar QLineEdit con validador para el fin del intervalo
        self.interval_end_input = QLineEdit()
        self.interval_end_input.setValidator(QDoubleValidator(-10000, 10000, 2))
        manual_layout.addRow("Fin:", self.interval_end_input)

        # Usar QLineEdit con validador para el paso
        self.interval_step_input = QLineEdit()
        self.interval_step_input.setValidator(QDoubleValidator(0.01, 10, 2))
        manual_layout.addRow("Paso:", self.interval_step_input)
        
        self.manual_interval_widget.setLayout(manual_layout)
        self.manual_interval_widget.setEnabled(False)
        interval_layout.addWidget(self.manual_interval_widget)
        
        interval_group.setLayout(interval_layout)
        layout.addWidget(interval_group)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.restore_button = QPushButton("Restaurar por Defecto")
        self.restore_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 11pt; /* Aumentado */
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 11pt; /* Aumentado */
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        self.save_button = QPushButton("Guardar")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #CD1C18;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 11pt; /* Aumentado */
            }
            QPushButton:hover {
                background-color: #a81614;
            }
        """)
        
        buttons_layout.addWidget(self.restore_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)
        
        layout.addLayout(buttons_layout)
    
    def _connect_signals(self):
        """Conecta las señales de los widgets"""
        self.auto_interval_check.toggled.connect(self._on_auto_interval_toggled)
        self.save_button.clicked.connect(self._on_save)
        self.cancel_button.clicked.connect(self.reject)
        self.restore_button.clicked.connect(self._restore_defaults)
        
    def _on_auto_interval_toggled(self, checked):
        """Habilita/deshabilita el intervalo manual y establece el foco."""
        self.manual_interval_widget.setEnabled(not checked)
        if not checked:
            self.interval_start_input.setFocus()
    
    def _load_settings(self):
        """Carga las configuraciones actuales en la interfaz"""
        # Método
        index = self.method_combo.findData(self.settings['method'])
        if index >= 0:
            self.method_combo.setCurrentIndex(index)
        
        # Convergencia (usando QLineEdit)
        self.tolerance_input.setText(str(self.settings['tolerance']))
        self.max_iter_input.setText(str(self.settings['max_iterations']))
        
        # Intervalo
        self.auto_interval_check.setChecked(self.settings['auto_interval'])
        self.interval_start_input.setText(str(self.settings['interval_start']))
        self.interval_end_input.setText(str(self.settings['interval_end']))
        self.interval_step_input.setText(str(self.settings['interval_step']))
        
        self._on_auto_interval_toggled(self.settings['auto_interval'])
    
    def _restore_defaults(self):
        """Restaura los valores por defecto"""
        self.settings = self.default_settings.copy()
        self._load_settings()
    
    def _on_save(self):
        """Guarda las configuraciones y cierra el diálogo"""
        try:
            # Capturar valores de QLineEdit y convertirlos
            tolerance_val = float(self.tolerance_input.text())
            max_iter_val = int(self.max_iter_input.text())
            interval_start_val = float(self.interval_start_input.text())
            interval_end_val = float(self.interval_end_input.text())
            interval_step_val = float(self.interval_step_input.text())

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
            
            self.accept()
        except ValueError:
            print("Error: Por favor, ingrese valores numéricos válidos en los campos de intervalo.")

    def get_settings(self):
        """Retorna las configuraciones actuales"""
        return self.settings.copy()
    
    def _apply_styles(self):
        """Aplica estilos personalizados a la ventana"""
        self.setStyleSheet("""
            QDialog {
                background-color: #F1F1F1;
            }
            
            QGroupBox {
                font-weight: bold;
                border: none;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                color: #CD1C18;
                background-color: none;
                font-size: 13pt; /* Aumentado */
            }
            
            QLabel {
                color: #333;
                font-size: 12pt; /* Aumentado */
            }
            
            QComboBox {
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                background-color: white; 
                color: black;            
                min-width: 200px;
                font-size: 11pt; /* Aumentado */
            }
                                        
            QComboBox QAbstractItemView {
                background-color: white; 
                color: black;            
                border: 1px solid #ddd;  
                font-size: 11pt; /* Aumentado */
            }
            
            QComboBox:hover {
                border: 2px solid #CD1C18;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            
            QComboBox::down-arrow {
                image: url(down_arrow.png);
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
                font-size: 11pt; /* Aumentado */
            }
            
            QLineEdit:hover {
                border: 2px solid #CD1C18;
            }
            
            QLineEdit:focus {
                border: 2px solid #CD1C18;
            }
            
            QCheckBox {
                font-size: 12pt; /* Aumentado */
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
                image: url(check.png);
            }
            
            QPushButton {
                font-size: 12pt; /* Aumentado */
            }
        """)