import os
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
import src.python.com.mlprograms.converter.converter as converter


if __name__ == '__main__':

    app = QApplication(sys.argv)

    # CSS laden
    resources_dir = "../../../../resources/"
    css_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__), resources_dir + "styles/styles.css")
    )

    try:
        with open(css_file, "r") as file:
            app.setStyleSheet(file.read())

    except FileNotFoundError:
        print(f"Die CSS-Datei wurde nicht gefunden: {css_file}")
        sys.exit(1)

    main_window = converter.UnitConverterApp()
    main_window.show()
    sys.exit(app.exec())