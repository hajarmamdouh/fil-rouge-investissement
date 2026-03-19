"""
PHASE 1 - ÉTAPE 2 : Collecte World Happiness Report
====================================================
INSTRUCTIONS AVANT DE LANCER CE SCRIPT :
─────────────────────────────────────────
1. Va sur : https://worldhappiness.report/data/
2. Télécharge les fichiers CSV/Excel pour les années 2015 à 2024
3. Place-les dans le dossier : data/raw/happiness/
   Exemples de noms de fichiers :
     - WHR2024.csv
     - WHR2023.csv
     - DataForFigure2.1WHR2022C2.xls  (les noms varient selon l'année)
     etc.
4. Lance ce script : python src/02_collecte_happiness.py

Ce script :
- Lit automatiquement tous les fichiers du dossier happiness/
- Normalise les noms de colonnes (ils changent d'une année à l'autre)
- Fusionne tout en un seul CSV propre
"""

import pandas as pd
import os
import glob

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
RAW_DIR      = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
HAPPINESS_DIR = os.path.join(RAW_DIR, 'happiness')
os.makedirs(HAPPINESS_DIR, exist_ok=True)

# ─── MAPPING DES COLONNES ─────────────────────────────────────────────────────
# Le WHR change ses noms de colonnes chaque année. Ce dictionnaire
# standardise tout vers les mêmes noms finaux.

COLUMN_MAPPING = {
    # Pays
    'country name':                     'country_name',
    'country':                          'country_name',
    'country or region':                'country_name',

    # Année
    'year':                             'year',

    # Score bonheur (variable cible principale)
    'life ladder':                      'happiness_score',
    'happiness score':                  'happiness_score',
    'score':                            'happiness_score',
    'ladder score':                     'happiness_score',

    # PIB
    'log gdp per capita':               'log_gdp_per_capita',
    'economy (gdp per capita)':         'log_gdp_per_capita',
    'explained by: log gdp per capita': 'log_gdp_per_capita',

    # Soutien social
    'social support':                   'social_support',
    'family':                           'social_support',
    'explained by: social support':     'social_support',

    # Espérance de vie
    'healthy life expectancy at birth': 'life_expectancy_whr',
    'health (life expectancy)':         'life_expectancy_whr',
    'explained by: healthy life expectancy': 'life_expectancy_whr',

    # Liberté
    'freedom to make life choices':     'freedom',
    'freedom':                          'freedom',
    'explained by: freedom to make life choices': 'freedom',

    # Générosité
    'generosity':                       'generosity',
    'explained by: generosity':         'generosity',

    # Corruption
    'perceptions of corruption':        'corruption',
    'trust (government corruption)':    'corruption',
    'explained by: perceptions of corruption': 'corruption',

    # Affect positif / négatif (bonus)
    'positive affect':                  'positive_affect',
    'negative affect':                  'negative_affect',

    # Classement
    'overall rank':                     'happiness_rank',
    'happiness rank':                   'happiness_rank',
}

FINAL_COLUMNS = [
    'country_name', 'year', 'happiness_score', 'happiness_rank',
    'log_gdp_per_capita', 'social_support', 'life_expectancy_whr',
    'freedom', 'generosity', 'corruption',
    'positive_affect', 'negative_affect'
]


def normalize_columns(df):
    """Normalise les noms de colonnes vers le standard du projet."""
    df.columns = df.columns.str.strip().str.lower()
    df.rename(columns=COLUMN_MAPPING, inplace=True)
    return df


def read_happiness_file(filepath):
    """Lit un fichier WHR (CSV ou Excel) et retourne un DataFrame normalisé."""
    ext = os.path.splitext(filepath)[1].lower()
    filename = os.path.basename(filepath)

    try:
        if ext in ['.xlsx', '.xls']:
            df = pd.read_excel(filepath)
        else:
            df = pd.read_csv(filepath, encoding='utf-8', on_bad_lines='skip')

        df = normalize_columns(df)

        # Ajouter l'année si elle n'est pas dans le fichier
        # (certains fichiers WHR n'ont pas de colonne year)
        if 'year' not in df.columns:
            # Essayer de l'extraire du nom du fichier (ex: WHR2023.csv → 2023)
            year_candidates = [s for s in filename if s.isdigit()]
            year_str = ''.join(year_candidates[:4])
            if len(year_str) == 4:
                df['year'] = int(year_str)
                print(f"  ℹ️  Année {year_str} extraite du nom de fichier")
            else:
                print(f"  ⚠️  Impossible de détecter l'année pour : {filename}")
                return None

        # S'assurer que year est bien numérique
        df['year'] = pd.to_numeric(df['year'], errors='coerce')

        # Ajouter les colonnes manquantes avec NaN
        for col in FINAL_COLUMNS:
            if col not in df.columns:
                df[col] = None

        return df[FINAL_COLUMNS]

    except Exception as e:
        print(f"  ❌ Erreur lecture {filename}: {e}")
        return None


# ─── LECTURE DE TOUS LES FICHIERS ─────────────────────────────────────────────
print("\n" + "="*60)
print("COLLECTE WORLD HAPPINESS REPORT")
print("="*60)

# Chercher tous les fichiers CSV et Excel
patterns = [
    os.path.join(HAPPINESS_DIR, '*.csv'),
    os.path.join(HAPPINESS_DIR, '*.xlsx'),
    os.path.join(HAPPINESS_DIR, '*.xls'),
]
all_files = []
for pattern in patterns:
    all_files.extend(glob.glob(pattern))

if not all_files:
    print(f"""
⚠️  AUCUN FICHIER TROUVÉ dans : {HAPPINESS_DIR}

➡️  INSTRUCTIONS :
1. Va sur : https://worldhappiness.report/data/
2. Clique sur "Download Data" pour chaque année (2015 à 2024)
3. Place les fichiers téléchargés dans :
   {HAPPINESS_DIR}

Puis relance ce script.
""")
else:
    print(f"\n📂 {len(all_files)} fichier(s) trouvé(s)")
    all_dfs = []
    for filepath in sorted(all_files):
        filename = os.path.basename(filepath)
        print(f"\n📄 Lecture : {filename}")
        df = read_happiness_file(filepath)
        if df is not None and not df.empty:
            print(f"  ✅ {len(df)} lignes | {df['year'].dropna().unique()} années")
            all_dfs.append(df)

    if all_dfs:
        df_happiness = pd.concat(all_dfs, ignore_index=True)
        df_happiness = df_happiness.drop_duplicates(subset=['country_name', 'year'])
        df_happiness = df_happiness.sort_values(['country_name', 'year'])

        output_path = os.path.join(RAW_DIR, 'happiness_all_years.csv')
        df_happiness.to_csv(output_path, index=False)

        print(f"\n\n✅ WORLD HAPPINESS REPORT CONSOLIDÉ")
        print(f"   → {df_happiness.shape[0]} lignes | {df_happiness['country_name'].nunique()} pays")
        print(f"   → Années : {sorted(df_happiness['year'].dropna().astype(int).unique())}")
        print(f"   → Sauvegardé : happiness_all_years.csv")
        print(f"\n   Colonnes disponibles :")
        for col in FINAL_COLUMNS:
            non_null = df_happiness[col].notna().sum()
            pct = non_null / len(df_happiness) * 100
            print(f"     - {col:<30} {non_null:>5} valeurs ({pct:.0f}%)")
    else:
        print("\n❌ Aucune donnée valide trouvée.")
