#!/usr/bin/env bash

#************************************************************************************************************
#
#   Script to Download and Prepare Taxon ID Metadata
#   Michael Nute, March 2020
#
#   Description: this script contains all the code to download the metadata for each taxon classification
#       tool, as well as to put it in a form that can be easily parsed by the python tool. This script does
#       this for:
#           1) RefSeq           3) Kaiju            5) The NCBI Taxonomy (reference)
#           2) Kraken2          4) Krakenuniq       
#
#       All files are downloaded and stored in subfolders of a single working folder (called $WORK). The
#       DB query tool uses that folder as a parameter also.
#
#************************************************************************************************************

# Variables:
export WORK=$(pwd)
metscale_scripts_folder=$(pwd)
metscale_data_folder=$metscale_scripts_folder/../workflows/data
metscale_container_folder=$metscale_scripts_folder/container_images

#
# **** NCBI Taxonomy ****
#
ncbi_fold=$WORK/ncbi_taxonomy
ncbi_tax_url=ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip

if [ ! -e $ncbi_fold ]; then
    mkdir $ncbi_fold
fi

cd $ncbi_fold
wget $ncbi_tax_url
unzip taxdmp.zip

#
# **** GenBank ****
#
accn2taxid=$ncbi_fold/accn2taxid
if [ ! -e $accn2taxid ]; then
    mkdir $accn2taxid
fi
cd $accn2taxid
wget ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/nucl_gb.accession2taxid.gz
wget ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/nucl_wgs.accession2taxid.gz
tar -xzf nucl_gb.accession2taxid.gz
tar -xzf nucl_wgs.accession2taxid.gz
cat $accn2taxid/nucl_gb.accession2taxid | cut -f 3 | sort | uniq > $accn2taxid/nucl_gb.taxid_list.txt
cat $accn2taxid/nucl_wgs.accession2taxid | cut -f 3 | sort | uniq > $accn2taxid/nucl_wgs.taxid_list.txt

#
# **** RefSeq ****
#

# download_refseq_archive=T         #Uncomment to download fresh copies of RefSeq archives
# download_refseq_latest=T          #Uncomment to download latest RefSeq
# convert_refseq_gz_to_taxid=T      #Uncomment to create new taxid lists from <ver>.catalog.gz files


# Start with Refseq
if [ ! -d $WORK/refseq]; then mkdir $WORK/refseq; fi;
if [ ! -d $WORK/refseq/catalog_gzip]; then mkdir $WORK/refseq/catalog_gzip; fi;
if [ ! -d $WORK/refseq/catalog_taxid]; then mkdir $WORK/refseq/catalog_taxid; fi;
refseq=$WORK/refseq

if [ $download_refseq_archive ]
then
    printf "--- Downloading RefSeq Archive ---\n"
    curl -q ftp://ftp.ncbi.nlm.nih.gov/refseq/release/release-catalog/archive/ | grep "RefSeq-release[0-9]\+.catalog.gz" -o > $refseq/refseq_archive_list.txt
    ftp_pref=ftp://ftp.ncbi.nlm.nih.gov/refseq/release/release-catalog/archive/
    cd $WORK/refseq/catalog_gzip
    for fn in $(cat $refseq/refseq_archive_list.txt)
    do
        wget $ftp_pref/$fn >> $refseq/refseq_archive_download_log.txt 2>&1
    done
    cd $WORK
fi

if [ $download_refseq_latest ]
then
    printf "--- Downloading RefSeq Latest ---\n"
    curl -q ftp://ftp.ncbi.nlm.nih.gov/refseq/release/release-catalog/ | grep "RefSeq-release[0-9]\+.catalog.gz" -o > $refseq/refseq_latest_catalog.txt
    ftp_pref=ftp://ftp.ncbi.nlm.nih.gov/refseq/release/release-catalog/
    fn=$(sed -n '1p' $refseq/refseq_latest_catalog.txt)
    refseq_latest=$ftp_pref/$fn
    
    cd $WORK/refseq/catalog_gzip
    wget $refseq_latest >> $refseq/refseq_latest_download_log.txt 2>&1
    cd $WORK
fi

if [ $convert_refseq_gz_to_taxid ]
then
    printf "--- Creating TaxID Text from *catalog.gz ---\n"
    for i in $(ls $refseq/catalog_gzip)
    do
        outfile=$(echo $i | sed 's/\.gz/\.taxid/g')
        gunzip $refseq/catalog_gzip/$i --stdout | cut -f 1 | sort | uniq > $refseq/catalog_taxid/$outfile
        echo $i
    done
fi

#
# **** Kraken2 ****
#   *DB located at: ftp://ftp.ccb.jhu.edu/pub/data/kraken2_dbs/minikraken2_v2_8GB_201904_UPDATE.tgz
#
kraken2_work_fold=$WORK/kraken
kraken2_db=minikraken2_v2_8GB_201904_UPDATE
kraken2_db_fold=$metscale_data_folder/$kraken2_db
kraken2_container_path=$metscale_container_folder/kraken2_2.0.8_beta--pl526h6bb024c_0.sif

