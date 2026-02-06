#!/usr/bin/env python3
"""
Auto-detect and process RNA-Seq files from a ZIP archive
Automatically finds FRASER and OUTRIDER files and runs the analysis pipeline
"""

import argparse
import zipfile
import tempfile
import shutil
from pathlib import Path
import logging
import sys
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ZipAnalyzer:
    """Analyze and extract RNA-Seq files from ZIP archives"""
    
    def __init__(self, zip_path):
        self.zip_path = Path(zip_path)
        self.temp_dir = None
        self.fraser_file = None
        self.outrider_file = None
        
    def extract_zip(self):
        """Extract ZIP to temporary directory"""
        logger.info(f"Extracting ZIP archive: {self.zip_path}")
        self.temp_dir = Path(tempfile.mkdtemp(prefix="rnaseq_zip_"))
        
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
        
        logger.info(f"Files extracted to: {self.temp_dir}")
        return self.temp_dir
    
    def detect_fraser_file(self):
        """Auto-detect FRASER output file"""
        logger.info("Detecting FRASER file...")
        
        # Common FRASER file patterns
        patterns = [
            r'fraser.*\.tab$',
            r'fraser.*\.tsv$',
            r'.*fraser.*\.txt$',
            r'fraser[_-]results.*',
        ]
        
        for root, dirs, files in self.temp_dir.walk():
            for file in files:
                file_lower = file.lower()
                for pattern in patterns:
                    if re.search(pattern, file_lower, re.IGNORECASE):
                        candidate = root / file
                        # Verify it looks like FRASER by checking headers
                        if self._verify_fraser_format(candidate):
                            logger.info(f"✓ Found FRASER file: {candidate.relative_to(self.temp_dir)}")
                            self.fraser_file = candidate
                            return candidate
        
        logger.warning("Could not auto-detect FRASER file")
        return None
    
    def detect_outrider_file(self):
        """Auto-detect OUTRIDER output file"""
        logger.info("Detecting OUTRIDER file...")
        
        # Common OUTRIDER file patterns
        patterns = [
            r'outrider.*\.tab$',
            r'outrider.*\.tsv$',
            r'.*outrider.*\.txt$',
            r'outrider[_-]results.*',
            r'.*htseq.*',
        ]
        
        for root, dirs, files in self.temp_dir.walk():
            for file in files:
                file_lower = file.lower()
                for pattern in patterns:
                    if re.search(pattern, file_lower, re.IGNORECASE):
                        candidate = root / file
                        # Verify it looks like OUTRIDER by checking headers
                        if self._verify_outrider_format(candidate):
                            logger.info(f"✓ Found OUTRIDER file: {candidate.relative_to(self.temp_dir)}")
                            self.outrider_file = candidate
                            return candidate
        
        logger.warning("Could not auto-detect OUTRIDER file")
        return None
    
    def _verify_fraser_format(self, file_path):
        """Verify file looks like FRASER output"""
        try:
            with open(file_path, 'r') as f:
                header = f.readline().strip().lower()
                # Check for FRASER-specific columns
                required = ['sampleid', 'hgncsymbol', 'pvalue', 'deltapsi']
                return all(col in header for col in required)
        except Exception as e:
            logger.debug(f"Error verifying FRASER format for {file_path}: {e}")
            return False
    
    def _verify_outrider_format(self, file_path):
        """Verify file looks like OUTRIDER output"""
        try:
            with open(file_path, 'r') as f:
                header = f.readline().strip().lower()
                # Check for OUTRIDER-specific columns
                required = ['geneid', 'sampleid', 'zscore', 'pvalue']
                return all(col in header for col in required)
        except Exception as e:
            logger.debug(f"Error verifying OUTRIDER format for {file_path}: {e}")
            return False
    
    def list_all_files(self):
        """List all files in the extracted ZIP"""
        logger.info("\nAll files in ZIP:")
        files = []
        for root, dirs, filenames in self.temp_dir.walk():
            for filename in filenames:
                file_path = root / filename
                rel_path = file_path.relative_to(self.temp_dir)
                size = file_path.stat().st_size
                files.append((rel_path, size))
        
        # Sort by size (largest first) to help identify data files
        files.sort(key=lambda x: x[1], reverse=True)
        
        for rel_path, size in files[:20]:  # Show top 20 files
            size_mb = size / (1024 * 1024)
            logger.info(f"  {rel_path} ({size_mb:.2f} MB)")
        
        if len(files) > 20:
            logger.info(f"  ... and {len(files) - 20} more files")
        
        return files
    
    def manual_file_selection(self):
        """Allow user to manually select files if auto-detection fails"""
        files = list(self.temp_dir.rglob('*.*'))
        
        # Filter for likely data files (tsv, tab, txt)
        data_files = [f for f in files if f.suffix.lower() in ['.tsv', '.tab', '.txt']]
        
        if not data_files:
            logger.error("No data files (*.tsv, *.tab, *.txt) found in ZIP")
            return False
        
        print("\n" + "="*60)
        print("Manual File Selection Required")
        print("="*60)
        print("\nAvailable data files:")
        for i, file in enumerate(data_files, 1):
            rel_path = file.relative_to(self.temp_dir)
            size = file.stat().st_size / (1024 * 1024)
            print(f"{i:2d}. {rel_path} ({size:.2f} MB)")
        
        # Select FRASER file
        if not self.fraser_file:
            print("\nWhich file is FRASER output?")
            try:
                choice = int(input("Enter number (or 0 to skip): "))
                if choice > 0 and choice <= len(data_files):
                    self.fraser_file = data_files[choice - 1]
                    logger.info(f"FRASER file set to: {self.fraser_file}")
            except (ValueError, KeyboardInterrupt):
                logger.warning("Skipping FRASER file selection")
        
        # Select OUTRIDER file
        if not self.outrider_file:
            print("\nWhich file is OUTRIDER output?")
            try:
                choice = int(input("Enter number (or 0 to skip): "))
                if choice > 0 and choice <= len(data_files):
                    self.outrider_file = data_files[choice - 1]
                    logger.info(f"OUTRIDER file set to: {self.outrider_file}")
            except (ValueError, KeyboardInterrupt):
                logger.warning("Skipping OUTRIDER file selection")
        
        return bool(self.fraser_file or self.outrider_file)
    
    def cleanup(self):
        """Clean up temporary directory"""
        if self.temp_dir and self.temp_dir.exists():
            logger.info(f"Cleaning up temporary directory: {self.temp_dir}")
            shutil.rmtree(self.temp_dir)


