import pandas as pd
import os
from sqlalchemy import create_engine

def format_quantity_as_sql_query(quantity):

    # Dict of quantities to extract using SQL queries
    quantities = return_quantities_to_query()
    
    # Only return SQL query if in quantities dict
    if quantity in quantities.keys():
        sql_query = f'{quantities.get(quantity)} AS {quantity}'
    else:
        sql_query = None
    return sql_query

def format_line_ratio_as_sql_query(num, den):

    lines = return_lines_to_query()

    if num in lines.keys() and den in lines.keys():
        print('num:', num, 'den:', den)
        sql_query = f'{lines.get(num)} / {lines.get(den)} AS {num}_{den}'

    return sql_query

def send_3mdbs_query(xquan, yquan, xnum, xden, ynum, yden, abundance, preshck_dens, shck_vel_lo, shck_vel_hi, precursor, shock, independent):

    print(xquan, yquan, xnum, xden, ynum, yden, abundance, preshck_dens, shck_vel_lo, shck_vel_hi, shock, precursor, independent)

    # Set environment variables
    host   = os.environ['MdB_HOST']
    user   = os.environ['MdB_USER']
    passwd = os.environ['MdB_PASSWD']
    port   = os.environ['MdB_PORT']
    dbname = "3MdBs"
    engine = create_engine(f"mysql+pymysql://{user}:{passwd}@{host}:{port}/{dbname}")

    # Select model type
    if shock and not precursor:
        model_type = 'shock'
    elif precursor and not shock:
        model_type = 'precursor'
    elif precursor and shock and not independent:
        model_type = 'shock_plus_precursor'
    elif precursor and shock and independent:
        model_type1 = 'shock'
        model_type2 = 'precursor'

    # Run two SQL queries for independent plottng of shock and precursor
    if independent:
        sel_shck = f"""SELECT
                    shock_params.shck_vel AS shck_vel,
                    {format_line_ratio_as_sql_query(xnum, xden)},
                    {format_line_ratio_as_sql_query(ynum, yden)},
                    {format_quantity_as_sql_query(xquan)},
                    {format_quantity_as_sql_query(yquan)},
                    shock_params.mag_fld AS mag_fld
                FROM shock_params
                    INNER JOIN emis_IR ON emis_IR.ModelID=shock_params.ModelID
                    INNER JOIN emis_VI ON emis_VI.ModelID=shock_params.ModelID
                    INNER JOIN abundances ON abundances.AbundID=shock_params.AbundID
                WHERE emis_VI.model_type='{model_type1}' AND emis_IR.model_type='{model_type1}'
                    AND abundances.name='{abundance}'
                    AND shock_params.ref='Allen08'
                    AND shock_params.shck_vel BETWEEN {shck_vel_lo} AND {shck_vel_hi}
                    AND shock_params.preshck_dens={preshck_dens}
                ORDER BY shck_vel;"""
        
        sel_prec = f"""SELECT
                    shock_params.shck_vel AS shck_vel,
                    {format_line_ratio_as_sql_query(xnum, xden)},
                    {format_line_ratio_as_sql_query(ynum, yden)},
                    {format_quantity_as_sql_query(xquan)},
                    {format_quantity_as_sql_query(yquan)},
                    shock_params.mag_fld AS mag_fld
                FROM shock_params
                    INNER JOIN emis_IR ON emis_IR.ModelID=shock_params.ModelID
                    INNER JOIN emis_VI ON emis_VI.ModelID=shock_params.ModelID
                    INNER JOIN abundances ON abundances.AbundID=shock_params.AbundID
                WHERE emis_VI.model_type='{model_type2}' AND emis_IR.model_type='{model_type2}'
                    AND abundances.name='{abundance}'
                    AND shock_params.ref='Allen08'
                    AND shock_params.shck_vel BETWEEN {shck_vel_lo} AND {shck_vel_hi}
                    AND shock_params.preshck_dens={preshck_dens}
                ORDER BY shck_vel;"""

        # Run query
        with engine.connect() as conn:
            result_shck = pd.read_sql(sel_shck, con=conn)
            result_prec = pd.read_sql(sel_prec, con=conn)
            return [result_shck, result_prec]
    else:
        sel = f"""SELECT
                    shock_params.shck_vel AS shck_vel,
                    {format_line_ratio_as_sql_query(xnum, xden)},
                    {format_line_ratio_as_sql_query(ynum, yden)},
                    {format_quantity_as_sql_query(xquan)},
                    {format_quantity_as_sql_query(yquan)},
                    shock_params.mag_fld AS mag_fld
                FROM shock_params
                    INNER JOIN emis_IR ON emis_IR.ModelID=shock_params.ModelID
                    INNER JOIN emis_VI ON emis_VI.ModelID=shock_params.ModelID
                    INNER JOIN abundances ON abundances.AbundID=shock_params.AbundID
                WHERE emis_VI.model_type='{model_type}' AND emis_IR.model_type='{model_type}'
                    AND abundances.name='{abundance}'
                    AND shock_params.ref='Allen08'
                    AND shock_params.shck_vel BETWEEN {shck_vel_lo} AND {shck_vel_hi}
                    AND shock_params.preshck_dens={preshck_dens}
                ORDER BY shck_vel;"""

        # Run query
        with engine.connect() as conn:
            result = pd.read_sql(sel, con=conn)
            return result

