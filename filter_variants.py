#!/usr/bin/env python3
"""
Filter and prioritize RNA-Seq variants based on various criteria
"""

import argparse
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VariantFilter:
    """Filter variants based on multiple criteria"""
    
    def __init__(self, input_file, output_dir):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data = None
        self.data_type = None  # 'fraser' or 'outrider'
    
    def load_data(self):
        """Load input data and determine type"""
        logger.info(f"Loading data from {self.input_file}")
        self.data = pd.read_csv(self.input_file, sep='\t')
        
        # Determine data type based on columns
        if 'hgncSymbol' in self.data.columns:
            self.data_type = 'fraser'
            logger.info("Detected FRASER data")
        elif 'geneID' in self.data.columns:
            self.data_type = 'outrider'
            logger.info("Detected OUTRIDER data")
        else:
            raise ValueError("Cannot determine data type (FRASER or OUTRIDER)")
        
        return self.data
    
    def filter_by_pvalue(self, threshold=0.05):
        """Filter by adjusted p-value"""
        logger.info(f"Filtering by adjusted p-value < {threshold}")
        filtered = self.data[self.data['padjust'] < threshold].copy()
        logger.info(f"Retained {len(filtered)}/{len(self.data)} variants")
        return filtered
    
    def filter_by_zscore(self, threshold=2.0):
        """Filter OUTRIDER by absolute z-score"""
        if self.data_type != 'outrider':
            logger.warning("Z-score filtering only applicable to OUTRIDER data")
            return self.data
        
        logger.info(f"Filtering by |z-score| > {threshold}")
        filtered = self.data[abs(self.data['zScore']) > threshold].copy()
        logger.info(f"Retained {len(filtered)}/{len(self.data)} variants")
        return filtered
    
    def filter_by_deltapsi(self, threshold=0.3):
        """Filter FRASER by deltaPsi"""
        if self.data_type != 'fraser':
            logger.warning("deltaPsi filtering only applicable to FRASER data")
            return self.data
        
        logger.info(f"Filtering by |deltaPsi| > {threshold}")
        filtered = self.data[abs(self.data['deltaPsi']) > threshold].copy()
        logger.info(f"Retained {len(filtered)}/{len(self.data)} variants")
        return filtered
    
    def filter_by_panelapp(self, confidence_levels=['green', 'amber']):
        """Filter by PanelApp confidence level"""
        if 'confidence_level' not in self.data.columns:
            logger.warning("PanelApp annotation not found, skipping")
            return self.data
        
        logger.info(f"Filtering by PanelApp confidence: {confidence_levels}")
        filtered = self.data[
            self.data['confidence_level'].str.lower().isin(
                [c.lower() for c in confidence_levels]
            )
        ].copy()
        logger.info(f"Retained {len(filtered)}/{len(self.data)} variants")
        return filtered
    
    def filter_by_gnomad_pli(self, threshold=0.9):
        """Filter by gnomAD pLI score"""
        if 'pLI' not in self.data.columns:
            logger.warning("gnomAD pLI not found, skipping")
            return self.data
        
        logger.info(f"Filtering by pLI > {threshold}")
        filtered = self.data[self.data['pLI'] > threshold].copy()
        logger.info(f"Retained {len(filtered)}/{len(self.data)} variants")
        return filtered
    
    def prioritize_variants(self, padjust_threshold=0.05, 
                           zscore_threshold=2.0, 
                           deltapsi_threshold=0.3):
        """
        Apply multiple filters to prioritize variants
        """
        logger.info("Prioritizing variants...")
        
        # Start with all data
        filtered = self.data.copy()
        
        # Apply p-value filter
        filtered = filtered[filtered['padjust'] < padjust_threshold]
        
        # Apply data-specific filters
        if self.data_type == 'outrider':
            filtered = filtered[abs(filtered['zScore']) > zscore_threshold]
        elif self.data_type == 'fraser':
            filtered = filtered[abs(filtered['deltaPsi']) > deltapsi_threshold]
        
        # Apply PanelApp filter if available
        if 'confidence_level' in filtered.columns:
            filtered = filtered[
                filtered['confidence_level'].str.lower().isin(['green', 'amber'])
            ]
        
        # Apply gnomAD pLI filter if available
        if 'pLI' in filtered.columns:
            filtered = filtered[filtered['pLI'] > 0.9]
        
        logger.info(f"Final prioritized variants: {len(filtered)}/{len(self.data)}")
        
        # Sort by significance
        filtered = filtered.sort_values('padjust')
        
        return filtered
    
    def create_summary_report(self, filtered_data):
        """Create summary statistics"""
        summary = {
            'total_variants': len(self.data),
            'filtered_variants': len(filtered_data),
            'samples': filtered_data['sampleID'].nunique(),
        }
        
        if self.data_type == 'fraser':
            summary['genes'] = filtered_data['hgncSymbol'].nunique()
        else:
            summary['genes'] = filtered_data['geneID'].nunique()
        
        logger.info("Summary:")
        for key, value in summary.items():
            logger.info(f"  {key}: {value}")
        
        return summary
    
    def save_results(self, filtered_data, suffix='prioritized'):
        """Save filtered results"""
        output_file = self.output_dir / f"{self.input_file.stem}_{suffix}.tsv"
        filtered_data.to_csv(output_file, sep='\t', index=False)
        logger.info(f"Saved results to {output_file}")
        return output_file


