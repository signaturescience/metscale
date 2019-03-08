
# Open Source Metagenomics Workflows

These open source metagenomics workflows are intended to analyze the biological contents of complex environmental samples. The expected input is paired-end Illumina FASTQ files, and the current outputs include filtered reads, assembled contigs, MultiQC reports for FastQC and QUAST results, metagenome comparison estimates, taxonomic classifications, and gene predictions. 

![](https://github.com/signaturescience/metagenomics/blob/master/documentation/figures/Overview_Flowchart.png)

Future outputs will include additional taxonomic classifications and visualizations, functional predictions, and alignments. We are actively developing these workflows, so please stay tuned for updates!

## Getting Started

The [wiki](https://github.com/signaturescience/metagenomics/wiki) for this project has helpful instructions for installing and running the workflows.

## Prerequisites

These workflows have been tested to run offline on CentOS, Red Hat, and Ubuntu.

## Example Data 

The workflows have been tested with a subsampled dataset from this publication:

[Shakya, M., C. Quince, J. H. Campbell, Z. K. Yang, C. W. Schadt and M. Podar (2013). "Comparative metagenomic and rRNA microbial diversity characterization using archaeal and bacterial synthetic communities." Environ Microbiol 15(6): 1882-1899.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3665634/)
 
The original Shakya et al. 2013 dataset is available online as [SRR606249](https://www.ebi.ac.uk/ena/data/view/SRR606249). The subsampled dataset, which was used as the default example in our metagenomics workflows, can be downloaded here:

[SRR606249_subset10_1.fq.gz](https://osf.io/xwk7m/)

[SRR606249_subset10_2.fq.gz](https://osf.io/6dmh5/)

More information about how the subsampled dataset was generated can be found [here](https://github.com/signaturescience/metagenomics/tree/master/workflows/dataset_construction).

## Scientific Benchmark Data

The [NIST-IMMSA ftp site](https://ftp-private.ncbi.nlm.nih.gov/nist-immsa/IMMSA) houses the raw data from the McIntyre et al. 2017 benchmarking study, which leveraged datasets from many previous publications. The following publications are relevant to the datasets used in our scientific benchmarks:

[McIntyre, Alexa B. R., Rachid Ounit, Ebrahim Afshinnekoo, Robert J. Prill, Elizabeth Hénaff, Noah Alexander, Samuel S. Minot, et al. 2017. “Comprehensive Benchmarking and Ensemble Approaches for Metagenomic Classifiers.” Genome Biology 18 (1): 182.](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-017-1299-7)

[Ounit, Rachid, and Stefano Lonardi. 2016. “Higher Classification Sensitivity of Short Metagenomic Reads with CLARK-S.” Bioinformatics  32 (24): 3823–25.](https://academic.oup.com/bioinformatics/article/32/24/3823/2525654)

## Contributing

Please read [CONTRIBUTING.md](https://github.com/signaturescience/metagenomics/blob/master/CONTRIBUTING.md) for details on our code of conduct and how to contribute to this project.

## License

This software is licensed under the [BSD 3-Clause License](https://github.com/signaturescience/metagenomics/blob/master/LICENSE).

## Acknowledgments

This project builds off work that began in the [Dahak project](https://github.com/dahak-metagenomics/dahak). A variety of open source tools are used within the workflows, and more information about those tools is available in the [DEPENDENCY_LICENSES](https://github.com/signaturescience/metagenomics/blob/master/DEPENDENCY_LICENSES) file. 
