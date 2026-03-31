# Projet Fil Rouge — Analyse Comparative des Pays pour l'Investissement et la Qualite de Vie



---

## Auteure

**Hajar Mamdouh** — Formation Data Analyst — Simplon Maghreb — Promotion 2025-2026

---

## Description

Pipeline de data analyse complet permettant de comparer **169 pays** selon leurs indicateurs economiques, sociaux et de qualite de vie sur **10 ans (2015-2024)**. Le projet repond a la question : **Comment identifier objectivement les pays les plus attractifs pour investir ou s'installer ?**

---

## Liens du Projet

| Ressource | Lien |
|-----------|------|
| Jira (Kanban) | https://mamdouhhajar66.atlassian.net/jira/software/projects/ACDPPLELQD/boards/34 |
| Confluence (Documentation) | https://mamdouhhajar66-1771237842656.atlassian.net/wiki/x/yAAH |
| Cahier des charges | https://github.com/hajarmamdouh/fil-rouge-investissement/blob/main/cahier%20des%20charges.pdf |

---

## Resultats Cles

| Indicateur | Valeur |
|------------|--------|
| Pays analyses | 169 pays |
| Periode couverte | 2015 – 2024 (10 ans) |
| Lignes en base de donnees | 1 222 lignes |
| Indicateurs par pays/annee | 21 indicateurs |
| Pays le plus heureux | Finland (7,84/10) |
| PIB moyen mondial | 18 053 USD/habitant |
| Score attractivite moyen | 0,53 / 1,00 |
| Impact Covid sur bonheur | +0,11 (leger mieux post-Covid) |

---

## Architecture du Projet

```
fil-rouge-investissement/
├── src/                              # Scripts Python ETL
│   ├── 01_collecte_worldbank.py      # Collecte API World Bank
│   ├── 02_collecte_happiness.py      # Collecte World Happiness Report
│   ├── 03_nettoyage_fusion.py        # Nettoyage, fusion, score attractivite
│   ├── 04_chargement_postgresql.py   # Chargement base de donnees
│   ├── 05_traitement_null.py         # Traitement valeurs manquantes (5 methodes)
│   ├── fix_unemployment2.py          # Correction taux de chomage
│   ├── fix_dim_pays.py               # Correction dim_pays (capital, coordonnees)
│   └── collecte_cout_vie.py          # Collecte cout de la vie (Numbeo)
│
├── notebooks/                        # Analyses Jupyter
│   ├── 00_eda_exploration_brute.ipynb  # EDA avant nettoyage
│   ├── 01_eda_analyse.ipynb            # EDA apres nettoyage
│   ├── 02_clustering.ipynb             # K-Means + PCA
│   └── 03_statistiques.ipynb           # Tests ANOVA, Pearson, Shapiro
│
├── data/
│   ├── raw/                          # Donnees brutes collectees
│   │   ├── worldbank_merged.csv      # Donnees World Bank fusionnees
│   │   ├── happiness_all_years.csv   # WHR 2015-2021
│   │   └── countries.csv             # Referentiel pays (capital, GPS)
│   └── final/
│       ├── master_clean.csv          # Donnees nettoyees (0 NULL)
│       └── master_with_clusters.csv  # Donnees avec clustering K-Means
│
├── reports/
│   └── plots/                        # Graphiques generes par les notebooks
│       ├── 00_heatmap_valeurs_manquantes.png
│       ├── 00_distributions_brutes.png
│       ├── 00_couverture_temporelle.png
│       ├── 09_elbow_silhouette.png
│       ├── 10_clustering_pca.png
│       ├── anova_bonheur_region.png
│       ├── correlation_pib_bonheur.png
│       └── matrice_correlations_spearman.png
│
├── sql/
│   ├── schema.sql                    # Schema de base
│   └── schema_pro.sql                # Schema professionnel final (vues incluses)
│
├── cahier_des_charges.pdf            # Cahier des charges valide
└── README.md                         # Ce fichier
```

---

## Pipeline ETL

```
World Bank API          World Happiness Report
      |                         |
01_collecte_worldbank.py   02_collecte_happiness.py
      |                         |
      └──────────┬──────────────┘
                 |
        03_nettoyage_fusion.py
        (mapping ISO3, fusion, score attractivite)
                 |
        05_traitement_null.py
        (5 methodes : interpolation, fill, mediane)
                 |
        04_chargement_postgresql.py
        (schema en etoile : 1 fact + 4 dimensions + 4 vues)
                 |
            Power BI Desktop
        (4 pages : Investisseurs, Qualite Vie, RH, Analyses)
```

---

## Schema en Etoile PostgreSQL

```
         dim_pays (169)          dim_annee (10)
              |                       |
          1   |   *               *   |   1
              └───────┬───────────────┘
                      |
               fact_indicateurs
                  (1 222 lignes)
                      |
          *   |   1               1   |   *
              |                       |
         dim_region (7)     dim_income_level (5)
```

