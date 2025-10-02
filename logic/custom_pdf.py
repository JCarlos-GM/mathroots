from fpdf import FPDF
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel
import os
import datetime

class CustomPDF(FPDF):
    def __init__(self, title, filename):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_title(title)
        self.filename = filename

    def header(self):
        # Logo (asegúrate de tener un archivo 'logo.png' en tu proyecto)
        # Puedes reemplazar 'logo.png' con la ruta a tu logo real
        if os.path.exists("logo.png"):
            self.image('logo.png', x=10, y=8, w=30)
        
        # Título de la aplicación
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'MathRoots: Informe de Análisis', 0, 0, 'C')
        
        # Línea de separación
        self.ln(12)
        self.set_line_width(0.5)
        self.line(10, 20, 200, 20)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
        
    def add_widget_to_pdf(self, widget, title):
        # Título del panel
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, title, ln=1, align='C')
        self.ln(5)

        # Capturar el widget como una imagen
        pixmap = widget.grab()
        image = pixmap.toImage()
        
        if image.isNull():
            return

        temp_image_path = "temp_widget_img.png"
        image.save(temp_image_path)
        
        img_width = image.width()
        img_height = image.height()
        
        page_width = 210
        page_height = 297

        # Escalar la imagen para que quepa en la página
        ratio = min((page_width - 20) / img_width, (page_height - 35) / img_height)
        new_width = img_width * ratio
        new_height = img_height * ratio
        
        x_pos = (page_width - new_width) / 2
        
        # Colocar la imagen y agregar un espacio
        self.image(temp_image_path, x=x_pos, y=self.get_y(), w=new_width, h=new_height)
        self.ln(new_height + 5)
        
        # Eliminar archivo temporal
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
            
    def generate(self):
        try:
            self.output(self.filename)
            return True
        except Exception as e:
            print(f"Error al guardar el PDF: {e}")
            return False

def create_report_cover(pdf, equation):
    pdf.add_page()
    pdf.set_font('Arial', 'B', 28)
    pdf.ln(50)
    pdf.multi_cell(0, 15, 'Informe de Raíces de Ecuaciones', 0, 'C')

    pdf.ln(30)
    pdf.set_font('Arial', '', 18)
    pdf.cell(0, 10, f'Ecuación Analizada:', 0, 1, 'C')
    pdf.set_font('Arial', 'B', 20)
    pdf.ln(5)
    pdf.multi_cell(0, 10, f"f(x) = {equation}", 0, 'C')

    pdf.ln(50)
    pdf.set_font('Arial', '', 12)
    # Reemplaza la línea problemática con esta
    current_date = datetime.date.today().strftime("%d/%m/%Y")
    pdf.cell(0, 10, f"Fecha del Informe: {current_date}", 0, 1, 'C')

    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, "Generado por MathRoots App", 0, 1, 'C')
    pdf.add_page()