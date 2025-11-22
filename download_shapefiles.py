#!/usr/bin/env python3
"""
Download ASGS 2021 Shapefiles from ABS for Spatial Analysis
Downloads SA1, SA2, SA3, SA4, LGA shapefiles required for spatial econometrics
"""

import os
import urllib.request
import zipfile
import sys

# Create directory for shapefiles
SHAPEFILE_DIR = "/home/user/Census/shapefiles"
os.makedirs(SHAPEFILE_DIR, exist_ok=True)

# ABS ASGS 2021 shapefile URLs (Digital Boundaries)
# These are from the ABS website: https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files
SHAPEFILE_URLS = {
    'SA1': 'https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files/SA1_2021_AUST_SHP_GDA2020.zip',
    'SA2': 'https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files/SA2_2021_AUST_SHP_GDA2020.zip',
    'SA3': 'https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files/SA3_2021_AUST_SHP_GDA2020.zip',
    'SA4': 'https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files/SA4_2021_AUST_SHP_GDA2020.zip',
    'LGA': 'https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files/LGA_2021_AUST_SHP_GDA2020.zip',
}

def download_file(url, destination):
    """Download file with progress indicator"""
    try:
        print(f"Downloading from: {url}")
        print(f"Saving to: {destination}")

        def progress_callback(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(100, (downloaded / total_size) * 100)
            sys.stdout.write(f"\rProgress: {percent:.1f}% ({downloaded / 1024 / 1024:.1f} MB / {total_size / 1024 / 1024:.1f} MB)")
            sys.stdout.flush()

        urllib.request.urlretrieve(url, destination, progress_callback)
        print("\n✓ Download complete!")
        return True
    except Exception as e:
        print(f"\n✗ Error downloading: {e}")
        return False

def extract_zip(zip_path, extract_dir):
    """Extract zip file"""
    try:
        print(f"Extracting {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print(f"✓ Extracted to {extract_dir}")
        return True
    except Exception as e:
        print(f"✗ Error extracting: {e}")
        return False

def main():
    print("="*100)
    print("DOWNLOADING ASGS 2021 DIGITAL BOUNDARY FILES")
    print("="*100)

    for geo_level, url in SHAPEFILE_URLS.items():
        print(f"\n{'-'*100}")
        print(f"Processing {geo_level} shapefile...")
        print(f"{'-'*100}")

        # Create directory for this geography level
        geo_dir = os.path.join(SHAPEFILE_DIR, geo_level)
        os.makedirs(geo_dir, exist_ok=True)

        # Download zip file
        zip_filename = f"{geo_level}_2021_AUST_SHP_GDA2020.zip"
        zip_path = os.path.join(geo_dir, zip_filename)

        if os.path.exists(zip_path):
            print(f"✓ Zip file already exists: {zip_path}")
        else:
            if not download_file(url, zip_path):
                print(f"✗ Failed to download {geo_level}")
                continue

        # Extract zip file
        if not extract_zip(zip_path, geo_dir):
            print(f"✗ Failed to extract {geo_level}")
            continue

        # List extracted files
        shp_files = [f for f in os.listdir(geo_dir) if f.endswith('.shp')]
        if shp_files:
            print(f"✓ Shapefile(s) extracted: {', '.join(shp_files)}")
        else:
            print(f"⚠ Warning: No .shp files found in extracted archive")

    print("\n" + "="*100)
    print("DOWNLOAD COMPLETE!")
    print("="*100)
    print(f"\nShapefiles saved to: {SHAPEFILE_DIR}")

    # List all shapefiles
    print("\nAvailable shapefiles:")
    for geo_level in SHAPEFILE_URLS.keys():
        geo_dir = os.path.join(SHAPEFILE_DIR, geo_level)
        if os.path.exists(geo_dir):
            shp_files = [f for f in os.listdir(geo_dir) if f.endswith('.shp')]
            for shp in shp_files:
                print(f"  • {geo_level}: {os.path.join(geo_dir, shp)}")

if __name__ == "__main__":
    main()
