"""
PHASE 2 : Nettoyage, préparation & fusion des données
======================================================
Ce script crée le dataset maître final en fusionnant :
  - World Bank (indicateurs économiques)
  - World Happiness Report (bien-être, corruption, liberté...)
  

Résultat : data/final/master_dataset.csv
"""

import pandas as pd
import numpy as np
import os

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
BASE_DIR   = os.path.join(os.path.dirname(__file__), '..')
RAW_DIR    = os.path.join(BASE_DIR, 'data', 'raw')
PROC_DIR   = os.path.join(BASE_DIR, 'data', 'processed')
FINAL_DIR  = os.path.join(BASE_DIR, 'data', 'final')

os.makedirs(PROC_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)


# ─── MAPPING ISO3 → NOM PAYS (pour jointure WHR ↔ World Bank) ─────────────────
# Le WHR utilise des noms en anglais, World Bank utilise ISO3.
# Ce dictionnaire couvre les cas les plus fréquents.
COUNTRY_NAME_TO_ISO3 = {
    'Afghanistan': 'AFG', 'Albania': 'ALB', 'Algeria': 'DZA',
    'Argentina': 'ARG', 'Armenia': 'ARM', 'Australia': 'AUS',
    'Austria': 'AUT', 'Azerbaijan': 'AZE', 'Bahrain': 'BHR',
    'Bangladesh': 'BGD', 'Belarus': 'BLR', 'Belgium': 'BEL',
    'Benin': 'BEN', 'Bolivia': 'BOL', 'Bosnia and Herzegovina': 'BIH',
    'Botswana': 'BWA', 'Brazil': 'BRA', 'Bulgaria': 'BGR',
    'Burkina Faso': 'BFA', 'Cambodia': 'KHM', 'Cameroon': 'CMR',
    'Canada': 'CAN', 'Chad': 'TCD', 'Chile': 'CHL',
    'China': 'CHN', 'Colombia': 'COL', 'Comoros': 'COM',
    'Congo (Brazzaville)': 'COG', 'Congo (Kinshasa)': 'COD',
    'Costa Rica': 'CRI', 'Croatia': 'HRV', 'Cuba': 'CUB',
    'Cyprus': 'CYP', 'Czech Republic': 'CZE', 'Czechia': 'CZE',
    'Denmark': 'DNK', 'Dominican Republic': 'DOM', 'Ecuador': 'ECU',
    'Egypt': 'EGY', 'El Salvador': 'SLV', 'Estonia': 'EST',
    'Ethiopia': 'ETH', 'Finland': 'FIN', 'France': 'FRA',
    'Gabon': 'GAB', 'Gambia': 'GMB', 'Georgia': 'GEO',
    'Germany': 'DEU', 'Ghana': 'GHA', 'Greece': 'GRC',
    'Guatemala': 'GTM', 'Guinea': 'GIN', 'Haiti': 'HTI',
    'Honduras': 'HND', 'Hong Kong S.A.R. of China': 'HKG',
    'Hungary': 'HUN', 'Iceland': 'ISL', 'India': 'IND',
    'Indonesia': 'IDN', 'Iran': 'IRN', 'Iraq': 'IRQ',
    'Ireland': 'IRL', 'Israel': 'ISR', 'Italy': 'ITA',
    'Ivory Coast': "CIV", "Côte d'Ivoire": 'CIV',
    'Jamaica': 'JAM', 'Japan': 'JPN', 'Jordan': 'JOR',
    'Kazakhstan': 'KAZ', 'Kenya': 'KEN', 'Kosovo': 'XKX',
    'Kuwait': 'KWT', 'Kyrgyzstan': 'KGZ', 'Laos': 'LAO',
    'Latvia': 'LVA', 'Lebanon': 'LBN', 'Liberia': 'LBR',
    'Libya': 'LBY', 'Lithuania': 'LTU', 'Luxembourg': 'LUX',
    'Madagascar': 'MDG', 'Malawi': 'MWI', 'Malaysia': 'MYS',
    'Mali': 'MLI', 'Malta': 'MLT', 'Mauritania': 'MRT',
    'Mauritius': 'MUS', 'Mexico': 'MEX', 'Moldova': 'MDA',
    'Mongolia': 'MNG', 'Montenegro': 'MNE', 'Morocco': 'MAR',
    'Mozambique': 'MOZ', 'Myanmar': 'MMR', 'Namibia': 'NAM',
    'Nepal': 'NPL', 'Netherlands': 'NLD', 'New Zealand': 'NZL',
    'Nicaragua': 'NIC', 'Niger': 'NER', 'Nigeria': 'NGA',
    'North Cyprus': 'CYP', 'North Macedonia': 'MKD',
    'Norway': 'NOR', 'Pakistan': 'PAK', 'Palestinian Territories': 'PSE',
    'Panama': 'PAN', 'Paraguay': 'PRY', 'Peru': 'PER',
    'Philippines': 'PHL', 'Poland': 'POL', 'Portugal': 'PRT',
    'Romania': 'ROU', 'Russia': 'RUS', 'Rwanda': 'RWA',
    'Saudi Arabia': 'SAU', 'Senegal': 'SEN', 'Serbia': 'SRB',
    'Sierra Leone': 'SLE', 'Singapore': 'SGP', 'Slovakia': 'SVK',
    'Slovenia': 'SVN', 'Somalia': 'SOM', 'South Africa': 'ZAF',
    'South Korea': 'KOR', 'Spain': 'ESP', 'Sri Lanka': 'LKA',
    'Sudan': 'SDN', 'Sweden': 'SWE', 'Switzerland': 'CHE',
    'Syria': 'SYR', 'Taiwan Province of China': 'TWN',
    'Tajikistan': 'TJK', 'Tanzania': 'TZA', 'Thailand': 'THA',
    'Togo': 'TGO', 'Trinidad and Tobago': 'TTO', 'Tunisia': 'TUN',
    'Turkey': 'TUR', 'Turkmenistan': 'TKM', 'Uganda': 'UGA',
    'Ukraine': 'UKR', 'United Arab Emirates': 'ARE',
    'United Kingdom': 'GBR', 'United States': 'USA',
    'Uruguay': 'URY', 'Uzbekistan': 'UZB', 'Venezuela': 'VEN',
    'Vietnam': 'VNM', 'Yemen': 'YEM', 'Zambia': 'ZMB',
    'Zimbabwe': 'ZWE',
}


