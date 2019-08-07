import unittest
import os
import contextlib
import subprocess
import sys



class TestReadFiltering(unittest.TestCase):
    '''
        Test the read filtering workflows: read_filtering_pretrim_workflow and read_filtering_posttrim_workflow
        We test by checking if the correct files are created at the end of the workflow.
        Replace cores with the number of cores to run
    '''

    
    def setUp(self):
        os.chdir("../workflows/")
        os.environ['SINGULARITY_BINDPATH'] = "data:/tmp"
       
    def test_1_read_filtering_pretrim_workflow(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_readfilt_workflow.json read_filtering_pretrim_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_1_reads_fastqc.zip")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_2_reads_fastqc.zip")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))
 
    def test_2_read_filtering_posttrim_workflow(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_readfilt_workflow.json read_filtering_posttrim_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2_2_fastqc.zip")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2_1_fastqc.zip")
        filename_3 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim30_2_fastqc.zip")
        filename_4 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim30_1_fastqc.zip")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2) and os.path.isfile(filename_3) and os.path.isfile(filename_4) )
        
    def test_3_read_filtering_multiqc_workflow(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_readfilt_workflow.json read_filtering_multiqc_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd() 
        filename = os.path.join(dirname, "data/SRR606249_subset10_1_reads_fastqc_multiqc_report.html")
        self.assertTrue(os.path.isfile(filename) )
        
    def test_4_read_filtering_khmer_interleave_reads_workflow(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_readfilt_workflow.json read_filtering_khmer_interleave_reads_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd() 
        filename_1 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim30_interleaved_reads.fq.gz")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2_interleaved_reads.fq.gz")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))
        
    def test_5_read_filtering_khmer_subsample_interleaved_reads_workflow(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_readfilt_workflow.json read_filtering_khmer_subsample_interleaved_reads_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd() 
        filename_1 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim30_subset10_interleaved_reads.fq.gz")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2_subset10_interleaved_reads.fq.gz")  
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2)) 
        
        
    def test_6_read_filtering_khmer_split_interleaved_reads_workflow(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_readfilt_workflow.json read_filtering_khmer_split_interleaved_reads_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd() 
        filename_1 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim30_subset10_2.fq.gz") 
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim30_subset10_1.fq.gz") 
        filename_3 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2_subset10_2.fq.gz") 
        filename_4 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2_subset10_1.fq.gz")  
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2) and os.path.isfile(filename_3) and os.path.isfile(filename_4) )  
         
        
    def test_7_read_filtering_khmer_count_unique_kmers_workflow(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_readfilt_workflow.json read_filtering_khmer_count_unique_reads_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd() 
        filename_1 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2_interleaved_uniqueK51.txt")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim30_interleaved_uniqueK51.txt")
        filename_3 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim30_interleaved_uniqueK21.txt")
        filename_4 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim30_interleaved_uniqueK31.txt") 
        filename_5 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2_interleaved_uniqueK31.txt")
        filename_6 = os.path.join(dirname, "data/SRR606249_subset10_1_reads_trim2_interleaved_uniqueK21.txt")     
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2) and os.path.isfile(filename_3) and os.path.isfile(filename_4) and os.path.isfile(filename_5) and os.path.isfile(filename_6) ) 
        

        
    def test_8_read_filtering_khmer_fastq_to_fasta_workflow(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_readfilt_workflow.json read_filtering_khmer_fastq_to_fasta_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd() 
        filename_1 = os.path.join(dirname, "data/SRR606249_subset10_trim30_1.fa")  
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10_trim30_2.fa")
        filename_3 = os.path.join(dirname, "data/SRR606249_subset10_trim2_2.fa")
        filename_4 = os.path.join(dirname, "data/SRR606249_subset10_trim2_1.fa")
        filename_5 = os.path.join(dirname, "data/SRR606249_subset10_2_reads.fa")
        filename_6 = os.path.join(dirname, "data/SRR606249_subset10_1_reads.fa")
        filename_7 = os.path.join(dirname, "data/SRR606249_subset10_trim2_subset10_1.fa")
        filename_8 = os.path.join(dirname, "data/SRR606249_subset10_trim2_subset10_2.fa")
        filename_9 = os.path.join(dirname, "data/SRR606249_subset10_trim30_subset10_1.fa")
        filename_10 = os.path.join(dirname, "data/SRR606249_subset10_trim30_subset10_2.fa")
        filename_11 = os.path.join(dirname, "data/SRR606249_subset10_trim30_subset_interleaved_reads.fa")
        filename_12 = os.path.join(dirname, "data/SRR606249_subset10_trim2_subset_interleaved_reads.fa")
        filename_13 = os.path.join(dirname, "data/SRR606249_subset10_trim30_interleaved_reads.fa")
        filename_14 = os.path.join(dirname, "data/SRR606249_subset10_trim2_interleaved_reads.fa")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2) and os.path.isfile(filename_3) and os.path.isfile(filename_4) and   
                os.path.isfile(filename_5) and os.path.isfile(filename_6) and os.path.isfile(filename_7) and os.path.isfile(filename_8) and 
                os.path.isfile(filename_9) and os.path.isfile(filename_10) and os.path.isfile(filename_11) and os.path.isfile(filename_12) and
                os.path.isfile(filename_13) and os.path.isfile(filename_14))
  
   
if __name__ == "__main__":
    unittest.main()
