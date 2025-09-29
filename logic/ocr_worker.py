# logic/ocr_worker.py
"""
Worker thread para procesamiento OCR sin bloquear la UI
"""

from PySide6.QtCore import QThread, Signal
from .ocr_processor import OCRProcessor


class OCRWorker(QThread):
    """Worker thread para procesar OCR de forma asíncrona"""
    
    # Señales
    finished = Signal(str, str)  # latex_result, method_used
    error = Signal(str)          # error_message
    progress = Signal(str)       # status_message
    
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.processor = OCRProcessor()
    
    def run(self):
        """Ejecutar procesamiento OCR"""
        try:
            # Verificar si hay métodos disponibles
            if not self.processor.is_ready():
                self.error.emit(self.processor._get_installation_message())
                return
            
            # Emitir progreso
            available_methods = self.processor.get_available_methods()
            self.progress.emit(f"Procesando con: {', '.join(available_methods)}")
            
            # Procesar imagen
            result = self.processor.process_image(self.image_path)
            
            if result["success"]:
                self.finished.emit(result["latex"], result["method"])
            else:
                self.error.emit(result["error"])
                
        except Exception as e:
            self.error.emit(f"Error inesperado: {str(e)}")