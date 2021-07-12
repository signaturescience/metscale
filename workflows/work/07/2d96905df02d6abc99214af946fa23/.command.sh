#!/bin/bash -ue
mkdir -p /tmp/SRR606249_subset10_1_reads_trim2_prokka.megahit_seqscreen_seqscreen_db/reportgeneration2
if [ -e /tmp/SRR606249_subset10_1_reads_trim2_prokka.megahit_seqscreen_seqscreen_db/reportgeneration2/seqscreen.log ]; then rm /tmp/SRR606249_subset10_1_reads_trim2_prokka.megahit_seqscreen_seqscreen_db/reportgeneration2/seqscreen.log; fi    
echo -n " #### Launching SeqScreen pipeline version 1.6.0 ....... " | tee -a /tmp/SRR606249_subset10_1_reads_trim2_prokka.megahit_seqscreen_seqscreen_db/reportgeneration2/seqscreen.log; date '+%H:%M:%S %Y-%m-%d' | tee -a /tmp/SRR606249_subset10_1_reads_trim2_prokka.megahit_seqscreen_seqscreen_db/reportgeneration2/seqscreen.log