singularity exec $kraken2_container_path kraken2-inspect --db $kraken2_db_fold --report-zero-counts > $kraken2_work_fold/kraken2_inspect_wzerocounts.txt

#
#  **** Krakenuniq ****
#
krakenuniq_work_fold=$WORK/krakenuniq
krakenuniq_seqid2taxid_url=https://ccb.jhu.edu/software/kraken/dl/seqid2taxid.map
krakenuniq_db=minikraken_20171019_8GB

cd $krakenuniq_work_fold
wget $krakenuniq_seqid2taxid_url


#
# **** Kaiju ****
#
# Need to have**:
#   1) Kaiju compiled from source locally. The 'bin' folder craeted there becomes SCRIPTDIR below
#   2) The nr database and the protein accession2taxid mapping downloaded
#   3) The nodes.dmp file (ideally) that was used to create the original .fmi database (still likely
#        to create date mismatch problems I suspect
#   
#   **Note that this only works for creating a new database. For the one offered by the developers of
#     Kaiju, I had to reach out to them directly for the list of sequence names which becomes 
#     'kaiju_db_nr_euk.faa' below.
#
kaijudir=$WORK/kaiju
nr_path=$kaijudir/nr.gz
prota2t=$accn2taxid/prot.accession2taxid
SCRIPTDIR=$kaijudir/bin
nodespath=$metscale_data_folder/nodes.dmp

if [ ! -e $kaijudir ]; then
    mkdir $kaijudir
fi

# Extract and compile Kaiju software
git clone https://github.com/bioinformatics-centre/kaiju/ $kaijudir/kaiju
cd $kaijudir/kaiju/src
make

cd $kaijudir
gunzip -c $nr_path | $SCRIPTDIR/kaiju-convertNR -t $nodespath -g $prota2t -e $SCRIPTDIR/kaiju-excluded-accessions.txt -a -o $kaijudir/kaiju_db_nr_euk.faa -l $SCRIPTDIR/kaiju-taxonlistEuk.tsv
grep "^>" $kaijudir/kaiju_db_nr_euk.faa | sed 's/.*_\([0-9]\+\)$/\1/g' | sort | uniq > $kaijudir/kaiju_db_nr_euk.taxid_list.txt


#
# **** MetaPhlan ****
#
# Getting Taxon IDs for Metaphlan:
#   - Doing this by parsing sequence names from the fna file
#       in the database download.
#   - Those sequence names are in one of three forms:
#       GenBank record:     "gi|345004010|ref|NC_015954.1|:c419000-417852"
#       GeneID only:        "GeneID:10192294"
#       Accession only:     "NC_015954.1"
#

# Make gene2taxid lookup:
cd $ncbi_fold
wget https://ftp.ncbi.nih.gov/gene/DATA/gene2accession.gz
gunzip gene2accession.gz  # 101,314,312 rows
# Consolidate to a two-column uniq GeneID to TaxonID lookup table (gene in first column)  # 26,920,037 rows
cat gene2accession | sed '1d' | cut -f 1,2 | sed 's/^\([^\t]\+\)\t\([^\t]\+\)$/\2\t\1/g' | sort | uniq > gene2taxidLkp.txt

# Pull down the metaphlan db and extract it
metaphlan_db_dir=$WORK/metaphlan
cd $metaphlan_db_dir
wget https://bitbucket.org/biobakery/metaphlan2/downloads/mpa_v20_m200.tar
tar -xf mpa_v20_m200.tar
bunzip2 mpa_v20_m200.fna.bz2

# make a list of the sequence names only:
grep "^>" mpa_v20_m200.fna | sed 's/>//g' > mpa_v20_m200.seq_names.txt

# separate the sequence names into three lists by type, seperate out NCBI accession number (or GeneID)
grep "^NC" mpa_v20_m200.seq_names.txt > mpa_v20_m200.seq_AccnOnly.txt                                           # (1)
grep "^gi" mpa_v20_m200.seq_names.txt | cut -f 4 -d '|' | sort | uniq > mpa_v20_m200.seq_AccnFromLongRec.txt    # (2)
grep "GeneID" mpa_v20_m200.seq_names.txt | sed 's/GeneID://g' > mpa_v20_m200.seq_GeneIDs.txt                    # (3)

# Next Steps:
#   1) Lookup accessions (files (1) and (2)) in:
#       dead_nucl.accession2taxid, dead_wgs.accession2taxid, nucl_gb.accession2taxid, nucl_wgs.accession2taxid
#       (in $ncbi_fold/accn2taxid)
#   2) Lookup GeneIDs (file (3)) in $ncbi_fold/gene2taxidLkp.txt
#   3) dump results to file 'mpa_v20_m200.TaxonIDmapping.FINAL.txt' (accn/gene, taxonID, type)
#   (code contained elsewhere)
cat mpa_v20_m200.TaxonIDmapping.FINAL.txt | cut -f 2 | sort | uniq > mpa_v20_m200.TaxonIDlist.FINAL.txt
