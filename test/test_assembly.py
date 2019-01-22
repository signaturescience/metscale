import unittest
import os
import subprocess


class TestAssembly(unittest.TestCase):
    '''
        Test the assembly workflows: assembly_workflow_metaspades, assembly_workflow_megahit, assembly_workflow_all
        We test by checking if the correct files are created at the end of the workflow.
    '''
    
    def setUp(self):
        os.chdir("../workflows/")
        os.environ['SINGULARITY_BINDPATH'] = "data:/tmp"
     
    def test_1_assembly_workflow_metaspades(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_assembly_workflow.json assembly_metaspades_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SRR606249_subset10_trim2.metaspades.contigs.fa")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10_trim30.metaspades.contigs.fa")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))  
             
    def test_2_assembly_workflow_megahit(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_assembly_workflow.json assembly_megahit_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SRR606249_subset10_trim30.megahit.contigs.fa")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10_trim2.megahit.contigs.fa")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))    
        
    def test_3_assembly_workflow_all(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_assembly_workflow.json assembly_all_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SRR606249_subset10_trim2.metaspades.contigs.fa")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10_trim30.metaspades.contigs.fa")
        filename_3 = os.path.join(dirname, "data/SRR606249_subset10_trim30.megahit.contigs.fa")
        filename_4 = os.path.join(dirname, "data/SRR606249_subset10_trim2.megahit.contigs.fa")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2) and os.path.isfile(filename_3) and os.path.isfile(filename_4) )  
      
    def test_4_assembly_quast_workflow(self): 
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_assembly_workflow.json assembly_quast_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SRR606249_subset10_trim2.megahit_quast/report.tsv")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10_trim30.megahit_quast/report.tsv")
        filename_3 = os.path.join(dirname, "data/SRR606249_subset10_trim30.metaspades_quast/report.tsv")
        filename_4 = os.path.join(dirname, "data/SRR606249_subset10_trim2.metaspades_quast/report.tsv")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2) and os.path.isfile(filename_3) and os.path.isfile(filename_4) )

    def test_5_assembly_multiqc_workflow(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_assembly_workflow.json assembly_multiqc_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SRR606249_subset10.megahit_multiqc_report_data/multiqc.log")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10.metaspades_multiqc_report_data/multiqc.log")        
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))  
    

if __name__ == '__main__':
    unittest.main()        
 