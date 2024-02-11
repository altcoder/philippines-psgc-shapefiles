#   ---------------------------------------------------------------------------------
#   Copyright (c) James Faeldon. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   ---------------------------------------------------------------------------------


from __future__ import annotations


def report_nulls(gdf, column_name, report_table=False):
    """
    Prints a report of null values in a GeoDataFrame column and provides an option to display the corresponding rows.
    Used for checking if outer join contains nulls.

    Args:
        gdf (GeoDataFrame): The GeoDataFrame containing the data.
        column_name (str): The name of the column to check for null values.
        report_table (bool, optional): Whether to display the corresponding rows with null values. Defaults to False.
    """
    # Count rows where the specific column is null
    null_psgc_count = gdf["name"].isnull().sum()
    if null_psgc_count > 0:
        print(f"MATCH REPORT: {null_psgc_count} rows from the shapefile didn't have a match from the PSGC table")
        if report_table:
            if column_name == "adm4_en":
                print(
                    gdf[gdf["name"].isnull()][
                        [
                            "psgc_code",
                            "corr_code",
                            "name",
                            column_name,
                            "adm3_en",
                            "adm2_en",
                            "adm1_en",
                        ]
                    ]
                    .sort_values(by=column_name)
                    .head(20)
                )
            else:
                print(
                    gdf[gdf["name"].isnull()][
                        [
                            "psgc_code",
                            "corr_code",
                            "name",
                            column_name,
                        ]
                    ]
                    .sort_values(by=column_name)
                    .head(20)
                )

    null_shape_count = gdf[column_name].isnull().sum()
    if null_shape_count > 0:
        print(f"MATCH REPORT: {null_shape_count} rows from the PSGC table didn't have a match from the shapefile")
        if report_table:
            if column_name == "adm4_en":
                print(
                    gdf[gdf[column_name].isnull()][
                        ["psgc_code", "corr_code", "name", column_name, "bgy_adm3_en", "bgy_adm2_en"]
                    ]
                    .sort_values(by="name")
                    .head(20)
                )
            else:
                print(
                    gdf[gdf[column_name].isnull()][
                        [
                            "psgc_code",
                            "corr_code",
                            "name",
                            column_name,
                        ]
                    ]
                    .sort_values(by="name")
                    .head(20)
                )
    if null_psgc_count == 0 and null_shape_count == 0:
        print("MATCH REPORT: All rows matched!")


def debug_bgy_log(bgy, psgc_df, bgysubmuns_gdf, unmatched_psgc_df=None, unmatched_shape_df=None):
    """
    Debug function to print information about a barangay (bgy) and whether it's matched or not.

    Parameters:
    - bgy (str): The name of the barangay.
    - psgc_df (DataFrame): DataFrame containing PSGC codes and names.
    - bgysubmuns_gdf (GeoDataFrame): GeoDataFrame containing shape information for barangays.
    - unmatched_psgc_df (DataFrame, optional): DataFrame containing unmatched PSGC codes and names. Defaults to None.
    - unmatched_shape_df (DataFrame, optional): DataFrame containing unmatched shape information for barangays.
    Defaults to None.
    """
    print("==============DEBUG================")
    print(bgy)
    shape_df = bgysubmuns_gdf[bgysubmuns_gdf["adm4_en"] == bgy][["psgc_code", "adm4_pcode", "adm4_en"]]
    if shape_df.shape[0] == 0:
        print("  SHAPE NOT FOUND!!!")
    else:
        print(f"  SHAPE: OK [{shape_df.iloc[0]['psgc_code']} {shape_df.iloc[0]['adm4_en']}]")

    psgc_df = psgc_df[psgc_df["name"] == bgy][["psgc_code", "name"]]
    if psgc_df.shape[0] == 0:
        print("  PSGC NOT FOUND!!!")
    else:
        print(f"  PSGC : OK [{psgc_df.iloc[0]['psgc_code']} {psgc_df.iloc[0]['name']}]")

    if unmatched_shape_df is not None and unmatched_shape_df[(unmatched_shape_df["adm4_en"] == bgy)].shape[0] > 0:
        shp = unmatched_shape_df[(unmatched_shape_df["adm4_en"] == bgy)].iloc[0]
        print(f"  SHAPE: NOT yet matched! [{shp['psgc_code']} {shp['adm4_en']}]")
    elif unmatched_psgc_df is not None:
        print("  SHAPE: Matched!")

    if unmatched_psgc_df is not None and unmatched_psgc_df[(unmatched_psgc_df["name"] == bgy)].shape[0] > 0:
        psgc = unmatched_psgc_df[(unmatched_psgc_df["name"] == bgy)].iloc[0]
        print(f"  PSGC : NOT yet matched! [{psgc['psgc_code']} {psgc['name']}]")
    elif unmatched_psgc_df is not None:
        print("  PSGC : Matched!")

    print("===================================\n\n")
