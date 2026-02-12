---
title: "Analyse Comparative des Pays"
author: "MAMDOUH HAJAR"
date: "2026"
output: github_document
---

# Projet Fil Rouge – Data Analyst

##  Description du projet

Ce projet a pour objectif d’analyser et comparer les pays du monde selon des indicateurs économiques et sociaux afin d’évaluer leur attractivité et leur niveau de qualité de vie.

L’analyse couvre l’ensemble du cycle de vie de la donnée :
- Cadrage du besoin
- Collecte multi-sources
- Nettoyage et transformation
- Analyse statistique
- Visualisation
- Restitution décisionnelle

---

#  Objectifs

## Objectifs métier

- Identifier les pays les plus attractifs.
- Comparer les pays selon leur richesse et leur qualité de vie.
- Fournir un support décisionnel clair via un dashboard interactif.

## Objectifs analytiques

- Étudier les corrélations entre indicateurs économiques et bien-être.
- Segmenter les pays selon leur niveau d’attractivité.
- Construire un score global comparatif.

## Objectifs techniques

- Mettre en place un pipeline ETL automatisé.
- Structurer les données dans une base relationnelle.
- Développer un dashboard Power BI.
- Assurer la reproductibilité des analyses.

---

#  Sources de données

- World Happiness Report
- World Bank Open Data
- Numbeo (Cost of Living)
- Fichiers CSV complémentaires

Période couverte : 2015–2025  
Nombre de pays : environ 200  

---

#  Architecture du projet

## 1. Extraction
- Appels API
- Import CSV
- Scripts automatisés

## 2. Transformation
- Nettoyage des données
- Gestion des valeurs manquantes
- Normalisation
- Calcul des indicateurs

## 3. Chargement
- Base de données SQL
- Structuration des tables analytiques

## 4. Visualisation
- Dashboard interactif
- KPI économiques et sociaux
- Score d’attractivité global

---

#  Indicateurs clés (KPI)

- PIB par habitant
- Inflation annuelle
- Croissance économique
- Indice de bonheur
- Coût de la vie
- Pouvoir d’achat
- Score global d’attractivité

---

#  Technologies utilisées

## Langages

- Python 3.10+
- SQL

## Librairies

- Pandas
- NumPy
- Matplotlib
- Seaborn


## Outils

- Jupyter Notebook
- PostgreSQL
- Power BI
- Git & GitHub


---

