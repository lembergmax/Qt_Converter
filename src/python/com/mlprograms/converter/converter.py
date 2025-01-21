import json
import os

from PyQt6.QtCore import Qt, pyqtSlot, QRect
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QListWidget

GEOMETRY_FILE = "window_geometry.json"
HISTORY_FILE = "history.json"

# Utility-Funktionen
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as file:
            return json.load(file)
    return []


def save_history(history):
    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)


def add_to_history(conversion):
    history = load_history()
    history.append(conversion)
    save_history(history)


def save_geometry_to_file(geometry):
    data = {
        "x": geometry.x(),
        "y": geometry.y(),
        "width": geometry.width(),
        "height": geometry.height(),
    }
    with open(GEOMETRY_FILE, "w") as file:
        json.dump(data, file)


def load_geometry_from_file():
    if os.path.exists(GEOMETRY_FILE):
        with open(GEOMETRY_FILE, "r") as file:
            return json.load(file)
    return None

class UnitConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.weight_converter = None
        self.volume_converter = None
        self.area_converter = None
        self.length_converter = None

        self.setWindowTitle("Einheitenumrechner")

        # Lade Geometrie aus Datei oder setze Standardwerte
        geometry = load_geometry_from_file()
        if geometry:
            self.setGeometry(geometry["x"], geometry["y"], geometry["width"], geometry["height"])
        else:
            self.setGeometry(100, 100, 800, 800)

        self.last_geometry = self.geometry()

        layout = QVBoxLayout()

        # Überschrift
        self.label = QLabel("Wähle die Umrechnungsart")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        layout.addWidget(self.label)

        # Buttons für Umrechnungsarten
        self.length_button = QPushButton("Längen")
        self.area_button = QPushButton("Flächen")
        self.volume_button = QPushButton("Volumen")
        self.weight_button = QPushButton("Gewicht")

        self.length_button.clicked.connect(self.open_length_converter)
        self.area_button.clicked.connect(self.open_area_converter)
        self.volume_button.clicked.connect(self.open_volume_converter)
        self.weight_button.clicked.connect(self.open_weight_converter)

        layout.addWidget(self.length_button)
        layout.addWidget(self.area_button)
        layout.addWidget(self.volume_button)
        layout.addWidget(self.weight_button)

        # Verlaufsanzeige
        self.history_label = QLabel("Gesamter Verlauf:")
        layout.addWidget(self.history_label)
        self.history_list = QListWidget(self)
        layout.addWidget(self.history_list)

        # Knopf zum Verlauf löschen
        self.clear_button = QPushButton("Verlauf löschen")
        self.clear_button.clicked.connect(self.clear_history)
        layout.addWidget(self.clear_button)

        self.update_history_view()

        self.setLayout(layout)

    def update_history_view(self):
        history = load_history()
        self.history_list.clear()

        # Die neuesten Einträge oben anzeigen
        for entry in reversed(history):
            self.history_list.addItem(
                f"[{entry['category']}] {entry['value']} {entry['from_unit']} -> {entry['result']} {entry['to_unit']}"
            )

    def clear_history(self):
        with open(HISTORY_FILE, "w") as file:
            json.dump([], file)
        self.update_history_view()

    def save_geometry(self):
        self.last_geometry = self.geometry()
        save_geometry_to_file(self.last_geometry)

    @pyqtSlot()
    def open_length_converter(self):
        self.save_geometry()
        self.hide()
        self.length_converter = LengthConverter(self, self.last_geometry)
        self.length_converter.show()

    @pyqtSlot()
    def open_area_converter(self):
        self.save_geometry()
        self.hide()
        self.area_converter = AreaConverter(self, self.last_geometry)
        self.area_converter.show()

    @pyqtSlot()
    def open_volume_converter(self):
        self.save_geometry()
        self.hide()
        self.volume_converter = VolumeConverter(self, self.last_geometry)
        self.volume_converter.show()

    @pyqtSlot()
    def open_weight_converter(self):
        self.save_geometry()
        self.hide()
        self.weight_converter = WeightConverter(self, self.last_geometry)
        self.weight_converter.show()

