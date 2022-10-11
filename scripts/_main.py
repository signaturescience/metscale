#! usr/bin/python3
import logging, configparser
from _parsing import command_args_parse, command_args_print_hidden_args_help, run_print_argparse_results
from _db_import import db_import_manifest_read, db_import_manifest_print_specs
from _containment import containment_dict_read_previous, containment_dict_show_build_plan, containment_dict_build, \
    containment_dict_summary, containment_dict_save, containment_dict_update_all_md5s
from _ncbi_taxonomy import ncbi_taxonomy_download_taxdmp
from _utils import run_recruit_sources_print_report,run_inspect_previous_containment_dict, \
    run_query_taxids_against_containment, run_random_taxon_sample_to_file


# purpose of this script
"""
This script will be used to store the information of the databases, allowing
a quick assesment of what databases contain what organisms. Overall, this will
give insights into why a certain database may not be able to classify an organism
of interest. In addition, it should allow for reasoning the pitfalls of certain 
public databases.
"""


# class options:
class Opts:
    working_folder = None
    refseq_folder = None
    containment_metadata_json_path = None
    fpath_ncbi_tax_nodes = None
    db_import_manifest = None
    # The following is deprecated, but I don't have time to test it if I delete it (MN 5/15/20)
    cfg_parameter_short_ids = {  # this variable is for storing argument requirements more easily later
        1: 'refseq_folder',
        2: 'containment_metadata_json_path',
        3: 'fpath_ncbi_tax_nodes',
        4: 'db_import_manifest'
        # 5: 'output',
        # 6: 'taxids',
        # 7: 'num_taxa'
    }
    source_working_folder = None
    source_containment = None
    source_ncbitax = None
    source_refseq = None
    source_db_import_manifest = None
    delimited_format_parse_specs = {
        # 'accn2taxid':       ('\t', 2, 1),
        # 'kraken2_inspect':  ('\t', 4, 0),
        # 'first_col':        ('\t', 0, 0),
        # 'refseq':           ('\t', 0, 0),
        # 'seqid2taxid':      ('\t', 1, 0)
    }
    MY_DEBUG = False
    parser_store = None
    command_arg_parameter_reqs = {}
    command_arg_selected = None



def main():
    # logging.info("*** DICTIONARY MAKER v3 ***")
    # dbqt_config = configparser.ConfigParser()

    dbqt_config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    dbqt_config.optionxform = lambda option: option

    # Define the class object
    options = Opts()

    # read the config file
    command_args_parse(options=options, dbqt_config=dbqt_config)
    if options.cmd_setup:
        ncbi_taxonomy_download_taxdmp(options=options)
        return
    if options.cmd_inspect_filelist:
        run_recruit_sources_print_report(options=options, dbqt_config=dbqt_config)
        return
    elif options.cmd_inspect_contain:
        run_inspect_previous_containment_dict(options=options, dbqt_config=dbqt_config)
        return
    elif options.cmd_compare_sources:
        sft, nfe, skips = db_import_manifest_read(options=options, dbqt_config=dbqt_config)
        contain = containment_dict_read_previous(options=options)
        imp_list = containment_dict_show_build_plan(sft, contain, clobber_old=options.clobber)
    elif options.cmd_build_containment:
        sft, nfe, skips = db_import_manifest_read(options=options, dbqt_config=dbqt_config)
        cd = containment_dict_build(sft, clobber_old=options.clobber)
        cd_sum = containment_dict_summary(cd)
        logging.info(cd_sum)
        containment_dict_save(cd)
    elif options.cmd_query_taxids:
        run_query_taxids_against_containment(options=options)
    elif options.cmd_random_taxon_sample:
        run_random_taxon_sample_to_file(options=options)
    elif options.cmd_print_db_import_manifest_specs:
        db_import_manifest_print_specs(options=options)
    elif options.cmd_print_debug_args_help:
        command_args_print_hidden_args_help(options=options)
    elif options.cmd_update_all_md5s:
        containment_dict_update_all_md5s(options=options)
    elif options.cmd_download_ncbi_taxonomy:
        ncbi_taxonomy_download_taxdmp(options=options)
    elif options.cmd_parseargs_report:
        run_print_argparse_results(options=options)

if __name__=='__main__':
    main()