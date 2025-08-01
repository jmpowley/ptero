import numpy as np
import pandas as pd
from data_io.calculate_quantities import calculate_S23, calculate_O23

custom_quantities = ["S23", "O23"]

def extract_quantity(df, xquan, yquan, vmin, vmax, vstep, select):
    if select not in ["x", "y"]:
        raise ValueError(f"<select> must be one of 'x', 'y'. You entered {select}")
    
    min_idx = int((vmin - 100) / 25)
    max_idx = int((vmax - 100) / 25)
    step = int(vstep / 25)

    if select == "x":
        # Handle X quantity
        if xquan in custom_quantities:
            if xquan == "S23":
                x_lab, x_data = xquan, calculate_S23(df)
            elif xquan == "O23":
                x_lab, x_data = xquan, calculate_O23(df)
            x_data = x_data[min_idx:max_idx+1:step]
            return x_lab, x_data
        else:
            # Extract non-custom X quantity
            x_row = df.loc[df['Emission lines'] == xquan].values[0]
            x_lab, x_data = x_row[0], x_row[1:]
            x_data = x_data[min_idx:max_idx+1:step]
            return x_lab, x_data
    else:
        # Handle Y quantity
        if yquan in custom_quantities:
            if yquan == "S23":
                y_lab, y_data = yquan, calculate_S23(df)
            elif yquan == "O23":
                y_lab, y_data = yquan, calculate_O23(df)
            y_data = y_data[min_idx:max_idx+1:step]
            return y_lab, y_data
        else:
            # Extract non-custom Y quantity
            y_row = df.loc[df['Emission lines'] == yquan].values[0]
            y_lab, y_data = y_row[0], y_row[1:]
            y_data = y_data[min_idx:max_idx+1:step]
            return y_lab, y_data

# def extract_quantity(df, xquan, yquan, vmin, vmax, vstep, select):
#     # Check for correct usage
#     if select not in ["x", "y"]:
#         raise ValueError(f"<select> must be one of 'x', 'y'. You entered {select}")
    
#     # Window based on shock velocity
#     min_idx = int((vmin - 100) / 25)
#     max_idx = int((vmax - 100) / 25)
#     step = int(vstep / 25)

#     # Calculate custom quantities
#     if xquan in custom_quantities:
#         # Calculate desired quantity
#         if xquan == "S23":
#             x_lab, x_data = xquan, calculate_S23(df)
#         elif xquan == "O23":
#             x_lab, x_data = xquan, calculate_O23(df)
#         x_data = x_data[min_idx:max_idx+1:step]
    
#     elif yquan in custom_quantities:
#         if yquan == "S23":
#             y_lab, y_data = yquan, calculate_S23(df)
#         elif yquan == "O23":
#             y_lab, y_data = yquan, calculate_O23(df)
#         y_data = y_data[min_idx:max_idx+1:step]

#     # Extract quantity label and data
#     else:
#         x_row = df.loc[df['Emission lines'] == xquan].values[0]
#         x_lab, x_data = x_row[0], x_row[1:]
#         x_data = x_data[min_idx:max_idx+1:step]

#         y_row = df.loc[df['Emission lines'] == yquan].values[0]
#         y_lab, y_data = y_row[0], y_row[1:]
#         y_data = y_data[min_idx:max_idx+1:step]

#     # Return different quantity depending on string given
#     if select == "x":
#         return x_lab, x_data
#     else:
#         return y_lab, y_data
    
def extract_line_ratio(df, xnum, xden, ynum, yden, vmin, vmax, vstep, select):

    # Check for correct usage
    if select not in ["x", "y"]:
        raise ValueError(f"<select> must be 'x' or 'y'. You entered {select}")
    
    # Extract line ratio label and data
    xnum_row = df.loc[df['Emission lines'] == xnum].values[0]
    xden_row = df.loc[df['Emission lines'] == xden].values[0]
    x_lab = xnum_row[0] + " / " + xden_row[0]
    x_numerator = pd.to_numeric(xnum_row[1:], errors='coerce')
    x_denominator = pd.to_numeric(xden_row[1:], errors='coerce')
    x_data = np.where(x_denominator != 0, x_numerator / x_denominator, np.nan)  # Avoid dividing by 0

    ynum_row = df.loc[df['Emission lines'] == ynum].values[0]
    yden_row = df.loc[df['Emission lines'] == yden].values[0]
    y_lab = ynum_row[0] + " / " + yden_row[0]
    y_numerator = pd.to_numeric(ynum_row[1:], errors='coerce')
    y_denominator = pd.to_numeric(yden_row[1:], errors='coerce')
    y_data = np.where(y_denominator != 0, y_numerator / y_denominator, np.nan)  # Avoid dividing by 0

    # Window based on shock velocity
    min_idx = int((vmin - 100) / 25)
    max_idx = int((vmax - 100) / 25)
    step = int(vstep / 25)
    x_data = x_data[min_idx:max_idx+1:step]
    y_data = y_data[min_idx:max_idx+1:step]

    # Return different quantity depending on string given
    if select == "x":
        return x_lab, x_data
    else:
        return y_lab, y_data
    
def extract_shocks(df, vmin, vmax, vstep):

    shocks = np.asarray(df.columns[1:].values, dtype=int)

    # Window based on shock velocity
    min_idx = int((vmin - 100) / 25)
    max_idx = int((vmax - 100) / 25)
    step = int(vstep / 25)
    shocks = shocks[min_idx:max_idx+1:step]

    return shocks

def extract_value(df, xqulr, yqulr, xquan, yquan, xnum, xden, ynum, yden):

    if xqulr == "Quantity":
        x_line, x_data = extract_quantity(df, xquan, yquan, select="x")
    else:
        x_line, x_data = extract_line_ratio(df, xnum, xden, ynum, yden, select="x")
        
    if yqulr == "Quantity":
        y_line, y_data = extract_quantity(df, xquan, yquan, select="y")
    else:
        y_line, y_data = extract_quantity(df, xnum, xden, ynum, yden, select="y")

    return x_line, x_data, y_line, y_data