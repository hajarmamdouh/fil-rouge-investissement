"""
PHASE 3 : Chargement PostgreSQL — Version Professionnelle Complète
Auteur : Hajar Mamdouh | Formation Data Analyst - Simplon
"""

import pandas as pd
import numpy as np
import sqlalchemy as sa
import os

DB_CONFIG = {
    'host':     'localhost',
    'port':     5432,
    'database': 'projet_pays',
    'user':     'postgres',
    'password': '123456',
}

FINAL_DIR = r'C:\Users\Amine Mamdouh\Desktop\fil-rouge-investissement-main\data\final'
RAW_DIR   = r'C:\Users\Amine Mamdouh\Desktop\fil-rouge-investissement-main\data\raw'

def get_engine():
    url = (f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
           f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    return sa.create_engine(url)

def load_data():
    print("\n" + "="*60)
    print("CHARGEMENT POSTGRESQL — VERSION PROFESSIONNELLE")
    print("="*60)

    master_path = os.path.join(FINAL_DIR, 'master_clean.csv')
    if not os.path.exists(master_path):
        master_path = os.path.join(FINAL_DIR, 'master_dataset.csv')
        print("master_clean.csv introuvable — utilisation de master_dataset.csv")

    df = pd.read_csv(master_path)
    print(f"Dataset charge : {df.shape}")

    countries_path = os.path.join(RAW_DIR, 'countries.csv')
    if os.path.exists(countries_path):
        df_countries = pd.read_csv(countries_path)
    else:
        df_countries = pd.DataFrame(columns=['country_code','capital','latitude','longitude'])

    engine = get_engine()

    with engine.begin() as conn:
        print("\nNettoyage tables...")
        conn.execute(sa.text("TRUNCATE TABLE fact_indicateurs CASCADE"))
        conn.execute(sa.text("TRUNCATE TABLE dim_pays CASCADE"))
        conn.execute(sa.text("TRUNCATE TABLE dim_region CASCADE"))
        print("   OK tables videes")

        # 1. DIM_REGION
        print("\nChargement dim_region...")
        region_codes = {
            'Latin America & Caribbean': 'LAC',
            'Latin America & Caribbean ': 'LAC',
            'Middle East & North Africa': 'MENA',
            'Middle East, North Africa, Afghanistan & Pakistan': 'MENAP',
            'Sub-Saharan Africa': 'SSA',
            'Sub-Saharan Africa ': 'SSA',
            'Europe & Central Asia': 'ECA',
            'East Asia & Pacific': 'EAP',
            'South Asia': 'SAS',
            'North America': 'NAM',
        }
        regions = df[['region']].dropna().drop_duplicates().rename(columns={'region': 'region_name'})
        regions['region_name'] = regions['region_name'].str.strip()
        regions['region_code'] = regions['region_name'].map(region_codes)
        regions.to_sql('dim_region', conn, if_exists='append', index=False, method='multi')
        print(f"   OK {len(regions)} regions inserees")

        # 2. DIM_INCOME_LEVEL
        result = conn.execute(sa.text("SELECT COUNT(*) FROM dim_income_level"))
        if result.scalar() == 0:
            income_data = pd.DataFrame([
                {'income_level': 'High income',         'income_description': 'PIB/hab > 13 845 USD',     'gdp_threshold_usd': 13845},
                {'income_level': 'Upper middle income', 'income_description': 'PIB/hab 4 466-13 845 USD', 'gdp_threshold_usd': 4466},
                {'income_level': 'Lower middle income', 'income_description': 'PIB/hab 1 136-4 465 USD',  'gdp_threshold_usd': 1136},
                {'income_level': 'Low income',          'income_description': 'PIB/hab < 1 136 USD',      'gdp_threshold_usd': 0},
                {'income_level': 'Not classified',      'income_description': 'Non classifie',            'gdp_threshold_usd': None},
            ])
            income_data.to_sql('dim_income_level', conn, if_exists='append', index=False)

        result = conn.execute(sa.text("SELECT income_id, income_level FROM dim_income_level"))
        income_map = {row.income_level: row.income_id for row in result}

        # 3. DIM_PAYS
        print("\nChargement dim_pays...")
        result = conn.execute(sa.text("SELECT region_id, region_name FROM dim_region"))
        region_map = {row.region_name.strip(): row.region_id for row in result}

        df_pays = df[['country_code','country_name','region','income_level']].drop_duplicates(subset=['country_code']).dropna(subset=['country_code']).copy()
        df_pays['region'] = df_pays['region'].str.strip()
        df_pays['region_id'] = df_pays['region'].map(region_map)
        df_pays['income_id'] = df_pays['income_level'].map(income_map)

        if not df_countries.empty:
            df_pays = df_pays.merge(df_countries[['country_code','capital','latitude','longitude']], on='country_code', how='left')
        else:
            df_pays['capital'] = None
            df_pays['latitude'] = None
            df_pays['longitude'] = None

        df_pays['latitude']  = pd.to_numeric(df_pays['latitude'],  errors='coerce')
        df_pays['longitude'] = pd.to_numeric(df_pays['longitude'], errors='coerce')
        df_pays['is_active'] = True

        df_pays[['country_code','country_name','region_id','income_id','capital','latitude','longitude','is_active']].to_sql(
            'dim_pays', conn, if_exists='append', index=False, method='multi')
        print(f"   OK {len(df_pays)} pays inseres")
        print(f"   Pays avec latitude  : {df_pays['latitude'].notna().sum()}")
        print(f"   Pays avec capital   : {df_pays['capital'].notna().sum()}")
        print(f"   Pays avec income_id : {df_pays['income_id'].notna().sum()}")

        # 4. FACT_INDICATEURS
        print("\nChargement fact_indicateurs...")
        fact_cols = ['country_code','year','gdp_per_capita','gdp_growth','inflation','population',
                     'gni_per_capita','unemployment_rate','life_expectancy','literacy_rate',
                     'happiness_score','social_support','life_expectancy_whr',
                     'freedom','generosity','corruption','positive_affect','negative_affect','attractivity_score']
        available = [c for c in fact_cols if c in df.columns]
        df_fact = df[available].dropna(subset=['country_code','year']).copy()

        df_fact['happiness_rank'] = df_fact.groupby('year')['happiness_score'].rank(
            ascending=False, method='min', na_option='bottom').astype(int)
        df_fact['data_source'] = 'WorldBank+WHR'

        total = 0
        for i in range(0, len(df_fact), 500):
            batch = df_fact.iloc[i:i+500]
            batch.to_sql('fact_indicateurs', conn, if_exists='append', index=False, method='multi')
            total += len(batch)
            print(f"   {total}/{len(df_fact)} lignes...", end='\r')
        print(f"\n   OK {total} lignes inserees")

    # VERIFICATION
    print("\n\n--- Verification finale ---")
    with engine.connect() as conn:
        for table in ['dim_region','dim_income_level','dim_pays','fact_indicateurs']:
            count = conn.execute(sa.text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"   {table:<25} -> {count} lignes")

        print("\n   NULL dans fact_indicateurs :")
        for col in ['happiness_score','gdp_per_capita','inflation','life_expectancy','attractivity_score','happiness_rank']:
            n = conn.execute(sa.text(f"SELECT COUNT(*) FROM fact_indicateurs WHERE {col} IS NULL")).scalar()
            status = "OK" if n == 0 else "!!"
            print(f"   {status} {col:<25} -> {n} NULL")

        print("\n   NULL dans dim_pays :")
        for col in ['region_id','income_id','latitude','capital']:
            n = conn.execute(sa.text(f"SELECT COUNT(*) FROM dim_pays WHERE {col} IS NULL")).scalar()
            status = "OK" if n == 0 else "!!"
            print(f"   {status} {col:<25} -> {n} NULL")

        print("\n   Top 5 pays les plus heureux (2020) :")
        result = conn.execute(sa.text("""
            SELECT p.country_name, f.happiness_score, f.happiness_rank, r.region_name, il.income_level
            FROM fact_indicateurs f
            JOIN dim_pays p ON f.country_code = p.country_code
            JOIN dim_region r ON p.region_id = r.region_id
            LEFT JOIN dim_income_level il ON p.income_id = il.income_id
            WHERE f.year = 2020 AND f.happiness_score IS NOT NULL
            ORDER BY f.happiness_rank LIMIT 5
        """))
        for row in result:
            print(f"     #{row.happiness_rank} {row.country_name:<25} score={row.happiness_score:.3f} | {row.income_level}")

    print(f"\n{'='*60}")
    print("CHARGEMENT TERMINE — BASE 100% PROPRE !")
    print(f"{'='*60}")

if __name__ == '__main__':
    load_data()