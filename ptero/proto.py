import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from matplotlib.collections import LineCollection
from matplotlib import cm
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QPushButton, QMessageBox, QFileDialog, QListWidget, QListWidgetItem, QSpinBox, QCheckBox
from PyQt6.QtGui import QGuiApplication, QPixmap
from PyQt6.QtCore import Qt
import os
from datetime import datetime

# Custom function declarations
from data_io.sorting import sort_key
from data_io.extract_values import extract_quantity, extract_line_ratio, extract_shocks
from data_io.handle_fits_data import load_fits_data, load_fits_data_new

# Get the base path to Allen08
base_path = '/Users/Jonah/MISCADA/Project/code/PTERO/3mdbs_data/'

# Custom quantities to plot
custom_quantities = ['S23', 'O23']

# All shocks available
all_shocks = list(np.arange(100, 1025, 25).astype(str)) 

class SelectableListWidget(QListWidget):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.addItem('Select All')  # Add 'Select All' item at the top
        for item in items:
            self.addItem(item)
        self.itemClicked.connect(self.handle_item_clicked)

    def handle_item_clicked(self, item):
        if item.text() == 'Select All':
            if item.isSelected():
                self.selectAll()
            else:
                self.clearSelection()
        else:
            select_all_item = self.item(0)  # 'Select All' is the first item
            all_selected = all(self.item(i).isSelected() for i in range(1, self.count()))
            select_all_item.setSelected(all_selected)

    def select_all_items(self):
        '''Check all items except 'Select All' itself (if desired).'''
        for i in range(1, self.model().rowCount()):
            it = self.model().item(i)
            it.setCheckState(Qt.CheckState.Checked)

    def deselect_all_items(self):
        '''Uncheck all items except 'Select All' itself (if desired).'''
        for i in range(1, self.model().rowCount()):
            it = self.model().item(i)
            it.setCheckState(Qt.CheckState.Unchecked)

    def checkedItems(self):
        '''Return a list of text for all items that are checked (excluding 'Select All').'''
        selected = []
        # Start from 1 if the 0th item is 'Select All'
        for i in range(1, self.model().rowCount()):
            item = self.model().item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
        return selected

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Central widget and main layout
        self.setWindowTitle('PTERO (Python Tool for Emission-line Ratio Observation)')
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
        layout1.addWidget(QLabel('Select Abundance:'))
        self.abun_combo = QComboBox()
        abun_path = base_path + 'Allen08' + '/'
        abundances = os.listdir(abun_path)
        self.abun_combo.addItems(abundances)
        self.abun_combo.currentIndexChanged.connect(self.update_dropdowns)
        layout1.addWidget(self.abun_combo)

        # Density dropdown and label
        layout1.addWidget(QLabel('Select Density:'))
        self.dens_combo = QComboBox()
        self.dens_combo.addItem('-')  # Default option
        layout1.addWidget(self.dens_combo)

        # Create a QSpinBox and set its minimum, maximum, and initial value.
        layout1.addWidget(QLabel('Min. Velocity'))
        self.min_box = QSpinBox()
        self.min_box.setRange(100, 1000)
        self.min_box.setSingleStep(25)
        self.min_box.setValue(100)
        layout1.addWidget(self.min_box)

        # Create a QSpinBox and set its minimum, maximum, and initial value.
        layout1.addWidget(QLabel('Max. Velocity'))
        self.max_box = QSpinBox()
        self.max_box.setRange(100, 1000)
        self.max_box.setSingleStep(25)
        self.max_box.setValue(1000)
        layout1.addWidget(self.max_box)

        # Create a QSpinBox and set its minimum, maximum, and initial value.
        layout1.addWidget(QLabel('Velocity Step'))
        self.step_box = QSpinBox()
        self.step_box.setRange(25, 250)
        self.step_box.setSingleStep(25)
        self.step_box.setValue(25)
        layout1.addWidget(self.step_box)

        # Create check boxes for using shock/precursor or both
        layout1.addWidget(QLabel('Shock?'))
        self.check_shock = QCheckBox()
        layout1.addWidget(self.check_shock)
        layout1.addWidget(QLabel('Precursor?'))
        self.check_precursor = QCheckBox()
        layout1.addWidget(self.check_precursor)

        # Button to load values
        self.val_button = QPushButton('Load Values', self)
        self.val_button.clicked.connect(self.on_val_button_clicked)
        layout1.addWidget(self.val_button)

        # Button to upload FITS data
        self.upload_button = QPushButton('Upload FITS', self)
        self.upload_button.clicked.connect(self.on_upload_clicked_new)
        layout1.addWidget(self.upload_button)

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

        # Button to plot diagnostic
        self.plt_button = QPushButton('Plot Diagnostic', self)
        self.plt_button.clicked.connect(self.on_plot_button_clicked)  # Connect to on_plt_button_clicked function
        layout3.addWidget(self.plt_button)

        # Button to save figure
        self.save_button = QPushButton('Save Figure', self)
        self.save_button.clicked.connect(self.on_save_button_clicked)  # Connect to on_save_button_clicked function
        layout3.addWidget(self.save_button)
        
        # Add the dropdown layout to the main layout
        main_layout.addLayout(layout1)
        main_layout.addLayout(layout2)
        main_layout.addLayout(layout3)

        # Initialise booleans
        self.plotting = False
        self.vals_loaded = False
        self.data_uploaded = False
        
        # Ensure initial values are populated
        self.update_dropdowns()

    def update_dropdowns(self):
        abun_path = os.path.join(base_path, 'Allen08', self.abun_combo.currentText())

        if not os.path.exists(abun_path):
            self.dens_combo.clear()
            return

        # Extract unique density values
        files = os.listdir(abun_path)
        res = [d.replace(self.abun_combo.currentText()+'_', '').replace('.csv', '').split('_') for d in files]
        densities = sorted(set(res[i][0] for i in range(len(res))), key=float)

        # Clear and repopulate density dropdown
        self.dens_combo.clear()
        self.dens_combo.addItems(densities)

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

    def abbreviate_x_y_variable_declarations(self):
        xqulr = self.xqulr_combo.currentText()
        yqulr = self.yqulr_combo.currentText()
        xquan = self.xquan_combo.currentText()
        yquan = self.yquan_combo.currentText()
        xnum = self.xnum_combo.currentText()
        xden = self.xnum_combo.currentText()
        ynum = self.ynum_combo.currentText()
        yden = self.yden_combo.currentText()

        return xqulr, yqulr, xquan, yquan, xnum, xden, ynum, yden
    
    def load_values(self):

        # Construct the nominal file path to load values
        abun = self.abun_combo.currentText()
        dens = self.dens_combo.currentText()
        filepath = os.path.join(base_path, 'Allen08', abun, f'{abun}_{dens}_0.1.csv')
        filepath = '/Users/Jonah/MISCADA/Project/code/PTERO/3mdbs_data/Allen08/Allen2008_Dopita2005/Allen2008_Dopita2005_1_0.0001.csv'

        if os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath)

                # Get the sorted values from the new table
                line_ratios = sorted(df['Emission lines'], key=sort_key)
                quantities = sorted(list(df['Emission lines']) + custom_quantities, key=sort_key)  # Add custom quantities

                # Check if we already have these emission lines
                if not (hasattr(self, 'line_ratios') and hasattr(self, 'quantities')) or (self.line_ratios != line_ratios and self.quantities != quantities):
                    # Update dropdowns only if the emission lines have changed
                    self.xquan_combo.clear()
                    self.yquan_combo.clear()
                    self.ynum_combo.clear()
                    self.yden_combo.clear()
                    self.xnum_combo.clear()
                    self.xden_combo.clear()

                    self.xquan_combo.addItems(quantities)
                    self.yquan_combo.addItems(quantities)
                    self.ynum_combo.addItems(line_ratios)
                    self.yden_combo.addItems(line_ratios)
                    self.xnum_combo.addItems(line_ratios)
                    self.xden_combo.addItems(line_ratios)

                    # Save the current list for future comparison
                    self.line_ratios = line_ratios
                    self.quantities = quantities

                self.show_message('Success', 'Values loaded successfully.')
                self.vals_loaded = True
            except Exception as e:
                self.show_message('Error', f'Failed to load values: {e}')
        else:
            self.show_message('Error', 'File does not exist.')

    def plot_diagnostic(self):
        xqulr, yqulr, xquan, yquan, xnum, xden, ynum, yden = self.abbreviate_x_y_variable_declarations()
        abun = self.abun_combo.currentText()
        dens = self.dens_combo.currentText()
        ax = self.ax
        vmin = self.min_box.value()
        vmax = self.max_box.value()
        vstep = self.step_box.value()

        # Extract filenames based on abundance and density
        directory = f'/Users/Jonah/MISCADA/Project/code/PTERO/3mdbs_data/Allen08/{abun}'
        search_string = f'{abun}_{dens}_'
        filenames = [f for f in os.listdir(directory) if f.startswith(search_string)]
        mags = [f.replace(search_string, '').replace('.csv', '') for f in filenames]
        filenames = [f'{abun}_{dens}_{mag}.csv' for mag in sorted(mags, key=float)]
        self.filenames = filenames
        
        # Initialize labels and lists
        self.x_lab = ''
        self.y_lab = ''
        self.x_data_list = []
        self.y_data_list = []
        self.shocks_list = []

        # Check for correct usage of vmin, vmax, and vstep
        try:
            if vmin >= vmax:
                raise ValueError(f'vmin must be less than vmax. You entered {vmin} and {vmax}')
            if vmin %25 != 0 or vmax %25 != 0:
                raise ValueError(f'vmin and vmax must be multiples of 25. You entered {vmin} and {vmax}')
            if vstep %25 != 0:
                raise ValueError(f'vstep must be a multiple of 25. You entered {vstep}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'{e}')
            return

        # Read data from each file
        for filename in filenames:
            filepath = os.path.join(directory, filename)
            df = pd.read_csv(filepath)
            shocks = extract_shocks(df, vmin, vmax, vstep)
            self.shocks_list.append(shocks)

            if xqulr == 'Quantity':
                try:
                    x_lab, x_data = extract_quantity(df, xquan, yquan, vmin, vmax, vstep, 'x')
                    self.x_lab = x_lab
                    self.x_data_list.append(x_data)
                except Exception as e:
                    QMessageBox.critical(self, 'Error', f'Failed to calculate X ' + xqulr + f': {e}')
            elif xqulr == 'Line Ratio':
                try:
                    x_lab, x_data = extract_line_ratio(df, xnum, xden, ynum, yden, vmin, vmax, vstep, 'x')
                    self.x_lab = x_lab
                    self.x_data_list.append(x_data)
                except Exception as e:
                    QMessageBox.critical(self, 'Error', f'Failed to calculate X ' + xqulr + f': {e}')
                    
            if yqulr == 'Quantity':
                try:
                    y_lab, y_data = extract_quantity(df, xquan, yquan, vmin, vmax, vstep, 'y')
                    self.y_lab = y_lab  # Store the label
                    self.y_data_list.append(y_data)
                except Exception as e:
                    QMessageBox.critical(self, 'Error', f'Failed to calculate Y ' + yqulr + f': {e}')
            elif yqulr == 'Line Ratio':
                try:
                    y_lab, y_data = extract_line_ratio(df, xnum, xden, ynum, yden, vmin, vmax, vstep, 'y')
                    self.y_lab = y_lab  # Store the label
                    self.y_data_list.append(y_data)
                except Exception as e:
                    QMessageBox.critical(self, 'Error', f'Failed to calculate Y ' + yqulr + f': {e}')

        # Plot new diagnostic diagram
        try:
            # Remove leftovers plots
            if hasattr(self, 'cbar'):
                self.cbar.remove()
            ax.clear()

            # Plot data and draw
            self.plot_data()
            self.canvas.draw()
            self.plotting = True
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to plot diagnostic: {e}')

        print(self.x_data_list, len(self.x_data_list))

    def plot_data(self):
        fig = self.fig
        ax = self.ax
        x_data_list = self.x_data_list
        y_data_list = self.y_data_list
        abun = self.abun_combo.currentText()
        dens = self.dens_combo.currentText()
        vmin = self.min_box.value()
        vmax = self.max_box.value()
        shocks_list = self.shocks_list

        # Plot shock model data
        for i in range(len(x_data_list)):
            
            # Convert x_data and y_data into a sequence of line segments
            points = np.array([x_data_list[i], y_data_list[i]]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)

            # Create a LineCollection with colors based on 'shocks'
            lc = LineCollection(segments, cmap='viridis', norm=plt.Normalize(vmin, vmax))
            lc.set_array(shocks_list[i])
            ax.add_collection(lc)

            # # Add gray connection to previous dataset
            if i > 0:
                ax.plot((x_data_list[i], x_data_list[i-1]), (y_data_list[i], y_data_list[i-1]), color='gray', alpha=0.5)

        # Plot fits data if uploaded
        if self.data_uploaded:
            ax.scatter(self.fits_x_data, self.fits_y_data, c=self.fits_z_data, cmap='viridis', vmin=vmin, vmax=vmax, marker='.', alpha=0.5)

        # Extra plotting code
        self.cbar = fig.colorbar(lc)
        self.cbar.set_label('Shock velocity / kms$^{-1}$')
        ax.set_xlabel(self.x_lab)
        ax.set_ylabel(self.y_lab)
        ax.set_title(f'{self.y_lab} against {self.x_lab}\nAbundance = {abun}; Density = {dens}' + ' cm$^{-3}$')
        ax.set_xscale('log')
        ax.set_yscale('log')

    def on_val_button_clicked(self):
        self.load_values()

    def on_upload_clicked(self):
        xqulr, yqulr, xquan, yquan, xnum, xden, ynum, yden = self.abbreviate_x_y_variable_declarations()

        file_path, _ = QFileDialog.getOpenFileName(self, 'Select FITS File', '', 'FITS Files (*.fits *.fit)')
        if file_path:
            try:
                self.fits_x_data, self.fits_y_data, self.fits_z_data = load_fits_data(file_path, xqulr, yqulr, xquan, yquan, xnum, xden, ynum, yden)
                QMessageBox.information(self, 'Success', 'FITS file loaded successfully.')
                self.data_uploaded = True
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to load FITS file: {e}')

    def on_upload_clicked_new(self):
        xqulr, yqulr, xquan, yquan, xnum, xden, ynum, yden = self.abbreviate_x_y_variable_declarations()

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
                QMessageBox.information(self, 'Success', 'FITS file loaded successfully.')
                self.data_uploaded = True
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to load FITS file: {e}')

    def on_plot_button_clicked(self):
        if self.vals_loaded:
            self.plot_diagnostic()
        else:
            QMessageBox.critical(self, 'Error', f'Please load values to produce a plot')

    def on_save_button_clicked(self):
        # Generate unique filename based on the current date and time.
        now = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = './output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Use a base filename and add a counter if necessary.
        base_filename = f'plot_{now}.jpg'
        filename = base_filename
        counter = 1
        while os.path.exists(os.path.join(output_dir, filename)):
            filename = f'plot_{now}_{counter}.jpg'
            counter += 1

        # Save figure if plotting; otherwise show an error.
        if self.plotting:
            plt.savefig(os.path.join(output_dir, filename), dpi=400)
            QMessageBox.information(self, 'Saved', f'Figure saved as {filename}')
        else:
            QMessageBox.critical(self, 'Error', 'Please produce a plot to save a figure.')

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()