"""
PHASE 1 - Collecte World Bank API (version corrigée)
"""

import requests
import pandas as pd
import os
import time

RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'raw')
os.makedirs(RAW_DIR, exist_ok=True)
ANNEES = list(range(2015, 2025))

def fetch_all_pages(url):
    all_data = []
    page = 1
    while True:
        paged_url = f"{url}&page={page}&per_page=500"
        try:
            response = requests.get(paged_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            if not data or len(data) < 2 or not data[1]:
                break
            all_data.extend(data[1])
            total_pages = data[0].get('pages', 1)
            if page >= total_pages:
                break
            page += 1
            time.sleep(0.3)
        except Exception as e:
            print(f"  Erreur page {page}: {e}")
            break
    return all_data

print("\n" + "="*60)
print("COLLECTE WORLD BANK API")
print("="*60)
print("\n Telechargement : Liste des pays et regions")

url_countries = "https://api.worldbank.org/v2/country?format=json&per_page=500"
response = requests.get(url_countries, timeout=30)
data = response.json()

countries_list = []
for c in data[1]:
    if not c or not c.get('id') or not c.get('name'):
        continue
    region_raw = c.get('region', '')
    region_value = region_raw.get('value', '') if isinstance(region_raw, dict) else str(region_raw)
    income_raw = c.get('incomeLevel', '')
    income_value = income_raw.get('value', '') if isinstance(income_raw, dict) else str(income_raw)
    countries_list.append({
        'country_code': c['id'],
        'country_name': c['name'],
        'region': region_value,
        'income_level': income_value,
        'capital': c.get('capitalCity', ''),
        'latitude': c.get('latitude', ''),
        'longitude': c.get('longitude', ''),
    })

df_countries = pd.DataFrame(countries_list)
df_countries = df_countries[df_countries['region'].str.strip() != '']
df_countries = df_countries[df_countries['region'] != 'Aggregates']
df_countries.to_csv(os.path.join(RAW_DIR, 'countries.csv'), index=False)
print(f"  OK {len(df_countries)} pays enregistres")

def fetch_indicator(indicator_code, col_name, description):
    print(f"\n Telechargement : {description}")
    url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator_code}?format=json&mrv=10"
    raw = fetch_all_pages(url)
    records = []
    for item in raw:
        if not item:
            continue
        code = item.get('countryiso3code', '')
        value = item.get('value')
        year_str = item.get('date', '')
        if not code or value is None or not year_str:
            continue
        try:
            year = int(year_str)
        except:
            continue
        if year in ANNEES:
            records.append({'country_code': code, 'year': year, col_name: value})
    df = pd.DataFrame(records) if records else pd.DataFrame(columns=['country_code', 'year', col_name])
    print(f"  OK {len(df)} lignes")
    return df

indicateurs = [
    ("NY.GDP.PCAP.CD",    "gdp_per_capita",    "PIB par habitant"),
    ("NY.GDP.MKTP.KD.ZG", "gdp_growth",        "Croissance economique"),
    ("FP.CPI.TOTL.ZG",    "inflation",         "Inflation"),
    ("SP.POP.TOTL",       "population",        "Population"),
    ("NY.GNP.PCAP.CD",    "gni_per_capita",    "Revenu National Brut"),
    ("SL.UEM.TOTL.ZS",    "unemployment_rate", "Chomage"),
    ("SP.DYN.LE00.IN",    "life_expectancy",   "Esperance de vie"),
    ("SE.ADT.LITR.ZS",    "literacy_rate",     "Alphabetisation"),
]

dataframes = {}
for code, col, desc in indicateurs:
    df = fetch_indicator(code, col, desc)
    if not df.empty:
        dataframes[col] = df
        df.to_csv(os.path.join(RAW_DIR, f'{col}.csv'), index=False)

print("\n--- Fusion ---")
if dataframes:
    df_merged = list(dataframes.values())[0]
    for col, df in list(dataframes.items())[1:]:
        df_merged = df_merged.merge(df, on=['country_code', 'year'], how='outer')
    df_merged = df_merged.merge(
        df_countries[['country_code', 'country_name', 'region', 'income_level']],
        on='country_code', how='left'
    )
    df_merged = df_merged[df_merged['country_name'].notna()]
    output_path = os.path.join(RAW_DIR, 'worldbank_merged.csv')
    df_merged.to_csv(output_path, index=False)
    print(f"\nTERMINE !")
    print(f"   {df_merged.shape[0]} lignes | {df_merged['country_code'].nunique()} pays")
    print(f"   Fichier cree : data/raw/worldbank_merged.csv")
    print(f"\nFichiers dans data/raw/ :")
    for f in os.listdir(RAW_DIR):
        size = os.path.getsize(os.path.join(RAW_DIR, f)) / 1024
        print(f"   - {f}  ({size:.0f} KB)")
else:
    print("Aucune donnee. Verifie ta connexion internet.")