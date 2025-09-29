# logic/ocr_processor.py
"""
Módulo para procesamiento OCR de imágenes matemáticas
Soporta múltiples engines: pix2tex, Tesseract
"""

import os
from PIL import Image


class OCRProcessor:
    """Procesador principal de OCR para imágenes matemáticas"""
    
    def __init__(self):
        self.available_methods = self._check_available_methods()
    
    def _check_available_methods(self):
        """Verificar qué métodos OCR están disponibles"""
        methods = []
        
        # Verificar pix2tex
        try:
            import pix2tex
            methods.append("pix2tex")
        except ImportError:
            pass
        
        # Verificar pytesseract
        try:
            import pytesseract
            methods.append("tesseract")
        except ImportError:
            pass
        
        return methods
    
    def process_image(self, image_path):
        """
        Procesar imagen con el mejor método disponible
        
        Returns:
            dict: {"latex": str, "method": str, "success": bool, "error": str}
        """
        if not os.path.exists(image_path):
            return {
                "latex": "",
                "method": "",
                "success": False,
                "error": "Archivo de imagen no encontrado"
            }
        
        # Intentar pix2tex primero (más preciso)
        if "pix2tex" in self.available_methods:
            try:
                result = self._process_with_pix2tex(image_path)
                return {
                    "latex": result,
                    "method": "pix2tex",
                    "success": True,
                    "error": ""
                }
            except Exception as e:
                print(f"pix2tex falló: {e}")
        
        # Fallback a Tesseract
        if "tesseract" in self.available_methods:
            try:
                result = self._process_with_tesseract(image_path)
                return {
                    "latex": result,
                    "method": "Tesseract OCR",
                    "success": True,
                    "error": ""
                }
            except Exception as e:
                print(f"Tesseract falló: {e}")
        
        # No hay métodos disponibles
        return {
            "latex": "",
            "method": "",
            "success": False,
            "error": self._get_installation_message()
        }
    
    def _process_with_pix2tex(self, image_path):
        """Procesamiento usando pix2tex"""
        from pix2tex.cli import LatexOCR
        
        model = LatexOCR()
        img = Image.open(image_path)
        latex_code = model(img)
        return latex_code
    
    def _process_with_tesseract(self, image_path):
        """Procesamiento usando Tesseract OCR"""
        import pytesseract
        
        # Configurar Tesseract en Windows si es necesario
        self._configure_tesseract()
        
        # Procesar imagen
        image = Image.open(image_path)
        image = image.convert('L')  # Escala de grises
        
        # OCR con configuración optimizada para matemáticas
        text = pytesseract.image_to_string(
            image,
            config='--psm 6 -c tessedit_char_whitelist=0123456789+-*/=()[]{}abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,<>^_'
        )
        
        # Convertir a LaTeX básico
        return self._convert_to_latex(text)
    
    def _configure_tesseract(self):
        """Configurar ruta de Tesseract en Windows"""
        if os.name != 'nt':  # Solo para Windows
            return
            
        import pytesseract
        
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME')),
            'tesseract'  # En PATH
        ]
        
        for path in possible_paths:
            if path == 'tesseract' or os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break
    
    def _convert_to_latex(self, text):
        """Convertir texto plano a LaTeX básico"""
        if not text.strip():
            return text
        
        # Diccionario de conversiones
        conversions = {
            '∞': r'\infty', '∑': r'\sum', '∫': r'\int', '√': r'\sqrt',
            'π': r'\pi', 'θ': r'\theta', 'α': r'\alpha', 'β': r'\beta',
            'γ': r'\gamma', '≤': r'\leq', '≥': r'\geq', '≠': r'\neq',
            '∈': r'\in', '⊆': r'\subseteq', 'log': r'\log', 'ln': r'\ln',
            'sin': r'\sin', 'cos': r'\cos', 'tan': r'\tan',
        }
        
        latex_text = text
        for symbol, latex in conversions.items():
            latex_text = latex_text.replace(symbol, latex)
        
        # Envolver en delimitadores matemáticos si contiene comandos LaTeX
        if any(cmd in latex_text for cmd in ['\\', 'frac', 'sqrt', 'sum', 'int']):
            latex_text = f"$${latex_text}$$"
        
        return latex_text
    
    def _get_installation_message(self):
        """Mensaje de ayuda para instalación"""
        return (
            "No hay métodos OCR disponibles.\n\n"
            "Instala alguno de estos:\n"
            "1. pip install pix2tex (recomendado para matemáticas)\n"
            "2. pip install pytesseract (requiere Tesseract instalado)\n\n"
            "Para Tesseract en Windows:\n"
            "- Descarga desde: https://github.com/UB-Mannheim/tesseract/wiki\n"
            "- O usa: winget install UB-Mannheim.TesseractOCR"
        )
    
    def get_available_methods(self):
        """Obtener lista de métodos disponibles"""
        return self.available_methods.copy()
    
    def is_ready(self):
        """Verificar si hay al menos un método disponible"""
        return len(self.available_methods) > 0