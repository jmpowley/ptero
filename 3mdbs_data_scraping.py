import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# Function to get options from a select element
def get_select_options(soup, select_id):
    options = {}
    select_element = soup.find("select", id=select_id)
    if select_element:
        for option in select_element.find_all("option"):
            value = option.get("value")
            text = option.get_text(strip=True)
            if value:  # Skip empty values
                options[value] = text
    return options

# Function to submit form and return the response soup
def submit_form(form_data):
    try:
        response = requests.post(url, data=form_data)
        if response.status_code == 200:
            return BeautifulSoup(response.text, "html.parser")
        else:
            print(f"Form submission failed. Status code: {response.status_code}")
            return None
    
    # If webpage does not open then move on to next value
    except requests.exceptions.ConnectionError as e:
        print(f"ConnectionError occured. Continuing to next value")
        return None

# Function to extract table data and convert to DataFrame
def extract_table_data(soup):
    table = soup.find("table", class_="table table-hover")

    if not table:
        return None
    else:
        # Extract all rows from the table
        emission_rows = []
        rows = table.find_all("tr")
        for i, row in enumerate(rows):

            # Get all cells in the current row
            cells = row.find_all(["td", "th"])
            # Extract text from each cell and strip extra whitespace
            cell_data = [cell.get_text(strip=True) for cell in cells]

            # Extract first row as header
            if i == 0:
                header = cell_data
            # Otherwise store row data as lists
            else:
                emission_label = [cell_data[0]]
                emission_data = list(np.asarray(cell_data[1:], dtype=float))  # Convert str to float
                emission_row = emission_label + emission_data
                emission_rows.append(emission_row)  # Add to master list
        
        # Create DataFrame
        return pd.DataFrame(emission_rows, columns=header)

# URL for the form page
url = "http://3mdb.astro.unam.mx:3686/emisstable"

# Start by getting the initial page
initial_response = requests.get(url)
if initial_response.status_code == 200:
    current_soup = BeautifulSoup(initial_response.text, "html.parser")

    # Submit form with selected reference
    ref_value = "Allen08"
    form_data = {
        "reference": ref_value,
        "submitbutton": "submit"
    }
    ref_soup = submit_form(form_data)
        
    # Get abundances options based on selected reference
    abundances_options = get_select_options(ref_soup, "abundances")
    print(f"  Abundances options for {ref_value}:", *abundances_options.values())
        
    # Iterate through each abundances option
    for abund_value, abund_text in abundances_options.items():
        print(f"  Testing abundances: {abund_value} ({abund_text})")
        
        # Submit form with selected reference and abundances
        form_data = {
            "reference": ref_value,
            "abundances": abund_value,
            "submitbutton": "submit"
        }
        
        abund_soup = submit_form(form_data)
        if not abund_soup or abund_soup is None:
            continue
        
        # Get density options based on selected reference and abundances
        density_options = get_select_options(abund_soup, "density")
        print(f"    Density options for {ref_value}, {abund_value}:", *density_options.values())
        
        # Iterate through each density option
        for dens_value, dens_text in density_options.items():
            print(f"    Testing density: {dens_value}")
            
            # Submit form with selected reference, abundances, and density
            form_data = {
                "reference": ref_value,
                "abundances": abund_value,
                "density": dens_value,
                "submitbutton": "submit"
            }
            
            dens_soup = submit_form(form_data)
            if not dens_soup or dens_soup is None:
                continue
            
            # Get magnetic options based on previous selections
            magnetic_options = get_select_options(dens_soup, "magnetic")
            print(f"      Magnetic options for {ref_value}, {abund_value}, {dens_value}:", *magnetic_options.values())
            
            # Iterate through each magnetic option
            for mag_value, mag_text in magnetic_options.items():
                print(f"      Testing magnetic: {mag_value}")
                
                # Submit form with all selected values to get the table
                form_data = {
                    "reference": ref_value,
                    "abundances": abund_value,
                    "density": dens_value,
                    "magnetic": mag_value,
                    "submitbutton": "print table"
                }

                final_soup = submit_form(form_data)
                if not final_soup or final_soup is None:
                    continue
                
                # Extract table data into DataFrame
                df = extract_table_data(final_soup)
                
                # Save DataFrame in specified directory
                if df is not None:
                    # Generate filename and filepath for this combination
                    filename = f"{abund_value}_{dens_value}_{mag_value}.csv"
                    filepath = f"3mdbs_data/{ref_value}/{abund_value}/" + filename
                    df.to_csv(filepath, index=False)
                else:
                    print(f"      No table found for this combination")
else:
    print(f"Failed to retrieve the initial page. Status code: {initial_response.status_code}")