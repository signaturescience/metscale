import unittest
import os
import subprocess


class TestComparison(unittest.TestCase):
    '''
        Test the comparison workflows: acomparison_workflow_reads, comparison_workflow_assembly, comparison_workflow_reads_assembly
        We test by checking if the correct files are created at the end of the workflow.
    '''
    
    def setUp(self):
        os.chdir("../workflows/")
        os.environ['SINGULARITY_BINDPATH'] = "data:/tmp"
    
    def test_1_comparison_workflow_reads(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_comparison_workflow.json comparison_reads_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SRR606249_allsamples_trim2and30_read_comparison.k31.csv")
        filename_2 = os.path.join(dirname, "data/SRR606249_allsamples_trim2and30_read_comparison.k21.csv")
        filename_3 = os.path.join(dirname, "data/SRR606249_allsamples_trim2and30_read_comparison.k51.csv")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2) and os.path.isfile(filename_3))
        
    def test_2_comparison_workflow_assembly(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_comparison_workflow.json comparison_assembly_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SRR606249_trim2and30_assembly_comparison.k31.csv")
        filename_2 = os.path.join(dirname, "data/SRR606249_trim2and30_assembly_comparison.k21.csv")
        filename_3 = os.path.join(dirname, "data/SRR606249_trim2and30_assembly_comparison.k51.csv")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2) and os.path.isfile(filename_3))
        
    def test_3_comparison_workflow_reads_assembly(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_comparison_workflow.json comparison_reads_assembly_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SRR606249_trim2and30_ra_comparison.k21.csv")
        filename_2 = os.path.join(dirname, "data/SRR606249_trim2and30_ra_comparison.k31.csv")
        filename_3 = os.path.join(dirname, "data/SRR606249_trim2and30_ra_comparison.k51.csv")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2) and os.path.isfile(filename_3))
        
if __name__ == '__main__':
    unittest.main()
        
        