from PySide6.QtCore import QThread, Signal
import speech_recognition as sr

class VoiceWorker(QThread):
    finished = Signal(str, str)
    error = Signal(str)
    progress = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.recognizer = sr.Recognizer()

    def run(self):
        self.progress.emit("⏳ Escuchando...")
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=8)
            
            self.progress.emit("⏳ Procesando audio...")
            
            recognized_text = self.recognizer.recognize_google(
                audio, 
                language="es-ES"
            )
            
            self.progress.emit("✅ Transcripción exitosa.")
            self.finished.emit(recognized_text, "Google Speech Recognition")

        except sr.UnknownValueError:
            self.error.emit("No se pudo entender la voz. Inténtalo de nuevo.")
        except sr.sr.WaitTimeoutError:
            self.error.emit("Tiempo de espera agotado. No se detectó voz.")
        except sr.RequestError as e:
            self.error.emit(f"Error de conexión con el servicio: {e}")
        except Exception as e:
            self.error.emit(f"Ha ocurrido un error inesperado: {e}")