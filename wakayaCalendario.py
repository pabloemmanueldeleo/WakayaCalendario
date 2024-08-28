from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QDialog, QLineEdit, QGridLayout, QTabWidget, QTextEdit, QFileDialog
)
from PySide6.QtCore import Qt, QTranslator, QLocale, QCoreApplication
from PySide6.QtGui import QPixmap
from datetime import datetime, timedelta, date
import calendar

class MosaicWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()

        # Agregar campos de título, imagen y descripción
        self.title_label = QLabel(self.tr("Title"))
        self.title_input = QLineEdit()

        self.image_label = QLabel(self.tr("No image loaded"))
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(150, 150)
        self.image_button = QPushButton(self.tr("Load Image"))
        self.image_button.clicked.connect(self.load_image)

        self.description_label = QLabel(self.tr("Description"))
        self.description_input = QTextEdit()

        self.edit_button = QPushButton(self.tr("Edit Content"))
        self.edit_button.clicked.connect(self.edit_content)

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.title_input)
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.image_button)
        self.layout.addWidget(self.description_label)
        self.layout.addWidget(self.edit_button)

        self.setLayout(self.layout)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, self.tr("Select Image"), "", self.tr("Images (*.png *.jpg *.jpeg)"))
        if file_name:
            pixmap = QPixmap(file_name)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))

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

class WeeklyPlannerWidget(QWidget):
    def __init__(self, parent=None, days=[]):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.layout.setSpacing(2)
        
        # Asegurar que la cuadrícula tenga 7 columnas (días de la semana)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)
        self.layout.setColumnStretch(3, 1)
        self.layout.setColumnStretch(4, 1)
        self.layout.setColumnStretch(5, 1)
        self.layout.setColumnStretch(6, 1)

        for i, day in enumerate(days):
            row = i // 7  # Filas de la cuadrícula
            col = i % 7   # Columnas de la cuadrícula
            day_layout = QVBoxLayout()
            label = QLabel(day.strftime("%a %d"))
            label.setAlignment(Qt.AlignCenter)
            day_layout.addWidget(label)

            for j in range(3):  # 3 slots per day as an example
                mosaic = MosaicWidget(self)
                day_layout.addWidget(mosaic)
            
            day_container = QWidget()
            day_container.setLayout(day_layout)
            self.layout.addWidget(day_container, row, col)

        # Rellenar días vacíos al principio o al final del mes
        self.fill_empty_days(days)

    def fill_empty_days(self, days):
        first_day_of_month = days[0].weekday()
        last_day_of_month = days[-1].weekday()

        # Rellenar días vacíos antes del primer día del mes
        for i in range(first_day_of_month):
            empty_label = QLabel("")
            self.layout.addWidget(empty_label, 0, i)

        # Rellenar días vacíos después del último día del mes
        for i in range(last_day_of_month + 1, 7):
            empty_label = QLabel("")
            self.layout.addWidget(empty_label, len(days) // 7, i)

class CalendarWidget(QMainWindow):
    def __init__(self, year=2024):
        super().__init__()
        self.setWindowTitle(self.tr(f"Yearly Planner - {year}"))
        self.setGeometry(100, 100, 1200, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.tab_widget = QTabWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.tab_widget)

        # Crear pestañas para cada mes
        months = [
            self.tr("January"), self.tr("February"), self.tr("March"), self.tr("April"), self.tr("May"), self.tr("June"),
            self.tr("July"), self.tr("August"), self.tr("September"), self.tr("October"), self.tr("November"), self.tr("December")
        ]

        for month_index in range(1, 13):
            first_day = date(year, month_index, 1)
            _, days_in_month = calendar.monthrange(year, month_index)
            days = [first_day + timedelta(days=i) for i in range(days_in_month)]

            weekly_planner = self.create_weekly_planner(days)
            self.tab_widget.addTab(weekly_planner, months[month_index - 1])

    def create_weekly_planner(self, days):
        weekly_planner_widget = QWidget()
        layout = QVBoxLayout(weekly_planner_widget)
        week_days = []

        for i, day in enumerate(days):
            week_days.append(day)
            if day.weekday() == 6 or i == len(days) - 1:  # Fin de la semana (Domingo) o fin del mes
                weekly_planner = WeeklyPlannerWidget(self, days=week_days)
                layout.addWidget(weekly_planner)
                week_days = []

        return weekly_planner_widget

if __name__ == "__main__":
    app = QApplication([])

    # Cargar traducción
    translator = QTranslator()
    locale = QLocale.system().name()  # Usa el locale del sistema
    print(locale, QLocale.system().uiLanguages())
    if translator.load(f"translations_{locale}.qm"):
        app.installTranslator(translator)

    window = CalendarWidget(2024)  # Pasar el año que desees
    window.show()

    app.exec()
