#!/usr/bin/env python3
"""
Download PanelApp gene panels data
"""

import argparse
import requests
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def download_panelapp_panels(output_dir, panel_ids=None):
    """
    Download gene panels from PanelApp API
    
    Args:
        output_dir: Directory to save the data
        panel_ids: List of panel IDs to download (None = download all)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    base_url = "https://panelapp.genomicsengland.co.uk/api/v1"
    
    # Get list of panels
    if panel_ids is None:
        logger.info("Fetching list of all panels...")
        response = requests.get(f"{base_url}/panels/")
        panels = response.json()['results']
        panel_ids = [p['id'] for p in panels]
        logger.info(f"Found {len(panel_ids)} panels")
    
    all_genes = []
    
    for panel_id in panel_ids:
        try:
            logger.info(f"Downloading panel {panel_id}...")
            response = requests.get(f"{base_url}/panels/{panel_id}/")
            panel_data = response.json()
            
            panel_name = panel_data['name']
            panel_version = panel_data['version']
            
            # Extract genes
            for gene in panel_data.get('genes', []):
                gene_data = gene.get('gene_data', {})
                all_genes.append({
                    'panel_id': panel_id,
                    'panel_name': panel_name,
                    'panel_version': panel_version,
                    'gene_symbol': gene_data.get('gene_symbol', ''),
                    'hgnc_id': gene_data.get('hgnc_id', ''),
                    'ensembl_id': gene_data.get('ensembl_genes', {}).get('GRch38', {}).get('82', {}).get('ensembl_id', ''),
                    'confidence_level': gene.get('confidence_level', ''),
                    'mode_of_inheritance': gene.get('mode_of_inheritance', ''),
                    'mode_of_pathogenicity': gene.get('mode_of_pathogenicity', ''),
                    'penetrance': gene.get('penetrance', ''),
                    'evidence': ','.join([e.get('name', '') for e in gene.get('evidence', [])]),
                    'publications': ','.join(gene.get('publications', []))
                })
        
        except Exception as e:
            logger.error(f"Error downloading panel {panel_id}: {e}")
            continue
    
    # Save to file
    df = pd.DataFrame(all_genes)
    output_file = output_dir / "panelapp_genes.tsv"
    df.to_csv(output_file, sep='\t', index=False)
    logger.info(f"Saved {len(df)} genes to {output_file}")
    
    return df


def download_mendelian_genes(output_dir):
    """
    Download Mendelian disease genes from OMIM/other sources
    This is a placeholder - you would need proper OMIM API access
    """
    logger.info("Note: For Mendelian gene data, please use OMIM API with proper credentials")
    logger.info("Alternative: Use ClinVar or HGMD databases")
    
    # Example: Download ClinVar gene summary
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Downloading ClinVar gene summary...")
    url = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/gene_condition_source_id"
    
    try:
        df = pd.read_csv(url, sep='\t')
        output_file = output_dir / "clinvar_genes.tsv"
        df.to_csv(output_file, sep='\t', index=False)
        logger.info(f"Saved ClinVar data to {output_file}")
        return df
    except Exception as e:
        logger.error(f"Error downloading ClinVar data: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='Download PanelApp and Mendelian disease data')
    parser.add_argument('--output', required=True, help='Output directory')
    parser.add_argument('--panels', nargs='+', type=int, 
                        help='Specific panel IDs to download (default: all)')
    parser.add_argument('--mendelian', action='store_true',
                        help='Download Mendelian disease genes')
    
    args = parser.parse_args()
    
    # Download PanelApp data
    download_panelapp_panels(args.output, args.panels)
    
    # Download Mendelian genes if requested
    if args.mendelian:
        download_mendelian_genes(args.output)


if __name__ == '__main__':
    main()