class BaseConverter(QWidget):
    def __init__(self, parent, geometry, title, units, category):
        super().__init__()
        self.setWindowTitle(title)
        self.parent = parent
        self.units = units
        self.category = category

        self.setGeometry(geometry if geometry else QRect(100, 100, 800, 800))

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.input_label = QLabel("Eingabe:")
        layout.addWidget(self.input_label)

        self.input_value = QLineEdit()
        layout.addWidget(self.input_value)

        self.from_unit_label = QLabel("Von Einheit:")
        layout.addWidget(self.from_unit_label)
        self.from_unit = QComboBox()
        self.from_unit.addItems(self.units)
        layout.addWidget(self.from_unit)

        self.to_unit_label = QLabel("Zu Einheit:")
        layout.addWidget(self.to_unit_label)
        self.to_unit = QComboBox()
        self.to_unit.addItems(self.units)
        layout.addWidget(self.to_unit)

        self.convert_button = QPushButton("Umrechnen")
        self.convert_button.clicked.connect(self.convert)
        layout.addWidget(self.convert_button)

        self.result_label = QLabel("Ergebnis:")
        layout.addWidget(self.result_label)

        self.back_button = QPushButton("Zurück")
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.history_label = QLabel(f"Verlauf ({self.category}):")
        layout.addWidget(self.history_label)
        self.history_list = QListWidget(self)
        layout.addWidget(self.history_list)
        self.update_history_view()

        self.setLayout(layout)

    def update_history_view(self):
        history = load_history()
        filtered_history = [entry for entry in history if entry["category"] == self.category]
        self.history_list.clear()
        for entry in reversed(filtered_history):
            self.history_list.addItem(f"{entry['value']} {entry['from_unit']} -> {entry['result']} {entry['to_unit']}")

    @pyqtSlot()
    def convert(self):
        try:
            value = float(self.input_value.text().replace(",", "."))
            from_unit = self.from_unit.currentText().split()[0]
            to_unit = self.to_unit.currentText().split()[0]
            factors = self.get_conversion_factors()

            if from_unit not in factors or to_unit not in factors:
                raise ValueError("Ungültige Einheit")

            value_in_base = value * factors[from_unit]
            converted_value = value_in_base / factors[to_unit]
            self.result_label.setText(f"Ergebnis: {converted_value:.4f} {to_unit}")

            add_to_history(
                {
                    "category": self.category,
                    "value": value,
                    "from_unit": from_unit,
                    "to_unit": to_unit,
                    "result": converted_value,
                }
            )
            self.update_history_view()
        except ValueError as e:
            QMessageBox.critical(self, "Fehler", f"Ungültige Eingabe! Gib eine gültige Zahl ein.\n\n({e})")

    @pyqtSlot()
    def go_back(self):
        self.parent.last_geometry = self.geometry()
        self.close()
        self.parent.update_history_view()
        self.parent.setGeometry(self.parent.last_geometry)
        self.parent.show()


class LengthConverter(BaseConverter):
    def __init__(self, parent, geometry):
        super().__init__(parent, geometry, 'Längenumrechner',
                         ['m (Meter)', 'km (Kilometer)', 'cm (Zentimeter)', 'mm (Millimeter)',
                          'ft (Fuß)', 'in (Zoll)', 'yd (Yards)'], 'Gewicht')

    def get_conversion_factors(self):
        return {
            'm': 1,
            'km': 1000,
            'cm': 0.01,
            'mm': 0.001,
            'ft': 0.3048,
            'in': 0.0254,
            'yd': 0.9144
        }


class AreaConverter(BaseConverter):
    def __init__(self, parent, geometry):
        super().__init__(parent, geometry, 'Flächenumrechner',
                         ['m² (Quadratmeter)', 'km² (Quadratkilometer)', 'ha (Hektar)',
                          'ft² (Quadratfuß)', 'in² (Quadratzoll)', 'yd² (Quadratyard)'], 'Fläche')

    def get_conversion_factors(self):
        return {
            'm²': 1,
            'km²': 1_000_000,
            'ha': 10_000,
            'ft²': 0.092903,
            'in²': 0.00064516,
            'yd²': 0.836127
        }


class VolumeConverter(BaseConverter):
    def __init__(self, parent, geometry):
        super().__init__(parent, geometry, 'Volumenumrechner',
                         ['m³ (Kubikmeter)', 'l (Liter)', 'ml (Milliliter)',
                          'gal (Gallone)', 'ft³ (Kubikfuß)', 'in³ (Kubikzoll)'], 'Volumen')

    def get_conversion_factors(self):
        return {
            'm³': 1,
            'l': 0.001,
            'ml': 0.000001,
            'gal': 0.00378541,
            'ft³': 0.0283168,
            'in³': 0.0000163871
        }


class WeightConverter(BaseConverter):
    def __init__(self, parent, geometry):
        super().__init__(parent, geometry, 'Gewichtsumrechner',
                         ['kg (Kilogramm)', 'g (Gramm)', 'mg (Milligramm)',
                          'lb (Pfund)', 'oz (Unze)'], 'Gewicht')

    def get_conversion_factors(self):
        return {
            'kg': 1,
            'g': 0.001,
            'mg': 0.000001,
            'lb': 0.453592,
            'oz': 0.0283495
        }