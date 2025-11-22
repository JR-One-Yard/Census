#!/usr/bin/env python3
"""
Phase 7: Generate MASSIVE Synthetic Australian Population
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("🧬 PHASE 7: SYNTHETIC POPULATION GENERATION")
print("Generating 1,000,000 synthetic Australians")
print("="*100)

OUTPUT_DIR = Path("/home/user/Census/dna_sequencer_results")
master_profile = pd.read_csv(OUTPUT_DIR / 'master_demographic_profile.csv')

np.random.seed(42)

def generate_synthetic_population(n_people=1_000_000):
    """Generate realistic synthetic Australians"""

    print(f"\n🧬 Generating {n_people:,} synthetic people...")

    # Age distribution (roughly matching Australian census)
    ages = np.random.normal(38, 23, n_people).astype(int)
    ages = np.clip(ages, 0, 100)

    # Sex (slightly more females)
    sexes = np.random.choice(['M', 'F'], n_people, p=[0.495, 0.505])

    # Income - log-normal distribution
    # Median Australian income ~$1,300/week
    incomes = np.random.lognormal(7.2, 0.8, n_people)
    incomes = np.clip(incomes, 0, 10000).astype(int)

    # Education levels
    education_levels = [
        'No qualification',
        'Year 12',
        'Certificate III/IV',
        'Diploma',
        'Bachelor',
        'Postgraduate'
    ]
    # Probabilities roughly matching census
    education_probs = [0.25, 0.20, 0.20, 0.10, 0.15, 0.10]
    educations = np.random.choice(education_levels, n_people, p=education_probs)

    # Occupation categories
    occupations = [
        'Manager',
        'Professional',
        'Technician',
        'Community/Personal Service',
        'Clerical/Administrative',
        'Sales',
        'Machinery Operator',
        'Labourer',
        'Not in labour force'
    ]
    occ_probs = [0.12, 0.22, 0.14, 0.10, 0.14, 0.09, 0.06, 0.09, 0.04]
    occupations_assigned = np.random.choice(occupations, n_people, p=occ_probs)

    # Assign to suburbs based on population
    suburb_populations = master_profile['Tot_P_P'].values if 'Tot_P_P' in master_profile.columns else np.ones(len(master_profile))
    suburb_populations = np.maximum(suburb_populations, 1)
    suburb_probs = suburb_populations / suburb_populations.sum()

    assigned_suburbs = np.random.choice(
        master_profile['SAL_CODE_2021'].values,
        n_people,
        p=suburb_probs
    )

    # Create dataframe
    synthetic_pop = pd.DataFrame({
        'person_id': range(n_people),
        'age': ages,
        'sex': sexes,
        'weekly_income': incomes,
        'education': educations,
        'occupation': occupations_assigned,
        'suburb_code': assigned_suburbs
    })

    return synthetic_pop

# Generate population
print(f"\nStart: {datetime.now().strftime('%H:%M:%S')}")
synthetic_pop = generate_synthetic_population(n_people=1_000_000)
print(f"End: {datetime.now().strftime('%H:%M:%S')}")

print(f"\n✓ Generated {len(synthetic_pop):,} synthetic people")

# Statistics
print("\n" + "="*80)
print("📊 SYNTHETIC POPULATION STATISTICS")
print("="*80)

print(f"\n👥 Demographics:")
print(f"  Age range: {synthetic_pop['age'].min()} - {synthetic_pop['age'].max()}")
print(f"  Mean age: {synthetic_pop['age'].mean():.1f} years")
print(f"  Median age: {synthetic_pop['age'].median():.0f} years")

print(f"\n💰 Income:")
print(f"  Mean income: ${synthetic_pop['weekly_income'].mean():.0f}/week")
print(f"  Median income: ${synthetic_pop['weekly_income'].median():.0f}/week")
print(f"  Top 10%: ${synthetic_pop['weekly_income'].quantile(0.9):.0f}/week")
print(f"  Top 1%: ${synthetic_pop['weekly_income'].quantile(0.99):.0f}/week")

print(f"\n🎓 Education distribution:")
for edu, count in synthetic_pop['education'].value_counts().sort_index().items():
    pct = count / len(synthetic_pop) * 100
    print(f"  {edu:25} {count:7,} ({pct:5.2f}%)")

print(f"\n💼 Occupation distribution:")
for occ, count in synthetic_pop['occupation'].value_counts().items():
    pct = count / len(synthetic_pop) * 100
    print(f"  {occ:30} {count:7,} ({pct:5.2f}%)")

# Save sample
print(f"\n💾 Saving data...")
sample_size = 100_000
synthetic_pop.head(sample_size).to_csv(
    OUTPUT_DIR / f'synthetic_population_sample_{sample_size}.csv',
    index=False
)
print(f"✓ Saved sample of {sample_size:,} people")

# Aggregate by suburb
print(f"\n🏘️ Aggregating by suburb...")
suburb_stats = synthetic_pop.groupby('suburb_code').agg({
    'person_id': 'count',
    'age': 'mean',
    'weekly_income': 'median',
    'education': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown'
}).reset_index()

suburb_stats.columns = [
    'SAL_CODE_2021',
    'synthetic_population',
    'avg_age_synthetic',
    'median_income_synthetic',
    'mode_education_synthetic'
]

suburb_stats.to_csv(OUTPUT_DIR / 'synthetic_suburb_aggregates.csv', index=False)
print(f"✓ Saved aggregates for {len(suburb_stats):,} suburbs")

# Find interesting synthetic people
print(f"\n🦄 Finding Interesting Synthetic People (Demographic Unicorns)...")

# High earners aged 20-30
young_high_earners = synthetic_pop[
    (synthetic_pop['age'] >= 20) &
    (synthetic_pop['age'] <= 30) &
    (synthetic_pop['weekly_income'] > 3000)
]
print(f"  Young high earners (20-30, >$3k/wk): {len(young_high_earners):,}")

# Retirees still working
working_retirees = synthetic_pop[
    (synthetic_pop['age'] >= 70) &
    (synthetic_pop['weekly_income'] > 500)
]
print(f"  Working retirees (70+, >$500/wk): {len(working_retirees):,}")

# Postgrads under 25
young_postgrads = synthetic_pop[
    (synthetic_pop['age'] < 25) &
    (synthetic_pop['education'] == 'Postgraduate')
]
print(f"  Young postgrads (<25): {len(young_postgrads):,}")

# Save unicorns
unicorns = pd.concat([
    young_high_earners.head(100),
    working_retirees.head(100),
    young_postgrads.head(100)
])
unicorns.to_csv(OUTPUT_DIR / 'synthetic_demographic_unicorns.csv', index=False)
print(f"✓ Saved {len(unicorns):,} demographic unicorns")

print("\n" + "="*100)
print("✓ PHASE 7 COMPLETE!")
print("="*100)
