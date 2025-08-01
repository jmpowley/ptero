import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QComboBox, QHBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sine Curve with Multiple Dropdown Menus")
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create a horizontal layout for dropdown menus and their labels
        dropdown_layout = QHBoxLayout()
        
        # Frequency dropdown and label
        freq_label = QLabel("Select Frequency:")
        dropdown_layout.addWidget(freq_label)
        self.freq_combo = QComboBox()
        self.freq_combo.addItems(["1", "2", "3", "4", "5"])
        self.freq_combo.currentIndexChanged.connect(self.update_plot)
        dropdown_layout.addWidget(self.freq_combo)
        
        # Amplitude dropdown and label
        amp_label = QLabel("Select Amplitude:")
        dropdown_layout.addWidget(amp_label)
        self.amp_combo = QComboBox()
        self.amp_combo.addItems(["0.5", "1", "1.5", "2"])
        self.amp_combo.currentIndexChanged.connect(self.update_plot)
        dropdown_layout.addWidget(self.amp_combo)

        # Color dropdown and label
        col_label = QLabel("Select Color:")
        dropdown_layout.addWidget(col_label)
        self.col_combo = QComboBox()
        self.col_combo.addItems(["red", "blue", "green", "yellow"])
        self.col_combo.currentIndexChanged.connect(self.update_plot)
        dropdown_layout.addWidget(self.col_combo)

        # Linestyle dropdown and label
        ls_label = QLabel("Select Linestyle:")
        dropdown_layout.addWidget(ls_label)
        self.ls_combo = QComboBox()
        self.ls_combo.addItems(["solid", "dashed", "dotted", "dashdot"])
        self.ls_combo.currentIndexChanged.connect(self.update_plot)
        dropdown_layout.addWidget(self.ls_combo)
        
        # Add the dropdown layout to the main layout
        main_layout.addLayout(dropdown_layout)
        
        # Create and embed the Matplotlib figure
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        main_layout.addWidget(self.canvas)
        
        # Plot the initial sine curve with default values
        self.update_plot()

    def update_plot(self):
        # Retrieve current values from both dropdown menus
        freq = float(self.freq_combo.currentText())
        amp = float(self.amp_combo.currentText())
        col = str(self.col_combo.currentText())
        ls = str(self.ls_combo.currentText())
        
        # Clear the current axes and plot the updated sine curve
        self.ax.clear()
        x = np.linspace(0, 2 * np.pi, 100)
        y = amp * np.sin(freq * x)
        self.ax.plot(x, y, color=col, ls=ls)
        self.ax.set_title(f"Sine Curve: Frequency {freq}, Amplitude {amp}")
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
