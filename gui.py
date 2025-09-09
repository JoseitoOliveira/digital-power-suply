from PySide6.QtWidgets import QWidget, QLabel, QPushButton
from PySide6.QtGui import QPixmap, QCursor, QFont, QPainter
from PySide6.QtCore import Qt, QSize, Signal, QThread
from PySide6.QtSvg import QSvgRenderer
from power_supply import PowerSupply
import time


def fmt(x):
    x = float(x)
    d = len(str(int(x)))
    f = max(1, 4 - d)
    return f"{x:.{f}f}"


class MonitorThread(QThread):
    """Thread for monitoring power supply values"""

    values_updated = Signal(float, float)
    error_occurred = Signal(str)

    def __init__(self, power_supply):
        super().__init__()
        self.power_supply = power_supply
        self._running = True

    def run(self):
        while self._running:
            try:
                voltage = self.power_supply.get_voltage()
                current = self.power_supply.get_current()
                self.values_updated.emit(voltage, current)
            except Exception as e:
                self.error_occurred.emit(str(e))
            time.sleep(0.1)

    def stop(self):
        self._running = False


class PowerSupplyGUI(QWidget):
    def __init__(self, power_supply: PowerSupply):
        super().__init__()
        self.power_supply = power_supply

        self.setWindowFlags(
            Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowMinimizeButtonHint
            | Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.MSWindowsFixedSizeDialogHint
        )

        self.setWindowTitle("Power Supply")

        self.bg_pixmap = QPixmap("resources/background.png")
        self.bg = QLabel(self)
        self.bg.setPixmap(self.bg_pixmap)
        self.bg.resize(self.bg_pixmap.size())

        self.resize(self.bg_pixmap.size())

        # Button output (on/off)
        self.out_button = QPushButton("", self)
        self.out_off_icon = QPixmap("resources/out-off.png")
        self.out_on_icon = QPixmap("resources/out-on.png")
        self.out_button.setIcon(self.out_off_icon)
        self.out_button.setIconSize(self.out_off_icon.size())

        self.out_button.setGeometry(
            20,
            self.height() - self.out_off_icon.height() - 20,
            self.out_off_icon.width(),
            self.out_off_icon.height(),
        )

        button_style = "QPushButton {background-color: transparent; border: none;}"

        self.out_button.setStyleSheet(button_style)
        self.out_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.out_button.clicked.connect(self.toggle_power)

        self.button_size = QSize(70, 70)
        self.svg_renderer = QSvgRenderer("resources/button.svg")

        self.button_icon = QPixmap(self.button_size)
        self.button_icon.fill(Qt.GlobalColor.transparent)
        painter = QPainter(self.button_icon)
        self.svg_renderer.render(painter)
        painter.end()

        self.button_angles = {"v_course": 0, "v_fine": 0, "i_course": 0, "i_fine": 0}

        x_pos = self.width() - self.button_icon.width() - 12

        self.v_course_button = QPushButton("", self)
        self.v_course_button.setIcon(self.button_icon)
        self.v_course_button.setIconSize(self.button_size)
        self.v_course_button.setGeometry(x_pos, 15, self.button_icon.width(), self.button_icon.height())
        self.v_course_button.setStyleSheet(button_style)
        self.v_course_button.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
        self.v_course_button.installEventFilter(self)
        self.v_course_button.setProperty("button_id", "v_course")

        self.v_fine_button = QPushButton("", self)
        self.v_fine_button.setIcon(self.button_icon)
        self.v_fine_button.setIconSize(self.button_size)
        self.v_fine_button.setGeometry(x_pos, 106, self.button_icon.width(), self.button_icon.height())
        self.v_fine_button.setStyleSheet(button_style)
        self.v_fine_button.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
        self.v_fine_button.installEventFilter(self)
        self.v_fine_button.setProperty("button_id", "v_fine")

        self.i_course_button = QPushButton("", self)
        self.i_course_button.setIcon(self.button_icon)
        self.i_course_button.setIconSize(self.button_size)
        self.i_course_button.setGeometry(x_pos, 196, self.button_icon.width(), self.button_icon.height())
        self.i_course_button.setStyleSheet(button_style)
        self.i_course_button.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
        self.i_course_button.installEventFilter(self)
        self.i_course_button.setProperty("button_id", "i_course")

        self.i_fine_button = QPushButton("", self)
        self.i_fine_button.setIcon(self.button_icon)
        self.i_fine_button.setIconSize(self.button_size)
        self.i_fine_button.setGeometry(x_pos, 287, self.button_icon.width(), self.button_icon.height())
        self.i_fine_button.setStyleSheet(button_style)
        self.i_fine_button.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
        self.i_fine_button.installEventFilter(self)
        self.i_fine_button.setProperty("button_id", "i_fine")

        font = QFont("DSEG7 Modern", 40, italic=True)

        self.voltage_label = QLabel("0.000", self)
        self.voltage_label.setFont(font)
        self.voltage_label.setStyleSheet("color: white")
        self.voltage_label.setGeometry(20, 10, 210, 100)

        self.current_label = QLabel("0.000", self)
        self.current_label.setFont(font)
        self.current_label.setStyleSheet("color: white")
        self.current_label.setGeometry(20, 100, 210, 100)

        self.power_label = QLabel("0.000", self)
        self.power_label.setFont(font)
        self.power_label.setStyleSheet("color: white")
        self.power_label.setGeometry(20, 191, 210, 100)

        try:
            self.power_supply.connect()
        except Exception as e:
            print(f"Error connecting to power supply: {e}")

        self.monitor_thread = MonitorThread(self.power_supply)
        self.monitor_thread.values_updated.connect(self.on_values_updated)
        self.monitor_thread.start()

    def closeEvent(self, event):
        """Disconnect from power supply when window is closed"""
        if self.power_supply.is_output_on():
            self.monitor_thread.stop()
            self.monitor_thread.wait()
        self.power_supply.disconnect()
        super().closeEvent(event)

    def toggle_power(self):
        """Toggles the power supply output ON/OFF"""
        try:
            if self.power_supply.is_output_on():
                self.power_supply.output_off()
                self.out_button.setIcon(self.out_off_icon)
            else:
                self.power_supply.output_on()
                self.out_button.setIcon(self.out_on_icon)

        except Exception as e:
            print(f"Error toggling output state: {e}")

    def on_values_updated(self, voltage: float, current: float):
        """Callback to update interface values"""
        if self.power_supply.is_output_on():
            power = voltage * current
        else:
            power = 0

        self.voltage_label.setText(fmt(voltage))
        self.current_label.setText(fmt(current))
        self.power_label.setText(fmt(power))

    def adjust_value(self, button_id, delta):
        """Adjusts voltage and current values"""
        try:
            if button_id.startswith("v_"):
                step = 0.1 if button_id == "v_course" else 0.001
                current_voltage = self.power_supply.get_voltage()
                new_voltage = max(0, current_voltage + (step if delta > 0 else -step))
                self.power_supply.set_voltage(new_voltage)

            elif button_id.startswith("i_"):
                step = 0.1 if button_id == "i_course" else 0.001
                current_current = self.power_supply.get_current()
                new_current = max(0, current_current + (step if delta > 0 else -step))
                self.power_supply.set_current(new_current)

        except Exception as e:
            print(f"Error adjusting values: {e}")

    def update_from_power_supply(self):
        """Updates displays with power supply values"""
        try:
            voltage = self.power_supply.get_voltage()
            current = self.power_supply.get_current()
            power = voltage * current

            self.voltage_label.setText(fmt(voltage))
            self.current_label.setText(fmt(current))
            self.power_label.setText(fmt(power))

            if self.power_supply.is_output_on():
                self.out_button.setIcon(self.out_on_icon)
            else:
                self.out_button.setIcon(self.out_off_icon)

        except Exception as e:
            print(f"Error updating values: {e}")

    def eventFilter(self, obj, event):
        """Manages button rotation events"""
        if event.type() == event.Type.Wheel and isinstance(obj, QPushButton):
            button_id = obj.property("button_id")
            if button_id:
                delta = event.angleDelta().y()
                rotation_amount = 15 if delta > 0 else -15

                self.button_angles[button_id] = (self.button_angles[button_id] + rotation_amount) % 360
                self.adjust_value(button_id, event.angleDelta().y())

                rotated_pixmap = QPixmap(self.button_size)
                rotated_pixmap.fill(Qt.GlobalColor.transparent)

                painter = QPainter(rotated_pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)

                painter.translate(self.button_size.width() / 2, self.button_size.height() / 2)
                painter.rotate(self.button_angles[button_id])
                painter.translate(-self.button_size.width() / 2, -self.button_size.height() / 2)

                self.svg_renderer.render(painter)
                painter.end()

                obj.setIcon(rotated_pixmap)
                return True

        return super().eventFilter(obj, event)
