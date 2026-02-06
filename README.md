# Annotation for RNAexplorer

Pipeline d'annotation pour les sorties FRASER2 et OUTRIDER avec intégration GTF, PanelApp et gnomAD.

## 🚀 Installation

### Prérequis

- Python 3.8+
- Git

### Installation via Git

```bash
# Cloner le repository
git clone https://github.com/votre-username/annotation_for_RNAexplorer.git
cd annotation_for_RNAexplorer

# Installer les dépendances
pip install -r requirements.txt
```

## 📋 Formats de fichiers requis

### 1. Fichier d'échantillons (samples.txt)
Un identifiant d'échantillon par ligne :
```
23D1192
24D1028.HOL.Hay.PUROMOINS
25D2089.LEC.Loa.STEMC.PUROMOINS
```

### 2. Sortie FRASER2
Format tabulé avec colonnes obligatoires :
- `sampleID` : identifiant échantillon
- `hgncSymbol` : symbole du gène
- `seqnames`, `start`, `end` : positions chromosomiques
- `pValue`, `padjust` : valeurs statistiques

### 3. Sortie OUTRIDER
Format tabulé avec colonnes obligatoires :
- `sampleID` : identifiant échantillon
- `geneID` : identifiant Ensembl du gène
- `pValue`, `padjust`, `zScore`, `l2fc` : valeurs statistiques

### 4. Fichier GTF
Format GTF standard (GENCODE, Ensembl, etc.)

### 5. PanelApp (optionnel)
Format tabulé avec colonnes suggérées :
- `gene_symbol` : symbole du gène
- `panel_name` : nom du panel
- `confidence_level` : niveau de confiance
- `mode_of_inheritance` : mode d'hérédité

### 6. gnomAD (optionnel)
Format tabulé avec colonnes suggérées :
- `gene` : symbole ou ID du gène
- `pLI` : probability of Loss-of-function Intolerance
- `oe_lof_upper` : observed/expected LoF ratio
- `constraint_flag` : drapeau de contrainte

## 🔧 Utilisation

### Option 1 : Analyse depuis un ZIP (RECOMMANDÉ)

Si vous avez un ZIP contenant vos fichiers FRASER et OUTRIDER :

```bash
# Auto-détection des fichiers
python analyze_from_zip.py \
  --zip results.zip \
  --samples samples.txt \
  --gtf /path/to/genes.gtf \
  --output results/

# Mode interactif si l'auto-détection échoue
python analyze_from_zip.py \
  --zip results.zip \
  --samples samples.txt \
  --gtf /path/to/genes.gtf \
  --output results/ \
  --interactive
```

### Option 2 : Analyse avec chemins directs

Si vos fichiers sont déjà extraits :

```bash
python rnaseq_analysis.py \
  --fraser /path/to/fraser.tab \
  --outrider /path/to/outrider.tab \
  --samples /path/to/samples.txt \
  --gtf /path/to/genes.gtf \
  --output /path/to/output/
```

### Commande complète avec toutes les annotations

```bash
# Échantillons spécifiques avec filtrage p-value
python rnaseq_analysis.py \
  --fraser /datawork/genetique/RNASeq/diag/prod/20260108_RUN45_NextSeq_High_16RNASEQ/pipeline_v0/fraser/fraser.tab \
  --outrider /datawork/genetique/RNASeq/diag/prod/20260108_RUN45_NextSeq_High_16RNASEQ/pipeline_v0/outrider/outrider_htseq.tab \
  --samples samples.txt \
  --gtf /path/to/gencode.v44.annotation.gtf \
  --panelapp /path/to/panelapp.tsv \
  --gnomad /path/to/gnomad_constraints.tsv \
  --output results/ \
  --mode samples \
  --pvalue 0.01 \
  --verbose

# TOUS les échantillons avec filtrage
python rnaseq_analysis.py \
  --fraser fraser.tab \
  --outrider outrider.tab \
  --gtf genes.gtf \
  --gnomad gnomad.tsv \
  --output results_all/ \
  --mode all \
  --pvalue 0.05 \
  --verbose
```

### Options

**Arguments requis** :
- `--fraser` : Fichier FRASER2 (requis)
- `--outrider` : Fichier OUTRIDER (requis)
- `--gtf` : Fichier GTF d'annotation (requis)
- `--output` : Répertoire de sortie (requis)

**Mode de traitement** :
- `--mode` : `samples` (défaut) ou `all`
  - `samples` : Traite uniquement les échantillons listés (requiert `--samples`)
  - `all` : Traite TOUS les échantillons du fichier
- `--samples` : Liste d'échantillons (requis si `--mode samples`)

