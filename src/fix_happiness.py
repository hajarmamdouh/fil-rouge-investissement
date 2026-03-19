import pandas as pd
import os

RAW_DIR = 'data/raw'
HAP_DIR = os.path.join(RAW_DIR, 'happiness')
all_dfs = []

for filename in os.listdir(HAP_DIR):
    filepath = os.path.join(HAP_DIR, filename)
    print(f"Lecture : {filename}")
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.lower()
    df = df.loc[:, ~df.columns.duplicated()]

    rename = {
        'country name': 'country_name',
        'country': 'country_name',
        'life ladder': 'happiness_score',
        'happiness score': 'happiness_score',
        'score': 'happiness_score',
        'ladder score': 'happiness_score',
        'log gdp per capita': 'log_gdp_per_capita',
        'social support': 'social_support',
        'healthy life expectancy at birth': 'life_expectancy_whr',
        'freedom to make life choices': 'freedom',
        'generosity': 'generosity',
        'perceptions of corruption': 'corruption',
        'positive affect': 'positive_affect',
        'negative affect': 'negative_affect',
        'year': 'year'
    }
    df.rename(columns=rename, inplace=True)

    if 'year' not in df.columns:
        year_str = ''.join(filter(str.isdigit, filename))[:4]
        df['year'] = int(year_str) if year_str else 0

    cols = ['country_name', 'year', 'happiness_score', 'log_gdp_per_capita',
            'social_support', 'life_expectancy_whr', 'freedom',
            'generosity', 'corruption', 'positive_affect', 'negative_affect']
    keep = [c for c in cols if c in df.columns]
    all_dfs.append(df[keep])
    print(f"  OK {len(df)} lignes")

df_final = pd.concat(all_dfs, ignore_index=True)
df_final = df_final.drop_duplicates(subset=['country_name', 'year'])
df_final = df_final[df_final['year'].between(2015, 2024)]
df_final.to_csv(os.path.join(RAW_DIR, 'happiness_all_years.csv'), index=False)

print(f"\nTERMINE !")
print(f"  {len(df_final)} lignes")
print(f"  {df_final['country_name'].nunique()} pays")
print(f"  Annees : {sorted(df_final['year'].unique())}")