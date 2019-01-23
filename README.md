
# Open Source Metagenomics Workflows

These open source metagenomics workflows are intended to analyze the biological contents of complex environmental samples. The expected input is paired-end Illumina FASTQ files, and the current outputs include filtered reads, MultiQC reports for FastQC and QUAST results, assembled contigs, metagenome comparison estimates, and taxonomic classifications. 

![](https://github.com/signaturescience/metagenomics/blob/master/workflows/Overview_Flowchart.png)

Future outputs will include additional taxonomic classifications and visualizations, functional predictions, and alignments. We are actively developing these workflows, so please stay tuned for updates!

## Getting Started

The [wiki](https://github.com/signaturescience/metagenomics/wiki) for this project has helpful instructions for installing and running the workflows.

## Prerequisites

It is currently assumed that all workflow steps will be run on CentOS, but other operating systems will be tested in the future.

## Data 

The workflows have been tested with subsampled data from this publication:

[Shakya, M., C. Quince, J. H. Campbell, Z. K. Yang, C. W. Schadt and M. Podar (2013). "Comparative metagenomic and rRNA microbial diversity characterization using archaeal and bacterial synthetic communities." Environ Microbiol 15(6): 1882-1899.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3665634/)
 
The subsampled datasets used for testing can be downloaded here:

[SRR606249_subset10_1.fq.gz](https://osf.io/xwk7m/)

[SRR606249_subset10_2.fq.gz](https://osf.io/6dmh5/)

More information about how the datasets were generated can be found [here](https://github.com/signaturescience/metagenomics/tree/master/workflows/dataset_construction).
 
## Contributing

Please read [CONTRIBUTING.md](https://github.com/signaturescience/metagenomics/blob/master/CONTRIBUTING.md) for details on our code of conduct and how to contribute to this project.

## License

This software is licensed under the [BSD 3-Clause License](https://github.com/signaturescience/metagenomics/blob/master/LICENSE).

## Acknowledgments

This project builds off work that began in the [Dahak project](https://github.com/dahak-metagenomics/dahak). A variety of open source tools are used within the workflows, and more information about those tools is available in the [DEPENDENCY_LICENSES](https://github.com/signaturescience/metagenomics/blob/master/DEPENDENCY_LICENSES) file. 
