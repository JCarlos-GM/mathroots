from PySide6.QtCore import QObject, Qt, QTimer, QRect
from PySide6.QtWidgets import (QFileDialog, QAbstractItemView, QTableWidgetItem,
                               QDialog, QVBoxLayout, QLabel)
from PySide6.QtGui import QPixmap, QColor, QPainter, QPen, QRegion
import os
import re

# Importamos la clase para el manejo matemático
from logic.math_methods import MathMethods
from logic.ocr_worker import OCRWorker
from logic.voice_worker import VoiceWorker


class VoiceIndicatorDialogAdvanced(QDialog):
    """Versión con animación de ondas de sonido"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.wave_offset = 0
        self.setup_ui()
        self.setup_animation()
        
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        self.setWindowTitle("Capturando voz...")
        self.setFixedSize(250, 250)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # AGREGAR LA MÁSCARA CIRCULAR
        region = QRegion(0, 0, 250, 250, QRegion.Ellipse)
        self.setMask(region)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.setLayout(layout)
    
    def setup_animation(self):
        """Configura el timer para la animación"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(50)
    
    def update_animation(self):
        """Actualiza la animación"""
        self.wave_offset += 5
        if self.wave_offset > 360:
            self.wave_offset = 0
        self.update()
    
    def paintEvent(self, event):
        """Dibuja la animación personalizada"""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # Dibujar fondo circular blanco
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(0, 0, 250, 250)
        
        # Dibujar círculos pulsantes (ondas de sonido)
        for i in range(3):
            radius = 30 + i * 20 + (self.wave_offset % 30)
            opacity = 255 - (i * 80) - (self.wave_offset % 30) * 3
            if opacity < 0:
                opacity = 0
            
            color = QColor(205, 28, 24, opacity)
            pen = QPen(color, 3)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(
                center_x - radius, 
                center_y - radius, 
                radius * 2, 
                radius * 2
            )
        
        # Dibujar micrófono central
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(205, 28, 24))
        painter.drawEllipse(center_x - 30, center_y - 30, 60, 60)
        
        # Texto del micrófono (emoji)
        painter.setPen(QColor(255, 255, 255))
        font = painter.font()
        font.setPointSize(35)
        font.setFamily("Segoe UI Emoji")
        painter.setFont(font)
        painter.drawText(
            QRect(center_x - 30, center_y - 30, 60, 60),
            Qt.AlignCenter,
            " 🎙️ "
        )
        
        # Texto "Escuchando..."
        painter.setPen(QColor(205, 28, 24))
        font.setPointSize(12)
        font.setFamily("Segoe UI")
        font.setBold(True)
        painter.setFont(font)
        
        dots = [".", "..", "..."]