def main():
    parser = argparse.ArgumentParser(
        description='Filter and prioritize RNA-Seq variants',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic filtering by p-value
  %(prog)s --input fraser_annotated.tsv --output results/ --padjust 0.01
  
  # Full prioritization
  %(prog)s --input outrider_annotated.tsv --output results/ \\
           --padjust 0.05 --zscore 3.0 --prioritize
  
  # Filter by PanelApp confidence
  %(prog)s --input fraser_annotated.tsv --output results/ \\
           --panelapp-confidence green
        """
    )
    
    parser.add_argument('--input', required=True, help='Input annotated TSV file')
    parser.add_argument('--output', required=True, help='Output directory')
    
    # Filter thresholds
    parser.add_argument('--padjust', type=float, default=0.05,
                        help='Adjusted p-value threshold (default: 0.05)')
    parser.add_argument('--zscore', type=float, default=2.0,
                        help='Z-score threshold for OUTRIDER (default: 2.0)')
    parser.add_argument('--deltapsi', type=float, default=0.3,
                        help='deltaPsi threshold for FRASER (default: 0.3)')
    parser.add_argument('--pli', type=float, default=0.9,
                        help='gnomAD pLI threshold (default: 0.9)')
    
    # PanelApp options
    parser.add_argument('--panelapp-confidence', nargs='+',
                        default=['green', 'amber'],
                        help='PanelApp confidence levels to keep (default: green amber)')
    
    # Mode
    parser.add_argument('--prioritize', action='store_true',
                        help='Apply all filters for prioritization')
    
    args = parser.parse_args()
    
    # Create filter object
    vf = VariantFilter(args.input, args.output)
    vf.load_data()
    
    if args.prioritize:
        # Apply full prioritization
        filtered = vf.prioritize_variants(
            padjust_threshold=args.padjust,
            zscore_threshold=args.zscore,
            deltapsi_threshold=args.deltapsi
        )
    else:
        # Apply individual filters
        filtered = vf.data.copy()
        
        if args.padjust:
            filtered = vf.filter_by_pvalue(args.padjust)
        
        if args.zscore and vf.data_type == 'outrider':
            filtered = filtered[abs(filtered['zScore']) > args.zscore]
        
        if args.deltapsi and vf.data_type == 'fraser':
            filtered = filtered[abs(filtered['deltaPsi']) > args.deltapsi]
        
        if args.panelapp_confidence:
            if 'confidence_level' in filtered.columns:
                filtered = filtered[
                    filtered['confidence_level'].str.lower().isin(
                        [c.lower() for c in args.panelapp_confidence]
                    )
                ]
        
        if args.pli:
            if 'pLI' in filtered.columns:
                filtered = filtered[filtered['pLI'] > args.pli]
    
    # Create summary
    vf.create_summary_report(filtered)
    
    # Save results
    vf.save_results(filtered)


if __name__ == '__main__':
    main()
