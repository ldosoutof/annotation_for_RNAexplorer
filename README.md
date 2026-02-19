# RNA-Seq Analysis Pipeline — Per Sample Output

Pipeline Python de post-traitement des résultats **FRASER2** et **OUTRIDER** (aberrations d'épissage et d'expression), avec annotation automatique et sortie d'un fichier TSV par sample.

---

## Fonctionnalités

- **Auto-détection** des fichiers FRASER2 et OUTRIDER depuis une archive ZIP
- **Annotation multi-couches** : GTF GENCODE, gnomAD v2.1.1, Mendeliome Australia (PanelApp)
- **Téléchargement automatique** des fichiers de référence (avec gestion de version pour le Mendeliome)
- **Parallélisation hybride** :
  - Chargement des fichiers → `ThreadPoolExecutor` (I/O-bound)
  - Annotation + écriture par sample → `ProcessPoolExecutor` (CPU-bound, contourne le GIL)
- **Filtre sur p-value ajustée** configurable
- **Correspondance partielle** des noms de samples
- **Export ZIP** de l'ensemble des fichiers de sortie

---

## Structure du projet

```
.
├── rnaseq_analysis_per_sample.py   # Pipeline principal (classe RNASeqProcessorPerSample)
├── analyze_from_zip_per_sample.py  # Wrapper avec auto-détection ZIP et gestion des références
├── requirements.txt                # Dépendances Python
└── samples_example.txt             # Exemple de fichier de liste de samples
```

---

## Installation

### Prérequis

- Python **3.10+**
- `wget` (optionnel, utilisé pour les téléchargements de références, avec fallback urllib)

### Dépendances

```bash
pip install -r requirements.txt
```

```
pandas>=2.0.0
numpy>=1.24.0
```

---

## Utilisation

### Script principal (`rnaseq_analysis_per_sample.py`)

Usage direct avec des fichiers TSV déjà disponibles localement.

```bash
# Samples spécifiques depuis un fichier liste + génération d'un ZIP
python rnaseq_analysis_per_sample.py \
  --fraser fraser.tab \
  --outrider outrider.tab \
  --samples samples.txt \
  --gtf genes.gtf \
  --output results/

# Tous les samples, filtre p-value, 8 workers parallèles
python rnaseq_analysis_per_sample.py \
  --fraser fraser.tab \
  --outrider outrider.tab \
  --gtf genes.gtf \
  --output results/ \
  --mode all \
  --pvalue 0.05 \
  --workers 8

# Avec annotations gnomAD et Mendeliome
python rnaseq_analysis_per_sample.py \
  --fraser fraser.tab \
  --outrider outrider.tab \
  --samples samples.txt \
  --gtf genes.gtf \
  --gnomad gnomad.txt \
  --mendeliome references/mendeliome_australia.json \
  --partial-match \
  --output results/
```

#### Arguments

| Argument | Requis | Description |
|---|---|---|
| `--fraser` | Non* | Fichier FRASER2 (TSV) |
| `--outrider` | Non* | Fichier OUTRIDER (TSV) |
| `--gtf` | **Oui** | Fichier GTF GENCODE |
| `--output` | **Oui** | Dossier de sortie |
| `--mode` | Non | `samples` (défaut) ou `all` |
| `--samples` | Cond. | Fichier liste de samples (requis si `--mode samples`) |
| `--partial-match` | Non | Correspondance partielle des noms de samples |
| `--pvalue` | Non | Seuil de p-value ajustée (ex. `0.05`) |
| `--gnomad` | Non | Fichier gnomAD (TSV) |
| `--mendeliome` | Non | Fichier Mendeliome (JSON) |
| `--no-zip` | Non | Désactive la création de l'archive ZIP de sortie |
| `--workers` | Non | Nombre de process parallèles (défaut : CPU logiques, max 16) |
| `--verbose` | Non | Logging détaillé |

*Au moins `--fraser` ou `--outrider` est requis.

---

### Script avec auto-détection ZIP (`analyze_from_zip_per_sample.py`)

Extrait automatiquement les fichiers FRASER2/OUTRIDER d'une archive ZIP et télécharge les références si nécessaire.

```bash
# Télécharger / mettre à jour les références uniquement
python analyze_from_zip_per_sample.py --download-refs

# Traiter tous les samples, références auto-téléchargées
python analyze_from_zip_per_sample.py \
  --zip results.zip \
  --mode all \
  --output results/

# Samples spécifiques + correspondance partielle
python analyze_from_zip_per_sample.py \
  --zip results.zip \
  --samples samples.txt \
  --output results/ \
  --partial-match

# Références déjà présentes dans un dossier custom
python analyze_from_zip_per_sample.py \
  --zip results.zip \
  --mode all \
  --output results/ \
  --refs-dir /data/references

# Avec seuil p-value et parallélisation
python analyze_from_zip_per_sample.py \
  --zip results.zip \
  --samples samples.txt \
  --output results/ \
  --pvalue 0.05 \
  --workers 4

# Mode interactif (si auto-détection incomplète)
python analyze_from_zip_per_sample.py \
  --zip results.zip \
  --mode all \
  --output results/ \
  --interactive
```

#### Arguments supplémentaires