**Filtrage** :
- `--pvalue` : Seuil de p-value ajustée (ex: `0.05`, `0.01`)

**Annotations** :
- `--panelapp` : Fichier d'annotation PanelApp (optionnel)
- `--gnomad` : Fichier de contraintes gnomAD avec pLI (optionnel)

**Autres** :
- `--verbose` : Mode verbeux pour plus de logs

## 📊 Sorties

Le pipeline génère deux fichiers annotés dans le répertoire de sortie :

1. **fraser_annotated.tsv** : Données FRASER filtrées et annotées
2. **outrider_annotated.tsv** : Données OUTRIDER filtrées et annotées

### Colonnes ajoutées

#### Pour FRASER :
- `chrom` : Chromosome
- `gene_id` : Identifiant Ensembl (depuis GTF)
- `gene_type` : Type de gène (depuis GTF)
- Colonnes PanelApp (si fourni)
- Colonnes gnomAD (si fourni)

#### Pour OUTRIDER :
- `gene_name` : Symbole du gène (depuis GTF)
- `chrom`, `start`, `end`, `strand` : Positions chromosomiques (depuis GTF)
- `gene_type` : Type de gène (depuis GTF)
- Colonnes PanelApp (si fourni)
- Colonnes gnomAD (si fourni)

## 🔍 Exemple de workflow complet

### 1. Préparer la liste d'échantillons

```bash
# Créer un fichier avec les échantillons d'intérêt
echo "23D1192" > samples.txt
echo "24D1028.HOL.Hay.PUROMOINS" >> samples.txt
echo "25D2089.LEC.Loa.STEMC.PUROMOINS" >> samples.txt
```

### 2. Télécharger les fichiers d'annotation (si nécessaire)

```bash
# Télécharger GTF GENCODE
wget https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.annotation.gtf.gz
gunzip gencode.v44.annotation.gtf.gz

# Télécharger gnomAD constraints
wget https://storage.googleapis.com/gcp-public-data--gnomad/release/2.1.1/constraint/gnomad.v2.1.1.lof_metrics.by_gene.txt.bgz
gunzip gnomad.v2.1.1.lof_metrics.by_gene.txt.bgz
```

### 3. Exécuter le pipeline

```bash
python rnaseq_analysis.py \
  --fraser fraser.tab \
  --outrider outrider_htseq.tab \
  --samples samples.txt \
  --gtf gencode.v44.annotation.gtf \
  --gnomad gnomad.v2.1.1.lof_metrics.by_gene.txt \
  --output results/
```

### 4. Analyser les résultats

```bash
# Voir les premières lignes
head results/fraser_annotated.tsv
head results/outrider_annotated.tsv

# Compter les variants par échantillon
cut -f6 results/fraser_annotated.tsv | sort | uniq -c

# Filtrer par p-value ajustée
awk -F'\t' '$10 < 0.05' results/fraser_annotated.tsv > results/fraser_significant.tsv
```

## 🛠️ Scripts utilitaires

### Télécharger les données PanelApp

```bash
# Script pour télécharger les panels PanelApp
python scripts/download_panelapp.py --output panelapp_data/
```

### Filtrer les variants

```bash
# Filtrer les résultats
python scripts/filter_variants.py \
  --input results/fraser_annotated.tsv \
  --output results/ \
  --prioritize
```

## 📝 Notes importantes

1. **Performance** : Pour les gros fichiers GTF, le chargement peut prendre quelques minutes
2. **Mémoire** : Prévoir au moins 4 GB de RAM pour les analyses complètes
3. **Formats** : Les fichiers doivent être tabulés (séparateur : tabulation)
4. **Encodage** : UTF-8 recommandé pour tous les fichiers

## 🐛 Dépannage

### Erreur "Sample not found"
Vérifiez que les identifiants dans samples.txt correspondent exactement à ceux dans les fichiers FRASER/OUTRIDER.

### Erreur de parsing GTF
Assurez-vous d'utiliser un fichier GTF standard (GENCODE ou Ensembl). Les fichiers GFF3 ne sont pas supportés.

### Problème de mémoire
Réduisez le nombre d'échantillons traités en une seule fois, ou augmentez la RAM disponible.

## 📧 Support

Pour toute question ou problème, ouvrez une issue sur GitHub.

## 📄 Licence

MIT License

## 🙏 Remerciements

Ce pipeline utilise les outils et bases de données suivants :
- FRASER2 pour l'analyse de splicing
- OUTRIDER pour l'analyse d'expression différentielle
- PanelApp pour les panels de gènes
- gnomAD pour les contraintes génétiques
- GENCODE/Ensembl pour les annotations génomiques
