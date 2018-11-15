
# Open Source Metagenomics Workflows

These open source metagenomics workflows are intended to analyze the biological contents of complex environmental samples. The expected input is Illumina FASTQ files, and the current outputs include filtered reads, FASTQC reports, assembled contigs, and metagenome comparison estimates. 

Future outputs will include taxonomic classifications and visualizations, functional predictions, and alignments. We are actively developing these workflows - please stay tuned for updates!

## Getting Started

The [wiki](https://github.com/signaturescience/metagenomics/wiki) for this project has helpful instructions for installing and running the workflows.

## Prerequisites

It is currently assumed that all workflow steps will be run on CentOS, but other operating systems will be tested in the future.

## Data 

Currently, the workflows have been tested with full and subsampled data from this publication:

[Shakya, M., C. Quince, J. H. Campbell, Z. K. Yang, C. W. Schadt and M. Podar (2013). "Comparative metagenomic and rRNA microbial diversity characterization using archaeal and bacterial synthetic communities." Environ Microbiol 15(6): 1882-1899.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3665634/)
 
## Contributing

Please read [CONTRIBUTING.md](https://github.com/signaturescience/metagenomics/blob/master/CONTRIBUTING.md) for details on our code of conduct and how to contribute to this project.

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](https://github.com/signaturescience/metagenomics/blob/master/LICENSE) file for details.

## Acknowledgments

This project builds off work that began in the [Dahak project](https://github.com/dahak-metagenomics/dahak). For more information about the tools that are used within these workflows, please see DEPENDENCY_LICENSES.txt. 
