#!/usr/bin/env python3
"""
Test script for RNA-Seq analysis pipeline
"""

import sys
from pathlib import Path
import pandas as pd
import tempfile
import shutil

def create_test_data(test_dir):
    """Create minimal test data"""
    test_dir = Path(test_dir)
    test_dir.mkdir(exist_ok=True)
    
    # Create test FRASER file
    fraser_data = """seqnames\tstart\tend\twidth\tstrand\tsampleID\thgncSymbol\ttype\tpValue\tpadjust\tpsiValue\tdeltaPsi\tcounts\ttotalCounts\tmeanCounts\tmeanTotalCounts\tnonsplitCounts\tnonsplitProportion\tnonsplitProportion_99quantile
1\t153991677\t153992064\t388\t+\t23D1192\tRPS27\tjaccard\t1.4554e-104\t3.6697e-98\t1\t0.48\t3607\t3614\t3205.1\t3212.77\t6\t0\t0.01
1\t32780279\t32781047\t769\t-\t23D1192\tYARS1\tjaccard\t2.7075e-84\t3.4133e-78\t0.99\t0.78\t1194\t1204\t877.25\t883.8\t9\t0.01\t0.03
1\t114733858\t114733988\t131\t-\t24D1028\tCSDE1\tjaccard\t4.3646e-84\t3.6682e-78\t1\t0.41\t1061\t1065\t1427.61\t1433.64\t3\t0\t0.01"""
    
    with open(test_dir / "fraser_test.tab", 'w') as f:
        f.write(fraser_data)
    
    # Create test OUTRIDER file
    outrider_data = """geneID\tsampleID\tpValue\tpadjust\tzScore\tl2fc\trawcounts\tmeanRawcounts\tnormcounts\tmeanCorrected\ttheta\taberrant\tAberrantBySample\tAberrantByGene\tpadj_rank
ENSG00000184831\t23D1192\t1.17493921220108e-70\t4.22351538007382e-65\t-18.4\t-7.18\t2\t517.08\t2.34\t505.51\t103.1\tFALSE\t0\t0\t1
ENSG00000185515\t23D1192\t7.7979117530048e-70\t2.80308971555863e-64\t-18.02\t-3.86\t105\t1606.56\t108.11\t1579.15\t111.04\tFALSE\t0\t0\t1
ENSG00000197372\t24D1028\t3.09698842353401e-68\t1.11326425255674e-62\t-18.49\t-8.27\t0\t687.28\t0\t667.16\t126.58\tFALSE\t0\t0\t1"""
    
    with open(test_dir / "outrider_test.tab", 'w') as f:
        f.write(outrider_data)
    
    # Create test samples file
    samples_data = "23D1192\n24D1028\n"
    with open(test_dir / "samples_test.txt", 'w') as f:
        f.write(samples_data)
    
    # Create minimal GTF file
    gtf_data = """chr1\tHAVANA\tgene\t11869\t14409\t.\t+\t.\tgene_id "ENSG00000223972"; gene_name "DDX11L1"; gene_type "transcribed_unprocessed_pseudogene";
chr1\tHAVANA\tgene\t153991677\t153992064\t.\t+\t.\tgene_id "ENSG00000142937"; gene_name "RPS27"; gene_type "protein_coding";
chr1\tHAVANA\tgene\t32780279\t32781047\t.\t-\t.\tgene_id "ENSG00000134684"; gene_name "YARS1"; gene_type "protein_coding";
chr1\tHAVANA\tgene\t114733858\t114733988\t.\t-\t.\tgene_id "ENSG00000009307"; gene_name "CSDE1"; gene_type "protein_coding";
chr1\tHAVANA\tgene\t32780280\t32781048\t.\t-\t.\tgene_id "ENSG00000184831"; gene_name "GENE1"; gene_type "protein_coding";
chr1\tHAVANA\tgene\t32780281\t32781049\t.\t-\t.\tgene_id "ENSG00000185515"; gene_name "GENE2"; gene_type "protein_coding";
chr1\tHAVANA\tgene\t32780282\t32781050\t.\t-\t.\tgene_id "ENSG00000197372"; gene_name "GENE3"; gene_type "protein_coding";"""
    
    with open(test_dir / "test.gtf", 'w') as f:
        f.write(gtf_data)
    
    print(f"✓ Created test data in {test_dir}")
    return test_dir


def test_pipeline(test_dir):
    """Test the main pipeline"""
    print("\n🧪 Testing RNA-Seq pipeline...")
    
    import rnaseq_analysis
    
    output_dir = test_dir / "test_output"
    output_dir.mkdir(exist_ok=True)
    
    try:
        processor = rnaseq_analysis.RNASeqProcessor(
            fraser_file=test_dir / "fraser_test.tab",
            outrider_file=test_dir / "outrider_test.tab",
            samples_file=test_dir / "samples_test.txt",
            gtf_file=test_dir / "test.gtf",
            output_dir=output_dir
        )
        
        processor.run()
        
        # Check outputs exist
        assert (output_dir / "fraser_annotated.tsv").exists(), "FRASER output not found"
        assert (output_dir / "outrider_annotated.tsv").exists(), "OUTRIDER output not found"
        
        # Check content
        fraser_result = pd.read_csv(output_dir / "fraser_annotated.tsv", sep='\t')
        outrider_result = pd.read_csv(output_dir / "outrider_annotated.tsv", sep='\t')
        
        assert len(fraser_result) > 0, "FRASER result is empty"
        assert len(outrider_result) > 0, "OUTRIDER result is empty"
        
        print("✓ Pipeline test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_filters():
    """Test the filter script"""
    print("\n🧪 Testing filter script...")
    
    # This would test the filter_variants.py script
    # For now, we'll just check it can be imported
    try:
        sys.path.insert(0, str(Path(__file__).parent / "scripts"))
        import filter_variants
        print("✓ Filter script imports successfully")
        return True
    except Exception as e:
        print(f"✗ Filter script test failed: {e}")
        return False


def main():
    print("=" * 60)
    print("Annotation for RNAexplorer - Test Suite")
    print("=" * 60)
    
    # Create temporary test directory
    test_dir = Path(tempfile.mkdtemp(prefix="rnaseq_test_"))
    
    try:
        # Create test data
        create_test_data(test_dir)
        
        # Run tests
        results = []
        results.append(("Pipeline", test_pipeline(test_dir)))
        results.append(("Filters", test_filters()))
        
        # Summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        
        for name, passed in results:
            status = "✓ PASSED" if passed else "✗ FAILED"
            print(f"{name:20s} {status}")
        
        all_passed = all(r[1] for r in results)
        
        if all_passed:
            print("\n🎉 All tests passed!")
            return 0
        else:
            print("\n⚠️  Some tests failed")
            return 1
    
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up test directory: {test_dir}")
        shutil.rmtree(test_dir)


if __name__ == '__main__':
    sys.exit(main())
