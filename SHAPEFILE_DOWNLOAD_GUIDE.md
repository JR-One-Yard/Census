# How to Download ASGS 2021 Shapefiles Manually

The automated download failed due to ABS website restrictions. Here's how to download them manually:

## Option 1: Download from ABS Website

1. Visit: https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files

2. Download the following files:
   - **SA1_2021_AUST_SHP_GDA2020.zip** (Statistical Area Level 1)
   - **SA2_2021_AUST_SHP_GDA2020.zip** (Statistical Area Level 2)
   - **SA3_2021_AUST_SHP_GDA2020.zip** (Statistical Area Level 3)
   - **SA4_2021_AUST_SHP_GDA2020.zip** (Statistical Area Level 4)
   - **LGA_2021_AUST_SHP_GDA2020.zip** (Local Government Areas)

3. Extract each zip file to the corresponding directory:
   ```
   /home/user/Census/shapefiles/SA1/
   /home/user/Census/shapefiles/SA2/
   /home/user/Census/shapefiles/SA3/
   /home/user/Census/shapefiles/SA4/
   /home/user/Census/shapefiles/LGA/
   ```

## Option 2: Run Analysis Without Shapefiles

The spatial analysis script can run without shapefiles using:
- **K-Nearest Neighbors** spatial weights (based on geographic code proximity)
- **Distance-based** spatial weights (estimated from area characteristics)
- **Graph-based** spatial relationships

This provides valid spatial econometric analysis, though without the ability to create map visualizations.

## Option 3: Use Alternative Data Sources

You can also obtain shapefiles from:
- **AURIN** (Australian Urban Research Infrastructure Network)
- **data.gov.au** (Australian Government Open Data Portal)
- **OpenStreetMap** derived boundaries

## After Downloading

Once you have the shapefiles in place, simply re-run:
```bash
python3 spatial_econometric_analysis.py
```

The script will automatically detect and use the shapefiles for enhanced spatial analysis.
