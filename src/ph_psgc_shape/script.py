#   ---------------------------------------------------------------------------------
#   Copyright (c) James Faeldon. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   ---------------------------------------------------------------------------------
from __future__ import annotations

import sys

import numpy as np
from debug import debug_bgy_log, report_nulls
from geo_utils import add_geometry_measures, convert_adm_pcode, read_excel_file, read_shapefile


def hello():
    print("Hello from process_psgc_2023_4q_region")


def process_psgc_2023_4q_country(psgc_df):
    country_gdf = read_shapefile("data/2023/Country/phl_admbnda_adm0_singlepart_psa_namria_20231106.shp")
    country_gdf.columns = [
        "shape_len",
        "shape_area",
        "adm0_en",
        "adm0_pcode",
        "date",
        "valid_on",
        "valid_to",
        "geometry",
    ]
    print(country_gdf.head())
    print(country_gdf.columns)
    print(country_gdf.shape)

    country_gdf = add_geometry_measures(country_gdf, epsg_code=32651)
    country_gdf = country_gdf[
        [
            "adm0_en",
            "len_crs",
            "area_crs",
            "len_km",
            "area_km2",
            "geometry",
        ]
    ]
    country_gdf.columns = [
        "adm0_en",
        "len_crs",
        "area_crs",
        "len_km",
        "area_km2",
        "geometry",
    ]

    print(country_gdf.head())
    country_gdf.to_file("dist/PH_Adm0_Country.shp.zip", driver="ESRI Shapefile")
    gdf_without_geometry = country_gdf.drop(columns=["geometry"])
    gdf_without_geometry.to_csv("dist/PH_Adm0_Country.csv", index=False)


def process_psgc_2023_4q_region(psgc_df):
    psgc_df = psgc_df[psgc_df["geo_level"] == "Reg"]

    regions_gdf = read_shapefile("data/2023/Regions/phl_admbnda_adm1_psa_namria_20231106.shp")
    regions_gdf.columns = [
        "adm1_en",
        "adm1_pcode",
        "adm0_en",
        "adm0_pcode",
        "date",
        "valid_on",
        "valid_to",
        "shape_len",
        "shape_area",
        "adm1_alt",
        "shape_sqkm",
        "geometry",
    ]
    regions_gdf["psgc_code"] = regions_gdf["adm1_pcode"].apply(lambda x: convert_adm_pcode(x, "00000000")).astype(int)
    print(regions_gdf.head())
    print(regions_gdf.columns)
    print(regions_gdf.shape)

    regions_shape_gdf = regions_gdf.merge(psgc_df, on="psgc_code", how="outer")
    regions_shape_gdf = regions_shape_gdf[
        [
            "psgc_code",
            "name",
            "corr_code",
            "geo_level",
            "city_class",
            "inc_class",
            "urb_rur",
            "pop_2015",
            "pop_2020",
            "status",
            "adm1_pcode",
            "adm1_en",
            "adm0_pcode",
            "shape_len",
            "shape_area",
            "shape_sqkm",
            "geometry",
        ]
    ]

    report_nulls(regions_shape_gdf, "adm1_en", report_table=True)

    regions_shape_gdf = add_geometry_measures(regions_shape_gdf, epsg_code=32651)
    regions_shape_gdf = regions_shape_gdf[
        [
            "psgc_code",
            "name",
            "geo_level",
            "len_crs",
            "area_crs",
            "len_km",
            "area_km2",
            "geometry",
        ]
    ]
    regions_shape_gdf.columns = [
        "adm1_psgc",
        "adm1_en",
        "geo_level",
        "len_crs",
        "area_crs",
        "len_km",
        "area_km2",
        "geometry",
    ]

    print(regions_shape_gdf.head())
    regions_shape_gdf.to_file("dist/PH_Adm1_Regions.shp.zip", driver="ESRI Shapefile")
    gdf_without_geometry = regions_shape_gdf.drop(columns=["geometry"])
    gdf_without_geometry.to_csv("dist/PH_Adm1_Regions.csv", index=False)


