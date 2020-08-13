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
### Quick Start:
After cloning the MetScale repository, some configuration is necessary before use. It can be done automatically using default settings by running the command:
```
python3 query_tool.py --setup
```
That will populate the setting `working_folder` in the default config file with the home folder of the DQT. Following that, the tool should be ready for use.

### Detailed Settings
The command above will automatically set the three important paths the DQT needs to run. Two of them are files: 1) the repository of taxon coverage information for the various MetScale tools, and 2) the full reference taxonomy maintained by NCBI. The third is a working folder for any outputs that are provided. Those are the first three settings listed in the config file:
```
[paths]
working_folder = 
path_to_containment_file = ${working_folder}/containment_dict.json
path_to_ncbi_taxonomy_nodes = ${working_folder}/ncbi_taxonomy/nodes.dmp
```
The command above first sets the value of `working_folder` in this file to be the path to the scripts folder containing the DQT. After this, it creates a folder for the NCBI taxonomy, then downloads and extracts the file needed to the path in the third setting above. Finally it decompresses the file `containment_dict.json.gz` to create the file in the middle entry abvoe.

These paths can be changed if needed, but by design they can be left alone except for periodic updates.

## Usage 
*Note: a complete list of the commands and options is available using the `--help` flag at the command line:*

```
python3 query_tool.py --help
```

### Taxon ID Querying

The default usage of the tool is to give one or more taxon IDs and output a text-based report showing which databases contain that taxon ID. The output goes to the console by default but can optionally be directed to a file. The included metadata file includes many databases of interest, including several of tools in the Taxon Classification workflows and all versions of RefSeq through v98, and is described in more detail below.


#### Details & Example

The query tool can be run using the following command (for example):

```
python3 query_tool.py -t <taxid_source>
```

Here, `<taxid_source>` can have one of three forms:

1. A file path to a text file with a list of line-separated taxon IDs. Excluding the newline and leading or trailing whitespace, each line must readily convert to an integer or the procedure will raise an error.
2. The string `stdin` (i.e. `python3 query_tool.py -t stdin`). In this case a line-separated list (formatted as above) is expected from standard input. When an empty or all-whitespace line is encountered, input is terminated.
3. A single integer representing a taxon ID. The procedure will run for only this taxon. Additionally, the output report will have a slightly different format than for multiple IDs.

**Example**:

<details><summary>(show example)</summary>

```
(metag) :~$ python3 query_tool.py -t testtax.txt

DB Column Names:
   1: minikraken_20171019_8GB
   2: minikraken2_v2_8GB_201904_UPDATE
   3: kaiju_db_nr_euk
   4: NCBI_nucl_gb
   5: NCBI_nucl_wgs
   6: RefSeq_v98

    taxid      rank 0 1 2 3 4 5
  1913708   species - - 1 1 - -
   980453   species - - - 1 - -
   146582   species - - - 1 - -
  1950923   species - - - - 1 -
  1420363   species - - - 1 - -
  1367599   species - - - 1 - -
    48959   species - - - 1 - -
  1594871   species - - - 1 - -
    69507     genus - - - - - -
   241522 subspecies - - - 1 - -
  1068967   species - - - 1 - -
  1007150   species - - - 1 - -
   498356   no rank - 2 1 1 - -
   
   (...truncated...)
```

</details>


## Output
To understand how to interpret the output of the DQT we will use the example query from the previous section:

```
(metag) :~$ python3 query_tool.py -t testtax.txt

DB Column Names:
   1: minikraken_20171019_8GB
   2: minikraken2_v2_8GB_201904_UPDATE
   3: kaiju_db_nr_euk
   4: NCBI_nucl_gb
   5: NCBI_nucl_wgs
   6: RefSeq_v98

    taxid      rank 0 1 2 3 4 5
  1913708   species - - 1 1 - -
   980453   species - - - 1 - -
   146582   species - - - 1 - -
  1950923   species - - - - 1 -
  1420363   species - - - 1 - -
  1367599   species - - - 1 - -
    48959   species - - - 1 - -
  1594871   species - - - 1 - -
    69507     genus - - - - - -
   241522 subspecies - - - 1 - -
  1068967   species - - - 1 - -
  1007150   species - - - 1 - -
   498356   no rank - 2 1 1 - -
   
   (...truncated...)
```

For the numeric values present in the matrix there are 3 possible outcomes:
    1: Taxon ID is present in that database
    2: Taxon ID is not present but it's species-level ancestor is
    0: Neither is present
    
*Note:* For taxon IDs above species level, only outcomes 1/0 are possible.

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
