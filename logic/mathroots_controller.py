from PySide6.QtCore import QObject, Qt, QRect
from PySide6.QtWidgets import (QFileDialog, QAbstractItemView, QTableWidgetItem,
                               QMessageBox, QDialog, QVBoxLayout, QLabel)
from PySide6.QtGui import QPixmap, QColor, QPainter, QPen
import os
import re

from fpdf import FPDF, FPDFException
from fpdf.errors import FPDFUnicodeEncodingException
from .math_methods import MathMethods
from .ocr_worker import OCRWorker
from .voice_worker import VoiceWorker
from ui.voice_indicator import VoiceIndicatorDialogAdvanced
from ui.ui_about_v2 import Ui_Dialog

from fpdf import FPDF
# Asumiendo que custom_pdf.py existe y tiene estas clases
from .custom_pdf import CustomPDF, create_report_cover

class MathRootsController(QObject):
    """Controlador de la ventana principal MathRoots"""
    
    def __init__(self, ui, main_window):
        super().__init__()
        self.ui = ui
        self.ocr_worker = None
        self.main_window = main_window
        self.voice_worker = None
        self.voice_indicator = None
        self.math_methods = MathMethods()
        self.graphics = None
        self.settings_widget = None
        self.history_widget = None
        self.ui.logo_header.setVisible(False)

        self.settings = {
            'method': 'biseccion',
            'tolerance': 1e-6,
            'max_iterations': 100,
            'auto_interval': True,
            'interval_start': -100,
            'interval_end': 100,
            'interval_step': 0.1,
        }

        self.setup_connections()
        self.setup_iterations_table()
        self._apply_result_roots_style()

    # (Métodos anteriores omitidos por brevedad)
    def set_graphics(self, graphics):
        self.graphics = graphics

    def setup_connections(self):
        self.ui.input_image.clicked.connect(self.image_mode)
        self.ui.load_image.clicked.connect(self.load_image)
        self.ui.input_voice.clicked.connect(self.voice_mode)
        self.ui.solve.clicked.connect(self.process_solve)
        self.ui.solve_3.clicked.connect(self.process_solve_keep_panel)
        self.ui.resultado_2.clicked.connect(lambda: self.seleccionar_boton(self.ui.resultado_2))
        self.ui.procedimiento_2.clicked.connect(lambda: self.seleccionar_boton(self.ui.procedimiento_2))
        self.ui.grafica_2.clicked.connect(lambda: self.seleccionar_boton(self.ui.grafica_2))
        self.ui.about.clicked.connect(self.info_window)

        if hasattr(self.ui, 'info'): 
            self.ui.info.clicked.connect(self.show_about_dialog)

        if hasattr(self.ui, 'history'):
            self.ui.history.clicked.connect(self.open_history)

        if hasattr(self.ui, 'save'):
            self.ui.save.clicked.connect(self.save_all_panels)

        if hasattr(self.ui, 'input_image_alt'):
            self.ui.input_image_alt.clicked.connect(self.load_image_direct)

        if hasattr(self.ui, 'settings'):
            self.ui.settings.clicked.connect(self.open_settings)

    def open_settings(self):
        from ui.settings_widget import SettingsWidget
        
        if self.settings_widget is None:
            self.settings_widget = SettingsWidget(current_settings=self.settings)
            self.settings_widget.settings_saved.connect(self._on_settings_saved)
            
            if hasattr(self.ui, 'resultados'):
                self.ui.resultados.addWidget(self.settings_widget)
                self.settings_index = self.ui.resultados.count() - 1
            else:
                print("Error: No se encuentra el stackedWidget 'resultados'")
                return
        else:
            self.settings_widget.update_settings(self.settings)
        
        if hasattr(self.ui, 'resultados'):
            self.ui.resultados.setCurrentWidget(self.settings_widget)
            print("Mostrando widget de configuraciones")

    def _on_settings_saved(self, new_settings):
        self.settings = new_settings.copy()
        print("Configuraciones actualizadas en el controlador")
        self.update_table_headers_for_method()

    def graficar_ecuacion_actual(self):
        if self.graphics is None:
            print("Error: graphics no está inicializado")
            return
            
        try:
            ecuacion_grafica = self.math_methods.get_equation_for_plot()
            
            if ecuacion_grafica:
                self.graphics.graficar_funcion(ecuacion_grafica, x_min=-50, x_max=50, limpiar=True)
                self.graphics.set_rango(x_min=-50, x_max=50, y_min=-50, y_max=50)
                print(f"Ecuación graficada: {ecuacion_grafica}")
        except Exception as e:
            print(f"Error al graficar: {e}")

    def setup_iterations_table(self):
        if hasattr(self.ui, 'tabla_iteraciones'):
            self.ui.tabla_iteraciones.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
            
            if self.settings['method'] == 'biseccion':
                headers = ['Iteración', '      xₗ', '     xᵣ', '     xₘ', '    f(xₗ)', '     f(xᵣ)', '     f(xₘ)', '  Error']
            else:
                headers = ['Iteración', '      xₗ', '     f(xₙ)', "     f'(xₙ)", '   xₙ₊₁', '  Error']
            
            self.ui.tabla_iteraciones.setColumnCount(len(headers))
            self.ui.tabla_iteraciones.setHorizontalHeaderLabels(headers)
            
            self.ui.tabla_iteraciones.setAlternatingRowColors(True)
            self.ui.tabla_iteraciones.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.ui.tabla_iteraciones.horizontalHeader().setStretchLastSection(True)
            
            print(f"Tabla de iteraciones configurada para método: {self.settings['method']}")

    def update_table_headers_for_method(self):
        if not hasattr(self.ui, 'tabla_iteraciones'):
            return
        
        if self.settings['method'] == 'biseccion':
            headers = ['Iteración', '      xₗ', '      xᵣ', '      xₘ', '      f(xₗ)', '      f(xᵣ)', '      f(xₘ)', '   Error']
        else:
            headers = ['Iteración', '      xₙ', '      f(xₙ)', "      f'(xₙ)", '     xₙ₊₁', '  Error']
        
        self.ui.tabla_iteraciones.setColumnCount(len(headers))
        self.ui.tabla_iteraciones.setHorizontalHeaderLabels(headers)
        print(f"Encabezados de tabla actualizados para método: {self.settings['method']}")

    def clear_iterations_table(self):
        if hasattr(self.ui, 'tabla_iteraciones'):
            self.ui.tabla_iteraciones.setRowCount(0)
            self.math_methods.clear_iterations()
            print("Tabla de iteraciones limpiada")

    def info_window(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    def seleccionar_boton(self, boton_seleccionado):
        botones = [self.ui.resultado_2, self.ui.procedimiento_2, self.ui.grafica_2]
        
        estilo_activo = """
            QPushButton {
                background-color: #CD1C18;
                color: white;
                border-radius: 25px;
            }
            QPushButton:hover {
                background-color: #a81614;
            }
        """
        
        estilo_inactivo = """
            QPushButton {
                background-color: #FFFFFF;
                color: black;
                border-radius: 25px;
                border: 2px solid #CD1C18;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """
        
        for boton in botones:
            if boton == boton_seleccionado:
                boton.setStyleSheet(estilo_activo)
            else:
                boton.setStyleSheet(estilo_inactivo)

        if boton_seleccionado == self.ui.resultado_2:
            self.ui.resultados.setCurrentIndex(1)
        elif boton_seleccionado == self.ui.procedimiento_2:
            self.ui.resultados.setCurrentIndex(0)
        elif boton_seleccionado == self.ui.grafica_2:
            self.ui.resultados.setCurrentIndex(2)

    def process_solve_keep_panel(self):
        current_panel_index = self.ui.resultados.currentIndex()
        
        if hasattr(self.ui, 'input_3') and self.ui.input_3.toPlainText().strip():
            input_text = self.ui.input_3.toPlainText().strip()
        else:
            input_text = self.ui.input.toPlainText().strip()
        
        if not input_text:
            print("No hay ecuación para resolver")
            return
        
        self.math_methods.equation = input_text
        
        if hasattr(self.ui, 'input_3'):
            self.ui.input_3.setPlainText(input_text)
        self.ui.input.setPlainText(input_text)
        
        print(f"La ecuación capturada es: {self.math_methods.equation}")
        
        self.display_current_method_info()
        self.update_table_headers_for_method()
        
        validation = self.math_methods.validate_equation()
        if validation['valid']:
            print(f"Ecuación válida: {validation['processed_equation']}")
        else:
            print(f"Ecuación inválida: {validation['error']}")
        
        self.change_main_index(1)
        
        if validation['valid']:
            self.graficar_ecuacion_actual()
            print(f"Ejecutando método: {self.settings['method'].upper()}")
            self.auto_find_and_solve()
            
            self.ui.resultados.setCurrentIndex(current_panel_index)
            self._update_button_styles_for_panel(current_panel_index)
        else:
            print(f"No se puede ejecutar: {validation['error']}")

    def _update_button_styles_for_panel(self, panel_index):
        estilo_activo = """
            QPushButton {
                background-color: #CD1C18;
                color: white;
                border-radius: 25px;
            }
            QPushButton:hover {
                background-color: #a81614;
            }
        """
        
        estilo_inactivo = """
            QPushButton {
                background-color: #FFFFFF;
                color: black;
                border-radius: 25px;
                border: 2px solid #CD1C18;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """
        
        botones_map = {
            0: self.ui.procedimiento_2,
            1: self.ui.resultado_2,
            2: self.ui.grafica_2
        }
        
        for idx, boton in botones_map.items():
            if idx == panel_index:
                boton.setStyleSheet(estilo_activo)
            else:
                boton.setStyleSheet(estilo_inactivo)
        
        print(f"Estilos de botones actualizados para panel índice: {panel_index}")

    def process_solve(self):
        self.ui.logo_header.setVisible(True)
        if hasattr(self.ui, 'input_3') and self.ui.input_3.toPlainText().strip():
            input_text = self.ui.input_3.toPlainText().strip()
        else:
            input_text = self.ui.input.toPlainText().strip()
        
        if not input_text:
            print("No hay ecuación para resolver")
            return
        
        self.math_methods.equation = input_text
        
        if hasattr(self.ui, 'input_3'):
            self.ui.input_3.setPlainText(input_text)
        self.ui.input.setPlainText(input_text)
        
        print(f"La ecuación capturada es: {self.math_methods.equation}")
        
        self.display_current_method_info()
        self.update_table_headers_for_method()
        
        validation = self.math_methods.validate_equation()
        if validation['valid']:
            print(f"Ecuación válida: {validation['processed_equation']}")
        else:
            print(f"Ecuación inválida: {validation['error']}")
        
        self.change_main_index(1)
        
        if validation['valid']:
            self.graficar_ecuacion_actual()
            print(f"Ejecutando método: {self.settings['method'].upper()}")
            self.auto_find_and_solve()
            
            self.ui.resultados.setCurrentIndex(1)
            self._update_button_styles_for_panel(1)
        else:
            print(f"No se puede ejecutar: {validation['error']}")

    def change_main_index(self, index: int):
        self.ui.stackedWidget.setCurrentIndex(index)

    def change_home_index(self, index: int):
        self.ui.HomeStackedWidgets.setCurrentIndex(index)

    def image_mode(self):
        self.ui.HomeStackedWidgets.setCurrentIndex(1)

    def voice_mode(self):
        self.ui.HomeStackedWidgets.setCurrentIndex(2)
        self._start_voice_recognition()

    def load_image_direct(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Selecciona una imagen",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif *.tiff);;Todos los archivos (*.*)"
        )

        if file_path:
            print("\n" + "="*60)
            print("PROCESAMIENTO DIRECTO DE IMAGEN")
            print("="*60)
            print("Archivo seleccionado:", file_path)
            self._start_ocr_processing_direct(file_path)
        else:
            print("No se seleccionó ningún archivo")

    def _start_ocr_processing_direct(self, image_path):
        print(f"Archivo: {os.path.basename(image_path)}")
        print(f"Ruta: {image_path}")
        print("Modo: Procesamiento directo (sin visualización)")
        
        self.ocr_worker = OCRWorker(image_path)
        self.ocr_worker.finished.connect(self._on_ocr_finished_direct)
        self.ocr_worker.error.connect(self._on_ocr_error)
        self.ocr_worker.progress.connect(self._on_ocr_progress)
        self.ocr_worker.start()

    def _on_ocr_finished_direct(self, latex_result, method_used):
        print(f"Motor usado: {method_used}")
        print("-" * 60)
        print("RESULTADO LATEX BRUTO:")
        print("-" * 30)
        print(latex_result)

        processed_result = self._clean_latex_exponents(latex_result)

        print("-" * 30)
        print("RESULTADO PROCESADO:")
        print("-" * 30)
        print(processed_result)

        self.ui.input.setText(processed_result)
        if hasattr(self.ui, 'input_3'):
            self.ui.input_3.setPlainText(processed_result)
        
        print(f"Texto insertado en campos de entrada")
        print("="*60 + "\n")
        
        self._cleanup_worker()

    def voice_mode_direct(self):
        print("\n" + "="*60)
        print("RECONOCIMIENTO DE VOZ DIRECTO")
        print("="*60)
        
        # Crear y mostrar el indicador de voz
        self.voice_indicator = VoiceIndicatorDialogAdvanced(self.main_window)
        self.voice_indicator.show()
        
        self._start_voice_recognition_direct()

    def _start_voice_recognition_direct(self):
        self.voice_worker = VoiceWorker()
        self.voice_worker.finished.connect(self._on_voice_finished_direct)
        self.voice_worker.error.connect(self._on_voice_error_direct)
        self.voice_worker.progress.connect(self._on_voice_progress_direct)
        self.voice_worker.start()

    def _on_voice_progress_direct(self, message):
        print(f"Progreso: {message}")
        
        # Actualizar el indicador de voz si existe
        if hasattr(self, 'voice_indicator') and self.voice_indicator:
            self.voice_indicator.update_status(message)
        
        # Puedes mostrar el progreso en la barra de estado si tienes una
        if hasattr(self.ui, 'status_bar'):
            self.ui.status_bar.showMessage(message)

    def _start_voice_recognition(self):
        print("\n" + "="*60)
        print("INICIANDO RECONOCIMIENTO DE VOZ")
        print("="*60)

        # Crear y mostrar el indicador de voz
        self.voice_indicator = VoiceIndicatorDialogAdvanced(self.main_window)
        self.voice_indicator.show()

        self.voice_worker = VoiceWorker()
        self.voice_worker.finished.connect(self._on_voice_finished)
        self.voice_worker.error.connect(self._on_voice_error)
        self.voice_worker.progress.connect(self._on_voice_progress)
        self.voice_worker.start()

    def _on_voice_progress(self, message):
        print(f"{message}")
        if hasattr(self.ui, 'voice_status_label'):
            self.ui.voice_status_label.setText(message)
        
        # Actualizar el indicador de voz si existe
        if hasattr(self, 'voice_indicator') and self.voice_indicator:
            self.voice_indicator.update_status(message)

    def _on_voice_finished_direct(self, text_result, method_used):
        print(f"Motor usado: {method_used}")
        print("-" * 60)
        print("RESULTADO DE LA TRANSCRIPCIÓN BRUTO:")
        print("-" * 30)
        print(text_result)
        
        processed_text = self._process_voice_text(text_result)
        
        print("-" * 30)
        print("RESULTADO PROCESADO:")
        print("-" * 30)
        print(processed_text)

        self.ui.input.setText(processed_text)
        print("="*60 + "\n")

        # Cerrar el indicador de voz
        if hasattr(self, 'voice_indicator') and self.voice_indicator:
            self.voice_indicator.close()
            self.voice_indicator = None

        self._cleanup_voice_worker()


    def _on_voice_error_direct(self, error_message):
        print("ERROR EN RECONOCIMIENTO DE VOZ")
        print("-" * 60)
        print(f"{error_message}")
        print("="*60 + "\n")
        
        # Cerrar el indicador de voz
        if hasattr(self, 'voice_indicator') and self.voice_indicator:
            self.voice_indicator.close()
            self.voice_indicator = None
        
        self._cleanup_voice_worker()


    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Selecciona una imagen",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif *.tiff);;Todos los archivos (*.*)"
        )

        if file_path:
            print("Archivo seleccionado:", file_path)
            self._display_image(file_path)
            self._start_ocr_processing(file_path)
        else:
            print("No se seleccionó ningún archivo")

    def _display_image(self, file_path):
        try:
            self.ui.label_20.setVisible(False)
            pixmap = QPixmap(file_path)
            
            if pixmap.isNull():
                print("Error: No se pudo cargar la imagen")
                return

            if pixmap.width() > 600:
                scaled_pixmap = pixmap.scaledToWidth(600, Qt.SmoothTransformation)
            else:
                scaled_pixmap = pixmap

            self.ui.image_icon.setPixmap(scaled_pixmap)
            self.ui.image_icon.setScaledContents(False)
            self.ui.image_icon.resize(scaled_pixmap.width(), scaled_pixmap.height())
            self._center_image_label(scaled_pixmap)
            
        except Exception as e:
            print(f"Error al mostrar imagen: {e}")

    def _center_image_label(self, pixmap):
        parent = self.ui.image_icon.parent()
        if parent:
            parent_width = parent.width()
            parent_height = parent.height()
            new_x = max(0, (parent_width - pixmap.width()) // 2)
            new_y = max(0, (parent_height - pixmap.height()) // 2)
            self.ui.image_icon.move(new_x, new_y)

    def _start_ocr_processing(self, image_path):
        print("\n" + "="*60)
        print("INICIANDO ANÁLISIS OCR")
        print("="*60)
        print(f"Archivo: {os.path.basename(image_path)}")
        print(f"Ruta: {image_path}")
        
        self.ocr_worker = OCRWorker(image_path)
        self.ocr_worker.finished.connect(self._on_ocr_finished)
        self.ocr_worker.error.connect(self._on_ocr_error)
        self.ocr_worker.progress.connect(self._on_ocr_progress)
        self.ocr_worker.start()

    def _start_voice_recognition(self):
        print("\n" + "="*60)
        print("INICIANDO RECONOCIMIENTO DE VOZ")
        print("="*60)

        self.voice_worker = VoiceWorker()
        self.voice_worker.finished.connect(self._on_voice_finished)
        self.voice_worker.error.connect(self._on_voice_error)
        self.voice_worker.progress.connect(self._on_voice_progress)
        self.voice_worker.start()

    def _on_ocr_progress(self, message):
        print(f"{message}")

    def _on_ocr_finished(self, latex_result, method_used):
        print(f"Motor usado: {method_used}")
        print("-" * 60)
        print("RESULTADO LATEX BRUTO:")
        print("-" * 30)
        print(latex_result)

        processed_result = self._clean_latex_exponents(latex_result)

        print("-" * 30)
        print("RESULTADO PROCESADO:")
        print("-" * 30)
        print(processed_result)

        self.ui.input.setText(processed_result)
        
        lines = processed_result.count('\n') + 1
        chars = len(processed_result)
        print(f"Estadísticas: {chars} caracteres, {lines} líneas")
        print("="*60 + "\n")
        
        self._cleanup_worker()

    def _on_voice_progress(self, message):
        print(f"{message}")
        if hasattr(self.ui, 'voice_status_label'):
            self.ui.voice_status_label.setText(message)

    def _on_voice_finished(self, text_result, method_used):
        print(f"Motor usado: {method_used}")
        print("-" * 60)
        print("RESULTADO DE LA TRANSCRIPCIÓN BRUTO:")
        print("-" * 30)
        print(text_result)
        
        processed_text = self._process_voice_text(text_result)
        
        print("-" * 30)
        print("RESULTADO PROCESADO:")
        print("-" * 30)
        print(processed_text)

        self.ui.input.setText(processed_text)
        print("="*60 + "\n")

        self._cleanup_voice_worker()

    def _on_ocr_error(self, error_message):
        print("ERROR EN PROCESAMIENTO")
        print("-" * 60)
        print(f"{error_message}")
        print("="*60 + "\n")
        
        self._cleanup_worker()
        
    def _on_voice_error(self, error_message):
        print("ERROR EN RECONOCIMIENTO DE VOZ")
        print("-" * 60)
        print(f"{error_message}")
        print("="*60 + "\n")
        
        self._cleanup_voice_worker()

    def _cleanup_worker(self):
        if self.ocr_worker:
            self.ocr_worker.deleteLater()
            self.ocr_worker = None

    def _cleanup_voice_worker(self):
        if self.voice_worker:
            self.voice_worker.deleteLater()
            self.voice_worker = None

    def cleanup(self):
        if self.ocr_worker and self.ocr_worker.isRunning():
            self.ocr_worker.quit()
            self.ocr_worker.wait()
        self._cleanup_worker()
        
        if self.voice_worker and self.voice_worker.isRunning():
            self.voice_worker.quit()
            self.voice_worker.wait()
        self._cleanup_voice_worker()
        
        if hasattr(self, 'voice_indicator') and self.voice_indicator:
            self.voice_indicator.close()
            self.voice_indicator = None

    def _clean_latex_exponents(self, latex_string: str) -> str:
        return re.sub(r'\^\{(.*?)\}', r'^\1', latex_string)

    def _process_voice_text(self, text: str) -> str:
        processed_text = text.lower()
        processed_text = processed_text.replace("más", "+")
        processed_text = processed_text.replace("menos", "-")
        processed_text = processed_text.replace("por", "*")
        processed_text = processed_text.replace("entre", "/")
        processed_text = processed_text.replace("igual a", "=")
        processed_text = processed_text.replace("raíz cuadrada", "\\sqrt")
        processed_text = re.sub(r'(\w+)\s+cuadrada', r'\1^2', processed_text)
        processed_text = re.sub(r'(\w+)\s+cúbica', r'\1^3', processed_text)
        processed_text = re.sub(r'(\w)\s*cuadrada', r'\1^2', processed_text)
        return processed_text

    def auto_find_and_solve(self):
        try:
            if not self.math_methods.equation.strip():
                print("No hay ecuación para resolver")
                return
            
            self.clear_iterations_table()
            
            if hasattr(self.ui, 'result_roots'):
                self.ui.result_roots.clear()
            
            method = self.settings['method']
            tolerance = self.settings['tolerance']
            max_iterations = self.settings['max_iterations']
            
            print(f"Método seleccionado: {method.upper()}")
            print(f"Tolerancia: {tolerance}, Max Iteraciones: {max_iterations}")
            
            if method == 'biseccion':
                self._solve_with_bisection(tolerance, max_iterations)
            else:
                self._solve_with_newton(tolerance, max_iterations)
                
        except Exception as e:
            print(f"Error en búsqueda automática: {e}")
            if hasattr(self.ui, 'result_roots'):
                self.ui.result_roots.append(f"Error: {str(e)}")

    def _solve_with_bisection(self, tolerance, max_iterations):
        """Método de bisección modificado para guardar en historial"""
        print("Buscando intervalos automáticamente para Bisección...")
        
        if self.settings['auto_interval']:
            start = self.settings['interval_start']
            end = self.settings['interval_end']
            step = self.settings['interval_step']
        else:
            start = self.settings['interval_start']
            end = self.settings['interval_end']
            step = self.settings['interval_step']
        
        all_intervals = self.math_methods.find_all_suitable_intervals(
            start=start, end=end, step=step
        )
        
        found_roots = []  # NUEVO: Lista para almacenar raíces
        total_iterations = 0  # NUEVO: Contador de iteraciones
        
        if all_intervals:
            print(f"Se encontraron {len(all_intervals)} intervalos adecuados.")
            
            for i, interval in enumerate(all_intervals):
                a, b = interval
                print(f"Resolviendo raíz #{i+1} en [{a:.2f}, {b:.2f}]")
                
                result = self.math_methods.bisection_method(a, b, tolerance, max_iterations)
                
                if result['success']:
                    found_roots.append(result['root'])  # NUEVO: Guardar raíz
                
                total_iterations += result['iterations']  # NUEVO: Sumar iteraciones
                
                if hasattr(self.ui, 'result_roots'):
                    self.ui.result_roots.append(f"<b style='color: #828282;'>Raíz {i+1}</b>")
                    self.ui.result_roots.append(f"  ●  <b>Raíz</b>: {result['root']:.8f}")
                    self.ui.result_roots.append(f"  ●  <b>Iteraciones</b>: {result['iterations']}")
                    self.ui.result_roots.append(f"  ●  <b>Error</b>: {result['final_error']:.20f}")
                    self.ui.result_roots.append("<br>")
                    self.ui.result_roots.verticalScrollBar().setValue(0)
                
                if result['success'] or (not result['success'] and result['iterations'] > 0):
                    self.math_methods.populate_table_rows(
                        self.ui.tabla_iteraciones, result['iterations_data']
                    )
                    
                    if i < len(all_intervals) - 1:
                        self._add_table_separator()
                
                if result['success']:
                    print(f"  > {result['message']}")
                else:
                    print(f"  > {result['error']}")
            
            # NUEVO: Guardar en historial si se encontraron raíces
            if found_roots and self.history_widget is not None:
                self.history_widget.add_history_entry(
                    equation=self.math_methods.equation,
                    method='Bisección',
                    roots=found_roots,
                    iterations=total_iterations,
                    settings=self.settings.copy()
                )
                print(f"Entrada guardada en historial: {len(found_roots)} raíces encontradas")
            
            self.ui.resultados.setCurrentIndex(1)
        else:
            print("No se encontraron intervalos adecuados.")
            if hasattr(self.ui, 'result_roots'):
                self.ui.result_roots.append("No se encontraron raíces en el rango especificado.")


    def _solve_with_newton(self, tolerance, max_iterations):
        """Método de Newton-Raphson modificado para guardar en historial"""
        print("Buscando valores iniciales para Newton-Raphson...")
        
        if self.settings['auto_interval']:
            start = self.settings['interval_start']
            end = self.settings['interval_end']
            step = self.settings['interval_step'] * 10
        else:
            start = self.settings['interval_start']
            end = self.settings['interval_end']
            step = self.settings['interval_step'] * 10
        
        initial_values = self.math_methods.find_suitable_initial_values(
            start=start, end=end, step=step, num_values=5
        )
        
        found_roots = []
        root_tolerance = 0.01
        total_iterations = 0  # NUEVO: Contador de iteraciones
        
        if initial_values:
            print(f"Se encontraron {len(initial_values)} valores iniciales.")
            
            for i, x0 in enumerate(initial_values):
                print(f"Probando con x₀ = {x0:.2f}")
                
                result = self.math_methods.newton_raphson_method(x0, tolerance, max_iterations)
                
                total_iterations += result['iterations']  # NUEVO: Sumar iteraciones
                
                if result['success']:
                    is_duplicate = False
                    for existing_root in found_roots:
                        if abs(result['root'] - existing_root) < root_tolerance:
                            is_duplicate = True
                            print(f"  > Raíz duplicada, saltando...")
                            break
                    
                    if not is_duplicate:
                        found_roots.append(result['root'])
                        root_num = len(found_roots)
                        
                        if hasattr(self.ui, 'result_roots'):
                            self.ui.result_roots.append(f"<b style='color: #828282;'>Raíz {i+1}</b>")
                            self.ui.result_roots.append(f"  ●  <b>Raíz</b>: {result['root']:.8f}")
                            self.ui.result_roots.append(f"  ●  <b>Iteraciones</b>: {result['iterations']}")
                            self.ui.result_roots.append(f"  ●  <b>Error</b>: {result['final_error']:.20f}")
                            self.ui.result_roots.append("<br>")
                            self.ui.result_roots.verticalScrollBar().setValue(0)
                        
                        self.math_methods.populate_table_newton(
                            self.ui.tabla_iteraciones, result['iterations_data']
                        )
                        
                        if root_num < len(initial_values):
                            self._add_table_separator()
                        
                        print(f"  > {result['message']}")
                else:
                    print(f"  > {result['error']}")
            
            # NUEVO: Guardar en historial si se encontraron raíces
            if found_roots:
                if self.history_widget is not None:
                    self.history_widget.add_history_entry(
                        equation=self.math_methods.equation,
                        method='Newton-Raphson',
                        roots=found_roots,
                        iterations=total_iterations,
                        settings=self.settings.copy()
                    )
                    print(f"Entrada guardada en historial: {len(found_roots)} raíces encontradas")
                
                self.ui.resultados.setCurrentIndex(1)
                print(f"Total de raíces únicas encontradas: {len(found_roots)}")
            else:
                print("No se encontraron raíces con Newton-Raphson.")
                if hasattr(self.ui, 'result_roots'):
                    self.ui.result_roots.append("No se encontraron raíces en el rango especificado.")
        else:
            print("No se encontraron valores iniciales adecuados.")
            if hasattr(self.ui, 'result_roots'):
                self.ui.result_roots.append("No se pudieron encontrar valores iniciales adecuados.")
                

    def _add_table_separator(self):
        for _ in range(2):
            row_count = self.ui.tabla_iteraciones.rowCount()
            self.ui.tabla_iteraciones.insertRow(row_count)
            for col in range(self.ui.tabla_iteraciones.columnCount()):
                item = QTableWidgetItem("")
                item.setBackground(QColor('#FFFFFF'))
                self.ui.tabla_iteraciones.setItem(row_count, col, item)
    
    def display_current_method_info(self):
        method_name = "Bisección" if self.settings['method'] == 'biseccion' else "Newton-Raphson"
        interval_type = "Automático" if self.settings['auto_interval'] else "Personalizado"
        
        info_text = f"""
        <div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin: 5px;'>
            <b>Método:</b> {method_name}<br>
            <b>Tolerancia:</b> {self.settings['tolerance']:.2e}<br>
            <b>Máx. Iteraciones:</b> {self.settings['max_iterations']}<br>
            <b>Intervalo:</b> {interval_type}
        </div>
        """
        
        if hasattr(self.ui, 'method_info_label'):
            self.ui.method_info_label.setText(info_text)
        
        print(f"\n{'='*50}")
        print(f"CONFIGURACIÓN ACTUAL")
        print(f"{'='*50}")
        print(f"Método: {method_name}")
        print(f"Tolerancia: {self.settings['tolerance']:.2e}")
        print(f"Máx. Iteraciones: {self.settings['max_iterations']}")
        print(f"Tipo de Intervalo: {interval_type}")
        if not self.settings['auto_interval']:
            print(f"Rango: [{self.settings['interval_start']}, {self.settings['interval_end']}]")
            print(f"Paso: {self.settings['interval_step']}")
        print(f"{'='*50}\n")

    def _apply_result_roots_style(self):
        if hasattr(self.ui, 'result_roots'):
            self.ui.result_roots.setStyleSheet("""
                QTextEdit, QTextBrowser {
                    background-color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    padding: 15px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 22px;
                    color: #333333;
                }
                
                /* Estilo para la barra de desplazamiento vertical */
                QTextEdit QScrollBar:vertical, 
                QTextBrowser QScrollBar:vertical {
                    border: none;
                    background: #f0f0f0;
                    width: 10px;
                    margin: 0;
                    border-radius: 5px;
                }
                
                /* Estilo para el handle (pulgar) de la barra */
                QTextEdit QScrollBar::handle:vertical,
                QTextBrowser QScrollBar::handle:vertical {
                    background-color: #CD1C18;
                    border-radius: 5px;
                    min-height: 20px;
                }

                /* Hover effect en el handle */
                QTextEdit QScrollBar::handle:vertical:hover,
                QTextBrowser QScrollBar::handle:vertical:hover {
                    background-color: #a81614;
                }

                /* Pressed effect en el handle */
                QTextEdit QScrollBar::handle:vertical:pressed,
                QTextBrowser QScrollBar::handle:vertical:pressed {
                    background-color: #8a1210;
                }

                /* Ocultar los botones de flecha */
                QTextEdit QScrollBar::add-line:vertical,
                QTextEdit QScrollBar::sub-line:vertical,
                QTextBrowser QScrollBar::add-line:vertical,
                QTextBrowser QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                    height: 0;
                    width: 0;
                }
                
                /* Zona antes y después del handle */
                QTextEdit QScrollBar::add-page:vertical,
                QTextEdit QScrollBar::sub-page:vertical,
                QTextBrowser QScrollBar::add-page:vertical,
                QTextBrowser QScrollBar::sub-page:vertical {
                    background: none;
                }

                /* Barra de desplazamiento horizontal (opcional) */
                QTextEdit QScrollBar:horizontal,
                QTextBrowser QScrollBar:horizontal {
                    border: none;
                    background: #f0f0f0;
                    height: 10px;
                    margin: 0;
                    border-radius: 5px;
                }

                QTextEdit QScrollBar::handle:horizontal,
                QTextBrowser QScrollBar::handle:horizontal {
                    background-color: #CD1C18;
                    border-radius: 5px;
                    min-width: 20px;
                }

                QTextEdit QScrollBar::handle:horizontal:hover,
                QTextBrowser QScrollBar::handle:horizontal:hover {
                    background-color: #a81614;
                }

                /* Ocultar botones horizontales */
                QTextEdit QScrollBar::add-line:horizontal,
                QTextEdit QScrollBar::sub-line:horizontal,
                QTextBrowser QScrollBar::add-line:horizontal,
                QTextBrowser QScrollBar::sub-line:horizontal {
                    border: none;
                    background: none;
                    height: 0;
                    width: 0;
                }
            """)
            print("Estilos aplicados a result_roots")
    

    def save_all_panels(self):
        """
        Genera un informe PDF completo, optimizando el flujo de contenido
        para evitar páginas en blanco y colocar la gráfica en su propia página.
        """
        # 1. Obtener la ruta de guardado del archivo
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window, "Guardar informe en PDF", "informe_raices.pdf", "Archivos PDF (*.pdf)"
        )

        if not file_path:
            return

        try:
            # 2. Configurar el PDF
            pdf = CustomPDF(title=f"Informe de Ecuación: {self.math_methods.equation}", filename=file_path)

            # 3. Añadir la página de portada
            create_report_cover(pdf, f"Análisis de la Ecuación: {self.math_methods.equation}")
            
            # 4. Añadir la información del método y la ecuación
            # Añade una nueva página para el contenido principal
            pdf.add_page()
            
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Configuración y Ecuación", ln=1, align='L')
            pdf.set_font("Arial", "", 12)
            
            # Establece la posición X en el margen izquierdo para asegurar
            # que el texto no se imprima fuera de la página
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(pdf.w - 2 * pdf.l_margin, 7, f"Ecuación: {self.math_methods.equation}")
            
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(pdf.w - 2 * pdf.l_margin, 7, f"Método: {'Bisección' if self.settings['method'] == 'biseccion' else 'Newton-Raphson'}")
            
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(pdf.w - 2 * pdf.l_margin, 7, f"Tolerancia: {self.settings['tolerance']:.2e}")
            
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(pdf.w - 2 * pdf.l_margin, 7, f"Máx. Iteraciones: {self.settings['max_iterations']}")
            
            pdf.ln(10)

            # 5. Añadir la tabla de iteraciones
            if hasattr(self.ui, 'widget_5') and self.ui.tabla_iteraciones.rowCount() > 0:
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "Procedimiento (Tabla de Iteraciones)", ln=1, align='L')
                pdf.ln(5)
                
                iterations_pixmap = self.ui.widget_5.grab()
                temp_table_path = "temp_table.png"
                iterations_pixmap.save(temp_table_path)
                
                with pdf.unbreakable():
                    pdf.image(temp_table_path, w=pdf.w - 2 * pdf.l_margin)
                    
                os.remove(temp_table_path)
                pdf.ln(10)
            
            # 6. Añadir el panel de resultados
            if hasattr(self.ui, 'resultadosW'):
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "Resultados del Análisis", ln=1, align='L')
                pdf.ln(5)
                
                results_text = self.ui.result_roots.toPlainText()
                clean_text = results_text.replace("●", "-")
                
                pdf.set_font("Arial", "", 12)
                pdf.multi_cell(pdf.w - 2 * pdf.l_margin, 7, clean_text)
                pdf.ln(10)
                
            # 7. Añadir la gráfica en su propia página
            if hasattr(self.ui, 'grafica_container') and self.math_methods.equation:
                pdf.add_page()
                
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "Gráfica de la Ecuación", ln=1, align='L')
                pdf.ln(5)
                
                graphics_pixmap = self.ui.grafica_container.grab()
                temp_graph_path = "temp_graph.png"
                graphics_pixmap.save(temp_graph_path)
                
                with pdf.unbreakable():
                    pdf.image(temp_graph_path, w=pdf.w - 2 * pdf.l_margin)
                    
                os.remove(temp_graph_path)
            
            # 8. Guardar el archivo
            pdf.output(file_path)

            # 9. Mostrar un mensaje de éxito
            QMessageBox.information(
                self.main_window, 
                "Informe Guardado",
                f"El informe se ha guardado correctamente en:\n`{file_path}`"
            )
            print(f"Informe guardado en: {file_path}")

        except Exception as e:
            QMessageBox.critical(
                self.main_window, 
                "Error al Guardar", 
                f"Ocurrió un error al intentar guardar el PDF: {e}"
            )
            print(f"Error al guardar el PDF: {e}")
    
    def open_history(self):
        """Abre el widget de historial"""
        from .history_widget import HistoryWidget
        
        if self.history_widget is None:
            self.history_widget = HistoryWidget()
            self.history_widget.equation_loaded.connect(self._on_history_equation_loaded)
            
            if hasattr(self.ui, 'resultados'):
                self.ui.resultados.addWidget(self.history_widget)
                self.history_index = self.ui.resultados.count() - 1
            else:
                print("Error: No se encuentra el stackedWidget 'resultados'")
                return
        else:
            # Actualizar el historial si ya existe
            self.history_widget.refresh_history()
        
        if hasattr(self.ui, 'resultados'):
            self.ui.resultados.setCurrentWidget(self.history_widget)
            print("Mostrando widget de historial")

    def _on_history_equation_loaded(self, history_data: dict):
        """
        Maneja cuando se carga una ecuación desde el historial
        
        Args:
            history_data: Diccionario con los datos del historial
        """
        equation = history_data.get('equation', '')
        settings = history_data.get('settings', {})
        
        # Cargar la ecuación en los campos de entrada
        if equation:
            self.math_methods.equation = equation
            self.ui.input.setPlainText(equation)
            if hasattr(self.ui, 'input_3'):
                self.ui.input_3.setPlainText(equation)
            
            print(f"Ecuación cargada desde historial: {equation}")
        
        # Aplicar configuraciones si están disponibles
        if settings:
            self.settings.update(settings)
            print(f"Configuraciones cargadas: {settings.get('method', 'N/A')}")
        
        # Cambiar a la vista principal
        self.change_main_index(1)
        
        # Opcional: Resolver automáticamente
        reply = QMessageBox.question(
            self.main_window,
            "Resolver ecuación",
            "¿Deseas resolver esta ecuación ahora?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self.process_solve()

    def show_about_dialog(self):
        """Abre la ventana emergente de 'Acerca de'."""
        # Crea una instancia del QDialog, pasando la ventana principal como padre
        about_dialog = QDialog(self.main_window)
        
        # Crea una instancia de la UI generada
        ui_about = Ui_Dialog()
        
        # Configura la UI en el diálogo
        ui_about.setupUi(about_dialog)
        
        # Muestra el diálogo de forma modal (bloquea la ventana principal)
        about_dialog.exec()