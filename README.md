
#  Analyse Comparative des Pays — Investissement & Qualité de Vie

**Formation :** Data Analyst - Simplon Maghreb  
**Étudiante :** Hajar Mamdouh  
**Formateur :** Yassine  
**Date :** Février 2026

---

##  Résumé du Projet

Ce projet analyse des données économiques, sociales et de qualité de vie de 150+ pays (2015-2024) pour aider les investisseurs, entreprises et particuliers à prendre des décisions éclairées sur l'investissement ou la mobilité internationale.

**Problématique :** Comment exploiter efficacement des données open data pour comparer objectivement les pays et fournir un support décisionnel clair ?

---

##  Structure du Projet

```
projet-fil-rouge/
├── data/
│   ├── raw/                    ← Données brutes (API + fichiers téléchargés)
│   │   ├── happiness/          ←  csv whr
│   │   ├── worldbank_merged.csv
│   │   └── happiness_all_years.csv
│   ├── processed/              ← Données nettoyées intermédiaires
│   └── final/
│       ├── master_dataset.csv          ← Dataset maître
│       └── master_with_clusters.csv   ← Avec segmentation K-Means
├── notebooks/
│   ├── 01_eda_analyse.py       ← EDA + corrélations + KPI
│   └── 02_clustering.py        ← K-Means + PCA + radar
├── sql/
│   └── schema.sql              ← Schéma PostgreSQL (étoile)
├── src/
│   ├── 01_collecte_worldbank.py   ← ETL World Bank API
│   ├── 02_collecte_happiness.py   ← Fusion WHR CSV
│   ├── 03_nettoyage_fusion.py     ← Nettoyage + merge + score attractivité
│   └── 04_chargement_postgresql.py ← Chargement BDD
├── reports/
│   └── plots/                  ← Graphiques générés automatiquement
├── requirements.txt
└── README.md
```

---

##  Guide d'Exécution — Étape par Étape

### Pré-requis

```bash
# Installer les dépendances
pip install -r requirements.txt

# Créer la base de données PostgreSQL
createdb projet_pays
```

---

### ÉTAPE 1 — Collecter les données World Bank

```bash
python src/01_collecte_worldbank.py
```

 Crée : `data/raw/worldbank_merged.csv`  
Contient : PIB/hab, croissance, inflation, population, RNB, chômage, espérance de vie, alphabétisation

---

### ÉTAPE 2 — Télécharger le World Happiness Report

**Action manuelle requise :**

1. Va sur 👉 **https://worldhappiness.report/data/**
2. Clique sur **"Download Data"** pour chaque année de 2015 à 2024
3. Place tous les fichiers téléchargés dans : `data/raw/happiness/`
4. Lance le script :

```bash
python src/02_collecte_happiness.py
```

 Crée : `data/raw/happiness_all_years.csv`  
Contient : score bonheur, PIB log, soutien social, espérance de vie, liberté, générosité, corruption

---

### ÉTAPE 3 — Nettoyer et fusionner les données

```bash
python src/03_nettoyage_fusion.py
```

 Crée : `data/final/master_dataset.csv`  
Actions : mapping ISO3, suppression doublons, traitement NaN, calcul score d'attractivité

---

### ÉTAPE 4 — Charger dans PostgreSQL

Avant de lancer, modifie `src/04_chargement_postgresql.py` :
```python
DB_CONFIG = {
    'user':     'ton_user',
    'password': 'ton_mdp',
    ...
}
```

Puis crée le schéma et charge les données :
```bash
psql -d projet_pays -f sql/schema.sql
python src/04_chargement_postgresql.py
```

 Tables créées : `dim_pays`, `dim_region`, `dim_annee`, `fact_indicateurs`  
 Vues créées : `v_top_pays_bonheur`, `v_evolution_temporelle`, `v_stats_region`, `v_matrice_pib_bonheur`

---

### ÉTAPE 5 — EDA & Analyses Statistiques

```bash
jupyter notebook
# Ouvrir notebooks/01_eda_analyse.py
```

Ou convertir en .ipynb :
```bash
jupytext --to notebook notebooks/01_eda_analyse.py
jupyter notebook notebooks/01_eda_analyse.ipynb
```

✅ Génère 8 graphiques dans `reports/plots/`

---

### ÉTAPE 6 — Clustering & Segmentation

```bash
# Ouvrir notebooks/02_clustering.py dans Jupyter
```

 Crée : `data/final/master_with_clusters.csv`  
 Génère 3 graphiques supplémentaires

---

### ÉTAPE 7 — Dashboard Power BI

1. Ouvre **Power BI Desktop**
2. **Obtenir les données** → **PostgreSQL** → `localhost:5432/projet_pays`
3. Importer les tables : `dim_pays`, `dim_region`, `fact_indicateurs` + toutes les vues
4. Ou importer directement : `data/final/master_with_clusters.csv`

**Pages recommandées du dashboard :**
-  Carte mondiale (choroplèthe happiness_score)
-  Top pays (bar chart attractivity_score)
-  Évolution temporelle par région
-  Corrélations PIB / Bonheur (scatter)
-  Clusters (scatter PCA coloré)
-  Comparateur de pays (slicers)

---

##  Sources de Données

| Source | Données | Lien |
|--------|---------|------|
| World Bank API | PIB, inflation, croissance, population, RNB | https://data.worldbank.org |
| World Happiness Report | Score bonheur, liberté, corruption, soutien social | https://worldhappiness.report/data/ |
| Numbeo (optionnel) | Coût de la vie, pouvoir d'achat | https://www.numbeo.com/cost-of-living/ |

**Période :** 2015–2024 | **Volume :** ~150–200 pays

---

##  KPI Principaux

| KPI | Description |
|-----|-------------|
| `happiness_score` | Score Cantril Ladder (0-10) — indicateur principal |
| `gdp_per_capita` | PIB par habitant en USD |
| `gdp_growth` | Croissance économique annuelle (%) |
| `inflation` | Taux d'inflation (%) |
| `social_support` | Soutien social perçu (0-1) |
| `freedom` | Liberté de faire des choix (0-1) |
| `corruption` | Perception corruption (0=peu, 1=très) |
| `life_expectancy` | Espérance de vie (années) |
| `attractivity_score` | Score composite normalisé (0-1) |
| `cluster_label` | Groupe K-Means du pays |

---

##  Limites du Projet

- Données agrégées au niveau national (pas régional)
- Variabilité méthodologique entre années (WHR)
- Certains pays ont peu de données disponibles
- Numbeo non intégré par défaut (données payantes)

---

##  Livrables

- [x] Scripts ETL (src/)
- [x] Schéma PostgreSQL (sql/)
- [x] Notebooks EDA + Clustering
- [ ] Dashboard Power BI (powerbi/)
- [ ] Rapport analytique (15-25 pages)
- [ ] Présentation PPTX (15-20 slides)
