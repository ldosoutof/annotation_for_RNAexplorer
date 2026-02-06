# ✅ Changement de Nom Effectué

## Nouveau Nom : **annotation_for_RNAexplorer**

Tous les fichiers ont été mis à jour avec le nouveau nom du projet.

---

## 📦 Ce qui a changé

### Répertoire
- ✅ `rnaseq-pipeline` → `annotation_for_RNAexplorer`

### Nom du Projet
- ✅ "RNA-Seq Analysis Pipeline" → "Annotation for RNAexplorer"
- ✅ Tous les fichiers de documentation
- ✅ Tous les scripts
- ✅ Tous les messages de commit

### URLs GitHub
- ✅ `github.com/USER/rnaseq-analysis-pipeline` → `github.com/USER/annotation_for_RNAexplorer`

---

## 🚀 Installation

```bash
# Cloner le repository
git clone https://github.com/YOUR-USERNAME/annotation_for_RNAexplorer.git
cd annotation_for_RNAexplorer

# Installer
bash setup.sh
```

---

## 📋 Fichiers du Projet

Tous les fichiers conservent leurs fonctionnalités, seuls les noms et références ont changé :

### Scripts Principaux
- `analyze_from_zip.py` - Auto-détection ZIP
- `rnaseq_analysis.py` - Pipeline d'annotation
- `test_pipeline.py` - Tests

### Scripts Utilitaires
- `scripts/filter_variants.py` - Filtrage
- `scripts/download_panelapp.py` - PanelApp

### Installation
- `setup.sh` - Installation automatique
- `git_setup.sh` - Configuration Git

### Documentation
- `README.md` - Documentation principale
- `README_GITHUB.md` - README pour GitHub
- `QUICKSTART.md` - Guide rapide
- `ADVANCED_USAGE.md` - Exemples avancés
- `ZIP_USAGE.md` - Guide ZIP
- `GIT_INTEGRATION.md` - Guide Git
- Et plus...

---

## 🎯 Utilisation

### Méthode 1 : Depuis ZIP (Recommandé)
```bash
python analyze_from_zip.py \
  --zip results.zip \
  --samples samples.txt \
  --gtf genes.gtf \
  --output results/
```

### Méthode 2 : Chemins Directs
```bash
python rnaseq_analysis.py \
  --fraser fraser.tab \
  --outrider outrider.tab \
  --samples samples.txt \
  --gtf genes.gtf \
  --output results/
```

---

## 📊 Description

**Annotation for RNAexplorer** est un pipeline d'annotation pour les sorties FRASER2 et OUTRIDER avec :

- 🔍 Auto-détection des fichiers depuis ZIP
- 🧬 Annotation GTF complète
- 🏥 Intégration PanelApp
- 📊 Contraintes gnomAD
- 🎯 Filtrage intelligent
- 📁 Export TSV
- 🚀 Mode interactif
- ✅ Tests intégrés

---

## 🔗 Documentation Complète

Consultez les fichiers suivants pour plus d'informations :

- **QUICKSTART.md** - Pour démarrer rapidement
- **README.md** - Documentation complète
- **GIT_INTEGRATION.md** - Pour intégrer à Git/GitHub
- **SUMMARY.md** - Vue d'ensemble du projet

---

## ✨ Prêt pour Git

```bash
# Configuration automatique
bash git_setup.sh

# Ou manuel
git init
git add .
git commit -m "Initial commit: Annotation for RNAexplorer"
git remote add origin https://github.com/YOUR-USERNAME/annotation_for_RNAexplorer.git
git push -u origin main
```

---

**Version** : 1.0.1  
**Nom** : annotation_for_RNAexplorer  
**Date** : Février 2026

Tous les fichiers sont maintenant à jour avec le nouveau nom ! 🎉