def process_psgc_2023_4q_provdists(psgc_df):
    psgc_df = psgc_df[
        (psgc_df["geo_level"] == "Prov")
        | (psgc_df["name"] == "City of Isabela (Not a Province)")
        | (psgc_df["geo_level"] == "Dist")
    ]

    provdists_gdf = read_shapefile("data/2023/ProvDists/phl_admbnda_adm2_psa_namria_20231106.shp")
    provdists_gdf.columns = [
        "adm2_en",
        "adm2_pcode",
        "adm1_en",
        "adm1_pcode",
        "adm0_en",
        "adm0_pcode",
        "date",
        "valid_on",
        "valid_to",
        "shape_len",
        "shape_area",
        "adm2_alt",
        "shape_sqkm",
        "geometry",
    ]
    provdists_gdf["psgc_code"] = provdists_gdf["adm2_pcode"].apply(lambda x: convert_adm_pcode(x, "00000")).astype(int)

    # Update PSGC code of City of Isabela (not a province)
    mask = provdists_gdf["psgc_code"] == 909700000
    provdists_gdf.loc[mask, "psgc_code"] = 990100000
    provdists_gdf.loc[mask, "adm2_pcode"] = "P09901"
    provdists_gdf.loc[mask, "geolevel"] = "NotProv"

    # Special Geographic Areas
    provdists_gdf[provdists_gdf["adm2_en"].str.startswith("Special Geographic Area")]["geo_level"] = "SGU"

    print(provdists_gdf.head())
    print(provdists_gdf.columns)
    print(provdists_gdf.shape)

    provdists_shape_gdf = provdists_gdf.merge(psgc_df, on="psgc_code", how="outer")
    provdists_shape_gdf = provdists_shape_gdf[
        [
            "psgc_code",
            "name",
            "corr_code",
            "geo_level",
            "city_class",
            "inc_class",
            "urb_rur",
            "pop_2015",
            "pop_2020",
            "status",
            "adm2_pcode",
            "adm2_en",
            "adm1_pcode",
            "adm0_pcode",
            "shape_len",
            "shape_area",
            "shape_sqkm",
            "geometry",
        ]
    ]
    report_nulls(provdists_shape_gdf, column_name="adm2_en", report_table=True)

    provdists_shape_gdf = add_geometry_measures(provdists_shape_gdf, epsg_code=32651)
    provdists_shape_gdf["adm1_psgc"] = (
        provdists_shape_gdf["adm1_pcode"].apply(lambda x: convert_adm_pcode(x, "00000000")).astype(int)
    )
    provdists_shape_gdf = provdists_shape_gdf[
        [
            "adm1_psgc",
            "psgc_code",
            "name",
            "geo_level",
            "len_crs",
            "area_crs",
            "len_km",
            "area_km2",
            "geometry",
        ]
    ]
    provdists_shape_gdf.columns = [
        "adm1_psgc",
        "adm2_psgc",
        "adm2_en",
        "geo_level",
        "len_crs",
        "area_crs",
        "len_km",
        "area_km2",
        "geometry",
    ]
    print(provdists_shape_gdf.head())
    provdists_shape_gdf.to_file("dist/PH_Adm2_ProvDists.shp.zip", driver="ESRI Shapefile")
    gdf_without_geometry = provdists_shape_gdf.drop(columns=["geometry"])
    gdf_without_geometry.to_csv("dist/PH_Adm2_ProvDists.csv", index=False)


def update_municities_psgc_code(municities_gdf, old_psgc_code, new_psgc_code):
    municities_gdf.loc[
        municities_gdf["psgc_code"] == old_psgc_code, "adm3_pcode"
    ] = f"P{str(new_psgc_code).zfill(10)[:7]}"
    municities_gdf.loc[
        municities_gdf["psgc_code"] == old_psgc_code, "adm2_pcode"
    ] = f"P{str(new_psgc_code).zfill(10)[:5]}"
    municities_gdf.loc[municities_gdf["psgc_code"] == old_psgc_code, "psgc_code"] = new_psgc_code


def update_bgysubmuns_psgc_code(bgysubmuns_gdf, old_psgc_code, new_psgc_code, adm4_en=None):
    if adm4_en is None:
        bgysubmuns_gdf.loc[
            bgysubmuns_gdf["psgc_code"] == old_psgc_code, "adm4_pcode"
        ] = f"P{str(new_psgc_code).zfill(10)}"
        bgysubmuns_gdf.loc[
            bgysubmuns_gdf["psgc_code"] == old_psgc_code, "adm3_pcode"
        ] = f"P{str(new_psgc_code).zfill(10)[:7]}"
        bgysubmuns_gdf.loc[
            bgysubmuns_gdf["psgc_code"] == old_psgc_code, "adm2_pcode"
        ] = f"P{str(new_psgc_code).zfill(10)[:5]}"
        bgysubmuns_gdf.loc[bgysubmuns_gdf["psgc_code"] == old_psgc_code, "psgc_code"] = new_psgc_code
    else:
        bgysubmuns_gdf.loc[
            (bgysubmuns_gdf["psgc_code"] == old_psgc_code) & (bgysubmuns_gdf["adm4_en"] == adm4_en), "adm4_pcode"
        ] = f"P{str(new_psgc_code).zfill(10)}"
        bgysubmuns_gdf.loc[
            (bgysubmuns_gdf["psgc_code"] == old_psgc_code) & (bgysubmuns_gdf["adm4_en"] == adm4_en), "adm3_pcode"
        ] = f"P{str(new_psgc_code).zfill(10)[:7]}"
        bgysubmuns_gdf.loc[
            (bgysubmuns_gdf["psgc_code"] == old_psgc_code) & (bgysubmuns_gdf["adm4_en"] == adm4_en), "adm2_pcode"
        ] = f"P{str(new_psgc_code).zfill(10)[:5]}"
        bgysubmuns_gdf.loc[
            (bgysubmuns_gdf["psgc_code"] == old_psgc_code) & (bgysubmuns_gdf["adm4_en"] == adm4_en), "psgc_code"
        ] = new_psgc_code


