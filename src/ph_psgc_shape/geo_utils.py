#   ---------------------------------------------------------------------------------
#   Copyright (c) James Faeldon. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   ---------------------------------------------------------------------------------
from __future__ import annotations

import re

import numpy as np
import geopandas as gpd
import pandas as pd


def read_excel_file(file_path, sheet_name=None):
    """
    Reads an Excel file and prints its contents.

    Args:
        file_path (str): The path to the Excel file.

    Raises:
        FileNotFoundError: If the specified file is not found.
        Exception: If any other error occurs while reading the file.

    Returns:
        None
    """
    try:
        # Attempt to read the Excel file
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def read_shapefile(shapefile_path):
    """
    Reads a shapefile into a GeoDataFrame.

    Parameters:
    - shapefile_path: str, the file path to the shapefile.

    Returns:
    - gdf: GeoDataFrame, the GeoDataFrame containing the shapefile data.
    """
    try:
        # Read the shapefile
        gdf = gpd.read_file(shapefile_path)
        return gdf
    except Exception as e:
        print(f"An error occurred while reading the shapefile: {e}")
        return None


def psgc_int_to_psgc_string(number):
    """
    Converts an integer to a string with a 'PH' prefix, ensuring the numeric
    part is always represented with exactly 9 digits by prepending zeros if necessary.

    Parameters:
    - number: int, the integer to be converted.

    Returns:
    - str: A string representation of the number with 'PH' prefix and 9 digits.
    """
    # Convert the number to a string and pad with zeros to ensure it has exactly 9 digits
    number_str = str(number).zfill(9)
    return f"PH{number_str}"


def convert_adm_pcode(input_str, suffix):
    """
    Converts amd_pcode to psgc_code.

    Parameters:
    - input_str: str, the input string to be converted.

    Returns:
    - str: The converted string.
    """

    if not isinstance(input_str, str):
        print(f"Data is not a string {input_str}")
        return "0"  # Need to maintain int format in the columns

    # Check and remove the 'PH' prefix
    if input_str.startswith("PH"):
        numeric_part = input_str[2:]
    elif input_str.startswith("P"):
        numeric_part = input_str[1:]
    else:
        numeric_part = input_str  # Assume the string is already in the desired format

    # Insert a zeroes to make the string exactly 10 digits long
    return numeric_part + suffix


def add_geometry_measures(gdf, epsg_code=None):
    """
    Adds columns for perimeter and area in both CRS units and in kilometers/square kilometers.

    Parameters:
    - gdf: GeoDataFrame - GeoDataFrame with geometries.
    - epsg_code: int or str (optional) - EPSG code of the projected CRS to use for accurate measurement in metric units.

    Returns:
    - GeoDataFrame with added columns for perimeter and area.
    """
    # Reproject GeoDataFrame if an EPSG code is provided
    if epsg_code and gdf.crs != epsg_code:
        gdf = gdf.to_crs(epsg=epsg_code)

    # Calculate perimeter and area in CRS units
    gdf["len_crs"] = gdf.geometry.length.fillna(0).astype(int)
    gdf["area_crs"] = gdf.geometry.area.fillna(0).astype(int)

    # Assuming the CRS units are meters, convert to kilometers and square kilometers
    # Adjust the conversion if the CRS units are different
    gdf["len_km"] = gdf["len_crs"] // 1000
    gdf["area_km2"] = gdf["area_crs"] // 1e6

    return gdf
