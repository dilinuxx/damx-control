from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel,
    QPushButton, QFrame
)
from PyQt5.QtGui import QFont


class ChamberPage(QWidget):
    """
    Chamber environment + gas control page.
    Converted from create_chamber_page().
    Requires ChamberControl instance.
    """

    def __init__(self, chamber, parent=None):
        super().__init__(parent)

        self.chamber = chamber   # <-- hardware controller

        self.setStyleSheet("""
            QLabel{ color:white; }

            QFrame{
                background-color:#252f3d;
                border-radius:8px;
            }

            QPushButton{
                background-color:#5A9BF6;
                color:white;
                padding:8px;
                border-radius:6px;
                font-size:14px;
            }

            QPushButton:hover{
                background-color:#74b9ff;
            }
        """)

        main_layout = QVBoxLayout(self)

        title = QLabel("Chamber Environment")
        title.setStyleSheet("font-size:22px;font-weight:bold")
        main_layout.addWidget(title)

        main_layout.addWidget(self._create_atmosphere_panel())
        main_layout.addWidget(self._create_environment_panel())
        main_layout.addWidget(self._create_controls())

        main_layout.addStretch()

    # -----------------------
    # ATMOSPHERE PANEL
    # -----------------------
    def _create_atmosphere_panel(self):
        frame = QFrame()
        layout = QVBoxLayout(frame)

        title = QLabel("Atmosphere")
        title.setStyleSheet("font-size:16px;font-weight:bold")

        self.o2_label = QLabel("O2: 00 ppm")
        self.argon_label = QLabel("Argon Flow: 0 L/min")
        self.nitrogen_label = QLabel("Nitrogen Flow: 0 L/min")

        for lbl in [self.o2_label, self.argon_label, self.nitrogen_label]:
            lbl.setFont(QFont("Arial", 14))
            layout.addWidget(lbl)

        layout.insertWidget(0, title)
        return frame

    # -----------------------
    # ENVIRONMENT PANEL
    # -----------------------
    def _create_environment_panel(self):
        frame = QFrame()
        layout = QVBoxLayout(frame)

        title = QLabel("Environment")
        title.setStyleSheet("font-size:16px;font-weight:bold")

        self.pressure_label = QLabel("Chamber Pressure: 000 bar")
        self.humidity_label = QLabel("Humidity: 00%")
        self.temp_label = QLabel("Temperature: 00 °C")

        for lbl in [self.pressure_label, self.humidity_label, self.temp_label]:
            lbl.setFont(QFont("Arial", 14))
            layout.addWidget(lbl)

        layout.insertWidget(0, title)
        return frame

    # -----------------------
    # CONTROLS
    # -----------------------
    def _create_controls(self):
        frame = QFrame()
        layout = QGridLayout(frame)

        on_style = """
        QPushButton { background-color: lightgray; border:1px solid #555; padding:6px; border-radius:4px; }
        QPushButton:checked { background-color:#4CAF50; color:white; font-weight:bold; }
        """

        off_style = """
        QPushButton { background-color: lightgray; border:1px solid #555; padding:6px; border-radius:4px; }
        QPushButton:checked { background-color:#E53935; color:white; font-weight:bold; }
        """

        # ---------- VACUUM ----------
        vacuum_label = QLabel("VACUUM")
        vacuum_label.setStyleSheet("font-weight:bold;font-size:14px;")

        vacuum_on_btn = QPushButton("ON"); vacuum_off_btn = QPushButton("OFF")
        valve_open_btn = QPushButton("VALVE OPEN"); valve_close_btn = QPushButton("VALVE CLOSE")

        for b in [vacuum_on_btn, vacuum_off_btn, valve_open_btn, valve_close_btn]:
            b.setCheckable(True)

        vacuum_on_btn.setStyleSheet(on_style)
        valve_open_btn.setStyleSheet(on_style)
        vacuum_off_btn.setStyleSheet(off_style)
        valve_close_btn.setStyleSheet(off_style)

        vacuum_on_btn.clicked.connect(lambda: vacuum_off_btn.setChecked(False))
        vacuum_off_btn.clicked.connect(lambda: vacuum_on_btn.setChecked(False))
        valve_open_btn.clicked.connect(lambda: valve_close_btn.setChecked(False))
        valve_close_btn.clicked.connect(lambda: valve_open_btn.setChecked(False))

        vacuum_on_btn.clicked.connect(self.chamber.vacuum_on)
        vacuum_off_btn.clicked.connect(self.chamber.vacuum_off)
        valve_open_btn.clicked.connect(self.chamber.vacuum_valve_open)
        valve_close_btn.clicked.connect(self.chamber.vacuum_valve_close)

        layout.addWidget(vacuum_label, 0, 0)
        layout.addWidget(vacuum_on_btn, 1, 0)
        layout.addWidget(vacuum_off_btn, 2, 0)
        layout.addWidget(valve_open_btn, 3, 0)
        layout.addWidget(valve_close_btn, 4, 0)

        # ---------- ARGON ----------
        argon_label = QLabel("ARGON")
        argon_label.setStyleSheet("font-weight:bold;font-size:14px;")

        argon_on_btn = QPushButton("ON"); argon_off_btn = QPushButton("OFF")
        inlet_open = QPushButton("INLET OPEN"); inlet_close = QPushButton("INLET CLOSE")
        outlet_open = QPushButton("OUTLET OPEN"); outlet_close = QPushButton("OUTLET CLOSE")

        for b in [argon_on_btn, argon_off_btn, inlet_open, inlet_close, outlet_open, outlet_close]:
            b.setCheckable(True)

        argon_on_btn.setStyleSheet(on_style)
        inlet_open.setStyleSheet(on_style)
        outlet_open.setStyleSheet(on_style)
        argon_off_btn.setStyleSheet(off_style)
        inlet_close.setStyleSheet(off_style)
        outlet_close.setStyleSheet(off_style)

        argon_on_btn.clicked.connect(lambda: argon_off_btn.setChecked(False))
        argon_off_btn.clicked.connect(lambda: argon_on_btn.setChecked(False))
        inlet_open.clicked.connect(lambda: inlet_close.setChecked(False))
        inlet_close.clicked.connect(lambda: inlet_open.setChecked(False))
        outlet_open.clicked.connect(lambda: outlet_close.setChecked(False))
        outlet_close.clicked.connect(lambda: outlet_open.setChecked(False))

        argon_on_btn.clicked.connect(self.chamber.argon_on)
        argon_off_btn.clicked.connect(self.chamber.argon_off)
        inlet_open.clicked.connect(self.chamber.argon_inlet_open)
        inlet_close.clicked.connect(self.chamber.argon_inlet_close)
        outlet_open.clicked.connect(self.chamber.argon_outlet_open)
        outlet_close.clicked.connect(self.chamber.argon_outlet_close)

        layout.addWidget(argon_label, 0, 1)
        layout.addWidget(argon_on_btn, 1, 1)
        layout.addWidget(argon_off_btn, 2, 1)
        layout.addWidget(inlet_open, 3, 1)
        layout.addWidget(inlet_close, 4, 1)
        layout.addWidget(outlet_open, 5, 1)
        layout.addWidget(outlet_close, 6, 1)

        # ---------- SYSTEM ----------
        system_label = QLabel("SYSTEM")
        system_label.setStyleSheet("font-weight:bold;font-size:14px;")

        purge_btn = QPushButton("Start Purge")
        vent_btn = QPushButton("Vent Chamber")
        seal_btn = QPushButton("Seal Chamber")

        purge_btn.clicked.connect(self.chamber.start_purge)
        vent_btn.clicked.connect(self.chamber.vent_chamber)
        seal_btn.clicked.connect(self.chamber.seal_chamber)

        layout.addWidget(system_label, 0, 2)
        layout.addWidget(purge_btn, 1, 2)
        layout.addWidget(vent_btn, 2, 2)
        layout.addWidget(seal_btn, 3, 2)

        layout.setHorizontalSpacing(40)
        layout.setVerticalSpacing(10)

        return frame