"""
Récupération chômage via API World Bank directe avec codes ISO3
"""
import requests
import pandas as pd
import sqlalchemy as sa

engine = sa.create_engine('postgresql+psycopg2://postgres:123456@localhost:5432/projet_pays')

# Récupérer les codes ISO3 existants dans la base
with engine.connect() as conn:
    result = conn.execute(sa.text("SELECT DISTINCT country_code FROM fact_indicateurs"))
    codes = [r[0] for r in result.fetchall()]

print(f"Pays dans la base : {len(codes)}")

rows = []
for year in range(2015, 2025):
    url = f"https://api.worldbank.org/v2/country/all/indicator/SL.UEM.TOTL.ZS?date={year}&format=json&per_page=500"
    try:
        r = requests.get(url, timeout=30)
        data = r.json()
        if len(data) > 1 and data[1]:
            for item in data[1]:
                iso3 = item.get('countryiso3code', '')
                val = item.get('value')
                if val is not None and iso3 in codes:
                    rows.append({
                        'country_code': iso3,
                        'year': year,
                        'unemployment_rate': float(val)
                    })
        count = len([x for x in rows if x['year'] == year])
        print(f"  {year} : {count} pays récupérés")
    except Exception as ex:
        print(f"  {year} erreur: {ex}")

df = pd.DataFrame(rows)
print(f"\nTotal : {len(df)} lignes")
print(df.head(10))

if len(df) > 0:
    print("\nMise à jour PostgreSQL...")
    with engine.begin() as conn:
        updated = 0
        for _, row in df.iterrows():
            result = conn.execute(sa.text("""
                UPDATE fact_indicateurs
                SET unemployment_rate = :val
                WHERE country_code = :code AND year = :year
            """), {
                'val': row['unemployment_rate'],
                'code': row['country_code'],
                'year': int(row['year'])
            })
            updated += result.rowcount
        print(f"Lignes mises à jour : {updated}")

    with engine.connect() as conn:
        r = conn.execute(sa.text("""
            SELECT COUNT(*) FROM fact_indicateurs
            WHERE unemployment_rate IS NOT NULL
        """)).scalar()
        print(f"Pays avec chômage : {r}")
        
        top5 = conn.execute(sa.text("""
            SELECT country_code, year, unemployment_rate
            FROM fact_indicateurs
            WHERE unemployment_rate IS NOT NULL
            LIMIT 5
        """)).fetchall()
        print("Exemples :")
        for row in top5:
            print(f"  {row[0]} {row[1]} : {row[2]:.1f}%")

    print("\nOK TERMINE !")