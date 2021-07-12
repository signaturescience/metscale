#!/bin/bash -ue
echo -n " # Launching initialize workflow .................... " | tee -a /tmp/SRR606249_subset10_1_reads_trim2_prokka.megahit_seqscreen_seqscreen_db/reportgeneration2/seqscreen.log; date '+%H:%M:%S %Y-%m-%d' | tee -a /tmp/SRR606249_subset10_1_reads_trim2_prokka.megahit_seqscreen_seqscreen_db/reportgeneration2/seqscreen.log
/usr/local/bin/workflows/../scripts/validate_fasta.pl -f /data/home/mscholz/metscale/workflows/data/SRR606249_subset10_1_reads_trim2_megahit.prokka_annotation/SRR606249_subset10_1_reads_trim2_megahit.fna --max_seq_size=1000000000
