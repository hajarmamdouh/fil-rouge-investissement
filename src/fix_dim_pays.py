"""
Correction dim_pays : capital, latitude, longitude
"""
import pandas as pd
import sqlalchemy as sa

engine = sa.create_engine('postgresql+psycopg2://postgres:123456@localhost:5432/projet_pays')

df = pd.read_csv(r'C:\Users\Amine Mamdouh\Desktop\fil-rouge-investissement-main\data\raw\countries.csv')
df['latitude']  = pd.to_numeric(df['latitude'],  errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
df['capital']   = df['capital'].str.strip()

print(f"Pays avec capital  : {df['capital'].notna().sum()}")
print(f"Pays avec latitude : {df['latitude'].notna().sum()}")

with engine.begin() as conn:
    for _, row in df.iterrows():
        conn.execute(sa.text("""
            UPDATE dim_pays
            SET capital   = :capital,
                latitude  = :latitude,
                longitude = :longitude
            WHERE country_code = :code
        """), {
            'capital':   row['capital']   if pd.notna(row['capital'])   else None,
            'latitude':  float(row['latitude'])  if pd.notna(row['latitude'])  else None,
            'longitude': float(row['longitude']) if pd.notna(row['longitude']) else None,
            'code':      row['country_code']
        })

with engine.connect() as conn:
    r1 = conn.execute(sa.text("SELECT COUNT(*) FROM dim_pays WHERE capital IS NOT NULL")).scalar()
    r2 = conn.execute(sa.text("SELECT COUNT(*) FROM dim_pays WHERE latitude IS NOT NULL")).scalar()
    r3 = conn.execute(sa.text("SELECT COUNT(*) FROM dim_pays WHERE income_id IS NOT NULL")).scalar()
    print(f"\nResultat dans la base :")
    print(f"  Pays avec capital   : {r1}")
    print(f"  Pays avec latitude  : {r2}")
    print(f"  Pays avec income_id : {r3}")
    print("\nOK dim_pays completement mis a jour !")