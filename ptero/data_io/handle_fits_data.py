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

def load_fits_data(filepath, xqulr, yqulr, xquan, yquan, xnum, xden, ynum, yden):

    fits_list = ["S23", "O23", "Ha6563"]

    # Convert between model label and fits label
    if yqulr == "Quantity":
        yquan_conv = convert_line_ratio_label(yquan)
    else:
        ynum_conv = convert_line_ratio_label(ynum)
        yden_conv = convert_line_ratio_label(yden)

    if xqulr == "Quantity":
        xquan_conv = convert_line_ratio_label(xquan)
    else:
        xnum_conv = convert_line_ratio_label(xnum)
        xden_conv = convert_line_ratio_label(xden)

    with fits.open(filepath, memmap=True) as hdul:

        # Select emission line ratio data from file using fits_list as key
        # NOTE: Currently works only for S23 and O23
        if xquan in fits_list: 
            hdu_x_data = hdul['DIAGNOSTICS'].data
            x_data = hdu_x_data[xquan_conv].flatten()
        if yquan in fits_list:
            hdu_y_data = hdul['DIAGNOSTICS'].data
            y_data = hdu_y_data[yquan_conv].flatten()

        # Extract velocity dispersion data
        hdul_z_data = hdul["SII6716"].data
        z_data = hdul_z_data["SIGMA"].flatten()

    return x_data, y_data, z_data

def load_fits_data_new(file_paths):

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

# # Test convert_line_ratio_label
# try:
#     print("Testing convert_line_ratio_label...")
#     convert_line_ratio_label("O23")
#     print("Passed!")
# except Exception as e:
#     print(f"Error: {e}")

# # Test load_fits_data
# filepath = "/Users/Jonah/MISCADA/Project/code/P2/code/all_maps.fits"
# xqulr = "Quantity"
# yqulr = "Quantity"
# xquan = "O23"
# yquan = "S23"
# xnum = None
# xden = None
# ynum = None
# yden = None

# try:
#     print("Testing load_fits_data...")
#     x_data, y_data = load_fits_data(filepath, xqulr, yqulr, xquan, yquan, xnum, xden, ynum, yden)
#     print("Passed!\n")
#     print(np.shape(x_data), np.shape(y_data))
# except Exception as e:
#     print(f"Error: {e}")