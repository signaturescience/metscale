import unittest
import os
import subprocess


class TestTaxonomicClassification(unittest.TestCase):
    '''
        Test the taxonomic classification workflows: 
        We test by checking if the correct files are created at the end of the workflow.
    '''
#     @classmethod
#     def setUpClass(cls):
#         os.chdir("../workflows/")
#         subprocess.run('export SINGULARITY_BINDPATH="data:/tmp"')
    
    def setUp(self):
        os.chdir("../workflows/")
        os.environ['SINGULARITY_BINDPATH'] = "data:/tmp"
        
    def test_1_taxclass_signatures_workflow(self):
        #Note: This runs the comparison/compute_read_signatures rule
        snakemake_command = "snakemake -q --core=6 --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_signatures_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/data/SRR606249_subset10_trim2_scaled10k.k21_31_51.sig")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_trim30_scaled10k.k21_31_51.sig")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))
        
    def test_2_taxclass_gather_workflow(self):
        snakemake_command = "snakemake -q --core=6 --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_gather_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_k51.gather_unassigned.csv")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_k51.gather_output.csv")
        filename_3 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_k51.gather_matches.csv")
        filename_4 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_k21.gather_unassigned.csv")
        filename_5 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_k21.gather_output.csv")
        filename_6 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_k21.gather_matches.csv")
        filename_7 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_k31.gather_unassigned.csv")
        filename_8 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_k31.gather_output.csv")
        filename_9 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_k31.gather_matches.csv")
        filename_10 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_k21.gather_unassigned.csv")
        filename_11 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_k21.gather_output.csv")
        filename_12 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_k21.gather_matches.csv")
        filename_13 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_k51.gather_unassigned.csv")
        filename_14 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_k51.gather_output.csv")
        filename_15 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_k51.gather_matches.csv")
        filename_16 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_k31.gather_unassigned.csv")
        filename_17 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_k31.gather_output.csv")
        filename_18 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_k31.gather_matches.csv")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2) and os.path.isfile(filename_3) and os.path.isfile(filename_4) and   
                        os.path.isfile(filename_5) and os.path.isfile(filename_6) and os.path.isfile(filename_7) and os.path.isfile(filename_8) and 
                        os.path.isfile(filename_9) and os.path.isfile(filename_10) and os.path.isfile(filename_11) and os.path.isfile(filename_12) and
                        os.path.isfile(filename_13) and os.path.isfile(filename_14) and os.path.isfile(filename_15) and os.path.isfile(filename_16) and
                        os.path.isfile(filename_17) and os.path.isfile(filename_18))
    
    def test_3_taxclass_kaijureport_workflow(self):
        snakemake_command = "snakemake -q --core=6 --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_kaijureport_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30.kaiju.out")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30.kaiju_genus.summary")
        filename_3 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2.kaiju.out")
        filename_4 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2.kaiju_genus.summary")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2)and os.path.isfile(filename_3) and os.path.isfile(filename_4))

    def test_4_taxclass_kaijureport_filtered_workflow(self):
        snakemake_command = "snakemake -q --core=6 --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_kaijureport_filtered_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30.kaiju_genus_filtered1_total.summary")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2.kaiju_genus_filtered1_total.summary")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))    
   
    def test_5_taxclass_kaijureport_filteredclass_workflow(self):
        snakemake_command = "snakemake -q --core=6 --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_kaijureport_filteredclass_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30.kaiju_genus_filtered1_classified.summary")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2.kaiju_genus_filtered1_classified.summary")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))  

    def test_6_taxclass_add_taxonnames_workflow(self):
        snakemake_command = "snakemake -q --core=6 --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_add_taxonnames_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()   
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2.kaiju_names.out")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30.kaiju_names.out")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))
     
    #This rule not being utilizied right now    
    def test_7_taxclass_convert_kaiju_to_krona_workflow(self):
        snakemake_command = "snakemake -q --core --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_convert_kaiju_to_krona_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_trim30.kaiju.kaiju_out_krona")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_trim2.kaiju.kaiju_out_krona")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))  
             
    def test_8_taxclass_kaiju_species_summary_workflow(self):
        snakemake_command = "snakemake -q --core --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_kaiju_species_summary_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30.kaiju_out_species.summary")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2.kaiju_out_species.summary")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))              
         
    def test_9_taxclass_visualize_krona_kaijureport_workflow(self):
        snakemake_command = "snakemake -q --core --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_visualize_krona_kaijureport_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30.kaiju_genus_krona.html")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2.kaiju_genus_krona.html")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))

    def test_10_taxclass_visualize_krona_kaijureport_filtered_workflow(self):
        snakemake_command = "snakemake -q --core --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_visualize_krona_kaijureport_filtered_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30.kaiju_genus_krona_filtered1_total.html")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2.kaiju_genus_krona_filtered1_total.html")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))

    def test_11_taxclass_visualize_krona_kaijureport_filteredclass_workflow(self):
        snakemake_command = "snakemake -q --core --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_visualize_krona_kaijureport_filteredclass_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30.kaiju_genus_krona_filtered1_classified.html")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2.kaiju_genus_krona_filtered1_classified.html")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))
        
    def test_12_taxclass_visualize_krona_species_summary_workflow(self):
        snakemake_command = "snakemake -q --core --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_visualize_krona_species_summary_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2.kaiju_species_krona.html")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30.kaiju_species_krona.html")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))        
     
    def test_13_taxclass_kaijureport_contigs_workflow(self):
        snakemake_command = "snakemake -q --core=6 --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_kaijureport_contigs_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_megahit.kaiju_genus.summary")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_metaspades.kaiju_genus.summary")
        filename_3 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_metaspades.kaiju_genus.summary")
        filename_4 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_megahit.kaiju_genus.summary")
        filename_5 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_megahit.kaiju.out")
        filename_6 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_metaspades.kaiju.out")
        filename_7 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_metaspades.kaiju.out")
        filename_8 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_megahit.kaiju.out")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2)and os.path.isfile(filename_3) and os.path.isfile(filename_4) and
                        os.path.isfile(filename_5) and os.path.isfile(filename_6)and os.path.isfile(filename_7) and os.path.isfile(filename_8))
        
        
    def test_14_taxclass_kaijureport_filtered_contigs_workflow(self):
        snakemake_command = "snakemake -q --core=6 --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_kaijureport_filtered_contigs_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_metaspades.kaiju_genus_filtered1_total.summary")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_megahit.kaiju_genus_filtered1_total.summary")
        filename_3 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_metaspades.kaiju_genus_filtered1_total.summary")
        filename_4 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_megahit.kaiju_genus_filtered1_total.summary")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2)and os.path.isfile(filename_3) and os.path.isfile(filename_4))
            
    def test_15_taxclass_kaijureport_filteredclass_contigs_workflow(self):
        snakemake_command = "snakemake -q --core=6 --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_kaijureport_filteredclass_contigs_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_megahit.kaiju_genus_filtered1_classified.summary")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_megahit.kaiju_genus_filtered1_classified.summary")
        filename_3 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_metaspades.kaiju_genus_filtered1_classified.summary")
        filename_4 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_metaspades.kaiju_genus_filtered1_classified.summary")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2)and os.path.isfile(filename_3) and os.path.isfile(filename_4))
        
    def test_16_taxclass_add_taxonnames_to_contigs_workflow(self):
        snakemake_command = "snakemake -q --core=6 --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_add_taxonnames_to_contigs_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_megahit.kaiju_names.out")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_metaspades.kaiju_names.out")
        filename_3 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_metaspades.kaiju_names.out")
        filename_4 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_megahit.kaiju_names.out")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2)and os.path.isfile(filename_3) and os.path.isfile(filename_4))  
        
    def test_17_taxclass_kaiju_species_summary_contigs_workflow(self):
        snakemake_command = "snakemake -q --core=6 --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_kaiju_species_summary_contigs_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_megahit.kaiju_out_species.summary")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_metaspades.kaiju_out_species.summary")
        filename_3 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_metaspades.kaiju_out_species.summary")
        filename_4 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_megahit.kaiju_out_species.summary")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2)and os.path.isfile(filename_3) and os.path.isfile(filename_4))                     

    def test_18_taxclass_visualize_krona_kaijureport_contigs_workflow(self):
        snakemake_command = "snakemake -q --core=6 --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_visualize_krona_kaijureport_contigs_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_megahit.kaiju_genus_krona.html")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_metaspades.kaiju_genus_krona.html")
        filename_3 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_megahit.kaiju_genus_krona.html")
        filename_4 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_metaspades.kaiju_genus_krona.html")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2)and os.path.isfile(filename_3) and os.path.isfile(filename_4))           

    def test_19_taxclass_visualize_krona_kaijureport_filtered_contigs_workflow(self):
        snakemake_command = "snakemake -q --core=6 --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_visualize_krona_kaijureport_filtered_contigs_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_megahit.kaiju_genus_krona_filtered1_total.html")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_megahit.kaiju_genus_krona_filtered1_total.html")
        filename_3 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_metaspades.kaiju_genus_krona_filtered1_total.html")
        filename_4 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_metaspades.kaiju_genus_krona_filtered1_total.html")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2)and os.path.isfile(filename_3) and os.path.isfile(filename_4))         

    def test_20_taxclass_visualize_krona_kaijureport_filteredclass_contigs_workflow(self):
        snakemake_command = "snakemake -q --core=6 --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_visualize_krona_kaijureport_filteredclass_contigs_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_metaspades.kaiju_genus_krona_filtered1_classified.html")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_megahit.kaiju_genus_krona_filtered1_classified.html")
        filename_3 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_megahit.kaiju_genus_krona_filtered1_classified.html")
        filename_4 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_metaspades.kaiju_genus_krona_filtered1_classified.html")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2)and os.path.isfile(filename_3) and os.path.isfile(filename_4))
        
    def test_21_taxclass_visualize_krona_species_summary_contigs_workflow(self):
        snakemake_command = "snakemake -q --core=6 --use-singularity --configfile=../test/test_tax_classification_workflow.json tax_class_visualize_krona_species_summary_contigs_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_metaspades.kaiju_species_krona.html")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_megahit.kaiju_species_krona.html")
        filename_3 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim2_megahit.kaiju_species_krona.html")
        filename_4 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_trim30_metaspades.kaiju_species_krona.html")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2)and os.path.isfile(filename_3) and os.path.isfile(filename_4))              



if __name__ == "__main__":
    unittest.main()
