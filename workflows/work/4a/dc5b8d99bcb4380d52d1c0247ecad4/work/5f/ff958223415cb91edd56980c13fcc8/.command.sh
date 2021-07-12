#!/bin/bash -ue
mkdir -p /tmp/SRR606249_subset10_1_reads_trim2_prokka.megahit_seqscreen_seqscreen_db/reportgeneration2
mkdir -p /tmp/SRR606249_subset10_1_reads_trim2_prokka.megahit_seqscreen_seqscreen_db/reportgeneration2/seqmapper

if [ -d /tmp/SRR606249_subset10_1_reads_trim2_prokka.megahit_seqscreen_seqscreen_db/reportgeneration2/seqmapper/bowtie2 ]; then rm -rf /tmp/SRR606249_subset10_1_reads_trim2_prokka.megahit_seqscreen_seqscreen_db/reportgeneration2/seqmapper/bowtie2; fi;
if [ -d /tmp/SRR606249_subset10_1_reads_trim2_prokka.megahit_seqscreen_seqscreen_db/reportgeneration2/seqmapper/rapsearch2 ]; then rm -rf /tmp/SRR606249_subset10_1_reads_trim2_prokka.megahit_seqscreen_seqscreen_db/reportgeneration2/seqmapper/rapsearch2; fi;
if [ -d /tmp/SRR606249_subset10_1_reads_trim2_prokka.megahit_seqscreen_seqscreen_db/reportgeneration2/seqmapper/pfam_hmm ]; then rm -rf /tmp/SRR606249_subset10_1_reads_trim2_prokka.megahit_seqscreen_seqscreen_db/reportgeneration2/seqmapper/pfam_hmm; fi;

mkdir /tmp/SRR606249_subset10_1_reads_trim2_prokka.megahit_seqscreen_seqscreen_db/reportgeneration2/seqmapper/bowtie2
mkdir /tmp/SRR606249_subset10_1_reads_trim2_prokka.megahit_seqscreen_seqscreen_db/reportgeneration2/seqmapper/rapsearch2
if false; then mkdir /tmp/SRR606249_subset10_1_reads_trim2_prokka.megahit_seqscreen_seqscreen_db/reportgeneration2/seqmapper/pfam_hmm; fi