**Vues analytiques creees :**
- `v_analyse_complete` — Vue principale toutes tables jointes
- `v_matrice_pib_bonheur` — Focus PIB vs Bonheur avec categories
- `v_evolution_temporelle` — Variations et tendances annuelles
- `v_stats_region` — Agregats par region geographique

---

## Dashboard Power BI — 4 Pages

| Page | Titre | Objectif | Visuels cles |
|------|-------|----------|--------------|
| 1 | Tableau de Bord Investisseurs | Identifier pays attractifs economiquement | KPI PIB, Top 10 attractivite, Carte mondiale, Scatter PIB/croissance |
| 2 | Qualite de Vie et Bonheur | Choisir pays pour s'installer | KPI bonheur, Top 15 heureux, Scatter liberte/bonheur, Carte mondiale |
| 3 | Mobilite Internationale RH | Comparer pays pour mobilite employes | KPI RH, Donut niveaux revenu, Courbes chomage, Tableau comparatif |
| 4 | Analyses Statistiques | Explorer correlations et tendances | Impact Covid, Scatter PIB/bonheur, Treemap population, Cascade regions |

---

## Analyse Statistique

| Test | Objectif |
|------|----------|
| Shapiro-Wilk | Tester la normalite des distributions |
| ANOVA une voie | Comparer bonheur moyen par region |
| Kruskal-Wallis | Comparer bonheur par niveau de revenu (non parametrique) |
| Pearson | Correlation entre PIB log et score de bonheur |
| Test T | Comparer bonheur pre-Covid vs post-Covid |

---

## Machine Learning — Clustering K-Means

- **Variables** : 8 indicateurs (PIB, bonheur, esperance vie, liberte, corruption, soutien social, inflation, croissance)
- **Methode de choix k** : Elbow + score Silhouette
- **k optimal** : k=2 (Silhouette=0,37) force a k=4 pour granularite analytique
- **Visualisation** : PCA 2D (PC1=53,2% + PC2=18,0% = 71,2% variance expliquee)

**Description des clusters :**
- Cluster 0 — Pays tres attractifs (Finland, Denmark, Singapore...)
- Cluster 1 — Pays emergents dynamiques (China, Brazil, Mexico...)
- Cluster 2 — Pays en developpement (India, Vietnam, Ghana...)
- Cluster 3 — Pays en grande difficulte (Afghanistan, Burundi, Chad...)

---

## Installation et Utilisation

### Prerequis
```bash
pip install pandas numpy scikit-learn scipy matplotlib seaborn sqlalchemy wbdata requests beautifulsoup4 --break-system-packages
```

### Base de donnees PostgreSQL
```bash
# Creer la base
psql -U postgres -c "CREATE DATABASE projet_pays;"

# Executer le schema
psql -U postgres -d projet_pays -f sql/schema_pro.sql
```

### Execution du pipeline
```bash
# 1. Collecte
python src/01_collecte_worldbank.py
python src/02_collecte_happiness.py

# 2. Nettoyage
python src/03_nettoyage_fusion.py
python src/05_traitement_null.py

# 3. Chargement
python src/04_chargement_postgresql.py

# 4. Corrections
python src/fix_unemployment2.py
python src/fix_dim_pays.py
```

### Notebooks (ordre recommande)
```
00_eda_exploration_brute.ipynb  → EDA avant nettoyage
01_eda_analyse.ipynb            → EDA apres nettoyage
02_clustering.ipynb             → Clustering K-Means
03_statistiques.ipynb           → Tests statistiques
```

---

## Technologies

| Technologie | Version | Role |
|-------------|---------|------|
| Python | 3.14 | Scripts ETL et analyse |
| Pandas | 2.x | Manipulation donnees |
| Scikit-learn | 1.x | K-Means, PCA, MinMaxScaler |
| Scipy | 1.x | Tests statistiques |
| PostgreSQL | 18 | Base de donnees relationnelle |
| Power BI Desktop | Latest | Dashboard interactif |
| Git / GitHub | Latest | Versioning |
| Jira / Confluence | Cloud | Gestion projet / Documentation |

---

## Gestion de Projet

**Methode** : Kanban avec 6 Epics

| Epic | Titre | Statut |
|------|-------|--------|
| EPIC 1 | Collecte et Extraction des Donnees | Termine |
| EPIC 2 | EDA Exploration Brute | Termine |
| EPIC 3 | Nettoyage et Preparation | Termine |
| EPIC 4 | Analyse Statistique et Machine Learning | Termine |
| EPIC 5 | Dashboard Power BI | Termine |
| EPIC 6 | Documentation et Soutenance | En cours |

---

## Licence

Projet academique — Simplon Maghreb — 2025-2026
