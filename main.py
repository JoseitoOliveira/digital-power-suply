from PySide6.QtWidgets import QApplication
import sys
from power_supply import MockPowerSupply
from gui import PowerSupplyGUI



def main():
    app = QApplication(sys.argv)
    power_supply = MockPowerSupply()
    window = PowerSupplyGUI(power_supply)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