| Argument | Description |
|---|---|
| `--zip` | Archive ZIP contenant les fichiers FRASER2/OUTRIDER |
| `--download-refs` | Télécharger les références puis quitter |
| `--refs-dir` | Dossier des références (défaut : `./references`) |
| `--gtf` | Chemin GTF custom (désactive le téléchargement auto) |
| `--gnomad` | Chemin gnomAD custom (désactive le téléchargement auto) |
| `--mendeliome` | Chemin Mendeliome JSON custom (désactive le téléchargement auto) |
| `--interactive` | Sélection manuelle si la détection automatique échoue |

---

## Fichiers de référence

Téléchargés automatiquement dans `./references/` (ou le dossier spécifié via `--refs-dir`) :

| Fichier | Source | Taille |
|---|---|---|
| `gencode.v44.annotation.gtf` | [GENCODE v44](https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/) | ~50 MB (compressé) |
| `gnomad.v2.1.1.lof_metrics.by_gene.txt` | [gnomAD v2.1.1](https://gnomad.broadinstitute.org/) | ~2 MB |
| `mendeliome_australia.json` | [PanelApp Australia – Panel 137](https://panelapp-aus.org/api/v1/panels/137/) | variable |

> Le Mendeliome est automatiquement mis à jour si une nouvelle version est détectée sur PanelApp Australia.

---

## Format des fichiers d'entrée

### FRASER2 (TSV)

Colonnes requises : `sampleID`, `hgncSymbol`, `pValue`, `deltaPsi`

Colonnes attendues complètes : `seqnames`, `start`, `end`, `width`, `strand`, `sampleID`, `type`, `pValue`, `padjust`, `psiValue`, `deltaPsi`, `counts`, `totalCounts`, `meanCounts`, `meanTotalCounts`, `nonsplitCounts`, `nonsplitProportion`, `nonsplitProportion_99quantile`

### OUTRIDER (TSV)

Colonnes requises : `geneID`, `sampleID`, `zScore`, `pValue`

Colonnes attendues complètes : `geneID`, `sampleID`, `pValue`, `padjust`, `zScore`, `l2fc`, `rawcounts`, `meanRawcounts`, `normcounts`, `meanCorrected`, `theta`, `aberrant`, `AberrantBySample`, `AberrantByGene`, `padj_rank`

> Les fichiers OUTRIDER peuvent contenir une colonne d'index R (gérée automatiquement avec `index_col=0`).

### Fichier de liste de samples (`--samples`)

Un identifiant de sample par ligne :

```
SAMPLE001
SAMPLE002
SAMPLE003
```

---

## Format de sortie

Les fichiers sont générés dans `<output>/per_sample_files/`, un fichier par sample et par outil :

```
results/
├── per_sample_files/
│   ├── SAMPLE001.fraser.tab
│   ├── SAMPLE001.outrider.tab
│   ├── SAMPLE002.fraser.tab
│   └── ...
└── run_20240101_120000.zip    # Archive de tous les fichiers (si --no-zip non spécifié)
```

### Colonnes de sortie FRASER

`seqnames`, `start`, `end`, `width`, `strand`, `sampleID`, `type`, `pValue`, `padjust`, `psiValue`, `deltaPsi`, `counts`, `totalCounts`, `meanCounts`, `meanTotalCounts`, `nonsplitCounts`, `nonsplitProportion`, `nonsplitProportion_99quantile`, `gene_name`, `gene_id`, `chrom`, `pLI`, `oe_lof`, `lof_z`, `mis_z`, `Mode_Of_Inheritance`, `Phenotypes`

### Colonnes de sortie OUTRIDER

`gene_id`, `sampleID`, `pValue`, `padjust`, `zScore`, `l2fc`, `rawcounts`, `meanRawcounts`, `normcounts`, `meanCorrected`, `theta`, `aberrant`, `AberrantBySample`, `AberrantByGene`, `padj_rank`, `gene_name`, `chrom`, `start`, `end`, `strand`, `pLI`, `oe_lof`, `lof_z`, `mis_z`, `Mode_Of_Inheritance`, `Phenotypes`

---

## Architecture et parallélisation

```
┌─────────────────────────────────────────────────┐
│              Étape 1 — Chargement               │
│          ThreadPoolExecutor (I/O-bound)          │
│   GTF ──┐                                        │
│ gnomAD ─┼──▶ parallel threads ──▶ dicts pickle  │
│ Mendel ─┤                                        │
│ FRASER ─┤                                        │
│OUTRIDER ┘                                        │
└─────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────┐
│          Étape 2 — Traitement par sample         │
│         ProcessPoolExecutor (CPU-bound)          │
│  sample_1 ──▶ [worker process] ──▶ .tab file    │
│  sample_2 ──▶ [worker process] ──▶ .tab file    │
│  sample_N ──▶ [worker process] ──▶ .tab file    │
│  (FRASER et OUTRIDER traités en pools séparés)   │
└─────────────────────────────────────────────────┘
                         │
                         ▼
              ZIP de l'ensemble des fichiers
```

Les données de référence (GTF, gnomAD, Mendeliome) sont converties en dictionnaires Python sérialisables (`pickle`) avant d'être distribuées aux workers, évitant tout partage mémoire inter-process.

---

## Licence

Usage interne. Voir les conditions d'utilisation des bases de données de référence :
- [GENCODE](https://www.gencodegenes.org/pages/data_access.html)
- [gnomAD](https://gnomad.broadinstitute.org/terms)
- [PanelApp Australia](https://panelapp-aus.org/)
