import numpy as np
from astropy.io import fits
from astropy.table import Table

def convert_line_ratio_label(label):
    
    # Two lists for model labels and fits labels to convert between them
    model_list = ["S23", "O23", "Hα λ6563"]
    fits_list = ["S23", "O23", "Ha6563"]

    if label in model_list:
        fits_label = fits_list[model_list.index(label)]
    else:
        fits_label = None
    
    return fits_label

def is_table_fits(file_path):
    """Return True if any extension is a BinTableHDU / TableHDU."""
    with fits.open(file_path, memmap=True) as hdul:
        # skip the PRIMARY, look for table‐type HDUs
        for hdu in hdul[1:]:
            if isinstance(hdu, (fits.BinTableHDU, fits.TableHDU)):
                return True
    return False

def load_fits_data(file_paths):

    # Loop over all filenames
    for i, file_path in enumerate(file_paths):

        if is_table_fits(file_path):
            # Open as table
            tb = Table.read(file_path)

            # For x and y dimensions, try looking at diagnostics and flux
            if i == 0:
                x_data = tb['FLUX'].data
            elif i == 1:
                y_data = tb['FLUX'].data
            # For z dimension, look only at sigma
            elif i == 2:
                z_data = tb['SIGMA'].data
        else:
            # Open as fits map
            with fits.open(file_path, memmap=True) as hdul:
                # For x and y dimensions, try looking at diagnostics and flux
                if i == 0:
                    try:
                        x_data = hdul['DIAGNOSTIC'].data
                    except Exception:
                        x_data = hdul['FLUX'].data
                elif i == 1:
                    try:
                        y_data = hdul['DIAGNOSTIC'].data
                    except Exception:
                        y_data = hdul['FLUX'].data
                # For z dimension, look only at sigma
                elif i == 2:
                    z_data = hdul['SIGMA'].data
    
    return x_data.flatten(), y_data.flatten(), z_data.flatten()

def load_fits_mask(file_path):

    with fits.open(file_path) as hdul:
        mask = hdul[0].data

    return mask.astype(bool)