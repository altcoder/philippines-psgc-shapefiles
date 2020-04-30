# Philippines PSGC Administrative Boundaries Shapefiles

Philippine PSGC administrative boundaries shapefiles.

This repository contains Philippines PSGC vector maps (shapefiles) sourced from
public datasets available online.

## Methodology

[QGIS](https://qgis.org) was used to update the maps to reflect the most recent
changes in the [PSGC Summary of
Changes](https://psa.gov.ph/classification/psgc/downloads/PSGC%20Summary%20of%20Changes%20Dec%202019.xlsx).

The most notebale change from the 2015 source files were:
- Removing the abolished NIR Region (moving all affected locations back to region 6 and 7)
- Renaming of ARMM to BARRM
- Various province/municipality/barangay naming changes

We now have the following administrative level shapefiles updated to date:
**Region** - Dec 2019
**Province** - Dec 2019
**Municipalities** - Dec 2019
**Barangays** - Dec 2017 

The barangay level cannot be updated because it requires new geometries
that is not yet available from public datasets.

Additional attributes were added to the dataset including centroid, area and perimeter.

## Source Files

Maps are using the WGS 1984, Lat/Long projection.

The 2015 Level 0 to 3 shapefiles came from [OCHA Services
Website](https://data.humdata.org/dataset/philippines-administrative-levels-0-to-3).

The 2015 Level 4 shapefiles came from [this Github Repo](https://github.com/justinelliotmeyers/official_philippines_shapefile_data_2016)

The 2011 Level 0 to 4 shapefiles came from [GADM Website Data](https://gadm.org)

Please refer to the [PSGC Summary of Changes](https://psa.gov.ph/classification/psgc/downloads/PSGC%20Summary%20of%20Changes%20Dec%202019.xlsx)
to take into account potential issues that may arise when using these maps together with your datasets. 

Here are some important considerations when using these maps.
- The presence of NIR Region -- was recently abolished
- Renaming of ARMM to BARRM
- Various location naming changes

## Contributing

Contributions are always welcome, no matter how large or small. Before contributing,
please read the [code of conduct](./.github/CODE_OF_CONDUCT.md).

Appreciate if someone can source a  more updated version of the maps based on the latest PSGC changes.