def report_missing(df, label):
    """Affiche un rapport des valeurs manquantes."""
    print(f"\n📊 Valeurs manquantes — {label}")
    for col in df.columns:
        n_missing = df[col].isna().sum()
        if n_missing > 0:
            pct = n_missing / len(df) * 100
            print(f"   {col:<35} {n_missing:>5} ({pct:.1f}%)")


# ─── CHARGEMENT DES DONNÉES ───────────────────────────────────────────────────
print("\n" + "="*60)
print("PHASE 2 : NETTOYAGE & FUSION")
print("="*60)

# 1. World Bank
wb_path = os.path.join(RAW_DIR, 'worldbank_merged.csv')
if not os.path.exists(wb_path):
    print("❌ worldbank_merged.csv introuvable. Lance d'abord : python src/01_collecte_worldbank.py")
    exit(1)

df_wb = pd.read_csv(wb_path)
print(f"\n✅ World Bank chargé : {df_wb.shape}")

# 2. Happiness
hap_path = os.path.join(RAW_DIR, 'happiness_all_years.csv')
has_happiness = os.path.exists(hap_path)

if has_happiness:
    df_hap = pd.read_csv(hap_path)
    # Ajouter le code ISO3 via le mapping
    df_hap['country_code'] = df_hap['country_name'].map(COUNTRY_NAME_TO_ISO3)
    unmapped = df_hap[df_hap['country_code'].isna()]['country_name'].unique()
    if len(unmapped) > 0:
        print(f"\n⚠️  {len(unmapped)} pays WHR sans correspondance ISO3 :")
        for c in sorted(unmapped): print(f"   - {c}")
    df_hap = df_hap.dropna(subset=['country_code'])
    print(f"✅ Happiness chargé : {df_hap.shape} | {df_hap['country_code'].nunique()} pays mappés")
else:
    print("⚠️  happiness_all_years.csv introuvable → fusion sans WHR")
    print("   (Lance src/02_collecte_happiness.py après téléchargement des fichiers)")


# ─── NETTOYAGE WORLD BANK ─────────────────────────────────────────────────────
print("\n\n--- Nettoyage World Bank ---")

# Types corrects
df_wb['year'] = pd.to_numeric(df_wb['year'], errors='coerce').astype('Int64')
numeric_cols = ['gdp_per_capita', 'gdp_growth', 'inflation', 'population',
                'gni_per_capita', 'unemployment_rate', 'life_expectancy', 'literacy_rate']
