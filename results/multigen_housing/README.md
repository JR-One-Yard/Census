# Multi-Generation Housing Demand Analysis Results

**Analysis Date:** November 2025
**Data Source:** 2021 Australian Census

## Files in this Directory

### Primary Outputs

1. **top_100_multigen_demand.csv**
   - Top 100 SA2 areas ranked by overall multi-generation housing demand
   - Combines generational overlap, cultural propensity, and family size patterns
   - Use for: Identifying prime markets for multi-gen housing products

2. **top_100_supply_gaps.csv**
   - Top 100 areas with highest supply-demand gap
   - High demand but limited suitable housing stock
   - Use for: Finding development opportunities where market needs are unmet

3. **top_100_market_opportunities.csv**
   - Top 100 areas combining high demand with high home ownership
   - Indicates viable markets for granny flats and renovations
   - Use for: Prioritizing owner-builder and renovation markets

4. **high_cultural_concentration.csv**
   - Areas with >20% population from high multi-gen cultures
   - Includes Asian, Middle Eastern, and Southern European communities
   - Use for: Culturally-targeted housing products and marketing

5. **granny_flat_potential_areas.csv**
   - Areas with >60% separate houses and >60 demand score
   - Prime markets for granny flat development
   - Use for: Granny flat construction, subdivision, dual-occupancy

6. **complete_multigen_analysis.csv**
   - Full dataset with all metrics for 2,355 SA2 areas
   - All demographic, cultural, housing, and demand indicators
   - Use for: Custom analysis, GIS mapping, research

## Key Metrics Explained

**MultiGen_Demand_Score (0-100)**
- Composite score combining:
  - Generational overlap (35%)
  - Cultural multi-gen propensity (35%)
  - Large family indicators (30%)
- Higher scores = stronger multi-gen housing demand

**Supply_Gap_Score**
- Difference between demand and housing supply suitability
- Positive values = high demand but low suitable supply
- Best development opportunities

**Market_Opportunity_Score (0-100)**
- Combines demand (60%) with ownership rates (40%)
- Indicates viable markets with purchasing power
- Higher scores = better commercial opportunities

**Cultural_MultiGen_Score**
- Weighted score based on cultural community composition
- High multi-gen cultures weighted 2x (Asia, Middle East, S. Europe)
- Medium multi-gen cultures weighted 1x

**Generational_Overlap_Score**
- Geometric mean of key generational proportions
- Measures coexistence of children, parents, grandparents
- Higher scores = more multi-generational presence

## Quick Insights

### Top States for Multi-Gen Demand
1. **New South Wales** - 7 of top 10 demand areas (Western Sydney corridor)
2. **Victoria** - Strong in regional growth centers
3. **Queensland** - Emerging regional markets
4. **ACT** - High ownership + demand combination

### Prime Development Zones
- **Western Sydney** - Highest overall demand (cultural + demographic)
- **Southeast Melbourne** - Strong suburban granny flat markets
- **Regional QLD** - Large block, affordable multi-gen potential
- **ACT** - Premium market with high ownership

### Market Segments
1. **Granny Flat Markets** - 1,710 areas with >70% separate houses
2. **Apartment Innovation** - High-density supply gap areas
3. **Cultural Hubs** - Communities with >20% multi-gen cultures
4. **Regional Growth** - Affordable large-block markets

## Usage Examples

### Example 1: Find Best Granny Flat Markets
```
Filter: granny_flat_potential_areas.csv
Sort by: Market_Opportunity_Score (descending)
Look for: Pct_Owned > 80%, Pct_Separate_Houses > 90%
```

### Example 2: Identify Supply Gap Opportunities
```
Filter: top_100_supply_gaps.csv
Sort by: Supply_Gap_Score (descending)
Look for: Pct_Apartments > 40%, Cultural_MultiGen_Score > 25
Opportunity: Innovative high-density multi-gen solutions
```

### Example 3: Target Cultural Communities
```
Filter: high_cultural_concentration.csv
Sort by: Pct_High_MultiGen_Culture (descending)
Look for: SA2 areas with >25% cultural concentration
Marketing: Culturally-specific housing features and campaigns
```

## Data Dictionary

| Column | Description | Range |
|--------|-------------|-------|
| SA2_CODE | Statistical Area 2 code | String |
| SA2_Name | Area name (suburb/locality) | String |
| Total_Pop | Total population | Integer |
| Total_Dwellings | Total occupied dwellings | Integer |
| MultiGen_Demand_Score | Overall multi-gen demand | 0-100 |
| Generational_Overlap_Score | Multi-generation presence | Continuous |
| Cultural_MultiGen_Score | Cultural propensity weighted | Continuous |
| Large_Family_Indicator | % large families (3+ kids) | Percentage |
| Pct_High_MultiGen_Culture | % from high multi-gen cultures | Percentage |
| Pct_Young_Children | % population aged 0-14 | Percentage |
| Pct_Parents | % population aged 35-54 | Percentage |
| Pct_Grandparents | % population aged 55-74 | Percentage |
| Pct_Separate_Houses | % separate house dwellings | Percentage |
| Pct_Apartments | % apartment dwellings | Percentage |
| Pct_Owned | % owned dwellings (outright + mortgage) | Percentage |
| Supply_Gap_Score | Demand minus supply suitability | Continuous |
| Market_Opportunity_Score | Demand + ownership viability | 0-100 |

## Analysis Methodology

See `MULTIGEN_HOUSING_ANALYSIS.md` in the repository root for detailed methodology, scoring formulas, and technical specifications.

## License & Attribution

**Data Source:** Australian Bureau of Statistics, 2021 Census
**License:** Creative Commons (subject to ABS licensing terms)
**Analysis:** Custom demographic and housing demand modeling

When using this data, please attribute to the Australian Bureau of Statistics for the underlying census data.

---

*For detailed analysis report, see `MULTIGEN_HOUSING_ANALYSIS.md` in repository root*
