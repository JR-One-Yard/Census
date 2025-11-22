# Comprehensive Spatial Econometric Analysis
## Australian Census 2021 - Full Geographic Decomposition

---

## 📊 Analysis Overview

This repository contains a **comprehensive spatial econometric analysis** of the 2021 Australian Census data, implementing advanced spatial statistical methods across multiple geographic levels.

### What This Analysis Does

✅ **Spatial Lag Models** - Models accounting for spatial dependence in the data
✅ **Geographically Weighted Regression (GWR)** - Regression with spatially varying coefficients
✅ **Moran's I Statistics** - Global spatial autocorrelation for 6,000+ variables
✅ **LISA Statistics** - Local Indicators of Spatial Association (hot/cold spot detection)
✅ **Spatial Regimes Modeling** - Different model parameters for different spatial regimes
✅ **Multiple Spatial Weights** - Queen, Rook, K-NN, and distance-based weights matrices

---

## 📂 Repository Structure

```
Census/
├── spatial_econometric_analysis.py      # Main analysis script (comprehensive)
├── visualize_spatial_results.py         # Visualization and reporting
├── test_spatial_setup.py                # Environment verification
├── run_spatial_analysis.sh              # Convenience runner script
├── download_shapefiles.py               # Shapefile download utility
│
├── spatial_analysis_results/            # Analysis outputs (created by script)
│   ├── SA2/
│   │   ├── SA2_combined_data.csv       # Merged census data
│   │   ├── SA2_morans_i.csv            # Moran's I results
│   │   ├── SA2_lisa_results.pkl        # LISA statistics
│   │   ├── SA2_spatial_lag_models.pkl  # Spatial lag models
│   │   ├── SA2_gwr_models.pkl          # GWR results
│   │   ├── SA2_spatial_regimes.pkl     # Regime models
│   │   └── SA2_weights_*.pkl           # Spatial weights matrices
│   ├── SA3/
│   ├── SA4/
│   └── LGA/
│
├── spatial_visualizations/              # Visualizations (created by viz script)
│   ├── SA2/
│   │   ├── morans_i/
│   │   │   ├── morans_i_overview.png
│   │   │   ├── morans_i_by_weights.png
│   │   │   └── top_spatial_autocorrelation.csv
│   │   └── SA2_analysis_summary.txt
│   └── ...
│
├── spatial_analysis_log.txt             # Full analysis log
└── SHAPEFILE_DOWNLOAD_GUIDE.md          # Guide for manual shapefile download
```

---

## 🚀 Quick Start

### 1. Verify Environment Setup

```bash
python3 test_spatial_setup.py
```

Expected output:
```
✓ All packages imported successfully!
✓ Found 119 SA2 data files
✓ Created test geodataframe
✓ Created KNN spatial weights
✓ Calculated Moran's I
ALL TESTS PASSED!
```

### 2. Run Full Analysis

```bash
# Option A: Using the runner script
./run_spatial_analysis.sh

# Option B: Direct execution
python3 spatial_econometric_analysis.py
```

**WARNING:** This analysis is computationally intensive and may take **several hours** to complete!

### 3. Generate Visualizations and Reports

```bash
python3 visualize_spatial_results.py
```

---

## 📈 Analysis Components

### 1. Global Spatial Autocorrelation (Moran's I)

Calculates Moran's I for **all variables** to identify spatial clustering or dispersion.

**Interpretation:**
- **I > 0**: Positive spatial autocorrelation (similar values cluster together)
- **I < 0**: Negative spatial autocorrelation (dissimilar values cluster together)
- **I ≈ 0**: Random spatial pattern

**Output:** `{GEO}_morans_i.csv`

Columns:
- `variable`: Variable name
- `I`: Moran's I statistic
- `expected_I`: Expected value under spatial randomness
- `p_value`: Statistical significance
- `z_score`: Z-score
- `significant`: Boolean (p < 0.05)
- `weights_method`: Spatial weights method used
- `interpretation`: Text interpretation

### 2. Local Spatial Autocorrelation (LISA)

Identifies **hot spots, cold spots, and spatial outliers** for key socioeconomic variables.

