"""
TRAITEMENT PROFESSIONNEL DES VALEURS MANQUANTES
================================================
Auteur  : Hajar Mamdouh | Formation Data Analyst - Simplon
Méthode : Interpolation + Moyenne régionale + Forward/Backward fill
Résultat: data/final/master_clean.csv — zéro NULL sur les colonnes clés
"""

import pandas as pd
import numpy as np
import os

# ─── CHEMINS ──────────────────────────────────────────────
FINAL_DIR = r'C:\Users\Amine Mamdouh\Desktop\fil-rouge-investissement-main\data\final'
df = pd.read_csv(os.path.join(FINAL_DIR, 'master_dataset.csv'))

print("="*60)
print("TRAITEMENT DES VALEURS MANQUANTES")
print("="*60)
print(f"\nDataset initial : {df.shape[0]} lignes x {df.shape[1]} colonnes")

# ─── RAPPORT AVANT ────────────────────────────────────────
print("\n📊 NULL AVANT traitement :")
for col in df.columns:
    n = df[col].isna().sum()
    if n > 0:
        pct = n / len(df) * 100
        print(f"   {col:<30} {n:>5} NULL ({pct:.1f}%)")

# ─── TRIER PAR PAYS ET ANNÉE ──────────────────────────────
df = df.sort_values(['country_code', 'year']).reset_index(drop=True)

# Colonne pour tracer les imputations
df['imputation_notes'] = ''

# ============================================================
# MÉTHODE 1 : INTERPOLATION LINÉAIRE PAR PAYS
# Pour : happiness_score, social_support, freedom, 
#        corruption, generosity, positive_affect, negative_affect
# Logique : ces valeurs évoluent lentement → on estime
#           les années manquantes entre deux valeurs connues
# ============================================================
cols_interpolation = [
    'happiness_score', 'social_support', 'freedom',
    'corruption', 'generosity', 'positive_affect', 'negative_affect',
    'life_expectancy_whr'
]

print("\n\n--- Méthode 1 : Interpolation linéaire par pays ---")
for col in cols_interpolation:
    if col not in df.columns:
        continue
    null_avant = df[col].isna().sum()
    if null_avant == 0:
        continue

    df[col] = df.groupby('country_code')[col].transform(
        lambda x: x.interpolate(method='linear', limit_direction='both')
    )
    null_apres = df[col].isna().sum()
    traites = null_avant - null_apres
    print(f"   {col:<30} {null_avant:>4} → {null_apres:>4} NULL  ({traites} valeurs interpolées)")

    # Marquer les imputations
    df.loc[df[col].notna() & (df['imputation_notes'].str.len() == 0), 'imputation_notes'] = ''
    

# ============================================================
# MÉTHODE 2 : FORWARD FILL + BACKWARD FILL PAR PAYS
# Pour : gdp_per_capita, gdp_growth, gni_per_capita,
#        literacy_rate, unemployment_rate, life_expectancy
# Logique : on propage la dernière valeur connue vers l'avant
#           puis vers l'arrière (pour les premières années)
# ============================================================
cols_ffill = [
    'gdp_per_capita', 'gdp_growth', 'gni_per_capita',
    'literacy_rate', 'unemployment_rate', 'life_expectancy',
    'population'
]

print("\n--- Méthode 2 : Forward/Backward fill par pays ---")
for col in cols_ffill:
    if col not in df.columns:
        continue
    null_avant = df[col].isna().sum()
    if null_avant == 0:
        continue

    df[col] = df.groupby('country_code')[col].transform(
        lambda x: x.fillna(method='ffill').fillna(method='bfill')
    )
    null_apres = df[col].isna().sum()
    traites = null_avant - null_apres
    print(f"   {col:<30} {null_avant:>4} → {null_apres:>4} NULL  ({traites} valeurs propagées)")


# ============================================================
# MÉTHODE 3 : MOYENNE RÉGIONALE PAR ANNÉE
# Pour : inflation et tout ce qui reste NULL après méthodes 1 et 2
# Logique : si un pays n'a aucune donnée, on prend
#           la moyenne des pays de la même région cette année-là
# ============================================================
cols_region = ['inflation', 'gdp_per_capita', 'gdp_growth', 
               'life_expectancy', 'unemployment_rate', 'literacy_rate',
               'happiness_score', 'social_support', 'freedom', 'corruption']

