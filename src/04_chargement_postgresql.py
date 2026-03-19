"""
PHASE 3 : Chargement des données dans PostgreSQL
=================================================
Prérequis :
  pip install psycopg2-binary sqlalchemy pandas

Avant de lancer :
  1. Créer la base : createdb projet_pays
  2. Créer le schéma : psql -d projet_pays -f sql/schema.sql
  3. Avoir data/final/master_dataset.csv prêt
"""

import pandas as pd
import sqlalchemy as sa
import os

# ─── CONFIGURATION CONNEXION ──────────────────────────────────────────────────
# Modifie ces valeurs selon ta configuration PostgreSQL locale
DB_CONFIG = {
    'host':     'localhost',
    'port':     5432,
    'database': 'projet_pays',
    'user':     'postgres',        # Ton username PostgreSQL
    'password': 'tonmotdepasse',   # Ton mot de passe PostgreSQL
}

FINAL_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'final')


def get_engine():
    url = (f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
           f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    return sa.create_engine(url)


def load_data():
    print("\n" + "="*60)
    print("PHASE 3 : CHARGEMENT POSTGRESQL")
    print("="*60)

    # ── Charger le dataset maître ──────────────────────────────
    master_path = os.path.join(FINAL_DIR, 'master_dataset.csv')
    if not os.path.exists(master_path):
        print("❌ master_dataset.csv introuvable.")
        print("   Lance d'abord : python src/03_nettoyage_fusion.py")
        return

    df = pd.read_csv(master_path)
    print(f"\n📂 Dataset chargé : {df.shape}")

    engine = get_engine()

    with engine.begin() as conn:

        # ── 1. dim_region ──────────────────────────────────────
        print("\n📋 Chargement dim_region...")
        regions = df[['region']].dropna().drop_duplicates()
        regions = regions.rename(columns={'region': 'region_name'})
        regions.to_sql('dim_region', conn, if_exists='append',
                       index=False, method='multi')
        print(f"   ✅ {len(regions)} régions insérées")

        # ── 2. dim_pays ────────────────────────────────────────
        print("\n📋 Chargement dim_pays...")
        pays_cols = ['country_code', 'country_name', 'income_level']
        if 'capital' in df.columns:
            pays_cols += ['capital']
        if 'latitude' in df.columns:
            pays_cols += ['latitude', 'longitude']

        df_pays = df[pays_cols].drop_duplicates(subset=['country_code']).dropna(subset=['country_code'])

        # Récupérer region_id depuis la BDD
        result = conn.execute(sa.text("SELECT region_id, region_name FROM dim_region"))
        region_map = {row.region_name: row.region_id for row in result}
        df_pays['region_id'] = df['region'].map(region_map)

        df_pays.to_sql('dim_pays', conn, if_exists='append',
                       index=False, method='multi')
        print(f"   ✅ {len(df_pays)} pays insérés")

        # ── 3. fact_indicateurs ────────────────────────────────
        print("\n📋 Chargement fact_indicateurs...")
        fact_cols = [
            'country_code', 'year',
            'gdp_per_capita', 'gdp_growth', 'inflation', 'population',
            'gni_per_capita', 'unemployment_rate', 'life_expectancy', 'literacy_rate',
            'happiness_score', 'happiness_rank', 'social_support', 'life_expectancy_whr',
            'freedom', 'generosity', 'corruption', 'positive_affect', 'negative_affect',
            'attractivity_score'
        ]
        available = [c for c in fact_cols if c in df.columns]
        df_fact = df[available].dropna(subset=['country_code', 'year'])

        # Chargement par batch pour éviter les timeouts
        batch_size = 1000
        total = 0
        for i in range(0, len(df_fact), batch_size):
            batch = df_fact.iloc[i:i+batch_size]
            batch.to_sql('fact_indicateurs', conn, if_exists='append',
                         index=False, method='multi')
            total += len(batch)
            print(f"   → {total}/{len(df_fact)} lignes insérées...", end='\r')

        print(f"\n   ✅ {total} lignes insérées dans fact_indicateurs")

    # ── Vérification finale ────────────────────────────────────
    print("\n\n--- Vérification ---")
    with engine.connect() as conn:
        for table in ['dim_region', 'dim_pays', 'fact_indicateurs']:
            count = conn.execute(sa.text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"   {table:<25} → {count:>6} lignes")

        print("\n   Top 5 pays par score de bonheur (2023) :")
        result = conn.execute(sa.text("""
            SELECT p.country_name, f.happiness_score, f.gdp_per_capita
            FROM fact_indicateurs f
            JOIN dim_pays p ON f.country_code = p.country_code
            WHERE f.year = 2023 AND f.happiness_score IS NOT NULL
            ORDER BY f.happiness_score DESC
            LIMIT 5
        """))
        for row in result:
            print(f"     {row.country_name:<25} bonheur={row.happiness_score:.3f}  PIB/hab=${row.gdp_per_capita:,.0f}")

    print(f"\n\n{'='*60}")
    print("✅ PHASE 3 TERMINÉE - Base de données chargée !")
    print(f"{'='*60}")
    print("   Connecte Power BI à : localhost:5432 / projet_pays")


if __name__ == '__main__':
    load_data()
