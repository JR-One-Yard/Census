#!/usr/bin/env python3
"""
Spatial Regression Models for Rental Stress Prediction
========================================================
Advanced spatial modeling to predict:
1. Future rental stress hotspots
2. Areas at risk of displacement
3. Optimal social housing investment locations
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Configuration
INPUT_FILE = Path("rental_stress_outputs/rental_stress_analysis_full.csv")
OUTPUT_DIR = Path("rental_stress_outputs/spatial_models")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

print("=" * 80)
print("SPATIAL REGRESSION MODELS FOR RENTAL STRESS PREDICTION")
print("=" * 80)
print()

# ============================================================================
# STEP 1: Load Processed Data
# ============================================================================
print("STEP 1: Loading processed rental stress data...")
print("-" * 80)

df = pd.read_csv(INPUT_FILE)
print(f"✓ Loaded {len(df):,} SA1 areas")
print()

# ============================================================================
# STEP 2: Prepare Features for Modeling
# ============================================================================
print("STEP 2: Preparing features for spatial regression...")
print("-" * 80)

# Select features for prediction
feature_columns = [
    'Median_tot_hhd_inc_weekly',
    'Median_tot_prsnl_inc_weekly',
    'Median_age_persons',
    'Average_household_size',
    'low_income_pct',
    'low_income_households',
    'total_households',
    'public_housing_dwellings',
    'total_rental_dwellings',
    'total_dwellings',
    'public_housing_rate',
    'unemployment_rate',
    'labour_force_participation'
]

# Target variables
target_rent_stress = 'rental_stress_score'
target_displacement = 'displacement_risk_score'
target_investment = 'investment_priority_score'

# Clean data - remove rows with missing values in key columns
df_clean = df[feature_columns + [target_rent_stress, target_displacement, target_investment]].copy()
df_clean = df_clean.replace([np.inf, -np.inf], np.nan)
df_clean = df_clean.dropna()

print(f"✓ Features selected: {len(feature_columns)}")
print(f"✓ Clean dataset: {len(df_clean):,} SA1 areas (after removing missing values)")
print()

# ============================================================================
# STEP 3: Build Rental Stress Prediction Model
# ============================================================================
print("STEP 3: Building Rental Stress prediction models...")
print("-" * 80)

X = df_clean[feature_columns]
y_stress = df_clean[target_rent_stress]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y_stress, test_size=0.2, random_state=42)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"Training set: {len(X_train):,} samples")
print(f"Test set: {len(X_test):,} samples")
print()

# Train multiple models
models_stress = {}

print("Training models...")
print()

# 1. Linear Regression
print("  → Linear Regression...")
lr_stress = LinearRegression()
lr_stress.fit(X_train_scaled, y_train)
y_pred_lr = lr_stress.predict(X_test_scaled)
models_stress['Linear Regression'] = {
    'model': lr_stress,
    'predictions': y_pred_lr,
    'r2': r2_score(y_test, y_pred_lr),
    'rmse': np.sqrt(mean_squared_error(y_test, y_pred_lr)),
    'mae': mean_absolute_error(y_test, y_pred_lr)
}
print(f"     R² = {models_stress['Linear Regression']['r2']:.4f}")

# 2. Ridge Regression
print("  → Ridge Regression...")
ridge_stress = Ridge(alpha=1.0)
ridge_stress.fit(X_train_scaled, y_train)
y_pred_ridge = ridge_stress.predict(X_test_scaled)
models_stress['Ridge Regression'] = {
    'model': ridge_stress,
    'predictions': y_pred_ridge,
    'r2': r2_score(y_test, y_pred_ridge),
    'rmse': np.sqrt(mean_squared_error(y_test, y_pred_ridge)),
    'mae': mean_absolute_error(y_test, y_pred_ridge)
}
print(f"     R² = {models_stress['Ridge Regression']['r2']:.4f}")

# 3. Lasso Regression
print("  → Lasso Regression...")
lasso_stress = Lasso(alpha=0.1)
lasso_stress.fit(X_train_scaled, y_train)
y_pred_lasso = lasso_stress.predict(X_test_scaled)
models_stress['Lasso Regression'] = {
    'model': lasso_stress,
    'predictions': y_pred_lasso,
    'r2': r2_score(y_test, y_pred_lasso),
    'rmse': np.sqrt(mean_squared_error(y_test, y_pred_lasso)),
    'mae': mean_absolute_error(y_test, y_pred_lasso)
}
print(f"     R² = {models_stress['Lasso Regression']['r2']:.4f}")

# 4. Random Forest
print("  → Random Forest Regressor...")
rf_stress = RandomForestRegressor(n_estimators=100, max_depth=20, random_state=42, n_jobs=-1)
rf_stress.fit(X_train, y_train)
y_pred_rf = rf_stress.predict(X_test)
models_stress['Random Forest'] = {
    'model': rf_stress,
    'predictions': y_pred_rf,
    'r2': r2_score(y_test, y_pred_rf),
    'rmse': np.sqrt(mean_squared_error(y_test, y_pred_rf)),
    'mae': mean_absolute_error(y_test, y_pred_rf)
}
print(f"     R² = {models_stress['Random Forest']['r2']:.4f}")

# 5. Gradient Boosting
print("  → Gradient Boosting Regressor...")
gb_stress = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
gb_stress.fit(X_train, y_train)
y_pred_gb = gb_stress.predict(X_test)
models_stress['Gradient Boosting'] = {
    'model': gb_stress,
    'predictions': y_pred_gb,
    'r2': r2_score(y_test, y_pred_gb),
    'rmse': np.sqrt(mean_squared_error(y_test, y_pred_gb)),
    'mae': mean_absolute_error(y_test, y_pred_gb)
}
print(f"     R² = {models_stress['Gradient Boosting']['r2']:.4f}")

print()

# Find best model
best_model_name = max(models_stress, key=lambda k: models_stress[k]['r2'])
print(f"✓ Best model for Rental Stress: {best_model_name}")
print(f"  R² Score: {models_stress[best_model_name]['r2']:.4f}")
print(f"  RMSE: {models_stress[best_model_name]['rmse']:.4f}")
print(f"  MAE: {models_stress[best_model_name]['mae']:.4f}")
print()

# ============================================================================
# STEP 4: Build Displacement Risk Prediction Model
# ============================================================================
print("STEP 4: Building Displacement Risk prediction models...")
print("-" * 80)

y_displacement = df_clean[target_displacement]
X_train, X_test, y_train, y_test = train_test_split(X, y_displacement, test_size=0.2, random_state=42)
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

models_displacement = {}

print("Training models...")
print()

# Random Forest (usually best for this type of data)
print("  → Random Forest Regressor...")
rf_displacement = RandomForestRegressor(n_estimators=100, max_depth=20, random_state=42, n_jobs=-1)
rf_displacement.fit(X_train, y_train)
y_pred_rf = rf_displacement.predict(X_test)
models_displacement['Random Forest'] = {
    'model': rf_displacement,
    'predictions': y_pred_rf,
    'r2': r2_score(y_test, y_pred_rf),
    'rmse': np.sqrt(mean_squared_error(y_test, y_pred_rf)),
    'mae': mean_absolute_error(y_test, y_pred_rf)
}
print(f"     R² = {models_displacement['Random Forest']['r2']:.4f}")

# Gradient Boosting
print("  → Gradient Boosting Regressor...")
gb_displacement = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
gb_displacement.fit(X_train, y_train)
y_pred_gb = gb_displacement.predict(X_test)
models_displacement['Gradient Boosting'] = {
    'model': gb_displacement,
    'predictions': y_pred_gb,
    'r2': r2_score(y_test, y_pred_gb),
    'rmse': np.sqrt(mean_squared_error(y_test, y_pred_gb)),
    'mae': mean_absolute_error(y_test, y_pred_gb)
}
print(f"     R² = {models_displacement['Gradient Boosting']['r2']:.4f}")

print()

best_displacement_model = max(models_displacement, key=lambda k: models_displacement[k]['r2'])
print(f"✓ Best model for Displacement Risk: {best_displacement_model}")
print(f"  R² Score: {models_displacement[best_displacement_model]['r2']:.4f}")
print(f"  RMSE: {models_displacement[best_displacement_model]['rmse']:.4f}")
print(f"  MAE: {models_displacement[best_displacement_model]['mae']:.4f}")
print()

# ============================================================================
# STEP 5: Build Investment Priority Prediction Model
# ============================================================================
print("STEP 5: Building Investment Priority prediction models...")
print("-" * 80)

y_investment = df_clean[target_investment]
X_train, X_test, y_train, y_test = train_test_split(X, y_investment, test_size=0.2, random_state=42)

models_investment = {}

print("Training models...")
print()

# Random Forest
print("  → Random Forest Regressor...")
rf_investment = RandomForestRegressor(n_estimators=100, max_depth=20, random_state=42, n_jobs=-1)
rf_investment.fit(X_train, y_train)
y_pred_rf = rf_investment.predict(X_test)
models_investment['Random Forest'] = {
    'model': rf_investment,
    'predictions': y_pred_rf,
    'r2': r2_score(y_test, y_pred_rf),
    'rmse': np.sqrt(mean_squared_error(y_test, y_pred_rf)),
    'mae': mean_absolute_error(y_test, y_pred_rf)
}
print(f"     R² = {models_investment['Random Forest']['r2']:.4f}")

# Gradient Boosting
print("  → Gradient Boosting Regressor...")
gb_investment = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
gb_investment.fit(X_train, y_train)
y_pred_gb = gb_investment.predict(X_test)
models_investment['Gradient Boosting'] = {
    'model': gb_investment,
    'predictions': y_pred_gb,
    'r2': r2_score(y_test, y_pred_gb),
    'rmse': np.sqrt(mean_squared_error(y_test, y_pred_gb)),
    'mae': mean_absolute_error(y_test, y_pred_gb)
}
print(f"     R² = {models_investment['Gradient Boosting']['r2']:.4f}")

print()

best_investment_model = max(models_investment, key=lambda k: models_investment[k]['r2'])
print(f"✓ Best model for Investment Priority: {best_investment_model}")
print(f"  R² Score: {models_investment[best_investment_model]['r2']:.4f}")
print(f"  RMSE: {models_investment[best_investment_model]['rmse']:.4f}")
print(f"  MAE: {models_investment[best_investment_model]['mae']:.4f}")
print()

# ============================================================================
# STEP 6: Feature Importance Analysis
# ============================================================================
print("STEP 6: Analyzing feature importance...")
print("-" * 80)

# Get feature importance from best Random Forest models
rf_stress_model = models_stress['Random Forest']['model']
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': rf_stress_model.feature_importances_
}).sort_values('importance', ascending=False)

print("Top 10 Features for Rental Stress Prediction:")
print(feature_importance.head(10).to_string(index=False))
print()

# Save feature importance
feature_importance.to_csv(OUTPUT_DIR / "feature_importance_rental_stress.csv", index=False)

# ============================================================================
# STEP 7: Generate Predictions for All SA1 Areas
# ============================================================================
print("STEP 7: Generating predictions for all SA1 areas...")
print("-" * 80)

# Prepare full dataset for prediction
df_predict = df[feature_columns].copy()
df_predict = df_predict.replace([np.inf, -np.inf], np.nan).fillna(0)

# Generate predictions using best models
print("  → Predicting rental stress scores...")
df['predicted_rental_stress'] = models_stress[best_model_name]['model'].predict(
    scaler.fit_transform(df_predict) if 'Regression' in best_model_name else df_predict
)

print("  → Predicting displacement risk scores...")
df['predicted_displacement_risk'] = models_displacement[best_displacement_model]['model'].predict(df_predict)

print("  → Predicting investment priority scores...")
df['predicted_investment_priority'] = models_investment[best_investment_model]['model'].predict(df_predict)

print()

# ============================================================================
# STEP 8: Identify Future Hotspots
# ============================================================================
print("STEP 8: Identifying future rental stress hotspots...")
print("-" * 80)

# Flag emerging hotspots (areas with low current stress but high predicted stress)
df['emerging_stress_hotspot'] = (
    (df['rental_stress_score'] < 50) &
    (df['predicted_rental_stress'] >= 60)
).astype(int)

df['emerging_displacement_risk'] = (
    (df['displacement_risk_score'] < 50) &
    (df['predicted_displacement_risk'] >= 60)
).astype(int)

print(f"✓ Emerging stress hotspots identified: {df['emerging_stress_hotspot'].sum():,}")
print(f"✓ Emerging displacement risk areas: {df['emerging_displacement_risk'].sum():,}")
print()

# ============================================================================
# STEP 9: Export Results
# ============================================================================
print("STEP 9: Exporting model results...")
print("-" * 80)

# Export full predictions
predictions_file = OUTPUT_DIR / "spatial_predictions_all_sa1.csv"
df.to_csv(predictions_file, index=False)
print(f"✓ Full predictions exported: {predictions_file}")

# Export emerging hotspots
emerging_hotspots = df[df['emerging_stress_hotspot'] == 1].nlargest(500, 'predicted_rental_stress')
hotspots_file = OUTPUT_DIR / "emerging_rental_stress_hotspots.csv"
emerging_hotspots.to_csv(hotspots_file, index=False)
print(f"✓ Emerging hotspots (top 500): {hotspots_file}")

# Export emerging displacement risks
emerging_displacement = df[df['emerging_displacement_risk'] == 1].nlargest(500, 'predicted_displacement_risk')
displacement_file = OUTPUT_DIR / "emerging_displacement_risk_areas.csv"
emerging_displacement.to_csv(displacement_file, index=False)
print(f"✓ Emerging displacement risks (top 500): {displacement_file}")

# ============================================================================
# STEP 10: Generate Model Performance Report
# ============================================================================
print()
print("=" * 80)
print("MODEL PERFORMANCE SUMMARY")
print("=" * 80)
print()

print("RENTAL STRESS PREDICTION MODELS")
print("-" * 40)
for model_name, metrics in sorted(models_stress.items(), key=lambda x: x[1]['r2'], reverse=True):
    print(f"{model_name:25s} | R² = {metrics['r2']:.4f} | RMSE = {metrics['rmse']:.4f} | MAE = {metrics['mae']:.4f}")
print()

print("DISPLACEMENT RISK PREDICTION MODELS")
print("-" * 40)
for model_name, metrics in sorted(models_displacement.items(), key=lambda x: x[1]['r2'], reverse=True):
    print(f"{model_name:25s} | R² = {metrics['r2']:.4f} | RMSE = {metrics['rmse']:.4f} | MAE = {metrics['mae']:.4f}")
print()

print("INVESTMENT PRIORITY PREDICTION MODELS")
print("-" * 40)
for model_name, metrics in sorted(models_investment.items(), key=lambda x: x[1]['r2'], reverse=True):
    print(f"{model_name:25s} | R² = {metrics['r2']:.4f} | RMSE = {metrics['rmse']:.4f} | MAE = {metrics['mae']:.4f}")
print()

print("=" * 80)
print("SPATIAL MODELING COMPLETE!")
print("=" * 80)
print()
print(f"All model outputs saved to: {OUTPUT_DIR}/")
print()
print("Key insights:")
print(f"1. {df['emerging_stress_hotspot'].sum():,} emerging rental stress hotspots identified")
print(f"2. {df['emerging_displacement_risk'].sum():,} areas at risk of future displacement")
print(f"3. Best model performance: R² = {models_stress[best_model_name]['r2']:.4f} for rental stress prediction")
print()
