import pandas as pd

def calculate_S23(df):
    """
    Calculates the emission-line ratio parameter S23

    S23 = ([S II] λλ6716+6731 + [S III] λ9069) / Hβ λ4861

    NOTE: MAPPINGS also includes [S III] λ9031 in its shock model grids
    """

    sii = df.loc[df['Emission lines'] == "[S II] λλ6716+6731"].values[0][1:]
    siii = df.loc[df['Emission lines'] == "[S III] λλ9069+9031"].values[0][1:]
    hbeta = df.loc[df['Emission lines'] == "Hβ λ4861"].values[0][1:]

    s23 = (sii + siii) / hbeta

    return s23

def calculate_O23(df):
    """
    Calculates the emission-line ratio parameter O23

    O23 = ([O II] λλ7320+7330) / [O III] λ5007
    """

    oii = df.loc[df['Emission lines'] == "[O II] λλ7319+7320"].values[0][1:]
    oiii = df.loc[df['Emission lines'] == "[O III] λ5007"].values[0][1:]

    o23 = oii / oiii

    return o23