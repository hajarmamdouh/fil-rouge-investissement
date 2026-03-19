import requests, pandas as pd, os, time

RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'raw')
ANNEES  = list(range(2015, 2025))

print("Téléchargement PIB par habitant...")
records = []

for year in ANNEES:
    url = f"https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.CD?format=json&date={year}&per_page=500"
    try:
        r = requests.get(url, timeout=40).json()
        if r and len(r) > 1 and r[1]:
            for item in r[1]:
                if item and item.get('countryiso3code') and item.get('value') is not None:
                    records.append({
                        'country_code': item['countryiso3code'],
                        'year': year,
                        'gdp_per_capita': item['value']
                    })
        print(f"  {year} → {len([x for x in records if x['year']==year])} pays")
    except Exception as e:
        print(f"  {year} → Erreur: {e}")
    time.sleep(1)

df = pd.DataFrame(records)
df.to_csv(os.path.join(RAW_DIR, 'gdp_per_capita.csv'), index=False)
print(f"\nOK → {len(df)} lignes sauvegardées dans gdp_per_capita.csv")

# Mettre à jour worldbank_merged.csv
df_merged = pd.read_csv(os.path.join(RAW_DIR, 'worldbank_merged.csv'))
if 'gdp_per_capita' in df_merged.columns:
    df_merged = df_merged.drop(columns=['gdp_per_capita'])
df_merged = df_merged.merge(df, on=['country_code', 'year'], how='left')
df_merged.to_csv(os.path.join(RAW_DIR, 'worldbank_merged.csv'), index=False)
print(f"worldbank_merged.csv mis à jour !")