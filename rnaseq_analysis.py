#!/usr/bin/env python3
"""
Annotation for RNAexplorer
Processes FRASER2 and OUTRIDER outputs with annotation from PanelApp, gnomAD, and GTF files
"""

import argparse
import pandas as pd
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RNASeqProcessor:
    """Process and annotate RNA-Seq analysis results"""
    
    def __init__(self, fraser_file, outrider_file, samples_file, gtf_file, 
                 output_dir, panelapp_file=None, gnomad_file=None,
                 annotate_all=False, annotate_pli=False,
                 filter_pvalue=None, filter_zscore=None, filter_deltapsi=None):
        self.fraser_file = Path(fraser_file)
        self.outrider_file = Path(outrider_file)
        self.samples_file = Path(samples_file) if samples_file else None
        self.gtf_file = Path(gtf_file)
        self.output_dir = Path(output_dir)
        self.panelapp_file = Path(panelapp_file) if panelapp_file else None
        self.gnomad_file = Path(gnomad_file) if gnomad_file else None
        
        # Options
        self.annotate_all = annotate_all
        self.annotate_pli = annotate_pli
        self.filter_pvalue = filter_pvalue
        self.filter_zscore = filter_zscore
        self.filter_deltapsi = filter_deltapsi
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load data
        self.samples = None
        self.fraser_data = None
        self.outrider_data = None
        self.gtf_data = None
        self.panelapp_data = None
        self.gnomad_data = None
    
    def load_samples(self):
        """Load sample list from file"""
        if self.annotate_all:
            logger.info("Mode: Annotating ALL samples (--annotate-all)")
            return None
        
        if not self.samples_file:
            logger.info("No sample list provided - will process all samples")
            return None
        
        logger.info(f"Loading samples from {self.samples_file}")
        with open(self.samples_file, 'r') as f:
            self.samples = [line.strip() for line in f if line.strip()]
        logger.info(f"Loaded {len(self.samples)} samples to filter")
        return self.samples
    
    def load_fraser(self):
        """Load FRASER2 data"""
        logger.info(f"Loading FRASER2 data from {self.fraser_file}")
        self.fraser_data = pd.read_csv(
            self.fraser_file, 
            sep='\t',
            low_memory=False
        )
        logger.info(f"Loaded {len(self.fraser_data)} FRASER2 records")
        return self.fraser_data
    
    def load_outrider(self):
        """Load OUTRIDER data"""
        logger.info(f"Loading OUTRIDER data from {self.outrider_file}")
        self.outrider_data = pd.read_csv(
            self.outrider_file,
            sep='\t',
            low_memory=False
        )
        logger.info(f"Loaded {len(self.outrider_data)} OUTRIDER records")
        return self.outrider_data
    
    def load_gtf(self):
        """Load GTF file and extract gene information"""
        logger.info(f"Loading GTF file from {self.gtf_file}")
        
        gtf_records = []
        with open(self.gtf_file, 'r') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                
                fields = line.strip().split('\t')
                if len(fields) < 9:
                    continue
                
                if fields[2] == 'gene':  # Only process gene features
                    chrom = fields[0]
                    start = int(fields[3])
                    end = int(fields[4])
                    strand = fields[6]
                    attributes = fields[8]
                    
                    # Parse attributes
                    attr_dict = {}
                    for attr in attributes.split(';'):
                        attr = attr.strip()
                        if attr:
                            parts = attr.split(' ', 1)
                            if len(parts) == 2:
                                key = parts[0]
                                value = parts[1].strip('"')
                                attr_dict[key] = value
                    
                    gtf_records.append({
                        'chrom': chrom,
                        'start': start,
                        'end': end,
                        'strand': strand,
                        'gene_id': attr_dict.get('gene_id', ''),
                        'gene_name': attr_dict.get('gene_name', ''),
                        'gene_type': attr_dict.get('gene_type', '')
                    })
        
        self.gtf_data = pd.DataFrame(gtf_records)
        logger.info(f"Loaded {len(self.gtf_data)} genes from GTF")
        return self.gtf_data
    
    def load_panelapp(self):
        """Load PanelApp annotation data"""
        if not self.panelapp_file or not self.panelapp_file.exists():
            logger.warning("PanelApp file not provided or doesn't exist")
            return None
        
        logger.info(f"Loading PanelApp data from {self.panelapp_file}")
        self.panelapp_data = pd.read_csv(
            self.panelapp_file,
            sep='\t',
            low_memory=False
        )
        logger.info(f"Loaded {len(self.panelapp_data)} PanelApp records")
        return self.panelapp_data
    
    def load_gnomad(self):
        """Load gnomAD constraint data"""
        if not self.gnomad_file or not self.gnomad_file.exists():
            if self.annotate_pli:
                logger.error("pLI annotation requested but gnomAD file not found!")
            else:
                logger.warning("gnomAD file not provided or doesn't exist")
            return None
        
        logger.info(f"Loading gnomAD data from {self.gnomad_file}")
        self.gnomad_data = pd.read_csv(
            self.gnomad_file,
            sep='\t',
            low_memory=False
        )
        logger.info(f"Loaded {len(self.gnomad_data)} gnomAD records")
        return self.gnomad_data
    
    def filter_samples_fraser(self):
        """Filter FRASER data by sample list"""
        if self.annotate_all or not self.samples:
            logger.info("Processing all FRASER samples")
            return self.fraser_data.copy()
        
        logger.info("Filtering FRASER data by samples")
        filtered = self.fraser_data[
            self.fraser_data['sampleID'].isin(self.samples)
        ].copy()
        logger.info(f"Filtered to {len(filtered)}/{len(self.fraser_data)} FRASER records")
        return filtered
    
    def filter_samples_outrider(self):
        """Filter OUTRIDER data by sample list"""
        if self.annotate_all or not self.samples:
            logger.info("Processing all OUTRIDER samples")
            return self.outrider_data.copy()
        
        logger.info("Filtering OUTRIDER data by samples")
        filtered = self.outrider_data[
            self.outrider_data['sampleID'].isin(self.samples)
        ].copy()
        logger.info(f"Filtered to {len(filtered)}/{len(self.outrider_data)} OUTRIDER records")
        return filtered
    
    def apply_pvalue_filter(self, data, dataset_name):
        """Apply p-value filtering if specified"""
        if self.filter_pvalue is None:
            return data
        
        logger.info(f"Filtering {dataset_name} by p-value < {self.filter_pvalue}")
        initial_count = len(data)
        filtered = data[data['padjust'] < self.filter_pvalue].copy()
        logger.info(f"Retained {len(filtered)}/{initial_count} records after p-value filter")
        return filtered
    
    def apply_zscore_filter(self, data):
        """Apply z-score filtering for OUTRIDER"""
        if self.filter_zscore is None:
            return data
        
        logger.info(f"Filtering OUTRIDER by |z-score| > {self.filter_zscore}")
        initial_count = len(data)
        filtered = data[abs(data['zScore']) > self.filter_zscore].copy()
        logger.info(f"Retained {len(filtered)}/{initial_count} records after z-score filter")
        return filtered
    
    def apply_deltapsi_filter(self, data):
        """Apply deltaPsi filtering for FRASER"""
        if self.filter_deltapsi is None:
            return data
        
        logger.info(f"Filtering FRASER by |deltaPsi| > {self.filter_deltapsi}")
        initial_count = len(data)
        filtered = data[abs(data['deltaPsi']) > self.filter_deltapsi].copy()
        logger.info(f"Retained {len(filtered)}/{initial_count} records after deltaPsi filter")
        return filtered
    
    def annotate_fraser_with_gtf(self, fraser_filtered):
        """Annotate FRASER data with GTF information"""
        logger.info("Annotating FRASER data with GTF")
        
        # FRASER already has chromosome positions, just add gene_id if available
        if self.gtf_data is not None:
            fraser_annotated = fraser_filtered.merge(
                self.gtf_data[['gene_name', 'gene_id', 'gene_type']],
                left_on='hgncSymbol',
                right_on='gene_name',
                how='left'
            )
            # Rename seqnames to chrom for consistency
            fraser_annotated['chrom'] = fraser_annotated['seqnames']
        else:
            fraser_annotated = fraser_filtered.copy()
            fraser_annotated['chrom'] = fraser_annotated['seqnames']
        
        return fraser_annotated
    
    def annotate_outrider_with_gtf(self, outrider_filtered):
        """Annotate OUTRIDER data with GTF information"""
        logger.info("Annotating OUTRIDER data with GTF")
        
        if self.gtf_data is not None:
            outrider_annotated = outrider_filtered.merge(
                self.gtf_data[['gene_id', 'gene_name', 'chrom', 'start', 'end', 'strand', 'gene_type']],
                left_on='geneID',
                right_on='gene_id',
                how='left'
            )
        else:
            outrider_annotated = outrider_filtered.copy()
            logger.warning("GTF data not available, skipping genomic position annotation")
        
        return outrider_annotated
    
    def annotate_with_panelapp(self, data, gene_column):
        """Annotate data with PanelApp information"""
        if self.panelapp_data is None:
            logger.warning("PanelApp data not available, skipping")
            return data
        
        logger.info("Annotating with PanelApp data")
        
        # Assuming PanelApp file has columns: gene_symbol, panel_name, confidence_level, mode_of_inheritance
        annotated = data.merge(
            self.panelapp_data,
            left_on=gene_column,
            right_on='gene_symbol',
            how='left'
        )
        
        return annotated
    
    def annotate_with_gnomad(self, data, gene_column):
        """Annotate data with gnomAD constraint metrics"""
        if self.gnomad_data is None:
            if self.annotate_pli:
                logger.warning("gnomAD data not available, cannot add pLI annotation")
            return data
        
        logger.info(f"Annotating with gnomAD constraint data (pLI={'enabled' if self.annotate_pli else 'all metrics'})")
        
        # Determine which columns to include
        if self.annotate_pli:
            # Only include pLI and essential columns
            gnomad_cols = ['gene', 'pLI']
            if 'oe_lof_upper' in self.gnomad_data.columns:
                gnomad_cols.append('oe_lof_upper')
        else:
            # Include all gnomAD columns
            gnomad_cols = self.gnomad_data.columns.tolist()
        
        annotated = data.merge(
            self.gnomad_data[gnomad_cols],
            left_on=gene_column,
            right_on='gene',
            how='left'
        )
        
        if self.annotate_pli and 'pLI' in annotated.columns:
            pli_count = annotated['pLI'].notna().sum()
            logger.info(f"Added pLI annotation for {pli_count}/{len(annotated)} records")
        
        return annotated
    
    def process_fraser(self):
        """Complete FRASER processing pipeline"""
        logger.info("=" * 60)
        logger.info("Processing FRASER data")
        logger.info("=" * 60)
        
        # Filter by samples
        fraser_filtered = self.filter_samples_fraser()
        
        # Apply p-value filter
        fraser_filtered = self.apply_pvalue_filter(fraser_filtered, "FRASER")
        
        # Apply deltaPsi filter
        fraser_filtered = self.apply_deltapsi_filter(fraser_filtered)
        
        # Annotate with GTF
        fraser_annotated = self.annotate_fraser_with_gtf(fraser_filtered)
        
        # Annotate with PanelApp
        fraser_annotated = self.annotate_with_panelapp(fraser_annotated, 'hgncSymbol')
        
        # Annotate with gnomAD
        fraser_annotated = self.annotate_with_gnomad(fraser_annotated, 'hgncSymbol')
        
        # Save results
        output_file = self.output_dir / "fraser_annotated.tsv"
        fraser_annotated.to_csv(output_file, sep='\t', index=False)
        logger.info(f"✓ Saved annotated FRASER results to {output_file}")
        logger.info(f"  Total records: {len(fraser_annotated)}")
        logger.info(f"  Unique samples: {fraser_annotated['sampleID'].nunique()}")
        logger.info(f"  Unique genes: {fraser_annotated['hgncSymbol'].nunique()}")
        
        return fraser_annotated
    
    def process_outrider(self):
        """Complete OUTRIDER processing pipeline"""
        logger.info("=" * 60)
        logger.info("Processing OUTRIDER data")
        logger.info("=" * 60)
        
        # Filter by samples
        outrider_filtered = self.filter_samples_outrider()
        
        # Apply p-value filter
        outrider_filtered = self.apply_pvalue_filter(outrider_filtered, "OUTRIDER")
        
        # Apply z-score filter
        outrider_filtered = self.apply_zscore_filter(outrider_filtered)
        
        # Annotate with GTF
        outrider_annotated = self.annotate_outrider_with_gtf(outrider_filtered)
        
        # Determine gene column (use gene_name if available from GTF, otherwise geneID)
        gene_col = 'gene_name' if 'gene_name' in outrider_annotated.columns else 'geneID'
        
        # Annotate with PanelApp
        outrider_annotated = self.annotate_with_panelapp(outrider_annotated, gene_col)
        
        # Annotate with gnomAD
        outrider_annotated = self.annotate_with_gnomad(outrider_annotated, gene_col)
        
        # Save results
        output_file = self.output_dir / "outrider_annotated.tsv"
        outrider_annotated.to_csv(output_file, sep='\t', index=False)
        logger.info(f"✓ Saved annotated OUTRIDER results to {output_file}")
        logger.info(f"  Total records: {len(outrider_annotated)}")
        logger.info(f"  Unique samples: {outrider_annotated['sampleID'].nunique()}")
        logger.info(f"  Unique genes: {outrider_annotated['geneID'].nunique()}")
        
        return outrider_annotated
    
    def run(self):
        """Run the complete pipeline"""
        logger.info("=" * 60)
        logger.info("Starting RNA-Seq analysis pipeline")
        logger.info("=" * 60)
        logger.info(f"Mode: {'Annotate ALL samples' if self.annotate_all else 'Filter by sample list'}")
        if self.filter_pvalue:
            logger.info(f"P-value filter: < {self.filter_pvalue}")
        if self.filter_zscore:
            logger.info(f"Z-score filter: |z| > {self.filter_zscore}")
        if self.filter_deltapsi:
            logger.info(f"DeltaPsi filter: |Δψ| > {self.filter_deltapsi}")
        if self.annotate_pli:
            logger.info("pLI annotation: ENABLED")
        logger.info("=" * 60)
        
        # Load all data
        self.load_samples()
        self.load_fraser()
        self.load_outrider()
        self.load_gtf()
        self.load_panelapp()
        self.load_gnomad()
        
        # Process both datasets
        fraser_results = self.process_fraser()
        outrider_results = self.process_outrider()
        
        logger.info("=" * 60)
        logger.info("✓ Pipeline completed successfully!")
        logger.info("=" * 60)
        
        return fraser_results, outrider_results