def process_psgc_2023_4q_municities(psgc_df):
    psgc_df = psgc_df[
        (psgc_df["geo_level"] == "Mun") | (psgc_df["geo_level"] == "City") | (psgc_df["geo_level"] == "SGU")
    ]

    municities_gdf = read_shapefile("data/2023/MuniCities/phl_admbnda_adm3_psa_namria_20231106.shp")
    municities_gdf.columns = [
        "adm3_en",
        "adm3_pcode",
        "adm2_en",
        "adm2_pcode",
        "adm1_en",
        "adm1_pcode",
        "adm0_en",
        "adm0_pcode",
        "date",
        "valid_on",
        "valid_to",
        "adm3_ref",
        "adm3_alt",
        "shape_len",
        "shape_area",
        "shape_sqkm",
        "geometry",
    ]
    municities_gdf["psgc_code"] = municities_gdf["adm3_pcode"].apply(lambda x: convert_adm_pcode(x, "000")).astype(int)

    # Update PSGC codes
    update_municities_psgc_code(municities_gdf, 305401000, 330100000)  # City of Angeles
    update_municities_psgc_code(municities_gdf, 307107000, 331400000)  # City of Olongapo
    update_municities_psgc_code(municities_gdf, 405624000, 431200000)  # City of Lucena
    update_municities_psgc_code(municities_gdf, 603022000, 631000000)  # City of Iloilo
    update_municities_psgc_code(municities_gdf, 604501000, 630200000)  # City of Bacolod
    update_municities_psgc_code(municities_gdf, 702217000, 730600000)  # City of Cebu
    update_municities_psgc_code(municities_gdf, 702226000, 731100000)  # City of Lapu-Lapu
    update_municities_psgc_code(municities_gdf, 702230000, 731300000)  # City of Mandaue
    update_municities_psgc_code(municities_gdf, 831600000, 803747000)  # City of Tacloban
    update_municities_psgc_code(municities_gdf, 907332000, 931700000)  # City of Zamboanga
    update_municities_psgc_code(municities_gdf, 302401000, 330100000)  # City of Angeles
    update_municities_psgc_code(municities_gdf, 803747000, 831600000)  # City of Tacloban
    update_municities_psgc_code(municities_gdf, 909701000, 990101000)  # City of Isabela
    update_municities_psgc_code(municities_gdf, 1004305000, 1030500000)  # City of Cagayan de Oro
    update_municities_psgc_code(municities_gdf, 1003504000, 1030900000)  # City of Iligan
    update_municities_psgc_code(municities_gdf, 1102402000, 1130700000)  # City of Davao
    update_municities_psgc_code(municities_gdf, 1206303000, 1230800000)  # City of General Santos
    update_municities_psgc_code(municities_gdf, 1307501000, 1380100000)  # City of Caloocan
    update_municities_psgc_code(municities_gdf, 1303901000, 1380600000)  # City of Manila
    update_municities_psgc_code(municities_gdf, 1307402000, 1380700000)  # City of Marikina
    update_municities_psgc_code(municities_gdf, 1307401000, 1380500000)  # City of Mandaluyong
    update_municities_psgc_code(municities_gdf, 1307403000, 1381200000)  # City of Pasig
    update_municities_psgc_code(municities_gdf, 1307503000, 1380900000)  # City of Navotas
    update_municities_psgc_code(municities_gdf, 1307603000, 1380800000)  # City of Muntinlupa
    update_municities_psgc_code(municities_gdf, 1307502000, 1380400000)  # City of Malabon
    update_municities_psgc_code(municities_gdf, 1307602000, 1380300000)  # City of Makati
    update_municities_psgc_code(municities_gdf, 1307601000, 1380200000)  # City of Las Piñas
    update_municities_psgc_code(municities_gdf, 1600202000, 1630400000)  # City of Butuan
    update_municities_psgc_code(municities_gdf, 1401102000, 1430300000)  # City of Baguio
    update_municities_psgc_code(municities_gdf, 1307606000, 1381701000)  # Pateros
    update_municities_psgc_code(municities_gdf, 1307504000, 1381600000)  # City of Valenzuela
    update_municities_psgc_code(municities_gdf, 1307607000, 1381500000)  # City of Taguig
    update_municities_psgc_code(municities_gdf, 1307405000, 1381400000)  # City of San Juan
    update_municities_psgc_code(municities_gdf, 1307404000, 1381300000)  # Quezon City
    update_municities_psgc_code(municities_gdf, 1307605000, 1381100000)  # Pasay City
    update_municities_psgc_code(municities_gdf, 1307604000, 1381000000)  # City of Parañaque
    update_municities_psgc_code(municities_gdf, 1705316000, 1731500000)  # City of Puerto Princesa
    update_municities_psgc_code(municities_gdf, 1908718000, 1908701000)  # Barira
    update_municities_psgc_code(municities_gdf, 1908730000, 1908704000)  # Datu Blah T. Sinsuat
    update_municities_psgc_code(municities_gdf, 1908734000, 1908708000)  # Northern Kabuntalan
    update_municities_psgc_code(municities_gdf, 1908715000, 1908713000)  # Upi
    update_municities_psgc_code(municities_gdf, 1908831000, 1908804000)  # Datu Anggal Midtimbang
    update_municities_psgc_code(municities_gdf, 1908826000, 1908809000)  # Datu Saudi Ampatuan
    update_municities_psgc_code(municities_gdf, 1908825000, 1908812000)  # Guindulungan
    update_municities_psgc_code(municities_gdf, 1908833000, 1908818000)  # Pandag
    update_municities_psgc_code(municities_gdf, 1908832000, 1908814000)  # Mangudadatu
    update_municities_psgc_code(municities_gdf, 1908837000, 1908821000)  # Shariff Saydona Mustapha
    update_municities_psgc_code(municities_gdf, 1908712000, 1908710000)  # Sultan Kudarat
    update_municities_psgc_code(municities_gdf, 1908816000, 1908824000)  # Talayan
    update_municities_psgc_code(municities_gdf, 1908822000, 1908815000)  # Pagagawan
    update_municities_psgc_code(municities_gdf, 1908819000, 1908811000)  # Gen. S.K. Pendatun
    update_municities_psgc_code(municities_gdf, 1908806000, 1908807000)  # Datu Piang
    update_municities_psgc_code(municities_gdf, 1908803000, 1908802000)  # Buluan
    update_municities_psgc_code(municities_gdf, 1908721000, 1908712000)  # Talitay
    update_municities_psgc_code(municities_gdf, 1908714000, 1908706000)  # Kabuntulan
    update_municities_psgc_code(municities_gdf, 1908707000, 1908705000)  # Datu Odin Sinsuat
    update_municities_psgc_code(municities_gdf, 1908709000, 1908707000)  # Matanog
    update_municities_psgc_code(municities_gdf, 1908828000, 1908803000)  # Datu Abdullah Sangki
    update_municities_psgc_code(municities_gdf, 1908805000, 1908806000)  # Datu Paglas
    update_municities_psgc_code(municities_gdf, 1908810000, 1908816000)  # Pagalungan
    update_municities_psgc_code(municities_gdf, 1908829000, 1908819000)  # Rajah Buayan
    update_municities_psgc_code(municities_gdf, 1908817000, 1908822000)  # South Upi
    update_municities_psgc_code(municities_gdf, 1908711000, 1908709000)  # Parang
    update_municities_psgc_code(municities_gdf, 1908835000, 1908805000)  # Datu Hoffer Ampatuan
    update_municities_psgc_code(municities_gdf, 1908827000, 1908810000)  # Datu Unsay
    update_municities_psgc_code(municities_gdf, 1908823000, 1908817000)  # Paglat
    update_municities_psgc_code(municities_gdf, 1908724000, 1908711000)  # Sultan Mastura
    update_municities_psgc_code(municities_gdf, 1908813000, 1908823000)  # Sultan Sa Barongis
    update_municities_psgc_code(municities_gdf, 1908820000, 1908813000)  # Mamasapano
    update_municities_psgc_code(municities_gdf, 1908808000, 1908820000)  # Shariff Aguak
    update_municities_psgc_code(municities_gdf, 1908836000, 1908808000)  # Datu Salibo

    # Special Geographic Areas
    update_municities_psgc_code(municities_gdf, 1909901000, 1999901000)  # Carmen Cluster
    update_municities_psgc_code(municities_gdf, 1909902000, 1999902000)  # Kabacan Cluster
    update_municities_psgc_code(municities_gdf, 1909903000, 1999903000)  # Midsayap Cluster I
    update_municities_psgc_code(municities_gdf, 1909904000, 1999904000)  # Midsayap Cluster II
    update_municities_psgc_code(municities_gdf, 1909905000, 1999905000)  # Pigcawayan Cluster
    update_municities_psgc_code(municities_gdf, 1909906000, 1999906000)  # Pikit Cluster I
    update_municities_psgc_code(municities_gdf, 1909907000, 1999907000)  # Pikit Cluster II
    update_municities_psgc_code(municities_gdf, 1909908000, 1999908000)  # Pikit Cluster III

    print(municities_gdf.head())
    print(municities_gdf.columns)
    print(municities_gdf.shape)

    municities_shape_gdf = municities_gdf.merge(psgc_df, on="psgc_code", how="outer")
    municities_shape_gdf = municities_shape_gdf[
        [
            "psgc_code",
            "name",
            "corr_code",
            "geo_level",
            "city_class",
            "inc_class",
            "urb_rur",
            "pop_2015",
            "pop_2020",
            "status",
            "adm3_pcode",
            "adm3_en",
            "adm2_pcode",
            "adm1_pcode",
            "adm0_pcode",
            "shape_len",
            "shape_area",
            "shape_sqkm",
            "geometry",
        ]
    ]
    report_nulls(municities_shape_gdf, column_name="adm3_en", report_table=True)

    municities_shape_gdf = add_geometry_measures(municities_shape_gdf, epsg_code=32651)
    municities_shape_gdf["adm1_psgc"] = (
        municities_shape_gdf["adm1_pcode"].apply(lambda x: convert_adm_pcode(x, "00000000")).astype(int)
    )
    municities_shape_gdf["adm2_psgc"] = (
        municities_shape_gdf["adm2_pcode"].apply(lambda x: convert_adm_pcode(x, "00000")).astype(int)
    )
    municities_shape_gdf = municities_shape_gdf[
        [
            "adm1_psgc",
            "adm2_psgc",
            "psgc_code",
            "name",
            "geo_level",
            "len_crs",
            "area_crs",
            "len_km",
            "area_km2",
            "geometry",
        ]
    ]
    municities_shape_gdf.columns = [
        "adm1_psgc",
        "adm2_psgc",
        "adm3_psgc",
        "adm3_en",
        "geo_level",
        "len_crs",
        "area_crs",
        "len_km",
        "area_km2",
        "geometry",
    ]
    print(municities_shape_gdf.head())
    municities_shape_gdf.to_file("dist/PH_Adm3_MuniCities.shp.zip", driver="ESRI Shapefile")
    gdf_without_geometry = municities_shape_gdf.drop(columns=["geometry"])
    gdf_without_geometry.to_csv("dist/PH_Adm3_MuniCities.csv", index=False)