def populate_abundance_dropdown():

    # Set environment variables
    host   = os.environ['MdB_HOST']
    user   = os.environ['MdB_USER']
    passwd = os.environ['MdB_PASSWD']
    port   = os.environ['MdB_PORT']
    dbname = "3MdBs"
    engine = create_engine(f"mysql+pymysql://{user}:{passwd}@{host}:{port}/{dbname}")

    # Define SQL query
    sel_abundance_query = """
        SELECT DISTINCT a.name
        FROM shock_params AS sp
        JOIN abundances  AS a ON a.AbundID = sp.AbundID
        WHERE sp.ref = 'Allen08'
        ORDER BY a.name;
    """

    # Perform query
    with engine.connect() as conn:
        result = pd.read_sql(sel_abundance_query, con=conn)
        abundances = list(result.get('name'))

    return abundances

def populate_density_dropdown(abundance):

    # Set environment variables
    host   = os.environ['MdB_HOST']
    user   = os.environ['MdB_USER']
    passwd = os.environ['MdB_PASSWD']
    port   = os.environ['MdB_PORT']
    dbname = "3MdBs"
    engine = create_engine(f"mysql+pymysql://{user}:{passwd}@{host}:{port}/{dbname}")

    # Define SQL query
    sel_density_query = f"""
        SELECT DISTINCT sp.preshck_dens
        FROM shock_params AS sp
        JOIN abundances AS a ON a.AbundID = sp.AbundID
        WHERE sp.ref = 'Allen08'
        AND a.name = '{abundance}'
        ORDER BY sp.preshck_dens;
    """

    # Perform query
    with engine.connect() as conn:
        result = pd.read_sql(sel_density_query, con=conn)
        densities = list(result.get('preshck_dens'))

    return densities

def return_lines_to_query():

    # All lines currently able to be calculated using SQL queries
    lines = {
        'Ha': 'emis_VI.HI_6563',
        'Hb': 'emis_VI.HI_4861',
        'OIII_5007': 'emis_VI.OIII_5007',
        'NII': 'emis_VI.NII_6548 + emis_VI.NII_6583',
        'SII': 'emis_VI.SII_6716 + emis_VI.SII_6731'
    }

    return lines

def return_quantities_to_query():
    
    # All quantities currently able to be calculated using SQL queries
    quantities = {
        'O23': '(emis_VI.OII_7320 + emis_VI.OII_7320) / emis_VI.OIII_5007',
        'S23': '(emis_VI.SII_6716 + emis_VI.SII_6731 + emis_IR.SIII_9069) / emis_VI.HI_4861',
        'OIII_Hb': 'emis_VI.OIII_5007 / emis_VI.HI_4861',
        'NII_Ha': 'emis_VI.NII_6583 / emis_VI.HI_6563'
        }
    
    return quantities