# Database Query Tool (DQT)

## Table of Contents
* [Workflow Overview](#Workflow-Overview)
* [Required Files](#Required-Files)
* [Workflow Execution](#Workflow-Execution)
* [Additional Information](#Additional-Information)
     * [Command Line Equivalents](#Command-Line-Equivalents)
     * [Expected Output Files for the Example Dataset](#Expected-Output-Files-for-the-Example-Dataset)

## Workflow Overview 
The Databse Query Tool is used to compare the contents of the reference databases used by the various taxonomic classification tools. Specifically, since the NCBI taxonomy is constantly changing and being updated, not all tools may be using the same version. Thus, comparing outputs from one tool to another requires accounting for differences in the coverage of their respective reference databases.

In its most basic form, the DQT allows the user to input one or more taxon IDs and output a list of the databases that contain that taxon ID. The metadata about the taxa in all of the various databases is contained in a single json file called (by default) `containment_dict.json`. The tool also contains several algorithms to construct, examine, add to, update or replace this file. It additionally has several functions that interface with the NCBI taxonomy to facilitate interpretation.

![](https://github.com/signaturescience/metagenomics/blob/master/scripts/DB_querytool.png)

## Required Files
If you have not already, you will need to clone the MetScale repository and activate your metag environment [Install](https://github.com/signaturescience/metagenomics/wiki/02.-Install) before proceeding:

```sh
[user@localhost ~]$ source activate metag 

(metag)[user@localhost ~]$ cd metagenomics/scripts

```

### Input Files

If you ran the MetScale installation correctly, the following files should be present in the `metagenomics/scripts` directory.

| File Name | File Size | MD5 Checksum |
| ------------- | ------------- | ------------- |
| `databases.png` | `177 KB` | `a37ee46c79ddbf59421f961fa7e440fb` |
| `DB_querytool.png` | `112 KB` | `f56f449cecc4851d85adac8e25f5eb0d` |
| `dictionary_maker_parameters.py` | `3.5 KB` | `27db92f1cecec971f18dfaf693142a2a` |
| `dictionary_maker.py` | `12 KB` | `175100ab02be48b65a2a21bd0c9c555b` |
| `query_tool.py` | `1.9 KB` | `6e3829b603ddf6d492b35aff5fe871d0` | 

If you are missing any of these files, you should re-clone the MetScale repository, as per instructions in [Install](https://github.com/signaturescience/metagenomics/wiki/02.-Install). 

 
## Workflow Execution
Workflows are executed according to the sample names and workflow parameters, as specified in the config file. For more information about config files, see the [Getting Started](https://github.com/signaturescience/metagenomics/wiki/04.-Getting-Started) wiki page.

After the config file is ready, be sure to specify the Singularity bind path from the `metagenomics/workflows` directory before running the read filtering workflow.

```sh
cd metagenomics/workflows
export SINGULARITY_BINDPATH="data:/tmp"
```

You can then execute of the workflow through snakemake using the following command: 

```sh
snakemake --use-singularity {rules} {other options}
```

The following rules are available for execution in the read filtering workflow (yellow stars indicate terminal rules): 

![](https://github.com/signaturescience/metagenomics/blob/master/documentation/figures/Read_Filtering_Rules.png)

The read filtering rules and their parameters are listed under "workflows" in the `metagenomics/workflows/config/default_workflowconfig.settings` config file.

| Rule | Description |
| ------------- | ------------- |
| `read_filtering_pretrim_workflow` | FastQC generates quality reports for raw reads | 
| `read_filtering_posttrim_workflow` | Trimmomatic trims raw reads, and FastQC generates quality reports for filtered reads | 
| `read_filtering_multiqc_workflow` | MultiQC aggregates all FastQC outputs into a single report for each sample | 
| `read_filtering_khmer_interleave_reads_workflow` | Khmer interleaves the quality trimmed, paired-end reads (forward and reverse) into a single *.fq.gz file | 
| `read_filtering_khmer_count_unique_kmers_workflow` | Khmer counts the number of unique k-mers in the interleaved dataset |
| `read_filtering_khmer_subsample_interleaved_reads_workflow` | Khmer subsamples a smaller percentage of the reads from the full interleaved dataset |
| `read_filtering_khmer_split_interleaved_reads_workflow` | Khmer splits the subsampled interleaved read file into two paired-end read files | 

For the read filtering workflow, rules can be run independently, or they can be run together by listing them back to back in the command as such:

```sh
snakemake --use-singularity read_filtering_pretrim_workflow read_filtering_posttrim_workflow read_filtering_multiqc_workflow read_filtering_khmer_interleave_reads_workflow read_filtering_khmer_count_unique_kmers_workflow read_filtering_khmer_subsample_interleaved_reads_workflow read_filtering_khmer_split_interleaved_reads_workflow
```

Note that the default config will count the number of unique k-mers in the original interleaved dataset.

Additional options for snakemake can be found in the snakemake documentation: https://snakemake.readthedocs.io/en/stable/executable.html

To specify your own parameters for this or any of the workflows prior to execution, see the [Workflow Architecture](https://github.com/signaturescience/metagenomics/wiki/11.-Workflow-Architecture) page for more information.

## Output
After successful execution of the read filtering workflow, you will find all of your outputs in the `metagenomics/workflows/data/` directory. The output files generated with the test dataset were created with the default input file pattern of `{sample}_1_reads_{direction}.fq.gz`, so the outputs include the `{sample}_1_reads_*` pattern in their file names. If the default Illumina FASTQ naming convention or another one is used, then a pattern other than `{sample}_1_reads_*` will appear in the output file names. For the input file pattern of `{sample}_1_reads_{direction}.fq.gz`, the following files will be created for each sample and read direction:

| Tool Output | File Name | Description |
| ------------- | ------------- | ------------- |
| FastQC | `{sample}_1_reads_{direction}_reads_fastqc.html` | FastQC HTML report before running Trimmomatic |
| FastQC | `{sample}_1_reads_{direction}_reads_fastqc.zip` | FastQC files before running Trimmomatic |
| Trimmomatic | `{sample}_1_reads_trim{quality_threshold} _{direction}.fq.gz` | Reads that retained their corresponding paired-end after running Trimmomatic |
| Trimmomatic | `{sample}_1_reads_trim{quality_threshold} _{direction}_se` | Reads that lost their paired-end partner after running Trimmomatic; now single end (SE) reads |
| Trimmomatic | `{sample}_1_reads_trim{quality_threshold} _trimmomatic_pe.log` | Log file generated by Trimmomatic |
| FastQC | `{sample}_1_reads_trim{quality_threshold} _{direction}_fastqc.html` | FastQC HTML report after running Trimmomatic |
| FastQC | `{sample}_1_reads_trim{quality_threshold} _{direction}_fastqc.zip` | FastQC files after running Trimmomatic |
| MultiQC | `{sample}_1_reads_fastqc_multiqc_report.html` | MultiQC HTML report, aggregating multiple FastQC outputs |
| MultiQC | `{sample}_1_reads_fastqc_multiqc_report_data` | Directory with additional MultiQC data and statistics |
| khmer script: interleave-reads.py | `{sample}_1_reads_trim{quality_threshold} _interleaved_reads.fq.gz` | Interleaved forward and reverse paired-end reads |
| khmer script: unique-kmers.py | `{sample}_1_reads_trim{quality_threshold} _interleaved_uniqueK{k-mer_length}.txt` | A text file for each k-mer length (default: k=21, k=31, and k=51) that lists the number of unique k-mers counted in an interleaved file |
| khmer script: sample-reads-randomly.py | `{sample}_1_reads_trim{quality_threshold} _subset{percent}_interleaved_reads.fq.gz` | A smaller subsampled percentage of the interleaved reads |
| khmer script: split-paired-reads.py | `{sample}_1_reads_trim{quality_threshold} _subset{percent}_{direction}.fq.gz` | Paired-end FASTQ reads from the subsampled data |
| khmer script: fastq-to-fasta.py | `{sample}_1_reads_{direction}_reads.fa` | FASTA files generated from raw paired-end FASTQ files |
| khmer script: fastq-to-fasta.py | `{sample}_1_reads_trim{quality_threshold} _{direction}.fa` | FASTA files generated from trimmed paired-end FASTQ files |
| khmer script: fastq-to-fasta.py | `{sample}_1_reads_trim{quality_threshold} _interleaved_reads.fa` | FASTA file generated from the full interleaved FASTQ file |
| khmer script: fastq-to-fasta.py | `{sample}_1_reads_trim{quality_threshold} _subset{percent}_interleaved_reads.fa` | FASTA file generated from a subset of an interleaved FASTQ file |
| khmer script: fastq-to-fasta.py | `{sample}_1_reads_trim{quality_threshold} _subset{percent}_{direction}.fa` | FASTA files generated from a subset of the original interleaved data, which was split into paired-end FASTQ files |

After you have reviewed these files, make sure they stay in the `metagenomics/workflows/data/` directory. You are now ready to proceed to the [Assembly](https://github.com/signaturescience/metagenomics/wiki/06.-Assembly) workflow page. Alternatively, the trimmed reads can now be used with specific rules in the [Taxonomic Classification](https://github.com/signaturescience/metagenomics/wiki/08.-Taxonomic-Classification), [Comparison](https://github.com/signaturescience/metagenomics/wiki/07.-Comparison), or [Functional Inference](https://github.com/signaturescience/metagenomics/wiki/09.-Functional-Inference) workflows.

## Additional Information

### Command Line Equivalents

To better understand how the workflows are operating, it may be helpful to see commands that could be used to generate equivalent outputs with the individual tools. Note that the file names in the below examples may not be exact replicates of the file naming conventions in the current workflows, but the commands are equivalent.

The pre-trimming quality control step is equivalent to running FastQC with these commands:
```sh
fastqc {input_reads_1_fq.gz} -o {output_reads_1_fastqc}
fastqc {input_reads_2_fq.gz} -o {output_reads_2_fastqc}
fastqc SRR606249_subset10_1_reads.fq.gz -o SRR606249_subset10_1_reads_fastqc
fastqc SRR606249_subset10_2_reads.fq.gz -o SRR606249_subset10_2_reads_fastqc
```

Read filtering with a quality score threshold of 2 is equivalent to running Trimmomatic with these commands:
```sh
trimmomatic PE {input_reads_1_fq.gz} {input_reads_2_fq.gz} {trimmomatic_output_trim2_1_fq.gz} {trimmomatic_output_trim2_1_se} {trimmomatic_output_trim2_2_fq.gz} {trimmomatic_output_trim2_2_se} ILLUMINACLIP:adapters_combined_256_unique.fasta:2:40:15 LEADING:2 TRAILING:2 SLIDINGWINDOW:4:2 MINLEN:25
trimmomatic PE SRR606249_subset10_1_reads.fq.gz SRR606249_subset10_2_reads.fq.gz SRR606249_subset10_trim2_1.fq.gz SRR606249_subset10_trim2_1_se SRR606249_subset10_trim2_2.fq.gz SRR606249_subset10_trim2_2_se ILLUMINACLIP:adapters_combined_256_unique.fasta:2:40:15 LEADING:2 TRAILING:2 SLIDINGWINDOW:4:2 MINLEN:25
```

Read filtering with a quality score threshold of 30 is equivalent to running Trimmomatic with these commands:
```sh
trimmomatic PE {input_reads_1_fq.gz} {input_reads_2_fq.gz} {trimmomatic_output_trim30_1_fq.gz} {trimmomatic_output_trim30_1_se} {trimmomatic_output_trim30_2_fq.gz} {trimmomatic_output_trim30_2_se} ILLUMINACLIP:adapters_combined_256_unique.fasta:2:40:15 LEADING:30 TRAILING:30 SLIDINGWINDOW:4:30 MINLEN:25
trimmomatic PE SRR606249_subset10_1_reads.fq.gz SRR606249_subset10_2_reads.fq.gz SRR606249_subset10_trim30_1.fq.gz SRR606249_subset10_trim30_1_se SRR606249_subset10_trim30_2.fq.gz SRR606249_subset10_trim30_2_se ILLUMINACLIP:adapters_combined_256_unique.fasta:2:40:15 LEADING:30 TRAILING:30 SLIDINGWINDOW:4:30 MINLEN:25
```

The post-trimming quality control step is the equivalent of running FastQC with these commands:
```sh
fastqc {input_trim2_1_fq.gz} -o {output_trim2_1_fastqc}
fastqc {input_trim2_2_fq.gz} -o {output_trim2_2_fastqc}
fastqc {input_trim30_1_fq.gz} -o {output_trim30_1_fastqc}
fastqc {input_trim30_2_fq.gz} -o {output_trim30_2_fastqc}
fastqc SRR606249_subset10_trim2_1.fq.gz -o SRR606249_subset10_trim2_1_fastqc
fastqc SRR606249_subset10_trim2_2.fq.gz -o SRR606249_subset10_trim2_2_fastqc
fastqc SRR606249_subset10_trim30_1.fq.gz -o SRR606249_subset10_trim30_1_fastqc
fastqc SRR606249_subset10_trim30_2.fq.gz -o SRR606249_subset10_trim30_2_fastqc
```
The MultiQC step in the read filtering workflow is the equivalent of running this command (where each input file name is individually listed):
```sh
multiqc {output_reads_1_fastqc.zip} {output_reads_2_fastqc.zip} {output_trim2_1_fastqc.zip} {output_trim2_2_fastqc.zip} {output_trim30_1_fastqc.zip} {output_trim30_2_fastqc.zip} -n {sample_multiqc_fastqc_report}
multiqc SRR606249_subset10_1_reads_fastqc.zip SRR606249_subset10_2_reads_fastqc.zip SRR606249_subset10_trim2_1_fastqc.zip SRR606249_subset10_trim2_2_fastqc.zip SRR606249_subset10_trim30_1_fastqc.zip SRR606249_subset10_trim30_2_fastqc.zip -n SRR606249_subset10_multiqc_fastqc_report
```

An equivalent MultiQC command could also be run by inputting all FastQC results in the directory (which in this case is from the same sample):
```sh
multiqc *_fastqc.zip -n {sample_multiqc_fastqc_report}
multiqc *_fastqc.zip -n SRR606249_subset10_multiqc_fastqc_report
```

The khmer interleave-reads.py script produces an interleaved file from each set of trimmed paired-end reads with the equivalent of these commands: 
```sh
interleave-reads.py {sample_trim2_1.fq.gz} {sample_trim2_2.fq.gz} --no-reformat -o {sample_trim2_interleave_reads.fq.gz} --gzip
interleave-reads.py {sample_trim30_1.fq.gz} {sample_trim30_2.fq.gz} --no-reformat -o {sample_trim30_interleave_reads.fq.gz} --gzip
interleave-reads.py SRR606249_subset10_trim2_1.fq.gz SRR606249_subset10_trim2_2.fq.gz --no-reformat -o SRR606249_subset10_trim2_interleave_reads.fq.gz --gzip
interleave-reads.py SRR606249_subset10_trim30_1.fq.gz SRR606249_subset10_trim30_2.fq.gz --no-reformat -o SRR606249_subset10_trim30_interleave_reads.fq.gz --gzip
```

The khmer unique-kmers.py script estimates the number of unique k-mers within an interleaved file at specified k-mer lengths (default: k=21, k=31, k=51) with the equivalent of these commands: 
```sh
unique-kmers.py -k 21 {sample_trim2_interleave_reads.fq.gz} -R {sample_trim2_interleaved_uniqueK21.txt}
unique-kmers.py -k 31 {sample_trim2_interleave_reads.fq.gz} -R {sample_trim2_interleaved_uniqueK31.txt}
unique-kmers.py -k 51 {sample_trim2_interleave_reads.fq.gz} -R {sample_trim2_interleaved_uniqueK51.txt}
unique-kmers.py -k 21 {sample_trim30_interleave_reads.fq.gz} -R {sample_trim30_interleaved_uniqueK21.txt}
unique-kmers.py -k 31 {sample_trim30_interleave_reads.fq.gz} -R {sample_trim30_interleaved_uniqueK31.txt}
unique-kmers.py -k 51 {sample_trim30_interleave_reads.fq.gz} -R {sample_trim30_interleaved_uniqueK51.txt}
unique-kmers.py -k 21 SRR606249_subset10_trim2_interleaved_reads.fq.gz -R SRR606249_subset10_trim2_interleaved_uniqueK21.txt
unique-kmers.py -k 31 SRR606249_subset10_trim2_interleaved_reads.fq.gz -R SRR606249_subset10_trim2_interleaved_uniqueK31.txt
unique-kmers.py -k 51 SRR606249_subset10_trim2_interleaved_reads.fq.gz -R SRR606249_subset10_trim2_interleaved_uniqueK51.txt
unique-kmers.py -k 21 SRR606249_subset10_trim30_interleaved_reads.fq.gz -R SRR606249_subset10_trim30_interleaved_uniqueK21.txt
unique-kmers.py -k 31 SRR606249_subset10_trim30_interleaved_reads.fq.gz -R SRR606249_subset10_trim30_interleaved_uniqueK31.txt
unique-kmers.py -k 51 SRR606249_subset10_trim30_interleaved_reads.fq.gz -R SRR606249_subset10_trim30_interleaved_uniqueK51.txt
```

The khmer sample-reads-randomly.py script uniformly subsamples reads from an interleaved file, using reservoir sampling. Note that the command line equivalent requires the exact number of subsampled reads to be specified (-N), so the read filtering workflow converts the specified percentage in the config file to a corresponding read number by multiplying it with the total number of reads in the sample. The following are the command line equivalents for subsampling reads:
```sh
sample-reads-randomly.py -N {10%_of_both_paired-ends_in_full_interleaved_file} -M {subsample_interleave_max_reads} -o {sample_trim2_subset_interleaved_reads.fq.gz} --gzip {sample_trim2_subset_interleaved_reads.fq.gz}
sample-reads-randomly.py -N {10%_of_both_paired-ends_in_full_interleaved_file} -M {subsample_interleave_max_reads} -o {sample_trim30_subset_interleaved_reads.fq.gz} --gzip {sample_trim30_subset_interleaved_reads.fq.gz}
sample-reads-randomly.py -N {number of reads representing a smaller percentage of the full interleaved file} -M 100000000 -o SRR606249_subset10_trim2_subset_interleaved_reads.fq.gz --gzip SRR606249_subset10_trim2_interleaved_reads.fq.gz 
sample-reads-randomly.py -N {number of reads representing a smaller percentage of the full interleaved file} -M 100000000 -o SRR606249_subset10_trim30_subset_interleaved_reads.fq.gz --gzip SRR606249_subset10_trim30_interleaved_reads.fq.gz 
```

The khmer split-paired-reads.py script splits an interleaved file into two paired-end reads. The following command line equivalent is used to split the subsampled interleaved file into two paired-end reads:
```sh
split-paired-reads.py {sample_trim2_subset_interleaved_reads.fq.gz} -1 {sample_trim2_subset10_1.fq.gz} -2 {sample_trim2_subset10_2.fq.gz} --gzip
split-paired-reads.py {sample_trim30_subset_interleaved_reads.fq.gz} -1 {sample_trim30_subset10_1.fq.gz} -2 {sample_trim30_subset10_2.fq.gz} --gzip
split-paired-reads.py SRR606249_subset10_trim2_subset_interleaved_reads.fq.gz -1 SRR606249_subset10_trim2_subset10_1.fq.gz -2 SRR606249_subset10_trim2_subset10_2.fq.gz --gzip
split-paired-reads.py SRR606249_subset10_trim30_subset_interleaved_reads.fq.gz -1 SRR606249_subset10_trim30_subset10_1.fq.gz -2 SRR606249_subset10_trim30_subset10_2.fq.gz --gzip
```

The khmer fastq-to-fasta.py script converts FASTQ files in the `metagenomics/workflows/data/` directory to FASTA files with equivalents of the following commands:
```sh
fastq-to-fasta.py -o {sample.fq.gz} {sample.fa}
fastq-to-fasta.py -o SRR606249_subset10_1_reads.fq.gz SRR606249_subset10_1_reads.fa
fastq-to-fasta.py -o SRR606249_subset10_2_reads.fq.gz SRR606249_subset10_2_reads.fa
fastq-to-fasta.py -o SRR606249_subset10_trim2_1.fq.gz SRR606249_subset10_1_reads_trim2_1.fa
fastq-to-fasta.py -o SRR606249_subset10_trim2_2.fq.gz SRR606249_subset10_1_reads_trim2_2.fa
fastq-to-fasta.py -o SRR606249_subset10_trim30_1.fq.gz SRR606249_subset10_1_reads_trim30_1.fa
fastq-to-fasta.py -o SRR606249_subset10_trim30_2.fq.gz SRR606249_subset10_1_reads_trim30_2.fa
fastq-to-fasta.py -o SRR606249_subset10_trim2_interleaved_reads.fq.gz SRR606249_subset10_1_reads_trim2_interleaved_reads.fa
fastq-to-fasta.py -o SRR606249_subset10_trim30_interleaved_reads.fq.gz SRR606249_subset10_1_reads_trim30_interleaved_reads.fa
fastq-to-fasta.py -o SRR606249_subset10_trim2_subset_interleaved_reads.fq.gz SRR606249_subset10_1_reads_trim2_subset10_interleaved_reads.fa
fastq-to-fasta.py -o SRR606249_subset10_trim30_subset_interleaved_reads.fq.gz SRR606249_subset10_1_reads_trim30_subset10_interleaved_reads.fa
fastq-to-fasta.py -o SRR606249_subset10_trim2_subset10_1.fq.gz SRR606249_subset10_1_reads_trim2_subset10_1.fa
fastq-to-fasta.py -o SRR606249_subset10_trim2_subset10_2.fq.gz SRR606249_subset10_1_reads_trim2_subset10_2.fa
fastq-to-fasta.py -o SRR606249_subset10_trim30_subset10_1.fq.gz SRR606249_subset10_1_reads_trim30_subset10_1.fa
fastq-to-fasta.py -o SRR606249_subset10_trim30_subset10_2.fq.gz SRR606249_subset10_1_reads_trim30_subset10_2.fa
```

### Expected Output Files for the Example Dataset

Below is a more detailed description of the output files expected in the `metagenomics/workflows/data/` directory after the read filtering workflow has been successfully run.

Using these example raw FASTQ files:

| File Name | File Size |
| ------------- | ------------- |
| `SRR606249_subset10_1_reads.fq.gz` | `375 MB` |
| `SRR606249_subset10_2_reads.fq.gz` | `368 MB` |

The following files are produced by [FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) after running the `read_filtering_pretrim_workflow` rule to generate quality reports on the raw reads:

| File Name | File Size |
| ------------- | ------------- |
| `SRR606249_subset10_1_reads_1_reads_fastqc.html` | `223 KB` |
| `SRR606249_subset10_1_reads_1_reads_fastqc.zip` | `235 KB` |
| `SRR606249_subset10_1_reads_2_reads_fastqc.html` | `224 KB` |
| `SRR606249_subset10_1_reads_2_reads_fastqc.zip` | `238 KB` |

There are 5,400,000 reads of 101bp in length within these FastQC HTML reports.

[Trimmomatic](http://www.usadellab.org/cms/?page=trimmomatic) generates the following files after running the `read_filtering_posttrim_workflow` rule with a quality score threshold of 2:

| File Name | File Size |
| ------------- | ------------- |
| `SRR606249_subset10_1_reads_trim2_1.fq.gz` | `381 MB` |
| `SRR606249_subset10_1_reads_trim2_1_se` | `5 MB` |
| `SRR606249_subset10_1_reads_trim2_2.fq.gz` | `374 MB` |
| `SRR606249_subset10_1_reads_trim2_2_se` | `4 MB` |
| `SRR606249_subset10_1_reads_trim2_trimmomatic_pe.log` | `364 MB` |

[Trimmomatic](http://www.usadellab.org/cms/?page=trimmomatic) generates the following files after running the `read_filtering_posttrim_workflow` rule with a quality score threshold of 30:

| File Name | File Size |
| ------------- | ------------- |
| `SRR606249_subset10_1_reads_trim30_1.fq.gz` | `327 MB` |
| `SRR606249_subset10_1_reads_trim30_1_se` | `25 MB` |
| `SRR606249_subset10_1_reads_trim30_2.fq.gz` | `313 MB` |
| `SRR606249_subset10_1_reads_trim30_2_se` | `21 MB` |
| `SRR606249_subset10_1_reads_trim30_trimmomatic_pe.log` | `359 MB` |

[FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) generates the following files after running the `read_filtering_posttrim_workflow` rule:

| File Name | File Size |
| ------------- | ------------- |
| `SRR606249_subset10_1_reads_trim2_1_fastqc.html` | `218 KB` |
| `SRR606249_subset10_1_reads_trim2_1_fastqc.zip` | `228 KB` |
| `SRR606249_subset10_1_reads_trim2_2_fastqc.html` | `222 KB` |
| `SRR606249_subset10_1_reads_trim2_2_fastqc.zip` | `232 KB` |
| `SRR606249_subset10_1_reads_trim30_1_fastqc.html` | `226 KB` |
| `SRR606249_subset10_1_reads_trim30_1_fastqc.zip` | `238 KB` |
| `SRR606249_subset10_1_reads_trim30_2_fastqc.html` | `228 KB` |
| `SRR606249_subset10_1_reads_trim30_2_fastqc.zip` | `240 KB` |

There are 5,337,063 reads of 25-101bp in length within the FastQC HTML reports after conservative trimming (trim2) and 5,044,284 reads of 25-101bp in length after aggressive trimming (trim30).

[MultiQC](https://multiqc.info/) produces the following HTML report of aggregated FastQC results, as well as a directory with supporting data files, after running the `read_filtering_multiqc_workflow` rule:

| File Name | File Size |
| ------------- | ------------- |
| `SRR606249_subset10_1_reads_fastqc_multiqc_report.html` | `1181 KB` |
| `SRR606249_subset10_1_reads_fastqc_multiqc_report_data` | `4 KB` |

MultiQC allows all of the FastQC HTML reports to be visualized at one time. Compared to the raw reads, the quality of the example dataset improves slightly after trim2 and moderately after trim30. Overall, this dataset was of fairly high quality before and after trimming, so the filtered reads do not look drastically different than the raw reads. In a lower quality dataset, the difference between raw and filtered reads would be more pronounced.

[Khmer](https://khmer.readthedocs.io/en/v2.1.2/user/scripts.html) is used within the read filtering workflow to process quality filtered reads. The following files are generated after interleaving paired-end reads with the khmer script interleave-reads.py, which is called by the `read_filtering_khmer_interleave_reads_workflow` rule:

| File Name | File Size |
| ------------- | ------------- |
| `SRR606249_subset10_1_reads_trim2_interleaved_reads.fq.gz` | `719 MB` |
| `SRR606249_subset10_1_reads_trim30_interleaved_reads.fq.gz` | `605 MB` |

There are 10,674,126 reads in the interleaved example dataset that was trimmed with a quality threshold of 2, and there are 10,088,568 reads in the interleaved example dataset that was trimmed with a quality threshold of 30. This is the expected result, since there were individually 5,337,063 reads in the paired-end files from trim2 (5,337,063 forward reads + 5,337,063 reverse reads = 10,674,126 total interleaved reads) and 5,044,284 reads in trim30 (5,044,284 forward reads + 5,044,284 reverse reads = 10,088,568 total interleaved reads).

The number of unique k-mers with default lengths of k=21, k=31, and k=51 are estimated within an interleaved file using the khmer script unique-kmers.py. The following files are created when that script is called by the `read_filtering_khmer_count_unique_kmers_workflow` rule:

| File Name | File Size |
| ------------- | ------------- |
| `SRR606249_subset10_1_reads_trim2_interleaved_uniqueK21.txt` | `1 KB` |
| `SRR606249_subset10_1_reads_trim2_interleaved_uniqueK31.txt` | `1 KB` |
| `SRR606249_subset10_1_reads_trim2_interleaved_uniqueK51.txt` | `1 KB` |
| `SRR606249_subset10_1_reads_trim30_interleaved_uniqueK21.txt` | `1 KB` |
| `SRR606249_subset10_1_reads_trim30_interleaved_uniqueK31.txt` | `1 KB` |
| `SRR606249_subset10_1_reads_trim30_interleaved_uniqueK51.txt` | `1 KB` |

These are the number of unique k-mers recorded within the above text files, as estimated at different k-mer lengths from the original interleaved files (note that as the length of the k-mer size increased, the number of unique k-mers decreased):

| File Name | Unique K-mer Count |
| ------------- | ------------- |
| `SRR606249_subset10_1_reads_trim2_interleaved_uniqueK21.txt` | `203,749,322` |
| `SRR606249_subset10_1_reads_trim2_interleaved_uniqueK31.txt` | `201,383,388` |
| `SRR606249_subset10_1_reads_trim2_interleaved_uniqueK51.txt` | `186,396,385` |
| `SRR606249_subset10_1_reads_trim30_interleaved_uniqueK21.txt` | `170,724,835` |
| `SRR606249_subset10_1_reads_trim30_interleaved_uniqueK31.txt` | `165,019,600` |
| `SRR606249_subset10_1_reads_trim30_interleaved_uniqueK51.txt` | `148,673,196` |

In cases where there is expected to be substantial redundancy in sequence information (beyond what is needed to capture the diversity of organisms within a sample), it may be helpful to work with a smaller percentage of the original dataset. The khmer script sample-reads-randomly.py can be used to down-sample a smaller percentage of the interleaved file with the `read_filtering_khmer_subsample_interleaved_reads_workflow` rule, which will generate the following files for the example dataset:

| File Name | File Size |
| ------------- | ------------- |
| `SRR606249_subset10_1_reads_trim2_subset10_interleaved_reads.fq.gz` | `144 MB` |
| `SRR606249_subset10_1_reads_trim30_subset10_interleaved_reads.fq.gz` | `121 MB` |

There are 2,134,824 reads in the subsampled `SRR606249_subset10_1_reads_trim2_subset10_interleaved_reads.fq.gz` dataset (2,134,824 subsampled reads / 10,674,126 reads in the original `SRR606249_subset10_1_reads_trim2_interleaved_reads.fq.gz` dataset = 20% of the original dataset) and 2,017,712 reads in the subsampled `SRR606249_subset10_1_reads_trim30_subset10_interleaved_reads.fq.gz` dataset (2,017,712 subsampled reads / 10,088,568 reads in the original `SRR606249_subset10_1_reads_trim30_interleaved_reads.fq.gz` dataset = 20% of the original dataset). Trimmomatic is not run again on the subsampled dataset, since the subsampling was performed on data that had already been trimmed.

In this example, the original dataset was actually a subsample of the full Shakya dataset, so the nomenclature has multiple "subset" instances in the file name. The second instance of "subset" after its trim quality information is meant to indicate that it is a smaller subsample of the original dataset, and in this case the first instance of "subset" occurred because original sample name was named "SRR606249_subset10." 
