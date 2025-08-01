import numpy as np
import pandas as pd
import sys

def txt_to_dataframe(filename: str):
    """Extracts the information from a txt file and structures the data so as to match the structure of the emission-line tables found at http://3mdb.astro.unam.mx:3686/emisstable

    The rows give different values of emission line ratios for a given shock velocity. The first column indicates the partiular emission line ratio of a given row

    Parameters
    ----------
    filename : str
        The filename of the txt file being processed.

    Returns
    -------
    df : dataframe
        The final modified processed dataframe, containing all the information
    """

    # Read the file and split into lines
    with open(filename, "r") as f:
        lines = f.read().splitlines()

    # Remove first line if empty
    if not lines[0]:
        lines = lines[1:]

    # Initialise column names and data
    row_labels = []
    data = []

    # Add columns and data from file
    for i in range(len(lines)):
        # For lines 0 to 7, the column names are on even lines and data are on the following odd line
        if i < 8:
            if i % 2 == 0:
                row_label = lines[i]
                row_labels.append(row_label)
            else:
                if i == 1:
                    values = np.asarray(lines[i].split(), dtype=int)  # Shock velocities are ints
                else:
                    values = np.asarray(lines[i].split(), dtype=float)
                data.append(values)

        # For lines 8 to 45, the data is on the same line as the column names
        else:
            line = lines[i].split("\t")
            row_label, values = line[0], np.asarray(line[1:], dtype=float)  # Separate into column label and values
            row_labels.append(row_label)
            data.append(values)

    # Create the DataFrame
    data = np.asarray(data)
    df = pd.DataFrame(data.T, columns=row_labels)  # Transpose data to fit shape of columns
    df = df.transpose()  # Transpose again to follow structure of online table

    # Set the first row as header and remove it from the DataFrame
    new_header = df.iloc[0]
    df = df.iloc[1:]         
    df.columns = new_header

    # Insert emission labels at beginning of DataFrame
    emission_labels = row_labels[1:]
    df.insert(0, "Emission line", emission_labels)

    # df = df.set_index(df.columns[0])

    return df

if __name__ == "__main__":
    # Get filename from command-line argument
    if len(sys.argv) != 2:
        print("Usage: python 3mbds_data_processing.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]

    # Process file
    df = txt_to_dataframe(filename)

    # Save DataFrame
    output_name = filename.strip("_original.txt") + "_processed.csv"
    df.to_csv(output_name, sep="\t", index=False)
    print(f"Processed file saved as: {output_name}")