print("\n--- Méthode 3 : Moyenne régionale par année ---")
for col in cols_region:
    if col not in df.columns:
        continue
    null_avant = df[col].isna().sum()
    if null_avant == 0:
        continue

    # Calculer la moyenne régionale par année
    region_mean = df.groupby(['region', 'year'])[col].transform('mean')
    df[col] = df[col].fillna(region_mean)

    null_apres = df[col].isna().sum()
    traites = null_avant - null_apres
    print(f"   {col:<30} {null_avant:>4} → {null_apres:>4} NULL  ({traites} valeurs par moyenne régionale)")


# ============================================================
# MÉTHODE 4 : MOYENNE MONDIALE PAR ANNÉE
# Pour : ce qui reste encore NULL après les 3 méthodes
# Logique : dernier recours — moyenne mondiale
# ============================================================
cols_numeriques = df.select_dtypes(include=[np.number]).columns.tolist()
cols_numeriques = [c for c in cols_numeriques if c not in ['year']]

print("\n--- Méthode 4 : Moyenne mondiale par année (dernier recours) ---")
for col in cols_numeriques:
    null_avant = df[col].isna().sum()
    if null_avant == 0:
        continue

    world_mean = df.groupby('year')[col].transform('mean')
    df[col] = df[col].fillna(world_mean)

    null_apres = df[col].isna().sum()
    traites = null_avant - null_apres
    if traites > 0:
        print(f"   {col:<30} {null_avant:>4} → {null_apres:>4} NULL  ({traites} valeurs par moyenne mondiale)")


# ============================================================
# MÉTHODE 5 : MÉDIANE GLOBALE
# Pour : les rares cas encore NULL (pays isolés sans région)
# ============================================================
print("\n--- Méthode 5 : Médiane globale (cas extrêmes) ---")
for col in cols_numeriques:
    null_avant = df[col].isna().sum()
    if null_avant == 0:
        continue
    mediane = df[col].median()
    df[col] = df[col].fillna(mediane)
    null_apres = df[col].isna().sum()
    traites = null_avant - null_apres
    if traites > 0:
        print(f"   {col:<30} {null_avant:>4} → {null_apres:>4} NULL  ({traites} valeurs par médiane)")


# ─── RECALCULER LE SCORE D'ATTRACTIVITÉ ───────────────────
print("\n--- Recalcul du score d'attractivité ---")
from sklearn.preprocessing import MinMaxScaler

pos_cols = ['gdp_per_capita', 'life_expectancy', 'happiness_score',
            'social_support', 'freedom', 'literacy_rate']
neg_cols = ['inflation', 'corruption', 'unemployment_rate']

available_pos = [c for c in pos_cols if c in df.columns]
available_neg = [c for c in neg_cols if c in df.columns]

scaler = MinMaxScaler()
norm_scores = []

for col in available_pos:
    vals = scaler.fit_transform(df[[col]])
    norm_scores.append(vals.flatten())

for col in available_neg:
    vals = scaler.fit_transform(df[[col]])
    norm_scores.append(1 - vals.flatten())

if norm_scores:
    df['attractivity_score'] = np.mean(norm_scores, axis=0)
    print(f"   ✅ Score recalculé avec {len(norm_scores)} indicateurs")


# ─── RAPPORT APRÈS ────────────────────────────────────────
print("\n\n📊 NULL APRÈS traitement :")
total_null = 0
for col in df.select_dtypes(include=[np.number]).columns:
    n = df[col].isna().sum()
    if n > 0:
        pct = n / len(df) * 100
        print(f"   ⚠️  {col:<30} {n:>5} NULL ({pct:.1f}%)")
        total_null += n

if total_null == 0:
    print("   ✅ AUCUN NULL sur les colonnes numériques !")
else:
    print(f"   Total restant : {total_null} NULL")


# ─── SAUVEGARDE ───────────────────────────────────────────
output_path = os.path.join(FINAL_DIR, 'master_clean.csv')
df.to_csv(output_path, index=False)

print(f"\n\n{'='*60}")
print("✅ TRAITEMENT TERMINÉ")
print(f"{'='*60}")
print(f"   Fichier créé : data/final/master_clean.csv")
print(f"   Dimensions   : {df.shape[0]} lignes x {df.shape[1]} colonnes")
print(f"   Pays         : {df['country_code'].nunique()}")
print(f"   Années       : {sorted(df['year'].unique().tolist())}")
print(f"\n   → Importe master_clean.csv dans Power BI !")
print(f"   → C'est ce fichier qui contient zéro NULL !")