def run_pipeline(fraser_file, outrider_file, samples_file, gtf_file, output_dir, 
                 panelapp_file=None, gnomad_file=None, annotate_all=False,
                 annotate_pli=False, filter_pvalue=None, filter_zscore=None,
                 filter_deltapsi=None, verbose=False):
    """Run the main RNA-Seq analysis pipeline"""
    logger.info("Running RNA-Seq analysis pipeline...")
    
    import rnaseq_analysis
    
    processor = rnaseq_analysis.RNASeqProcessor(
        fraser_file=fraser_file,
        outrider_file=outrider_file,
        samples_file=samples_file,
        gtf_file=gtf_file,
        output_dir=output_dir,
        panelapp_file=panelapp_file,
        gnomad_file=gnomad_file,
        annotate_all=annotate_all,
        annotate_pli=annotate_pli,
        filter_pvalue=filter_pvalue,
        filter_zscore=filter_zscore,
        filter_deltapsi=filter_deltapsi
    )
    
    return processor.run()


def main():
    parser = argparse.ArgumentParser(
        description='Auto-detect and analyze RNA-Seq files from ZIP archive',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect files and process specific samples
  %(prog)s --zip results.zip --samples samples.txt --gtf genes.gtf --output results/
  
  # Process ALL samples with filtering
  %(prog)s --zip results.zip --gtf genes.gtf --output results/ --annotate-all --filter-pvalue 0.05
  
  # With pLI annotation only and advanced filtering
  %(prog)s --zip results.zip --samples samples.txt --gtf genes.gtf \\
           --gnomad gnomad.tsv --annotate-pli \\
           --filter-pvalue 0.01 --filter-zscore 3.0 --filter-deltapsi 0.5 --output results/
  
  # Interactive mode if auto-detection fails
  %(prog)s --zip results.zip --samples samples.txt --gtf genes.gtf \\
           --output results/ --interactive
        """
    )
    
    # Required arguments
    parser.add_argument('--zip', required=True,
                        help='ZIP archive containing FRASER and/or OUTRIDER files')
    parser.add_argument('--gtf', required=True,
                        help='GTF annotation file')
    parser.add_argument('--output', required=True,
                        help='Output directory')
    
    # Sample filtering options (mutually exclusive)
    sample_group = parser.add_mutually_exclusive_group(required=False)
    sample_group.add_argument('--samples',
                        help='Sample list file (one sample ID per line)')
    sample_group.add_argument('--annotate-all', action='store_true',
                        help='Annotate ALL samples in the input files (ignore sample list)')
    
    # Annotation options
    parser.add_argument('--panelapp',
                        help='PanelApp annotation file (optional)')
    parser.add_argument('--gnomad',
                        help='gnomAD constraint file (optional)')
    parser.add_argument('--annotate-pli', action='store_true',
                        help='Add ONLY pLI score from gnomAD (requires --gnomad). Without this, all gnomAD metrics are included.')
    
    # Filtering options
    parser.add_argument('--filter-pvalue', type=float, metavar='THRESHOLD',
                        help='Filter by adjusted p-value threshold (e.g., 0.05, 0.01)')
    parser.add_argument('--filter-zscore', type=float, metavar='THRESHOLD',
                        help='Filter OUTRIDER by absolute z-score threshold (e.g., 2.0, 3.0)')
    parser.add_argument('--filter-deltapsi', type=float, metavar='THRESHOLD',
                        help='Filter FRASER by absolute deltaPsi threshold (e.g., 0.3, 0.5)')
    
    # Other options
    parser.add_argument('--interactive', action='store_true',
                        help='Enable interactive file selection if auto-detection fails')
    parser.add_argument('--keep-temp', action='store_true',
                        help='Keep temporary extracted files (for debugging)')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.annotate_pli and not args.gnomad:
        parser.error('--annotate-pli requires --gnomad to be specified')
    
    if not args.samples and not args.annotate_all:
        logger.warning('No sample list provided and --annotate-all not set. All samples will be processed.')
        args.annotate_all = True
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize analyzer
    analyzer = ZipAnalyzer(args.zip)
    
    try:
        # Extract ZIP
        analyzer.extract_zip()
        
        # List all files
        analyzer.list_all_files()
        
        # Auto-detect files
        analyzer.detect_fraser_file()
        analyzer.detect_outrider_file()
        
        # Manual selection if needed and interactive mode enabled
        if args.interactive and not (analyzer.fraser_file and analyzer.outrider_file):
            logger.info("\nAuto-detection incomplete. Starting interactive mode...")
            analyzer.manual_file_selection()
        
        # Check if we have at least one file
        if not analyzer.fraser_file and not analyzer.outrider_file:
            logger.error("No FRASER or OUTRIDER files detected!")
            logger.error("Try using --interactive flag for manual selection")
            return 1
        
        # Show what we found
        print("\n" + "="*60)
        print("Files detected:")
        print("="*60)
        if analyzer.fraser_file:
            print(f"FRASER:   {analyzer.fraser_file.relative_to(analyzer.temp_dir)}")
        else:
            print("FRASER:   NOT FOUND")
        
        if analyzer.outrider_file:
            print(f"OUTRIDER: {analyzer.outrider_file.relative_to(analyzer.temp_dir)}")
        else:
            print("OUTRIDER: NOT FOUND")
        print("="*60)
        
        # Confirm before proceeding
        if args.interactive:
            response = input("\nProceed with analysis? [Y/n] ")
            if response.lower() == 'n':
                logger.info("Analysis cancelled by user")
                return 0
        
        # Run pipeline
        run_pipeline(
            fraser_file=analyzer.fraser_file,
            outrider_file=analyzer.outrider_file,
            samples_file=args.samples,
            gtf_file=args.gtf,
            output_dir=args.output,
            panelapp_file=args.panelapp,
            gnomad_file=args.gnomad,
            annotate_all=args.annotate_all,
            annotate_pli=args.annotate_pli,
            filter_pvalue=args.filter_pvalue,
            filter_zscore=args.filter_zscore,
            filter_deltapsi=args.filter_deltapsi,
            verbose=args.verbose
        )
        
        logger.info("✓ Analysis completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        return 1
        
    finally:
        # Cleanup unless --keep-temp is set
        if not args.keep_temp:
            analyzer.cleanup()
        else:
            logger.info(f"Temporary files kept at: {analyzer.temp_dir}")


if __name__ == '__main__':
    sys.exit(main())