def process_psgc_2023_4q_bgysubmuns(psgc_df):
    debug_bgy = "Kulimpang"
    debug_bgy_psgc = 1908702008

    psgc_df.columns = [
        "psgc_code",
        "name",
        "corr_code",
        "geo_level",
        "city_class",
        "inc_class",
        "urb_rur",
        "pop_2015",
        "pop_2020",
        "status",
        "bgy_adm3_pcode",
        "bgy_adm2_pcode",
        "bgy_adm3_en",
        "bgy_adm2_en",
    ]
    # bgysubmuns_gdf = read_shapefile("data/2023/BgySubMuns/phl_admbnda_adm4_psa_namria_20231106.shp")
    bgysubmuns_gdf = read_shapefile("data/edit/20240210/ph_adm4_20240210.shp")
    bgysubmuns_gdf.columns = [
        "adm4_en",
        "adm4_pcode",
        "adm4_ref",
        "adm3_en",
        "adm3_pcode",
        "adm2_en",
        "adm2_pcode",
        "adm1_en",
        "adm1_pcode",
        "adm0_en",
        "adm0_pcode",
        "date",
        "valid_on",
        "valid_to",
        "shape_len",
        "shape_area",
        "shape_sqkm",
        "layer",
        "path",
        "geometry",
    ]
    bgysubmuns_gdf["psgc_code"] = bgysubmuns_gdf["adm4_pcode"].apply(lambda x: convert_adm_pcode(x, "")).astype(int)

    # Remove forest reserves, unclaimed area, watershed, and tutban and manila north cemetery (except actual locations)
    bgysubmuns_gdf = bgysubmuns_gdf[
        (bgysubmuns_gdf["psgc_code"] % 1000 < 900) | (bgysubmuns_gdf["adm4_pcode"].str.startswith("PH13039"))
    ]
    # Remove locations in Manila like Paco, Malate that's not part of city or municipality
    # psgc_df.dropna(subset=["bgy_adm3_en"], inplace=True)

    # debug_bgy
    debug_bgy_log(debug_bgy, psgc_df, bgysubmuns_gdf)

    print("==== STAGE 0: PSGC code and name exact match =====")

    bgysubmuns_shape_gdf = bgysubmuns_gdf.merge(
        psgc_df, left_on=["psgc_code", "adm4_en"], right_on=["psgc_code", "name"], how="outer"
    )
    bgysubmuns_shape_gdf = bgysubmuns_shape_gdf[
        [
            "psgc_code",
            "name",
            "corr_code",
            "geo_level",
            "city_class",
            "inc_class",
            "urb_rur",
            "pop_2015",
            "pop_2020",
            "status",
            "adm4_pcode",
            "adm4_en",
            "adm3_pcode",
            "adm3_en",
            "bgy_adm3_pcode",
            "bgy_adm3_en",
            "adm2_pcode",
            "adm2_en",
            "bgy_adm2_pcode",
            "bgy_adm2_en",
            "adm1_pcode",
            "adm1_en",
            "adm0_pcode",
            "adm0_en",
            "shape_len",
            "shape_area",
            "shape_sqkm",
            "geometry",
        ]
    ]
    report_nulls(bgysubmuns_shape_gdf, column_name="adm4_en")
    # Debug
    unmatched_psgc_df = bgysubmuns_shape_gdf[bgysubmuns_shape_gdf["adm4_en"].isnull()]
    unmatched_shape_df = bgysubmuns_shape_gdf[bgysubmuns_shape_gdf["name"].isnull()]
    debug_bgy_log(debug_bgy, psgc_df, bgysubmuns_gdf, unmatched_psgc_df, unmatched_shape_df)

    # ==============================================================================================================

    print("==== STAGE 1: PSGC code match with correction =====")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908707001, 1908705001)  # Ambolodto
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908707002, 1908705002)  # Awang
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908718001, 1908701001)  # Barira
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908709001, 1908707001)  # Bayanga Norte
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908709002, 1908707002)  # Bayanga Sur
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908711014, 1908709001)  # Bongo Island
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908721002, 1908712001, "Bintan (Bentan)")  # Bintan
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908714003, 1908706003)  # Dadtumog
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908712012, 1908710008)  # Dalumangcob
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908805014, 1908806008)  # Kalumenga
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908712028, 1908710016)  # Katamlangan
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908833003, 1908818003)  # Kayupo
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908715017, 1908713013)  # Kinitan
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908724006, 1908711006)  # Macabico
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908831004, 1908804004)  # Midtimbang
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908831005, 1908804005)  # Nunangan
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908837016, 1908821013)  # Pagatin (Pagatin I)
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908837011, 1908821012)  # Pagatin
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908712037, 1908710031)  # Pigkelegan
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908806034, 1908807015)  # Poblacion
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908711020, 1908709020)  # Poblacion
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908817010, 1908822010)  # Romangaob
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908829010, 1908819010)  # Sapakan
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908707030, 1908705028)  # Sifaren
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908828010, 1908803010)  # Tukanolocong

    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908806001, 1908807001)  # Alonganan
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908805001, 1908806001)  # Alip
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908820002, 1908813002)  # Dabenayan
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908808004, 1908820002)  # Bialong
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908822001, 1908815001)  # Balatungkayo
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908817002, 1908822001)  # Biarong
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908712001, 1908710001, "Alamada")  # Alamada
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908823001, 1908817002)  # Damakling
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908813001, 1908823001)  # Angkayamat
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908822002, 1908815002, "Bulit")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908817003, 1908822002)  # Bongo
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908808002, 1908820001)  # Bagong
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908813003, 1908823002, "Barurao")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908709003, 1908707003, "Bugasan Norte")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908709004, 1908707004, "Bugasan Sur (Pob.)")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908805003, 1908806005, "Damawato")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908810008, 1908816005, "Galakit")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908817004, 1908822003, "Itaw")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908709005, 1908707005, "Kidama")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908817005, 1908822004, "Kigan")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908702012, 1908702008, "Kulimpang")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908817001, 1908822005, "Kuya")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908817006, 1908822006, "Lamud")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908709008, 1908707006, "Langco")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908709009, 1908707007, "Langkong")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908819008, 1908811006, "Lasangan")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908817007, 1908822007, "Looy")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908805007, 1908806015, "Mangadeg")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908711008, 1908709005, "Gadungan")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908813008, 1908823005, "Gadungan")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908813013, 1908823006, "Kulambog")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908702012, 1908702008, "Kulimpang")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908808011, 1908820003, "Kuloy")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908702017, 1908702009, "Mataya")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908817008, 1908822008, "Pandan")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908805010, 1908806021, "Puya")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908813004, 1908823003, "Bulod")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908813006, 1908823004, "Darampua")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908709007, 1908707008, "Sapad")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908702017, 1908702009, "Mataya")
    update_bgysubmuns_psgc_code(bgysubmuns_gdf, 1908808012, 1908820004, "Labu-labu")

    bgysubmuns_shape_s1_gdf = bgysubmuns_gdf.merge(psgc_df, on="psgc_code", how="outer")
    report_nulls(bgysubmuns_shape_s1_gdf, column_name="adm4_en")

    # Debug
    unmatched_psgc_df = bgysubmuns_shape_s1_gdf[bgysubmuns_shape_s1_gdf["adm4_en"].isnull()]
    unmatched_shape_df = bgysubmuns_shape_s1_gdf[bgysubmuns_shape_s1_gdf["name"].isnull()]
    debug_bgy_log(debug_bgy, psgc_df, bgysubmuns_gdf, unmatched_psgc_df, unmatched_shape_df)

    print("==== STAGE 2: Corresponce code and name exact match =====")

    # Try to match unmatched rows using old PSGC code
    for _, row in unmatched_psgc_df.iterrows():
        if np.isnan(row["corr_code"]):
            print(f"{row['name']} skipped because corr_code is nan")
            continue
        corr_code = int(row["corr_code"])
        new_psgc_code = row["psgc_code"]
        old_psgc_code = ((corr_code // 10_000_000) * 100_000_000) + corr_code % 10_000_000
        with_old_psgc_code = unmatched_shape_df[unmatched_shape_df["psgc_code"] == old_psgc_code]
        if with_old_psgc_code.shape[0] == 1:
            if old_psgc_code // 100_000 != 13039:  # Skip Manila
                update_bgysubmuns_psgc_code(bgysubmuns_gdf, old_psgc_code, new_psgc_code)
        elif with_old_psgc_code.shape[0] > 1:
            print(f"{row['name']} skipped because multiple match found for old PSGC code {old_psgc_code}")
            print(with_old_psgc_code.head())

    bgysubmuns_shape_s2_gdf = bgysubmuns_gdf.merge(psgc_df, on="psgc_code", how="outer")
    report_nulls(bgysubmuns_shape_s2_gdf, column_name="adm4_en")

    # Debug
    unmatched_psgc_df = bgysubmuns_shape_s2_gdf[bgysubmuns_shape_s2_gdf["adm4_en"].isnull()]
    unmatched_shape_df = bgysubmuns_shape_s2_gdf[bgysubmuns_shape_s2_gdf["name"].isnull()]
    debug_bgy_log(debug_bgy, psgc_df, bgysubmuns_gdf, unmatched_psgc_df, unmatched_shape_df)

    print("==== STAGE 3: Municipality name exact match =====")

    # Try to match unmatched rows using municipality name
    unmatched_bgys = unmatched_psgc_df.dropna(subset=["bgy_adm3_en"])
    for _, row in unmatched_bgys.iterrows():
        bgy_name = row["name"].strip()
        bgy_adm3_en = row["bgy_adm3_en"].strip()

        new_psgc_code = row["psgc_code"]
        exact_muni = bgysubmuns_gdf[
            (
                (bgysubmuns_gdf["adm4_en"] == bgy_name)
                | bgysubmuns_gdf["adm4_en"].str.contains(bgy_name, regex=False)
                | bgysubmuns_gdf["adm4_en"].apply(lambda x, bgy_name=bgy_name: x in bgy_name)
            )
            & (
                (bgysubmuns_gdf["adm3_en"] == bgy_adm3_en)
                | bgysubmuns_gdf["adm3_en"].str.contains(bgy_adm3_en, regex=False)
                | bgysubmuns_gdf["adm3_en"].apply(lambda x, bgy_adm3_en=bgy_adm3_en: x in bgy_adm3_en)
            )
        ]
        if exact_muni.shape[0] == 1:
            old_psgc_code = exact_muni.iloc[0]["psgc_code"]
            if old_psgc_code == debug_bgy_psgc:
                print("Change here 1!")
                print(new_psgc_code)
                print(bgy_name, exact_muni.iloc[0]["adm4_en"])
                print(bgy_adm3_en, exact_muni.iloc[0]["adm3_en"])
            update_bgysubmuns_psgc_code(bgysubmuns_gdf, old_psgc_code, new_psgc_code, exact_muni.iloc[0]["adm4_en"])
        elif exact_muni.shape[0] > 1:
            print(f"{row['name']} skipped because multiple match found")
            # print(exact_muni.head())

    psgc_df_with_adm3_en = psgc_df.dropna(subset=["bgy_adm3_en"])
    for _, row in unmatched_shape_df.iterrows():
        bgy_name = row["adm4_en"].strip()
        mun_name = row["adm3_en"].replace("-", " ").strip()  # Sultan Kudarat has a dash
        old_psgc_code = row["psgc_code"]

        exact_muni = psgc_df_with_adm3_en[
            (psgc_df_with_adm3_en["name"] == bgy_name)
            & (
                (psgc_df_with_adm3_en["bgy_adm3_en"] == mun_name)
                | psgc_df_with_adm3_en["bgy_adm3_en"].str.contains(mun_name, regex=False)
                | psgc_df_with_adm3_en["bgy_adm3_en"].apply(lambda x, mun_name=mun_name: x in mun_name)
            )
        ]
        if exact_muni.shape[0] == 1:
            new_psgc_code = exact_muni.iloc[0]["psgc_code"]
            update_bgysubmuns_psgc_code(bgysubmuns_gdf, old_psgc_code, new_psgc_code)
        elif exact_muni.shape[0] > 1:
            print(f"{bgy_name} skipped because multiple match found")
            # print(exact_muni.head())

    bgysubmuns_shape_s3_gdf = bgysubmuns_gdf.merge(psgc_df, on="psgc_code", how="outer")
    report_nulls(bgysubmuns_shape_s3_gdf, column_name="adm4_en")

    # Debug
    unmatched_psgc_df = bgysubmuns_shape_s3_gdf[bgysubmuns_shape_s3_gdf["adm4_en"].isnull()]
    unmatched_shape_df = bgysubmuns_shape_s3_gdf[bgysubmuns_shape_s3_gdf["name"].isnull()]
    debug_bgy_log(debug_bgy, psgc_df, bgysubmuns_gdf, unmatched_psgc_df, unmatched_shape_df)

    print("==== STAGE 4: Special Geographic Areas =====")

    # Try to match special geographic areas
    for _, row in unmatched_shape_df.iterrows():
        if str(row["psgc_code"]).startswith("19099"):
            old_psgc_code = row["psgc_code"]
            new_psgc_code = int("19999" + str(row["psgc_code"])[5:])
            update_bgysubmuns_psgc_code(bgysubmuns_gdf, old_psgc_code, new_psgc_code)

    bgysubmuns_shape_s4_gdf = bgysubmuns_gdf.merge(psgc_df, on="psgc_code", how="outer")
    report_nulls(bgysubmuns_shape_s4_gdf, column_name="adm4_en")

    # Debug
    unmatched_psgc_df = bgysubmuns_shape_s4_gdf[bgysubmuns_shape_s4_gdf["adm4_en"].isnull()]
    unmatched_shape_df = bgysubmuns_shape_s4_gdf[bgysubmuns_shape_s4_gdf["name"].isnull()]
    debug_bgy_log(debug_bgy, psgc_df, bgysubmuns_gdf, unmatched_psgc_df, unmatched_shape_df)

    print("==== STAGE 5: Municipality/Province/Metro Manila exact and name exact match =====")
    # Try to match adm3_en
    for _, row in unmatched_psgc_df.iterrows():
        new_psgc_code = row["psgc_code"]
        new_psgc_code_str = str(new_psgc_code).zfill(10)
        name = row["name"]
        bgysubmuns_gdf["psgc_code_str"] = bgysubmuns_gdf["psgc_code"].astype(str).str.zfill(10)

        match_df = bgysubmuns_gdf[
            # Municipality match and same name or alt_name
            (
                bgysubmuns_gdf["psgc_code_str"].str.startswith(new_psgc_code_str[:7])
                & (bgysubmuns_gdf["adm4_en"] == name)
            )
            # Province match and same name
            # | (
            #    ~bgysubmuns_gdf["psgc_code_str"].str.startswith(new_psgc_code_str[:7])
            #    & bgysubmuns_gdf["psgc_code_str"].str.startswith(new_psgc_code_str[:5])
            #    & (bgysubmuns_gdf["adm4_en"] == name)
            # )
            # Region match and same name in NCR
            | (
                new_psgc_code_str.startswith("13806")
                & (
                    bgysubmuns_gdf["psgc_code_str"].str.startswith("13039")
                    # | bgysubmuns_gdf["psgc_code_str"].str.startswith("13806")
                )
                & (bgysubmuns_gdf["adm4_en"] == name)
            )
        ]
        bgysubmuns_gdf.drop(columns=["psgc_code_str"], inplace=True)
        if match_df.shape[0] > 1:
            print(f"Skipping due to multiple matches for {name} [{new_psgc_code}]")
            print(match_df[["psgc_code", "adm4_pcode", "adm4_en", "adm3_en", "adm2_en", "adm1_en"]].head())
            continue
        elif match_df.shape[0] == 1:  # Match found
            old_psgc_code = match_df.iloc[0]["psgc_code"]
            update_bgysubmuns_psgc_code(bgysubmuns_gdf, old_psgc_code, new_psgc_code, name)

    bgysubmuns_shape_s5_gdf = bgysubmuns_gdf.merge(psgc_df, on="psgc_code", how="outer")
    report_nulls(bgysubmuns_shape_s5_gdf, column_name="adm4_en", report_table=True)

    # Debug
    unmatched_psgc_df = bgysubmuns_shape_s5_gdf[bgysubmuns_shape_s5_gdf["adm4_en"].isnull()]
    unmatched_shape_df = bgysubmuns_shape_s5_gdf[bgysubmuns_shape_s5_gdf["name"].isnull()]
    debug_bgy_log(debug_bgy, psgc_df, bgysubmuns_gdf, unmatched_psgc_df, unmatched_shape_df)

    # print(bgysubmuns_shape_gdf.head())
    bgysubmuns_shape_s5_gdf = bgysubmuns_shape_s5_gdf[
        [
            "psgc_code",
            "name",
            "corr_code",
            "geo_level",
            "city_class",
            "inc_class",
            "urb_rur",
            "pop_2015",
            "pop_2020",
            "status",
            "adm4_pcode",
            "adm4_en",
            "adm3_pcode",
            "adm3_en",
            "bgy_adm3_pcode",
            "bgy_adm3_en",
            "adm2_pcode",
            "adm2_en",
            "bgy_adm2_pcode",
            "bgy_adm2_en",
            "adm1_pcode",
            "adm1_en",
            "adm0_pcode",
            "adm0_en",
            "geometry",
        ]
    ]

    bgysubmuns_shape_s5_gdf = add_geometry_measures(bgysubmuns_shape_s5_gdf, epsg_code=32651)
    bgysubmuns_shape_s5_gdf["adm1_psgc"] = (
        bgysubmuns_shape_s5_gdf["adm1_pcode"].apply(lambda x: convert_adm_pcode(x, "00000000")).astype(int)
    )
    bgysubmuns_shape_s5_gdf["adm2_psgc"] = (
        bgysubmuns_shape_s5_gdf["adm2_pcode"].apply(lambda x: convert_adm_pcode(x, "00000")).astype(int)
    )
    bgysubmuns_shape_s5_gdf["adm3_psgc"] = (
        bgysubmuns_shape_s5_gdf["adm3_pcode"].apply(lambda x: convert_adm_pcode(x, "000")).astype(int)
    )
    bgysubmuns_shape_s5_gdf = bgysubmuns_shape_s5_gdf[
        [
            "adm1_psgc",
            "adm2_psgc",
            "adm3_psgc",
            "psgc_code",
            "name",
            "geo_level",
            "len_crs",
            "area_crs",
            "len_km",
            "area_km2",
            "geometry",
        ]
    ]
    bgysubmuns_shape_s5_gdf.columns = [
        "adm1_psgc",
        "adm2_psgc",
        "adm3_psgc",
        "adm4_psgc",
        "adm4_en",
        "geo_level",
        "len_crs",
        "area_crs",
        "len_km",
        "area_km2",
        "geometry",
    ]
    print(bgysubmuns_shape_s5_gdf.head())
    bgysubmuns_shape_s5_gdf.to_file("dist/PH_Adm4_BgySubMuns.shp.zip", driver="ESRI Shapefile")
    gdf_without_geometry = bgysubmuns_shape_s5_gdf.drop(columns=["geometry"])
    gdf_without_geometry.to_csv("dist/PH_Adm4_BgySubMuns.csv", index=False)


def process_psgc_2023_4q(file_path, sheet_name):
    df = read_excel_file(file_path, sheet_name)
    df.columns = [
        "psgc_code",
        "name",
        "corr_code",
        "geo_level",
        "city_class",
        "inc_class",
        "urb_rur",
        "pop_2015",
        "_pop_2015",
        "pop_2020",
        "_pop_2020",
        "status",
        "_status",
    ]
    df.drop(columns=["_pop_2015", "_pop_2020", "_status"], inplace=True)

    # Set psgc_code of NCR districts
    df.loc[df["name"] == "NCR, City of Manila, First District (Not a Province)", "psgc_code"] = 1303900000
    df.loc[df["name"] == "NCR, Second District (Not a Province)", "psgc_code"] = 1307400000
    df.loc[df["name"] == "NCR, Third District (Not a Province)", "psgc_code"] = 1307500000
    df.loc[df["name"] == "NCR, Fourth District (Not a Province)", "psgc_code"] = 1307600000

    df.dropna(subset=["psgc_code"], inplace=True)
    df["psgc_code"] = df["psgc_code"].astype(int)
    if df is None:
        return

    print("==== PSGC Table Read =====")
    print(df.head())

    print(df.shape)

    adm2_df = df[(df["geo_level"] == "Prov") | (df["geo_level"] == "Dist")].copy()
    adm2_df = adm2_df[["psgc_code", "name"]]
    adm2_df.columns = ["adm2_pcode", "adm2_en"]
    adm3_df = df[(df["geo_level"] == "Mun") | (df["geo_level"] == "City") | (df["geo_level"] == "SGU")].copy()
    adm3_df = adm3_df[["psgc_code", "name"]]
    adm3_df.columns = ["adm3_pcode", "adm3_en"]

    adm4_df = df[(df["geo_level"] == "Bgy") | (df["geo_level"] == "SubMun")].copy()
    adm4_df["adm3_pcode"] = adm4_df["psgc_code"].apply(lambda x: str(x).zfill(10)[:7] + "000").astype(int)
    adm4_df["adm2_pcode"] = adm4_df["psgc_code"].apply(lambda x: str(x).zfill(10)[:5] + "00000").astype(int)
    adm4_w3_df = adm4_df.merge(adm3_df, on="adm3_pcode", how="left")
    adm4_w32_df = adm4_w3_df.merge(adm2_df, on="adm2_pcode", how="left")
    # print(adm4_w32_df.sort_values(by="name").head())

    # process_psgc_2023_4q_country(df)
    # process_psgc_2023_4q_region(df)
    # process_psgc_2023_4q_provdists(df)
    # process_psgc_2023_4q_municities(df)
    process_psgc_2023_4q_bgysubmuns(adm4_w32_df)


def main():
    # ex.
    # $ python src/ph_psgc_shape/script.py data/psgc/PSGC-4Q-2023-Publication-Datafile.xlsx PSGC
    if len(sys.argv) != 3:
        print("Usage: python script.py <path_to_excel_file> <sheet_name>")
        return
    file_path = sys.argv[1]
    sheet_name = sys.argv[2]
    process_psgc_2023_4q(file_path, sheet_name)


if __name__ == "__main__":
    main()
