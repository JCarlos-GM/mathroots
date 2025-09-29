"""
Módulo de estilos minimalistas para tablas QTableView
Basado en el tema light_red de qt-material con diseño moderno
"""

from PySide6.QtWidgets import QAbstractItemView, QHeaderView
from PySide6.QtCore import Qt


class TableStyleManager:
    """
    Gestor de estilos minimalistas para tablas QTableView
    """

    @staticmethod
    def get_minimal_light_red_style():
        """
        Retorna el estilo CSS minimalista y moderno para tablas

        Returns:
            str: Cadena CSS con el estilo completo
        """
        return """
            /* Estilo principal minimalista */
            QTableView {
                background-color: #ffffff;
                color: #1a1a1a;
                alternate-background-color: #fafafa;
                border: none;
                gridline-color: #f0f0f0;
                selection-background-color: rgba(244, 67, 54, 0.1);
                selection-color: #d32f2f;
                font-size: 18px;
                font-weight: 400;
                outline: none;
                border-radius: 8px;
            }
            
            /* Filas seleccionadas con diseño sutil */
            QTableView::item:selected {
                background-color: rgba(244, 67, 54, 0.08);
                color: #d32f2f;
                border: none;
            }
            
            /* Hover minimalista */
            QTableView::item:hover {
                background-color: #f8f8f8;
                transition: background-color 0.2s ease;
            }
            
            /* Header moderno y limpio */
            QHeaderView::section {
                background-color: #ffffff;
                color: #424242;
                padding: 16px 20px;
                border: none;
                border-bottom: 2px solid #f44336;
                font-weight: bold; /* <-- Puesto en negrita */
                font-size: 18px;
                text-align: center; /* <-- Centrado */
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            /* Header hover sutil */
            QHeaderView::section:hover {
                background-color: #fafafa;
                color: #d32f2f;
            }
            
            /* Header activo */
            QHeaderView::section:pressed {
                background-color: #f5f5f5;
                color: #b71c1c;
            }
            
            /* Scrollbar ultra minimalista */
            QScrollBar:vertical {
                background-color: transparent;
                width: 6px;
                border: none;
                margin: 0px;
            }
            
            /* Handle del scrollbar minimalista */
            QScrollBar::handle:vertical {
                background-color: rgba(189, 189, 189, 0.3);
                min-height: 30px;
                border-radius: 3px;
                margin: 0px;
            }
            
            /* Handle hover más visible */
            QScrollBar::handle:vertical:hover {
                background-color: rgba(244, 67, 54, 0.4);
            }
            
            /* Handle activo */
            QScrollBar::handle:vertical:pressed {
                background-color: rgba(244, 67, 54, 0.6);
            }
            
            /* Sin botones en scrollbar */
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            
            /* Scrollbar horizontal minimalista */
            QScrollBar:horizontal {
                background-color: transparent;
                height: 6px;
                border: none;
                margin: 0px;
            }
            
            /* Handle horizontal minimalista */
            QScrollBar::handle:horizontal {
                background-color: rgba(189, 189, 189, 0.3);
                min-width: 30px;
                border-radius: 3px;
                margin: 0px;
            }
            
            /* Handle horizontal hover */
            QScrollBar::handle:horizontal:hover {
                background-color: rgba(244, 67, 54, 0.4);
            }
            
            /* Handle horizontal activo */
            QScrollBar::handle:horizontal:pressed {
                background-color: rgba(244, 67, 54, 0.6);
            }
            
            /* Sin botones horizontales */
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
                width: 0px;
            }
            
            /* Área de scrollbar limpia */
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical,
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: transparent;
            }
        """

    @staticmethod
    def apply_minimal_style_to_table(table):
        """
        Aplica el estilo minimalista a una tabla específica

        Args:
            table (QTableView): La tabla a la que aplicar el estilo
        """
        if table is None:
            return

        # Aplicar el estilo CSS
        table.setStyleSheet(TableStyleManager.get_minimal_light_red_style())

        # Configurar comportamiento moderno
        TableStyleManager._configure_modern_behavior(table)

    @staticmethod
    def _configure_modern_behavior(table):
        """
        Configura el comportamiento moderno de una tabla

        Args:
            table (QTableView): La tabla a configurar
        """
        # Habilitar filas alternadas sutiles
        table.setAlternatingRowColors(True)

        # Configurar selección moderna
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)

        # Sin bordes en las celdas para look minimalista
        table.setShowGrid(False)

        # Configurar el header moderno
        header = table.horizontalHeader()
        if header:
            # TODAS las columnas se estiran para llenar el ancho total
            header.setStretchLastSection(True)
            header.setSectionResizeMode(QHeaderView.Stretch)
            header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            header.setMinimumHeight(50)
            header.setSectionsClickable(True)

        # Header vertical minimalista
        v_header = table.verticalHeader()
        if v_header:
            v_header.setVisible(False)  # Ocultar números de fila para look más limpio

        # Espaciado más amplio entre filas
        table.verticalHeader().setDefaultSectionSize(45)

        # Configurar el ajuste automático de columnas para llenar todo el ancho
        TableStyleManager._setup_column_resize_full_width(table)

    @staticmethod
    def apply_to_multiple_tables(ui_object, table_names):
        """
        Aplica el estilo a múltiples tablas de un objeto UI

        Args:
            ui_object: Objeto UI que contiene las tablas
            table_names (list): Lista con los nombres de las tablas a estilizar
        """
        for table_name in table_names:
            if hasattr(ui_object, table_name):
                table = getattr(ui_object, table_name)
                TableStyleManager.apply_minimal_style_to_table(table)

    @staticmethod
    def apply_to_ui(ui_object):
        """
        Aplica el estilo automáticamente a tablas comunes en un objeto UI

        Args:
            ui_object: Objeto UI que contiene las tablas
        """
        # Lista de nombres comunes de tablas
        common_table_names = [
            "tabla_iteraciones",
            "tabla_resultados",
            "tabla_historial",
            "tabla_datos",
            "table_iterations",
            "table_results",
            "table_history",
            "table_data",
        ]

        TableStyleManager.apply_to_multiple_tables(ui_object, common_table_names)

    @staticmethod
    def _setup_column_resize_full_width(table):
        """
        Configura todas las columnas para que se ajusten al ancho total de la tabla

        Args:
            table (QTableView): La tabla a configurar
        """
        header = table.horizontalHeader()
        if header:
            # Todas las columnas se estiran proporcionalmente para llenar todo el ancho
            header.setSectionResizeMode(QHeaderView.Stretch)
            header.setStretchLastSection(True)

            # Opcional: establecer anchos mínimos para evitar columnas demasiado pequeñas
            if table.model():
                column_count = table.model().columnCount()
                min_width = (
                    max(100, table.width() // max(column_count, 1) // 2)
                    if column_count > 0
                    else 100
                )

                for i in range(column_count):
                    header.setMinimumSectionSize(min_width)

    @staticmethod
    def _setup_column_resize(table):
        """
        MÉTODO ORIGINAL REEMPLAZADO - Ahora usa _setup_column_resize_full_width
        Mantener para compatibilidad hacia atrás
        """
        TableStyleManager._setup_column_resize_full_width(table)

    @staticmethod
    def set_column_resize_mode(table, mode="stretch"):
        """
        Configura el modo de redimensionamiento de columnas
        MODIFICADO: Por defecto usa 'stretch' para llenar todo el ancho

        Args:
            table (QTableView): La tabla a configurar
            mode (str): Modo de redimensionamiento:
                       'stretch' - Todas las columnas se estiran proporcionalmente (NUEVO DEFECTO)
                       'content' - Ajustar al contenido
                       'interactive' - Usuario puede redimensionar
                       'auto' - Automático según número de columnas (ahora usa stretch)
        """
        header = table.horizontalHeader()
        if not header:
            return

        if mode == "stretch" or mode == "auto":
            header.setSectionResizeMode(QHeaderView.Stretch)
            header.setStretchLastSection(True)
        elif mode == "content":
            header.setSectionResizeMode(QHeaderView.ResizeToContents)
        elif mode == "interactive":
            header.setSectionResizeMode(QHeaderView.Interactive)

    @staticmethod
    def force_full_width_columns(table):
        """
        NUEVO MÉTODO: Fuerza que todas las columnas ocupen todo el ancho disponible

        Args:
            table (QTableView): La tabla a configurar
        """
        header = table.horizontalHeader()
        if not header:
            return

        # Configurar para que todas las columnas se estiren
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStretchLastSection(True)

        # Asegurar que no hay scroll horizontal innecesario
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Actualizar el header
        header.update()


# Función de conveniencia para uso rápido - MODIFICADA
def apply_minimal_table_style(table_or_ui, table_names=None, column_mode="stretch"):
    """
    Función de conveniencia para aplicar estilos rápidamente
    MODIFICADO: Por defecto usa 'stretch' para columnas de ancho completo

    Args:
        table_or_ui: Puede ser una tabla individual o un objeto UI
        table_names (list, optional): Si table_or_ui es un UI, lista de nombres de tablas
        column_mode (str): Modo de redimensionamiento de columnas (por defecto 'stretch')
    """
    if hasattr(table_or_ui, "setStyleSheet"):
        # Es una tabla individual
        TableStyleManager.apply_minimal_style_to_table(table_or_ui)
        TableStyleManager.set_column_resize_mode(table_or_ui, column_mode)
        # Forzar ancho completo
        TableStyleManager.force_full_width_columns(table_or_ui)
    else:
        # Es un objeto UI
        if table_names:
            TableStyleManager.apply_to_multiple_tables(table_or_ui, table_names)
            # Aplicar modo de columnas a cada tabla
            for table_name in table_names:
                if hasattr(table_or_ui, table_name):
                    table = getattr(table_or_ui, table_name)
                    TableStyleManager.set_column_resize_mode(table, column_mode)
                    TableStyleManager.force_full_width_columns(table)
        else:
            TableStyleManager.apply_to_ui(table_or_ui)


# NUEVA función específica para ancho completo
def apply_full_width_table_style(table):
    """
    Aplica estilo minimalista con columnas que ocupan todo el ancho de la tabla

    Args:
        table (QTableView): La tabla a estilizar
    """
    TableStyleManager.apply_minimal_style_to_table(table)
    TableStyleManager.force_full_width_columns(table)