**Cluster Types:**
- **Hot Spot (HH)**: High values surrounded by high values
- **Cold Spot (LL)**: Low values surrounded by low values
- **Spatial Outlier (LH)**: Low value surrounded by high values
- **Spatial Outlier (HL)**: High value surrounded by low values

**Output:** `{GEO}_lisa_results.pkl`

### 3. Spatial Lag Models

Estimates regression models that account for spatial dependence:

**Model:** `y = ρWy + Xβ + ε`

Where:
- `ρ` (rho): Spatial lag coefficient
- `Wy`: Spatially lagged dependent variable
- `X`: Independent variables
- `β`: Regression coefficients
- `ε`: Error term

**Output:** `{GEO}_spatial_lag_models.pkl`

### 4. Geographically Weighted Regression (GWR)

Estimates **spatially varying coefficients** - regression coefficients that change across space.

**Key Features:**
- Adaptive or fixed bandwidth
- Gaussian or bisquare kernel
- Local R² values for each location
- Bandwidth selection using AIC/CV/BIC

**Output:** `{GEO}_gwr_models.pkl`

Contains:
- `params`: Spatially varying coefficients for each location
- `local_R2`: Local R² values
- `t_values`: Local t-statistics
- `bandwidth`: Selected bandwidth

### 5. Spatial Regimes Modeling

Divides the study area into **spatial regimes** (clusters) and estimates separate models for each regime.

**Output:** `{GEO}_spatial_regimes.pkl`

---

## 🔧 Configuration

Edit `spatial_econometric_analysis.py` to customize:

```python
class Config:
    # Geographic levels to analyze
    GEO_LEVELS = ['SA2', 'SA3', 'SA4', 'LGA']  # Add/remove as needed

    # Spatial weights methods
    SPATIAL_WEIGHTS_METHODS = ['queen', 'rook', 'knn_5', 'knn_10', 'distance']

    # Minimum observations for analysis
    MIN_OBSERVATIONS = 30

    # GWR settings
    GWR_BANDWIDTH_METHODS = ['AIC', 'CV', 'BIC']
    GWR_KERNEL = 'gaussian'  # or 'bisquare'
```

---

## 📊 Dataset Information

### Census Data

- **Source:** Australian Bureau of Statistics (ABS)
- **Dataset:** 2021 Census General Community Profile (GCP) DataPack R2
- **Tables:** 119 tables (G01-G62) per geographic level
- **Variables:** 6,000+ socioeconomic variables per geography

### Geographic Levels Analyzed

| Level | Description | # Areas | Granularity |
|-------|-------------|---------|-------------|
| **SA2** | Statistical Area Level 2 | ~2,500 | Medium |
| **SA3** | Statistical Area Level 3 | ~358 | Regional |
| **SA4** | Statistical Area Level 4 | ~107 | Large regions |
| **LGA** | Local Government Areas | ~565 | Council areas |

**Note:** SA1 (~61,844 areas) is excluded by default due to computational intensity.

### Key Variables Analyzed

**Demographics:**
- Population counts, age distribution, sex ratios
- Indigenous status

**Education:**
- Highest year of school completed
- Non-school qualifications (Certificate, Diploma, Bachelor, Postgraduate)

**Income:**
- Personal income (weekly)
- Family income (weekly)
- Household income (weekly)

**Employment:**
- Labor force status
- Occupation categories
- Industry of employment

**Housing:**
- Dwelling types
- Tenure (owned, rented, etc.)
- Mortgage/rent costs

---

## 🛠️ Technical Requirements

### Python Packages

```bash
pip install geopandas libpysal esda spreg mgwr \
            mapclassify pyproj shapely rtree \
            scipy numpy pandas matplotlib seaborn tqdm
```

### System Requirements

- **RAM:** Minimum 8GB (16GB+ recommended for full analysis)
- **Storage:** ~5GB for results
- **CPU:** Multi-core recommended (analysis uses all available cores)
- **Time:** 2-6 hours depending on hardware

---

## 📖 Reading the Results

### Moran's I Results

