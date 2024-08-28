import sys
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QDialog, QLineEdit, QGridLayout, QTabWidget, QTextEdit, QFileDialog
)
from PySide6.QtCore import Qt, QTranslator, QLocale, QCoreApplication
from PySide6.QtGui import QPixmap, QIcon, QFont
from datetime import date, timedelta
import calendar

# Global variable to manage the instance
window_instance = None

def load_config():
    """Load the configuration file for UI settings."""
    try:
        with open("config.json", "r") as file:
            config = json.load(file)
    except FileNotFoundError:
        print("Configuration file not found. Using default settings.")
        config = {}
    return config

config = load_config()

class MosaicWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = config
        self.layout = QVBoxLayout()

        # Campos de título, imagen y descripción
        self.title_label = QLabel(self.tr("Title"))
        self.title_input = QLineEdit()
        self.image_button = QPushButton(self.tr("Load Image"))
        self.image_button.setFixedSize(*self.config.get("field_size", [300, 300]))
        self.image_button.clicked.connect(self.load_image)

        self.description_label = QLabel(self.tr("Description"))
        self.description_input = QTextEdit()

        self.edit_button = QPushButton(self.tr("Edit Content"))
        self.edit_button.clicked.connect(self.edit_content)

        # Aplicar estilos
        self.apply_styles()

        # Añadir widgets al layout
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.title_input)
        self.layout.addWidget(self.image_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.description_label)
        self.layout.addWidget(self.description_input)
        self.layout.addWidget(self.edit_button)

        self.setLayout(self.layout)

    def apply_styles(self):
        """Apply styles from the configuration file."""
        font_size = self.config.get("font_size", 12)
        font_color = self.config.get("font_color", "#333333")
        bg_color = self.config.get("background_color", "#f0f0f0")
        button_color = self.config.get("button_color", "#4CAF50")
        button_text_color = self.config.get("button_text_color", "#ffffff")
        title_font = self.config.get("title_font", "Arial")
        title_font_size = self.config.get("title_font_size", 14)
        title_color = self.config.get("title_color", "#000000")

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                font-size: {font_size}px;
                color: {font_color};
            }}
            QLabel {{
                font-size: {font_size}px;
                color: {font_color};
            }}
            QPushButton {{
                background-color: {button_color};
                color: {button_text_color};
                border: none;
                border-radius: 8px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
            QLineEdit, QTextEdit {{
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 4px;
            }}
        """)
        self.title_label.setFont(QFont(title_font, title_font_size))
        self.title_label.setStyleSheet(f"color: {title_color};")

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, self.tr("Select Image"), "", self.tr("Images (*.png *.jpg *.jpeg)"))
        if file_name:
            pixmap = QPixmap(file_name)
            icon = QIcon(pixmap.scaled(self.image_button.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.image_button.setIcon(icon)
            self.image_button.setIconSize(self.image_button.size())

    def edit_content(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr("Edit Content"))
        layout = QVBoxLayout()

        title_input = QLineEdit()
        title_input.setText(self.title_input.text())

        description_input = QTextEdit()
        description_input.setText(self.description_input.toPlainText())

        save_button = QPushButton(self.tr("Save"))
        save_button.clicked.connect(lambda: self.save_content(dialog, title_input.text(), description_input.toPlainText()))

        layout.addWidget(QLabel(self.tr("Edit Title")))
        layout.addWidget(title_input)
        layout.addWidget(QLabel(self.tr("Edit Description")))
        layout.addWidget(description_input)
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.exec()

    def save_content(self, dialog, new_title, new_description):
        self.title_input.setText(new_title)
        self.description_input.setText(new_description)
        dialog.accept()


class MonthlyPlannerWidget(QWidget):
    def __init__(self, days):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # Encabezados de los días de la semana
        header_layout = QHBoxLayout()
        days_of_week = [self.tr("Mon"), self.tr("Tue"), self.tr("Wed"), self.tr("Thu"),
                        self.tr("Fri"), self.tr("Sat"), self.tr("Sun")]
        for day in days_of_week:
            header_label = QLabel(day)
            header_label.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(header_label)

        # Grilla para los días del mes
        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)

        # Crear una cuadrícula de 6 filas x 7 columnas
        total_cells = 6 * 7
        first_day_index = days[0].weekday()  # Índice del primer día (0=Monday, ..., 6=Sunday)

        # Añadir celdas vacías antes del primer día del mes
        day_counter = 1
        for cell in range(total_cells):
            row = cell // 7
            col = cell % 7

            if cell < first_day_index or day_counter > len(days):
                grid_layout.addWidget(QLabel(""), row, col)  # Celdas vacías
            else:
                # Crear mosaico para cada día del mes
                day = days[day_counter - 1]
                day_layout = QVBoxLayout()
                label = QLabel(day.strftime("%d %b %Y"))
                label.setAlignment(Qt.AlignCenter)
                day_layout.addWidget(label)

                mosaic = MosaicWidget(self)
                day_layout.addWidget(mosaic)

                day_container = QWidget()
                day_container.setLayout(day_layout)
                grid_layout.addWidget(day_container, row, col)

                day_counter += 1

        # Agregar encabezados y grilla al layout principal
        self.layout.addLayout(header_layout)
        self.layout.addLayout(grid_layout)


class CalendarWidget(QMainWindow):
    def __init__(self, year=2024):
        super().__init__()
        self.setWindowTitle(self.tr(f"Yearly Planner - {year}"))
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.tab_widget = QTabWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.tab_widget)

        # Crear pestañas para cada mes
        months = [
            self.tr("January"), self.tr("February"), self.tr("March"), self.tr("April"),
            self.tr("May"), self.tr("June"), self.tr("July"), self.tr("August"),
            self.tr("September"), self.tr("October"), self.tr("November"), self.tr("December")
        ]

        for month_index in range(1, 13):
            first_day = date(year, month_index, 1)
            _, days_in_month = calendar.monthrange(year, month_index)
            days = [first_day + timedelta(days=i) for i in range(days_in_month)]

            monthly_planner = MonthlyPlannerWidget(days)
            self.tab_widget.addTab(monthly_planner, months[month_index - 1])


def open_single_instance():
    global window_instance
    if window_instance is not None:
        window_instance.close()  # Close the previous instance if it exists

    window_instance = CalendarWidget(2024)
    window_instance.show()


if __name__ == "__main__":
    app = QApplication([])

    # Cargar traducción
    translator = QTranslator()
    locale = QLocale.system().name()
    if translator.load(f"translations_{locale}.qm"):
        app.installTranslator(translator)

    open_single_instance()  # Open a single instance of the window

    sys.exit(app.exec())
