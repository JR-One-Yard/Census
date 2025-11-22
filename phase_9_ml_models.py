#!/usr/bin/env python3
"""
Phase 9: Machine Learning Models
Train models to predict demographics and classify suburbs
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import classification_report, mean_absolute_error, r2_score
import json

print("="*100)
print("🤖 PHASE 9: MACHINE LEARNING MODELS")
print("="*100)

OUTPUT_DIR = Path("/home/user/Census/dna_sequencer_results")

# Load data
master_profile = pd.read_csv(OUTPUT_DIR / 'master_demographic_profile.csv')
clustering = pd.read_csv(OUTPUT_DIR / 'clustering_results.csv')

master_with_clusters = master_profile.merge(
    clustering[['SAL_CODE_2021', 'KMeans_10']],
    on='SAL_CODE_2021'
)

feature_cols = [c for c in master_profile.columns
                if c not in ['SAL_CODE_2021', 'Suburb_Name', 'Median_age_persons', 'Median_tot_prsnl_inc_weekly']]

X = master_with_clusters[feature_cols].fillna(0).values

# ============================================================================
# MODEL 1: Predict Suburb Cluster (Classification)
# ============================================================================
print("\n📊 MODEL 1: Suburb Cluster Classification")
print("Predicting which demographic cluster a suburb belongs to")
print("="*80)

y_cluster = master_with_clusters['KMeans_10'].values

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y_cluster, test_size=0.2, random_state=42
)

# Train Random Forest
print("\nTraining Random Forest Classifier...")
rf_classifier = RandomForestClassifier(
    n_estimators=100,
    max_depth=20,
    random_state=42,
    n_jobs=-1
)
rf_classifier.fit(X_train, y_train)

# Evaluate
train_score = rf_classifier.score(X_train, y_train)
test_score = rf_classifier.score(X_test, y_test)

print(f"✓ Training accuracy: {train_score:.3f}")
print(f"✓ Testing accuracy: {test_score:.3f}")

# Feature importance
feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': rf_classifier.feature_importances_
}).sort_values('importance', ascending=False)

print("\n🔍 Top 10 Most Important Features for Cluster Prediction:")
for i, row in feature_importance.head(10).iterrows():
    print(f"  {row['feature']:40} {row['importance']:.4f}")

# Save model results
model_results = {
    'cluster_classification': {
        'model': 'RandomForestClassifier',
        'train_accuracy': float(train_score),
        'test_accuracy': float(test_score),
        'top_features': feature_importance.head(20).to_dict('records')
    }
}

# ============================================================================
# MODEL 2: Predict Median Age (Regression)
# ============================================================================
print("\n" + "="*80)
print("📊 MODEL 2: Median Age Prediction")
print("="*80)

if 'Median_age_persons' in master_with_clusters.columns:
    y_age = master_with_clusters['Median_age_persons'].fillna(master_with_clusters['Median_age_persons'].median()).values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_age, test_size=0.2, random_state=42
    )

    print("\nTraining Gradient Boosting Regressor...")
    gb_age = GradientBoostingRegressor(
        n_estimators=100,
        max_depth=5,
        random_state=42
    )
    gb_age.fit(X_train, y_train)

    # Predict
    y_pred_train = gb_age.predict(X_train)
    y_pred_test = gb_age.predict(X_test)

    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    test_r2 = r2_score(y_test, y_pred_test)

    print(f"✓ Training MAE: {train_mae:.2f} years")
    print(f"✓ Testing MAE: {test_mae:.2f} years")
    print(f"✓ Testing R²: {test_r2:.3f}")

    model_results['age_prediction'] = {
        'model': 'GradientBoostingRegressor',
        'train_mae': float(train_mae),
        'test_mae': float(test_mae),
        'test_r2': float(test_r2)
    }

# ============================================================================
# MODEL 3: Predict Median Income (Regression)
# ============================================================================
print("\n" + "="*80)
print("📊 MODEL 3: Median Income Prediction")
print("="*80)

if 'Median_tot_prsnl_inc_weekly' in master_with_clusters.columns:
    y_income = master_with_clusters['Median_tot_prsnl_inc_weekly'].fillna(
        master_with_clusters['Median_tot_prsnl_inc_weekly'].median()
    ).values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_income, test_size=0.2, random_state=42
    )

    print("\nTraining Random Forest Regressor...")
    rf_income = RandomForestRegressor(
        n_estimators=100,
        max_depth=20,
        random_state=42,
        n_jobs=-1
    )
    rf_income.fit(X_train, y_train)

    # Predict
    y_pred_train = rf_income.predict(X_train)
    y_pred_test = rf_income.predict(X_test)

    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    test_r2 = r2_score(y_test, y_pred_test)

    print(f"✓ Training MAE: ${train_mae:.0f}/week")
    print(f"✓ Testing MAE: ${test_mae:.0f}/week")
    print(f"✓ Testing R²: {test_r2:.3f}")

    # Feature importance
    income_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': rf_income.feature_importances_
    }).sort_values('importance', ascending=False)

    print("\n🔍 Top 10 Features for Income Prediction:")
    for i, row in income_importance.head(10).iterrows():
        print(f"  {row['feature']:40} {row['importance']:.4f}")

    model_results['income_prediction'] = {
        'model': 'RandomForestRegressor',
        'train_mae': float(train_mae),
        'test_mae': float(test_mae),
        'test_r2': float(test_r2),
        'top_features': income_importance.head(20).to_dict('records')
    }

# ============================================================================
# Save Results
# ============================================================================
print("\n💾 Saving model results...")

with open(OUTPUT_DIR / 'ml_model_results.json', 'w') as f:
    json.dump(model_results, f, indent=2)

print("\n" + "="*100)
print("✓ PHASE 9 COMPLETE!")
print("="*100)

print(f"\n📊 Models Trained:")
print(f"  ✓ Cluster Classification (Accuracy: {model_results['cluster_classification']['test_accuracy']:.3f})")
if 'age_prediction' in model_results:
    print(f"  ✓ Age Prediction (MAE: {model_results['age_prediction']['test_mae']:.2f} years)")
if 'income_prediction' in model_results:
    print(f"  ✓ Income Prediction (MAE: ${model_results['income_prediction']['test_mae']:.0f}/week)")