```python
import pandas as pd

# Load Moran's I results
morans = pd.read_csv('spatial_analysis_results/SA2/SA2_morans_i.csv')

# Filter for significant results
significant = morans[morans['significant'] == True]

# Top variables with spatial clustering
top_clustering = morans.nlargest(20, 'I')
print(top_clustering[['variable', 'I', 'p_value']])
```

### LISA Results

```python
import pickle

# Load LISA results
with open('spatial_analysis_results/SA2/SA2_lisa_results.pkl', 'rb') as f:
    lisa = pickle.load(f)

# Example: Income variable
for key, result in lisa.items():
    if 'income' in key.lower():
        hot_spots = (result['spots'] == 'Hot Spot (HH)').sum()
        cold_spots = (result['spots'] == 'Cold Spot (LL)').sum()
        print(f"{key}: {hot_spots} hot spots, {cold_spots} cold spots")
```

### GWR Results

```python
import pickle
import numpy as np

# Load GWR results
with open('spatial_analysis_results/SA2/SA2_gwr_models.pkl', 'rb') as f:
    gwr = pickle.load(f)

# First model
model = gwr[0]
print(f"Model: {model['y_variable']} ~ {' + '.join(model['x_variables'])}")
print(f"Bandwidth: {model['bandwidth']:.2f}")
print(f"Mean local R²: {np.mean(model['local_R2']):.4f}")
print(f"R² range: [{np.min(model['local_R2']):.4f}, {np.max(model['local_R2']):.4f}]")
```

---

## 📚 References

### Spatial Econometrics

- Anselin, L. (1988). *Spatial Econometrics: Methods and Models*. Kluwer Academic Publishers.
- LeSage, J., & Pace, R. K. (2009). *Introduction to Spatial Econometrics*. CRC Press.
- Fotheringham, A. S., Brunsdon, C., & Charlton, M. (2002). *Geographically Weighted Regression*. Wiley.

### Python Libraries

- **PySAL**: Rey, S. J., & Anselin, L. (2007). PySAL: A Python library of spatial analytical methods.
- **GeoPandas**: Jordahl, K., et al. (2020). GeoPandas: Python tools for geographic data.
- **MGWR**: Oshan, T., et al. (2019). Mgwr: A Python implementation of multiscale geographically weighted regression.

### Data Source

- Australian Bureau of Statistics (2022). *2021 Census of Population and Housing*.
  Retrieved from: https://www.abs.gov.au/census

---

## ⚠️ Important Notes

### Data Confidentiality

- The ABS applies **small random adjustments** to all cell values to protect confidentiality
- Row/column totals may differ slightly from sum of components
- Results should be interpreted with this in mind

### Computational Intensity

**GWR is extremely computationally intensive:**
- Fits a separate regression for EVERY location
- For 2,472 SA2 areas with 10 variables, this requires ~25,000 regression estimations
- Memory usage can exceed 8GB
- Consider analyzing a subset of variables if resources are limited

### Spatial Weights Without Shapefiles

When shapefiles are not available, the analysis uses:
- **K-nearest neighbors** based on geographic codes
- **Distance-based** weights using estimated distances
- Results are still valid but cannot produce choropleth maps

To get shapefiles: See `SHAPEFILE_DOWNLOAD_GUIDE.md`

---

## 🤝 Contributing

This analysis framework can be extended to:
- Add more geographic levels (SA1, POA, CED, etc.)
- Include additional spatial econometric methods
- Create interactive visualizations
- Perform temporal analysis (comparing with previous Census years)
- Export results to GIS formats (shapefile, GeoJSON, KML)

---

## 📧 Contact & Support

For questions about:
- **This analysis:** Check the code comments and documentation
- **Census data:** ABS Client Services - client.services@abs.gov.au or 1300 135 070
- **Spatial methods:** Refer to PySAL documentation: https://pysal.org/

---

## 📄 License

- **Census Data:** Creative Commons (see ABS licensing documentation)
- **Analysis Code:** MIT License

---

**Last Updated:** 2025-11-22
**Analysis Version:** 1.0
**Census Year:** 2021
