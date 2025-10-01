from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QFileDialog, QAbstractItemView, QTableWidgetItem
from PySide6.QtGui import QPixmap, QColor
import os
import re

# Importamos la clase para el manejo matemático
from .math_methods import MathMethods
from .ocr_worker import OCRWorker
from .voice_worker import VoiceWorker


class MathRootsController(QObject):
    """Controlador de la ventana principal MathRoots"""

    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.ocr_worker = None
        self.voice_worker = None
        self.math_methods = MathMethods()
        self.graphics = None

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


    def set_graphics(self, graphics):
        """Establece la referencia al objeto Graphic"""
        self.graphics = graphics

    def setup_connections(self):
        """Conecta los botones y otros eventos"""
        self.ui.input_image.clicked.connect(self.image_mode)
        self.ui.load_image.clicked.connect(self.load_image)
        self.ui.input_voice.clicked.connect(self.voice_mode)
        self.ui.solve.clicked.connect(self.process_solve)
        self.ui.solve_3.clicked.connect(self.process_solve)  # ← CAMBIAR ESTA LÍNEA
        self.ui.resultado_2.clicked.connect(lambda: self.seleccionar_boton(self.ui.resultado_2))
        self.ui.procedimiento_2.clicked.connect(lambda: self.seleccionar_boton(self.ui.procedimiento_2))
        self.ui.grafica_2.clicked.connect(lambda: self.seleccionar_boton(self.ui.grafica_2))
        self.ui.info.clicked.connect(self.info_window)

        if hasattr(self.ui, 'settings'):
            self.ui.settings.clicked.connect(self.open_settings)

    def graficar_ecuacion_actual(self):
        """Grafica la ecuación actual almacenada en math_methods"""
        if self.graphics is None:
            print("Error: graphics no está inicializado")
            return
            
        try:
            ecuacion_grafica = self.math_methods.get_equation_for_plot()
            
            if ecuacion_grafica:
                # Dibuja la función en un rango amplio.
                # Esta línea se encarga de crear los datos.
                self.graphics.graficar_funcion(ecuacion_grafica, x_min=-50, x_max=50, limpiar=True)

                # AHORA, para asegurarnos de que el rango de la vista no se modifique
                # por otras acciones (como graficar la raíz), lo fijamos explícitamente.
                self.graphics.set_rango(x_min=-50, x_max=50, y_min=-50, y_max=50)

                print(f"Ecuación graficada: {ecuacion_grafica}")
        except Exception as e:
            print(f"Error al graficar: {e}")

    def setup_iterations_table(self):
        """Configura la tabla de iteraciones inicial"""
        if hasattr(self.ui, 'tabla_iteraciones'):
            self.ui.tabla_iteraciones.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
            
            # Usar el método actual de las configuraciones
            if self.settings['method'] == 'biseccion':
                headers = ['Iteración', 'xₗ', 'xᵣ', 'xₘ', 'f(xₗ)', 'f(xᵣ)', 'f(xₘ)', 'Error']
            else:  # newton
                headers = ['Iteración', 'xₙ', 'f(xₙ)', "f'(xₙ)", 'xₙ₊₁', 'Error']
            
            self.ui.tabla_iteraciones.setColumnCount(len(headers))
            self.ui.tabla_iteraciones.setHorizontalHeaderLabels(headers)
            
            self.ui.tabla_iteraciones.setAlternatingRowColors(True)
            self.ui.tabla_iteraciones.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.ui.tabla_iteraciones.horizontalHeader().setStretchLastSection(True)
            
            print(f"Tabla de iteraciones configurada para método: {self.settings['method']}")

    def update_iterations_table(self):
        """Actualiza la tabla de iteraciones con los datos del método de bisección"""
        if hasattr(self.ui, 'tabla_iteraciones'):
            try:
                self.math_methods.populate_table(self.ui.tabla_iteraciones)
                print("Tabla de iteraciones actualizada")
            except Exception as e:
                print(f"Error actualizando tabla de iteraciones: {e}")

    def execute_bisection_method(self, a: float, b: float, tolerance: float = 1e-6, max_iterations: int = 100):
        """
        Ejecuta el método de bisección y actualiza la tabla de iteraciones
        """
        try:
            if not self.math_methods.equation.strip():
                print("No hay ecuación para resolver")
                return
            
            print(f"Ejecutando método de bisección para: {self.math_methods.equation}")
            print(f"Intervalo: [{a}, {b}], Tolerancia: {tolerance}")
            
            result = self.math_methods.bisection_method(a, b, tolerance, max_iterations)
            self.update_iterations_table()
            
            if result['success']:
                print(f"{result['message']}")
                
                if hasattr(self.ui, 'resultado_label'):
                    self.ui.resultado_label.setText(f"Raíz: {result['root']:.8f}")
                
                stats = self.math_methods.get_summary_statistics()
                if stats:
                    print(f"Estadísticas:")
                    print(f"   - Iteraciones totales: {stats['total_iterations']}")
                    print(f"   - Raíz final: {stats['final_root']:.8f}")
                    print(f"   - Error final: {stats['final_error']:.2e}")
                    print(f"   - Valor de función: {stats['final_function_value']:.2e}")
            else:
                print(f"{result['error']}")
            
        except Exception as e:
            print(f"Error ejecutando bisección: {e}")

    def auto_find_and_solve(self):
        """
        Busca automáticamente todos los intervalos adecuados y ejecuta bisección para cada uno,
        agregando una separación visual en la tabla para cada raíz encontrada.
        """
        try:
            if not self.math_methods.equation.strip():
                print("No hay ecuación para resolver")
                return
            
            self.clear_iterations_table()
            
            # Limpia el widget de resultados antes de cada ejecución
            if hasattr(self.ui, 'result_roots'):
                self.ui.result_roots.clear()

            print("Buscando intervalos automáticamente...")
            
            all_intervals = self.math_methods.find_all_suitable_intervals(start=-100, end=100, step=0.1)
            
            if all_intervals:
                print(f"Se encontraron {len(all_intervals)} intervalos adecuados.")
                
                for i, interval in enumerate(all_intervals):
                    a, b = interval
                    print(f"Resolviendo para la posible raíz #{i+1} en el intervalo: [{a:.2f}, {b:.2f}]")
                    
                    result = self.math_methods.bisection_method(a, b)
                    
                    # Añadir resultados al panel de texto
                    if hasattr(self.ui, 'result_roots'):
                        self.ui.result_roots.append(f"<b>Raíz #{i+1}</b>")
                        self.ui.result_roots.append(f"  > <b>Raíz</b>: {result['root']:.8f}")
                        self.ui.result_roots.append(f"  > <b>Iteraciones</b>: {result['iterations']}")
                        self.ui.result_roots.append(f"  > <b>Error Aproximado</b>: {result['final_error']:.2e}")
                        self.ui.result_roots.append("<br>") # Salto de línea para separar visualmente
                    
                    if result['success'] or (not result['success'] and result['iterations'] > 0):
                        self.math_methods.populate_table_rows(self.ui.tabla_iteraciones, result['iterations_data'])
                        
                        if i < len(all_intervals) - 1:
                            for _ in range(2):
                                row_count = self.ui.tabla_iteraciones.rowCount()
                                self.ui.tabla_iteraciones.insertRow(row_count)
                                for col in range(self.ui.tabla_iteraciones.columnCount()):
                                    item = QTableWidgetItem("")
                                    item.setBackground(QColor('#FFFFFF'))
                                    self.ui.tabla_iteraciones.setItem(row_count, col, item)
                    
                    if result['success']:
                        print(f"  > {result['message']}")
                    else:
                        print(f"  > {result['error']}")
                        
                self.ui.resultados.setCurrentIndex(1)
            else:
                print("No se pudo encontrar un intervalo adecuado automáticamente.")
                if hasattr(self.ui, 'result_roots'):
                    self.ui.result_roots.append("No se encontró una raíz en el rango predeterminado.")
                    
        except Exception as e:
            print(f"Error en búsqueda automática: {e}")
            if hasattr(self.ui, 'result_roots'):
                self.ui.result_roots.append(f"Error: {str(e)}")

    def clear_iterations_table(self):
        """Limpia la tabla de iteraciones"""
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
        """
        
        estilo_inactivo = """
            QPushButton {
                background-color: #FFFFFF;
                color: black;
                border-radius: 25px;
                border: 2px solid #CD1C18;
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


    def process_solve(self):
        """Función que se ejecuta al hacer click en 'solve' o 'solve_3'"""
        # Intentar leer de ambos inputs posibles
        if hasattr(self.ui, 'input_3') and self.ui.input_3.toPlainText().strip():
            input_text = self.ui.input_3.toPlainText().strip()
        else:
            input_text = self.ui.input.toPlainText().strip()
        
        if not input_text:
            print("No hay ecuación para resolver")
            return
        
        self.math_methods.equation = input_text
        
        # Sincronizar ambos inputs
        if hasattr(self.ui, 'input_3'):
            self.ui.input_3.setPlainText(input_text)
        self.ui.input.setPlainText(input_text)
        
        print(f"La ecuación capturada es: {self.math_methods.equation}")
        
        # AGREGAR: Mostrar configuración actual
        self.display_current_method_info()
        
        # AGREGAR: Actualizar encabezados de tabla según método
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
        else:
            print(f"No se puede ejecutar: {validation['error']}")

    def change_main_index(self, index: int):
        self.ui.stackedWidget.setCurrentIndex(index)

    def change_home_index(self, index: int):
        self.ui.HomeStackedWidgets.setCurrentIndex(index)

    def image_mode(self):
        self.ui.HomeStackedWidgets.setCurrentIndex(1)

    def voice_mode(self):
        """Cambia a la página de entrada de voz e inicia el reconocimiento"""
        self.ui.HomeStackedWidgets.setCurrentIndex(2)
        self._start_voice_recognition()

    def load_image(self):
        """Abre un file chooser para seleccionar una imagen"""
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
        """Mostrar imagen en la interfaz"""
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
        """Centrar el label de imagen en su contenedor"""
        parent = self.ui.image_icon.parent()
        if parent:
            parent_width = parent.width()
            parent_height = parent.height()
            new_x = max(0, (parent_width - pixmap.width()) // 2)
            new_y = max(0, (parent_height - pixmap.height()) // 2)
            self.ui.image_icon.move(new_x, new_y)

    def _start_ocr_processing(self, image_path):
        """Iniciar procesamiento OCR automáticamente"""
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
        """Iniciar el procesamiento de reconocimiento de voz"""
        print("\n" + "="*60)
        print("INICIANDO RECONOCIMIENTO DE VOZ")
        print("="*60)

        self.voice_worker = VoiceWorker()
        self.voice_worker.finished.connect(self._on_voice_finished)
        self.voice_worker.error.connect(self._on_voice_error)
        self.voice_worker.progress.connect(self._on_voice_progress)
        self.voice_worker.start()

    def _on_ocr_progress(self, message):
        """Callback para actualizaciones de progreso del OCR"""
        print(f"{message}")

    def _on_ocr_finished(self, latex_result, method_used):
        """Callback cuando OCR termina exitosamente"""
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
        """Callback para actualizaciones de progreso de la voz"""
        print(f"{message}")
        if hasattr(self.ui, 'voice_status_label'):
            self.ui.voice_status_label.setText(message)

    def _on_voice_finished(self, text_result, method_used):
        """Callback cuando el reconocimiento de voz termina exitosamente"""
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
        """Callback cuando OCR falla"""
        print("ERROR EN PROCESAMIENTO")
        print("-" * 60)
        print(f"{error_message}")
        print("="*60 + "\n")
        
        self._cleanup_worker()
        
    def _on_voice_error(self, error_message):
        """Callback cuando el reconocimiento de voz falla"""
        print("ERROR EN RECONOCIMIENTO DE VOZ")
        print("-" * 60)
        print(f"{error_message}")
        print("="*60 + "\n")
        
        self._cleanup_voice_worker()

    def _cleanup_worker(self):
        """Limpiar recursos del worker thread (OCR)"""
        if self.ocr_worker:
            self.ocr_worker.deleteLater()
            self.ocr_worker = None

    def _cleanup_voice_worker(self):
        """Limpiar recursos del worker thread (Voz)"""
        if self.voice_worker:
            self.voice_worker.deleteLater()
            self.voice_worker = None

    def cleanup(self):
        """Limpiar recursos al cerrar la aplicación"""
        if self.ocr_worker and self.ocr_worker.isRunning():
            self.ocr_worker.quit()
            self.ocr_worker.wait()
        self._cleanup_worker()
        if self.voice_worker and self.voice_worker.isRunning():
            self.voice_worker.quit()
            self.voice_worker.wait()
        self._cleanup_voice_worker()

    def _clean_latex_exponents(self, latex_string: str) -> str:
        """
        Elimina las llaves de los exponentes en una cadena de LaTeX si son innecesarias.
        Ejemplo: 'x^{3}' -> 'x^3'
        """
        return re.sub(r'\^\{(.*?)\}', r'^\1', latex_string)

    def _process_voice_text(self, text: str) -> str:
        """
        Procesa el texto transcribido de la voz para convertirlo a una notación matemática más formal.
        """
        processed_text = text.lower()
        
        # Reemplazos de operadores y funciones simples
        processed_text = processed_text.replace("más", "+")
        processed_text = processed_text.replace("menos", "-")
        processed_text = processed_text.replace("por", "*")
        processed_text = processed_text.replace("entre", "/")
        processed_text = processed_text.replace("igual a", "=")
        processed_text = processed_text.replace("raíz cuadrada", "\\sqrt")

        # Reemplazos de exponentes y otras expresiones usando Regex
        processed_text = re.sub(r'(\w+)\s+cuadrada', r'\1^2', processed_text)
        processed_text = re.sub(r'(\w+)\s+cúbica', r'\1^3', processed_text)
        processed_text = re.sub(r'(\w)\s*cuadrada', r'\1^2', processed_text)
        
        return processed_text
    
    def open_settings(self):
        """Abre la ventana de configuraciones"""
        from ui.settings_dialog import SettingsDialog
        
        dialog = SettingsDialog(parent=None, current_settings=self.settings)
        dialog.settings_saved.connect(self._on_settings_saved)
        dialog.exec()

    def _on_settings_saved(self, new_settings):
        """Callback cuando se guardan nuevas configuraciones"""
        self.settings = new_settings.copy()
        print("Configuraciones actualizadas en el controlador")
        
        # Actualizar encabezados de tabla según el método
        self.update_table_headers_for_method()

    def update_table_headers_for_method(self):
        """Actualiza los encabezados de la tabla según el método seleccionado"""
        if not hasattr(self.ui, 'tabla_iteraciones'):
            return
        
        if self.settings['method'] == 'biseccion':
            headers = ['Iteración', 'xₗ', 'xᵣ', 'xₘ', 'f(xₗ)', 'f(xᵣ)', 'f(xₘ)', 'Error']
        else:  # newton
            headers = ['Iteración', 'xₙ', 'f(xₙ)', "f'(xₙ)", 'xₙ₊₁', 'Error']
        
        self.ui.tabla_iteraciones.setColumnCount(len(headers))
        self.ui.tabla_iteraciones.setHorizontalHeaderLabels(headers)
        print(f"Encabezados de tabla actualizados para método: {self.settings['method']}")

    def auto_find_and_solve(self):
        """
        Busca automáticamente intervalos/valores iniciales y ejecuta el método seleccionado.
        Versión mejorada que usa las configuraciones.
        """
        try:
            if not self.math_methods.equation.strip():
                print("No hay ecuación para resolver")
                return
            
            self.clear_iterations_table()
            
            # Limpia el widget de resultados
            if hasattr(self.ui, 'result_roots'):
                self.ui.result_roots.clear()
            
            method = self.settings['method']
            tolerance = self.settings['tolerance']
            max_iterations = self.settings['max_iterations']
            
            print(f"Método seleccionado: {method.upper()}")
            print(f"Tolerancia: {tolerance}, Max Iteraciones: {max_iterations}")
            
            if method == 'biseccion':
                self._solve_with_bisection(tolerance, max_iterations)
            else:  # newton
                self._solve_with_newton(tolerance, max_iterations)
                
        except Exception as e:
            print(f"Error en búsqueda automática: {e}")
            if hasattr(self.ui, 'result_roots'):
                self.ui.result_roots.append(f"Error: {str(e)}")

    def _solve_with_bisection(self, tolerance, max_iterations):
        """Resuelve usando método de bisección"""
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
        
        if all_intervals:
            print(f"Se encontraron {len(all_intervals)} intervalos adecuados.")
            
            for i, interval in enumerate(all_intervals):
                a, b = interval
                print(f"Resolviendo raíz #{i+1} en [{a:.2f}, {b:.2f}]")
                
                result = self.math_methods.bisection_method(a, b, tolerance, max_iterations)
                
                # Añadir resultados al panel
                if hasattr(self.ui, 'result_roots'):
                    self.ui.result_roots.append(f"<b>Raíz #{i+1}</b>")
                    self.ui.result_roots.append(f"  > <b>Raíz</b>: {result['root']:.8f}")
                    self.ui.result_roots.append(f"  > <b>Iteraciones</b>: {result['iterations']}")
                    self.ui.result_roots.append(f"  > <b>Error</b>: {result['final_error']:.2e}")
                    self.ui.result_roots.append("<br>")
                
                if result['success'] or (not result['success'] and result['iterations'] > 0):
                    self.math_methods.populate_table_rows(
                        self.ui.tabla_iteraciones, result['iterations_data']
                    )
                    
                    # Separador visual
                    if i < len(all_intervals) - 1:
                        self._add_table_separator()
                
                if result['success']:
                    print(f"  > {result['message']}")
                else:
                    print(f"  > {result['error']}")
            
            self.ui.resultados.setCurrentIndex(1)
        else:
            print("No se encontraron intervalos adecuados.")
            if hasattr(self.ui, 'result_roots'):
                self.ui.result_roots.append("No se encontraron raíces en el rango especificado.")

    def _solve_with_newton(self, tolerance, max_iterations):
        """Resuelve usando método de Newton-Raphson"""
        print("Buscando valores iniciales para Newton-Raphson...")
        
        if self.settings['auto_interval']:
            start = self.settings['interval_start']
            end = self.settings['interval_end']
            step = self.settings['interval_step'] * 10  # Paso más grande para Newton
        else:
            start = self.settings['interval_start']
            end = self.settings['interval_end']
            step = self.settings['interval_step'] * 10
        
        initial_values = self.math_methods.find_suitable_initial_values(
            start=start, end=end, step=step, num_values=5
        )
        
        if initial_values:
            print(f"Se encontraron {len(initial_values)} valores iniciales.")
            
            # Para evitar encontrar la misma raíz múltiples veces
            found_roots = []
            root_tolerance = 0.01  # Considera raíces iguales si están a menos de esta distancia
            
            for i, x0 in enumerate(initial_values):
                print(f"Probando con x₀ = {x0:.2f}")
                
                result = self.math_methods.newton_raphson_method(x0, tolerance, max_iterations)
                
                if result['success']:
                    # Verificar si ya encontramos esta raíz
                    is_duplicate = False
                    for existing_root in found_roots:
                        if abs(result['root'] - existing_root) < root_tolerance:
                            is_duplicate = True
                            print(f"  > Raíz duplicada, saltando...")
                            break
                    
                    if not is_duplicate:
                        found_roots.append(result['root'])
                        root_num = len(found_roots)
                        
                        # Añadir resultados
                        if hasattr(self.ui, 'result_roots'):
                            self.ui.result_roots.append(f"<b>Raíz #{root_num}</b>")
                            self.ui.result_roots.append(f"  > <b>Raíz</b>: {result['root']:.8f}")
                            self.ui.result_roots.append(f"  > <b>Iteraciones</b>: {result['iterations']}")
                            self.ui.result_roots.append(f"  > <b>Error</b>: {result['final_error']:.2e}")
                            self.ui.result_roots.append("<br>")
                        
                        self.math_methods.populate_table_newton(
                            self.ui.tabla_iteraciones, result['iterations_data']
                        )
                        
                        # Separador visual
                        if root_num < len(initial_values):
                            self._add_table_separator()
                        
                        print(f"  > {result['message']}")
                else:
                    print(f"  > {result['error']}")
            
            if found_roots:
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
        """Agrega filas de separación visual en la tabla"""
        from PySide6.QtWidgets import QTableWidgetItem
        from PySide6.QtGui import QColor
        
        for _ in range(2):
            row_count = self.ui.tabla_iteraciones.rowCount()
            self.ui.tabla_iteraciones.insertRow(row_count)
            for col in range(self.ui.tabla_iteraciones.columnCount()):
                item = QTableWidgetItem("")
                item.setBackground(QColor('#FFFFFF'))
                self.ui.tabla_iteraciones.setItem(row_count, col, item)
    
    def display_current_method_info(self):
        """
        Muestra información sobre el método y configuración actual.
        Puedes llamar esto después de process_solve() para informar al usuario.
        """
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
        
        # Si tienes un label o text widget para mostrar info, úsalo aquí
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