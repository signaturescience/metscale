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
    
    def test_1_comparison_reads_workflow(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_comparison_workflow.json comparison_reads_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2and30_read_comparison.k51.csv")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2and30_read_comparison.k21.csv")
        filename_3 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2and30_read_comparison.k31.csv")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2) and os.path.isfile(filename_3))
        
    def test_2_comparison_assembly_workflow(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_comparison_workflow.json comparison_assembly_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2and30_assembly_comparison.k21.csv")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2and30_assembly_comparison.k51.csv")
        filename_3 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2and30_assembly_comparison.k31.csv")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2) and os.path.isfile(filename_3))
        
    def test_3_comparison_reads_assembly_workflow(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_comparison_workflow.json comparison_reads_assembly_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SRR606249_subset10_1_readsandSRR606249_subset10_1_reads_read_assembly_comparison.k51.csv")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10_1_readsandSRR606249_subset10_1_reads_read_assembly_comparison.k21.csv")
        filename_3 = os.path.join(dirname, "data/SRR606249_subset10_1_readsandSRR606249_subset10_1_reads_read_assembly_comparison.k31.csv")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2) and os.path.isfile(filename_3))
    
    def test_4_comparison_output_heatmap_plots_reads_assembly_workflow(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_comparison_workflow.json comparison_output_heatmap_plots_reads_assembly_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SRR606249_subset10_1_readsandSRR606249_subset10_1_reads_read_assembly_comparison.k31.png")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10_1_readsandSRR606249_subset10_1_reads_read_assembly_comparison.k51.png")
        filename_3 = os.path.join(dirname, "data/SRR606249_subset10_1_readsandSRR606249_subset10_1_reads_read_assembly_comparison.k21.png")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2) and os.path.isfile(filename_3))
        
    def test_5_comparison_output_heatmap_plots_reads_workflow(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_comparison_workflow.json comparison_output_heatmap_plots_reads_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2and30_read_comparison.k31.png")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2and30_read_comparison.k51.png")
        filename_3 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2and30_read_comparison.k21.png")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2) and os.path.isfile(filename_3))

    def test_6_comparison_output_heatmap_plots_assembly_workflow(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_comparison_workflow.json comparison_output_heatmap_plots_assembly_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2and30_assembly_comparison.k21.png")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2and30_assembly_comparison.k51.png")
        filename_3 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2and30_assembly_comparison.k31.png")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2) and os.path.isfile(filename_3))
        

    def test_6_comparison_output_heatmap_plots_all_workflow(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_comparison_workflow.json comparison_output_heatmap_plots_all_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SRR606249_subset10_1_readsandSRR606249_subset10_1_reads_read_assembly_comparison.k31.png")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10_1_readsandSRR606249_subset10_1_reads_read_assembly_comparison.k51.png")
        filename_3 = os.path.join(dirname, "data/SRR606249_subset10_1_readsandSRR606249_subset10_1_reads_read_assembly_comparison.k21.png")
        filename_4 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2and30_read_comparison.k31.png")
        filename_5 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2and30_read_comparison.k51.png")
        filename_6 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2and30_read_comparison.k21.png")
        filename_7 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2and30_assembly_comparison.k21.png")
        filename_8 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2and30_assembly_comparison.k51.png")
        filename_9 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2and30_assembly_comparison.k31.png")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2) and os.path.isfile(filename_3) and
                        os.path.isfile(filename_4) and os.path.isfile(filename_5) and os.path.isfile(filename_6) and
                        os.path.isfile(filename_7) and os.path.isfile(filename_8) and os.path.isfile(filename_9))
        
               
if __name__ == '__main__':
    unittest.main()
        
        
