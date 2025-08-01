import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QPushButton, QMessageBox, QFileDialog, QListWidget, QListWidgetItem, QSpinBox, QCheckBox
from PyQt6.QtGui import QPixmap
import os
from functools import partial

# Custom function declarations
from data_io.sorting import sort_key
from data_io.extract_values import extract_quantity, extract_line_ratio, extract_shocks
from data_io.handle_fits_data import load_fits_data, load_fits_data_new, load_fits_mask
from data_io.query_3mdbs_tools import send_3mdbs_query, populate_abundance_dropdown, populate_density_dropdown, return_lines_to_query, return_quantities_to_query
from plotter import draw_model_curves, draw_fits_points, finalize_plot

# Get the base path to Allen08
base_path = '/Users/Jonah/MISCADA/Project/code/PTERO/3mdbs_data/'

# Custom quantities to plot
custom_quantities = ['S23', 'O23']

# All shocks available
all_shocks = list(np.arange(100, 1025, 25).astype(str))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Central widget and main layout
        self.setWindowTitle('PTERO (Python Tool for Emission line Ratio Observation)')
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Set a custom icon
        custom_icon_path = 'PTERO_icon.png'  # Replace with your image path
        self.custom_pixmap = QPixmap(custom_icon_path)

        # Create and embed the Matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        plt.subplots_adjust(left=0.25, bottom=0.15, right=0.75, top=0.85)
        self.canvas = FigureCanvas(self.fig)
        main_layout.addWidget(self.canvas)
        self.ax.clear()
        plt.axis('off')

        # Add the Navigation Toolbar.
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        main_layout.addWidget(self.toolbar)
        
        # Create a horizontal layout for dropdown menus and their labels
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()

        # Abundance dropdown and label
        layout1.addWidget(QLabel('Abundance:'))
        self.abundance_combo = QComboBox()
        abundances = populate_abundance_dropdown()
        # abun_path = base_path + 'Allen08' + '/'
        # abundances = os.listdir(abun_path)
        self.abundance_combo.addItems(abundances)
        self.abundance_combo.currentIndexChanged.connect(self.update_dropdowns)
        layout1.addWidget(self.abundance_combo)

        # Density dropdown and label
        layout1.addWidget(QLabel('Density (cm-3):'))
        self.density_combo = QComboBox()
        self.density_combo.addItem('-')  # Default option
        layout1.addWidget(self.density_combo)

        # Create a QSpinBox and set its minimum, maximum, and initial value.
        layout1.addWidget(QLabel('Min. Velocity'))
        self.min_box = QSpinBox()
        self.min_box.setRange(100, 1000)
        self.min_box.setSingleStep(25)
        self.min_box.setValue(100)
        self.min_box.valueChanged.connect(partial(self.enforce_spinbox_constraints, self.min_box))
        layout1.addWidget(self.min_box)

        # Create a QSpinBox and set its minimum, maximum, and initial value.
        layout1.addWidget(QLabel('Max. Velocity'))
        self.max_box = QSpinBox()
        self.max_box.setRange(100, 1000)
        self.max_box.setSingleStep(25)
        self.max_box.setValue(1000)
        self.max_box.valueChanged.connect(partial(self.enforce_spinbox_constraints, self.max_box))
        layout1.addWidget(self.max_box)

        # Create a QSpinBox and set its minimum, maximum, and initial value.
        layout1.addWidget(QLabel('Velocity Step'))
        self.step_box = QSpinBox()
        self.step_box.setRange(25, 250)
        self.step_box.setSingleStep(25)
        self.step_box.setValue(25)
        self.step_box.valueChanged.connect(partial(self.enforce_spinbox_constraints, self.step_box))
        layout1.addWidget(self.step_box)

        # Create check boxes for using shock/precursor or both
        layout1.addWidget(QLabel('Shock?'))
        self.check_shock = QCheckBox()
        self.check_shock.setChecked(True)  # Shock is checked by default
        layout1.addWidget(self.check_shock)
        self.check_shock.stateChanged.connect(self.enforce_shock_precursor_checkboxes)
        layout1.addWidget(QLabel('Precursor?'))
        self.check_precursor = QCheckBox()
        self.check_precursor.stateChanged.connect(self.enforce_shock_precursor_checkboxes)
        layout1.addWidget(self.check_precursor)

        layout1.addWidget(QLabel('Each Independently?'))
        self.check_independent = QCheckBox()
        self.check_independent.stateChanged.connect(self.enforce_shock_precursor_checkboxes)
        layout1.addWidget(self.check_independent)

        # Y-axis numerator dropdown
        ynum = QLabel('Y Numerator:')
        layout2.addWidget(ynum)
        self.ynum_combo = QComboBox()
        self.ynum_combo.addItems(['-'])
        layout2.addWidget(self.ynum_combo)

        # Y-axis denominator dropdown
        yden = QLabel('Y Denominator:')
        layout2.addWidget(yden)
        self.yden_combo = QComboBox()
        self.yden_combo.addItems(['-'])
        layout2.addWidget(self.yden_combo)

        # X-axis numerator dropdown
        xnum = QLabel('X Numerator:')
        layout2.addWidget(xnum)
        self.xnum_combo = QComboBox()
        self.xnum_combo.addItems(['-'])
        layout2.addWidget(self.xnum_combo)

        # X-axis denominator dropdown
        xden = QLabel('X Denominator:')
        layout2.addWidget(xden)
        self.xden_combo = QComboBox()
        self.xden_combo.addItems(['-'])
        layout2.addWidget(self.xden_combo)

        # Y-axis quantity dropdown
        yquan = QLabel('Y Quantity:')
        layout2.addWidget(yquan)
        self.yquan_combo = QComboBox()
        self.yquan_combo.addItems(['-'])
        layout2.addWidget(self.yquan_combo)

        # X-axis quantity dropdown
        xquan = QLabel('X Quantity:')
        layout2.addWidget(xquan)
        self.xquan_combo = QComboBox()
        self.xquan_combo.addItems(['-'])
        layout2.addWidget(self.xquan_combo)

        # Quantity/ratio dropdown
        yqulr = QLabel('Y Quantity/Line Ratio')
        layout3.addWidget(yqulr)
        self.yqulr_combo = QComboBox()
        self.yqulr_combo.addItems(['Quantity', 'Line Ratio'])
        layout3.addWidget(self.yqulr_combo)

        # Quantity/ratio dropdown
        xqulr = QLabel('X Quantity/Line Ratio')
        layout3.addWidget(xqulr)
        self.xqulr_combo = QComboBox()
        self.xqulr_combo.addItems(['Quantity', 'Line Ratio'])
        layout3.addWidget(self.xqulr_combo)

        # Button to upload FITS data
        self.upload_fits_button = QPushButton('Upload FITS', self)
        self.upload_fits_button.clicked.connect(self.on_fits_upload_clicked)
        layout3.addWidget(self.upload_fits_button)

        # Button to upload FITS data
        self.upload_mask_button = QPushButton('Upload Badpix Mask', self)
        self.upload_mask_button.clicked.connect(self.on_mask_upload_clicked)
        layout3.addWidget(self.upload_mask_button)

        # Button to plot diagnostic
        self.plt_button = QPushButton('Plot Diagnostic', self)
        self.plt_button.clicked.connect(self.on_plot_button_clicked)  # Connect to on_plt_button_clicked function
        layout3.addWidget(self.plt_button)
        
        # Add the dropdown layout to the main layout
        main_layout.addLayout(layout1)
        main_layout.addLayout(layout2)
        main_layout.addLayout(layout3)

        # Initialise booleans
        self.plotting = False
        self.values_loaded = False
        self.data_uploaded = False
        self.mask_uploaded = False
        
        # Ensure initial values are populated
        self.update_dropdowns()

        # Load lines and quantities for selection
        self.load_lines_and_quantities()

    def update_dropdowns(self):
        abundance = self.abundance_combo.currentText()
        densities = populate_density_dropdown(abundance)
        densities = [str(d) for d in densities]

        # Clear and repopulate density dropdown
        self.density_combo.clear()
        self.density_combo.addItems(densities)

    def show_message(self, window_title: str, message_text: str) -> int:
        msg_box = QMessageBox()
        msg_box.setWindowTitle(window_title)
        msg_box.setText(message_text)

        # Load custom icons
        success_icon = QPixmap('/Users/Jonah/MISCADA/Project/code/PTERO/proto/PTERO_icon.png')
        
        if window_title == 'Error':
            msg_box.setIcon(QMessageBox.Icon.Critical)
        elif window_title == 'Success':
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setIconPixmap(success_icon)
        elif window_title == 'Warning':
            msg_box.setIcon(QMessageBox.Icon.Warning)
        
        return msg_box.exec()

    def enforce_spinbox_constraints(self, spin_box):
        min_val = spin_box.minimum()
        max_val = spin_box.maximum()
        step = spin_box.singleStep()
        value = spin_box.value()

        # Check if the value is aligned with the step
        if (value - min_val) % step != 0 or not (min_val <= value <= max_val):
            corrected_value = round((value - min_val) / step) * step + min_val
            corrected_value = min(max(corrected_value, min_val), max_val)
            spin_box.blockSignals(True)  # Prevent recursive calls
            spin_box.setValue(corrected_value)
            spin_box.blockSignals(False)

    def enforce_shock_precursor_checkboxes(self):
        if not (self.check_shock.isChecked() or self.check_precursor.isChecked()):
            self.show_message('Error', 'shock or precursor must be selected in order to plot a diagnostic')
            self.check_shock.setChecked(True)

        if self.check_independent.isChecked() and not (self.check_shock.isChecked() and self.check_precursor.isChecked()):
            self.show_message('Error', 'shock and precursor must be selected in order to plot each grid independently')
            self.check_independent.setChecked(False)

    def abbreviate_x_y_variable_declarations(self):
        xqulr = self.xqulr_combo.currentText()
        yqulr = self.yqulr_combo.currentText()
        xquan = self.xquan_combo.currentText()
        yquan = self.yquan_combo.currentText()
        xnum = self.xnum_combo.currentText()
        xden = self.xden_combo.currentText()
        ynum = self.ynum_combo.currentText()
        yden = self.yden_combo.currentText()

        return xqulr, yqulr, xquan, yquan, xnum, xden, ynum, yden

    def load_lines_and_quantities(self):

        # Extract lines and quantites from query_3mdbs_tools
        lines = list(return_lines_to_query().keys())
        quantities = list(return_quantities_to_query().keys())

        # Update dropdowns only if the emission lines have changed
        self.xquan_combo.clear()
        self.yquan_combo.clear()
        self.ynum_combo.clear()
        self.yden_combo.clear()
        self.xnum_combo.clear()
        self.xden_combo.clear()

        self.xquan_combo.addItems(quantities)
        self.yquan_combo.addItems(quantities)
        self.ynum_combo.addItems(lines)
        self.yden_combo.addItems(lines)
        self.xnum_combo.addItems(lines)
        self.xden_combo.addItems(lines)

    def read_model_data(self):
        xqulr, yqulr, xquan, yquan, xnum, xden, ynum, yden = self.abbreviate_x_y_variable_declarations()
        abundance = self.abundance_combo.currentText()
        density = self.density_combo.currentText()
        vmin = self.min_box.value()
        vmax = self.max_box.value()
        vstep = self.step_box.value()
        precursor = self.check_precursor.isChecked()
        shock = self.check_shock.isChecked()
        independent = self.check_independent.isChecked()

        # Initialize labels
        if xqulr == 'Quantity':
            self.x_lab = self.xquan_combo.currentText()
        if yqulr == 'Quantity':
            self.y_lab = self.yquan_combo.currentText()

        # Initialise lists
        self.x_data_list = []
        self.y_data_list = []
        self.shocks_list = []

        # Send SQL query
        result = send_3mdbs_query(xquan, yquan, xnum, xden, ynum, yden, abundance, density, vmin, vmax, precursor, shock, independent)

        if independent:
            # Process results for shock_df and precursor_df separately
            shock_df, prec_df = result
            self.shock_data_grouped = self.process_df(shock_df)
            self.precursor_data_grouped = self.process_df(prec_df)
            
            # For backward compatibility, combine but mark as independent
            self.model_data_grouped = self.shock_data_grouped + self.precursor_data_grouped
                    
        else:
            self.model_data_grouped = self.process_df(result)
            self.shock_data_grouped = []
            self.precursor_data_grouped = []

    def process_df(self, df):
        vmin = self.min_box.value()
        vmax = self.max_box.value()
        vstep = self.step_box.value()
        df = df.copy()
        df['shck_vel'] = df['shck_vel'].astype(float)
        df = df.set_index('shck_vel')
        vels = np.arange(vmin, vmax + 1e-6, vstep)
        
        grouped_data = []
        for mag_value, subdf in df.groupby('mag_fld'):
            reindexed = subdf.reindex(vels)
            reindexed['mag_fld'] = mag_value
            reindexed = reindexed.reset_index().rename(columns={'index': 'shck_vel'})
            grouped_data.append(reindexed)
        return grouped_data

    def plot_diagnostic(self):

        # Read in the model data
        self.read_model_data()

        # Plot new diagnostic diagram
        try:
            self.clear_plot()
            self.plot_data()
            self.canvas.draw()
            self.plotting = True
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to plot diagnostic: {e}')

    def clear_plot(self):
        if hasattr(self, 'cbar'):
            self.cbar.remove()
        self.ax.clear()

    def plot_data(self):
        fig = self.fig
        ax = self.ax
        abundance = self.abundance_combo.currentText()
        density = self.density_combo.currentText()
        vmin = self.min_box.value()
        vmax = self.max_box.value()
        vstep = self.step_box.value()
        xqulr, yqulr,_,_,_,_,_,_ = self.abbreviate_x_y_variable_declarations()
        independent = self.check_independent.isChecked()

        # Plot model curves, and FITS data if uploaded
        try:
            lc = draw_model_curves(ax, xqulr, yqulr, self.model_data_grouped, self.shock_data_grouped, self.precursor_data_grouped, vmin, vmax, vstep, independent)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to draw model curves: {e}')
        
        if self.data_uploaded:
            try:
                draw_fits_points(ax, self.fits_x_data, self.fits_y_data, self.fits_z_data, self.mask_uploaded, self.fits_mask, vmin, vmax)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to draw fits points: {e}')
        
        try:
            self.cbar = finalize_plot(fig, ax, lc, self.x_lab, self.y_lab, abundance, density)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to finalise curves: {e}')

    def on_fits_upload_clicked(self):
        # Load in file paths
        file_paths = []
        while len(file_paths) < 3:
            file_path,_ = QFileDialog.getOpenFileName(self, 'Select FITS File', '', 'FITS Files (*.fits *.fit)')
            file_paths.append(file_path)

        # Check all paths are valid
        if np.all([os.path.exists(file_path) for file_path in file_paths]):
            try:
                # Load FITS data from files
                self.fits_x_data, self.fits_y_data, self.fits_z_data = load_fits_data_new(file_paths)
                QMessageBox.information(self, 'Success', 'FITS files loaded successfully.')
                self.data_uploaded = True

                # Initialise bad pixel mask to include all pixels if not uploaded
                if not self.mask_uploaded:
                    self.fits_mask = np.zeros_like(self.fits_x_data).astype(bool)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to load FITS file: {e}')

    def on_mask_upload_clicked(self):
        # Load in file path
        file_path,_ = QFileDialog.getOpenFileName(self, 'Select FITS File', '', 'FITS Files (*.fits *.fit)')

        # Check path is valid
        if os.path.exists(file_path):
            try:
                # Load FITS data from files
                self.fits_mask = load_fits_mask(file_path)
                QMessageBox.information(self, 'Success', 'FITS mask loaded successfully.')
                self.mask_uploaded = True
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to load FITS mask: {e}')

    def on_plot_button_clicked(self):
        self.plot_diagnostic()