from PySide6.QtCore import QThread, Signal
import speech_recognition as sr

class VoiceWorker(QThread):
    """
    Worker para realizar el reconocimiento de voz en un hilo secundario.
    """
    finished = Signal(str, str)
    error = Signal(str)
    progress = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.recognizer = sr.Recognizer()

    def run(self):
        """
        Ejecuta la lógica de reconocimiento de voz.
        Captura y emite errores a través de señales para evitar el cierre de la app.
        """
        try:
            self.progress.emit("⏳ Escuchando...")
            
            with sr.Microphone() as source:
                # Ajusta el reconocedor a las condiciones del ruido ambiental.
                # Es crucial que PyAudio esté instalado correctamente para esta línea.
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=8)
            
            self.progress.emit("⏳ Procesando audio...")
            
            # Reconocimiento usando la API de Google
            recognized_text = self.recognizer.recognize_google(
                audio, 
                language="es-ES"
            )
            
            self.progress.emit("✅ Transcripción exitosa.")
            self.finished.emit(recognized_text, "Google Speech Recognition")

        # Excepciones específicas del reconocimiento de voz
        except sr.UnknownValueError:
            self.error.emit("No se pudo entender la voz. Inténtalo de nuevo.")
        except sr.WaitTimeoutError:
            self.error.emit("Tiempo de espera agotado. No se detectó voz.")
        except sr.RequestError as e:
            self.error.emit(f"Error de conexión con el servicio: {e}")
        
        # Excepción general para capturar cualquier otro problema
        # (ej. problemas con PyAudio, falta de permisos, etc.)
        except Exception as e:
            self.error.emit(f"Ha ocurrido un error inesperado: {e}")