def main():
    parser = argparse.ArgumentParser(
        description='Annotation for RNAexplorer: Process FRASER2 and OUTRIDER outputs with annotations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Annotate only specific samples
  %(prog)s --fraser fraser.tab --outrider outrider.tab --samples samples.txt --gtf genes.gtf --output results/
  
  # Annotate ALL samples in the files
  %(prog)s --fraser fraser.tab --outrider outrider.tab --gtf genes.gtf --output results/ --annotate-all
  
  # With pLI annotation and p-value filtering
  %(prog)s --fraser fraser.tab --outrider outrider.tab --samples samples.txt \
           --gtf genes.gtf --gnomad gnomad.tsv --annotate-pli --filter-pvalue 0.05 --output results/
  
  # Complete annotation with all options
  %(prog)s --fraser fraser.tab --outrider outrider.tab --samples samples.txt \
           --gtf genes.gtf --panelapp panelapp.tsv --gnomad gnomad.tsv \
           --annotate-pli --filter-pvalue 0.01 --filter-zscore 3.0 --filter-deltapsi 0.5 --output results/
        """
    )
    
    # Required arguments
    parser.add_argument('--fraser', required=True,
                        help='Path to FRASER2 output file (tab-separated)')
    parser.add_argument('--outrider', required=True,
                        help='Path to OUTRIDER output file (tab-separated)')
    parser.add_argument('--gtf', required=True,
                        help='Path to GTF annotation file')
    parser.add_argument('--output', required=True,
                        help='Output directory for annotated results')
    
    # Sample filtering options (mutually exclusive)
    sample_group = parser.add_mutually_exclusive_group(required=False)
    sample_group.add_argument('--samples',
                        help='Path to sample list file (one sample ID per line). If not provided with --annotate-all, all samples will be processed.')
    sample_group.add_argument('--annotate-all', action='store_true',
                        help='Annotate ALL samples in the input files (ignore sample list)')
    
    # Annotation arguments
    parser.add_argument('--panelapp', 
                        help='Path to PanelApp annotation file (tab-separated)')
    parser.add_argument('--gnomad',
                        help='Path to gnomAD constraint file (tab-separated)')
    parser.add_argument('--annotate-pli', action='store_true',
                        help='Add ONLY pLI score annotation from gnomAD (requires --gnomad). Without this flag, all gnomAD metrics are included.')
    
    # Filtering options
    parser.add_argument('--filter-pvalue', type=float, metavar='THRESHOLD',
                        help='Filter results by adjusted p-value threshold (e.g., 0.05, 0.01). Applied to both FRASER and OUTRIDER.')
    parser.add_argument('--filter-zscore', type=float, metavar='THRESHOLD',
                        help='Filter OUTRIDER by absolute z-score threshold (e.g., 2.0, 3.0)')
    parser.add_argument('--filter-deltapsi', type=float, metavar='THRESHOLD',
                        help='Filter FRASER by absolute deltaPsi threshold (e.g., 0.3, 0.5)')
    
    # Other options
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.annotate_pli and not args.gnomad:
        parser.error('--annotate-pli requires --gnomad to be specified')
    
    if not args.samples and not args.annotate_all:
        logger.warning('No sample list provided and --annotate-all not set. All samples will be processed.')
        args.annotate_all = True
    
    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Run pipeline
    processor = RNASeqProcessor(
        fraser_file=args.fraser,
        outrider_file=args.outrider,
        samples_file=args.samples,
        gtf_file=args.gtf,
        output_dir=args.output,
        panelapp_file=args.panelapp,
        gnomad_file=args.gnomad,
        annotate_all=args.annotate_all,
        annotate_pli=args.annotate_pli,
        filter_pvalue=args.filter_pvalue,
        filter_zscore=args.filter_zscore,
        filter_deltapsi=args.filter_deltapsi
    )
    
    try:
        processor.run()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