for col in numeric_cols:
    if col in df_wb.columns:
        df_wb[col] = pd.to_numeric(df_wb[col], errors='coerce')

# Supprimer doublons
df_wb = df_wb.drop_duplicates(subset=['country_code', 'year'])
print(f"✅ Doublons supprimés | Taille finale : {df_wb.shape}")

report_missing(df_wb, "World Bank")


# ─── NETTOYAGE HAPPINESS ──────────────────────────────────────────────────────
if has_happiness:
    print("\n--- Nettoyage Happiness ---")
    df_hap['year'] = pd.to_numeric(df_hap['year'], errors='coerce').astype('Int64')
    hap_numeric = ['happiness_score', 'happiness_rank', 'log_gdp_per_capita',
                   'social_support', 'life_expectancy_whr', 'freedom',
                   'generosity', 'corruption', 'positive_affect', 'negative_affect']
    for col in hap_numeric:
        if col in df_hap.columns:
            df_hap[col] = pd.to_numeric(df_hap[col], errors='coerce')

    df_hap = df_hap.drop_duplicates(subset=['country_code', 'year'])
    print(f"✅ Taille après nettoyage : {df_hap.shape}")


# ─── FUSION FINALE ────────────────────────────────────────────────────────────
print("\n\n--- Fusion des datasets ---")

df_master = df_wb.copy()

if has_happiness:
    hap_cols = ['country_code', 'year', 'happiness_score', 'happiness_rank',
                'social_support', 'life_expectancy_whr', 'freedom',
                'generosity', 'corruption', 'positive_affect', 'negative_affect']
    available_hap_cols = [c for c in hap_cols if c in df_hap.columns]
    df_master = df_master.merge(
        df_hap[available_hap_cols],
        on=['country_code', 'year'],
        how='left'
    )
    print(f"✅ Fusion avec WHR réussie")


# ─── CALCUL DU SCORE D'ATTRACTIVITÉ ───────────────────────────────────────────
print("\n--- Calcul du Score d'Attractivité Global ---")

from sklearn.preprocessing import MinMaxScaler

# Indicateurs positifs (plus = mieux) et négatifs (plus = moins bien)
positive_indicators = ['gdp_per_capita', 'life_expectancy', 'happiness_score',
                       'social_support', 'freedom', 'literacy_rate']
negative_indicators = ['inflation', 'corruption', 'unemployment_rate']

available_pos = [c for c in positive_indicators if c in df_master.columns]
available_neg = [c for c in negative_indicators if c in df_master.columns]

score_df = df_master[['country_code', 'year'] + available_pos + available_neg].copy()

scaler = MinMaxScaler()

# Normaliser indicateurs positifs (0→1, 1 = meilleur)
for col in available_pos:
    col_data = score_df[[col]].fillna(score_df[col].median())
    score_df[f'{col}_norm'] = scaler.fit_transform(col_data)

# Normaliser indicateurs négatifs (inverser : 0→1, 1 = meilleur)
for col in available_neg:
    col_data = score_df[[col]].fillna(score_df[col].median())
    normalized = scaler.fit_transform(col_data)
    score_df[f'{col}_norm'] = 1 - normalized  # Inverser

norm_cols = [c for c in score_df.columns if c.endswith('_norm')]
if norm_cols:
    score_df['attractivity_score'] = score_df[norm_cols].mean(axis=1)
    df_master = df_master.merge(
        score_df[['country_code', 'year', 'attractivity_score']],
        on=['country_code', 'year'],
        how='left'
    )
    print(f"✅ Score d'attractivité calculé ({len(norm_cols)} indicateurs utilisés)")


# ─── SAUVEGARDE ───────────────────────────────────────────────────────────────
output_path = os.path.join(FINAL_DIR, 'master_dataset.csv')
df_master.to_csv(output_path, index=False)

print(f"\n\n{'='*60}")
print("✅ PHASE 2 TERMINÉE")
print(f"{'='*60}")
print(f"📁 Dataset maître : data/final/master_dataset.csv")
print(f"   → {df_master.shape[0]} lignes | {df_master.shape[1]} colonnes")
print(f"   → {df_master['country_code'].nunique()} pays | {df_master['year'].nunique()} années")
print(f"\n   Colonnes finales :")
for col in df_master.columns:
    print(f"   - {col}")
