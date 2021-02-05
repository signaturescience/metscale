#! usr/bin/python3
import pickle, copy, datetime, shutil, argparse, configparser
import os, logging, sys
import glob
import json
# from dictionary_maker_parameters import *

# purpose of this script
"""
This script will be used to store the information of the databases, allowing
a quick assesment of what databases contain what organisms. Overall, this will
give insights into why a certain database may not be able to classify an organism
of interest. In addition, it should allow for reasoning the pitfalls of certain 
public databases.
"""

# logging.info("*** DICTIONARY MAKER v3 ***")
# dbqt_config = configparser.ConfigParser()
dbqt_config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
dbqt_config.optionxform = lambda option: option

# define some global variables
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

options = Opts()


# Specifies how to parse file types that are just delimited text. Each entry is:
#   ( <Delimiter>, <Taxon ID Column>, <# Header Rows to Skip> )
#   NOTE: moved to the config file.


taxid_dict = {}
ncbi_tax_levels = ['no rank', 'superkingdom', 'kingdom', 'subkingdom', 'superphylum', 'phylum', 'subphylum',
                   'superclass', 'class', 'subclass', 'infraclass', 'cohort', 'subcohort', 'superorder', 'order',
                   'suborder', 'infraorder', 'parvorder', 'superfamily', 'family', 'subfamily', 'tribe', 'subtribe',
                   'genus', 'subgenus', 'section', 'subsection', 'series', 'species group', 'species subgroup',
                   'species', 'subspecies', 'varietas', 'forma','strain', 'clade']
hidden_args_help_strings = {}

#
# Utility Functions First:
#
rank2index = lambda x: ncbi_tax_levels.index(x)

def command_args_parse():
    '''
    Separate function set up to create the argument parser and define all the arguments. Also executes parse_args at
    the very end.
    :return:
    '''
    global options
    p = argparse.ArgumentParser()
#description='Module to build and manipulate the Taxon ID metadata and the database'
#                                            ' containment_dict.json')

    help_taxid_list = 'The NCBI taxonomy ID(s) to query against the containment_dict metadatabase. Can be in one of ' \
                      'three forms: a) a single integer, which will be queried and the results output, b) a valid path ' \
                      'to a text file containing one taxon ID per line, all of which will be queried and the results ' \
                      'output as tab-delimited text, or c) \'stdin\' in which case a list of taxon_ids is pulled from ' \
                      'standard input and processed as with a file.'
    p.add_argument('-t', '--taxids', dest='taxid_list', type=str, default=None, help=help_taxid_list)
    p.add_argument('-o', '--output', dest='output_path', type=str, default=None, help=argparse.SUPPRESS)#help='output file path')
    p.add_argument('--all_refseq_versions', action='store_true', default=False,
                   help='Prints whatever results are called for including all versions of RefSeq, not just the latest '
                        'version (default).')
    p.add_argument('--setup', action='store_true', default=False, dest = 'cmd_setup',
                   help='runs a general setup routine to prepare for a first use. Does two things: 1) sets \'working_folder\''
                        'in the config file dbqt_config to be the path to this scripts folder. 2) Downloads the NCBI '
                        'taxonomy and extracts the file needed for the DQT.')
    configgroup = p.add_argument_group()
    #configgroup = p.add_argument_group('Configuration Options',
    #                                   'Paths to key locations and files required by the tool. Arguments not supplied '
    #                                   'will be pulled from the default config file \'dbqt_config\' and if needed will '
    #                                   'be assigned their default values (where applicable).')
    configgroup.add_argument('-wd', '--workdir', type=str, default=None, help=argparse.SUPPRESS)
                   #help='The working folder in which we assume the script \'prepare_taxid_metadata.sh\' has run. '
                   #     '(default: current directory)')
    configgroup.add_argument('-cn', '--containment_json', type=str, default=None, help=argparse.SUPPRESS)
                             #help='Path to the containment_dict.json file.')
    configgroup.add_argument('-dbs', '--db_import_manifest', type=str, default=None, help=argparse.SUPPRESS)
                #   help='Path to the file containing the Source File List. Typically named \'db_import_manifest.txt\'. '
                #        'This is a specifically formatted text file (tab-delimited) containing the target DBs and '
                #        'metadata files.')
    configgroup.add_argument('-c', '--config', type=str, default=None, help=argparse.SUPPRESS)
                        #     help='Optional config file (overrides default file path: \'dbqt_config\'')


    logginggroup = p.add_argument_group('Logging Options', 'Options related to how much information the program prints '
                                                           'while running (to stdout by default, but optioanlly to a logfile.')
    logginggroup.add_argument('-qt', '--quiet', action='store_true', default=False,
                   help='If given, disables logging to the console except for warnings or errors (overrides --debug)')
    logginggroup.add_argument('-vqt', '--veryquiet', action='store_true', default=False,
                   help='If given, disables logging to the console (overrides --quiet and --debug)')
    logginggroup.add_argument('--debug', action='store_true', default=False,
                   help='If given, enables more detailed logging useful in debugging.')
    logginggroup.add_argument('-lf', '--logfile', type=str, default=None, help=argparse.SUPPRESS)
                  # help='If given, sends logging messages to a file instead of the console. Note that if the path'
#                        'given is not a valid path to open a new file, the behavior is undefined.')

    # COMMAND ARGUMENTS (determine what procedure for the tool to run):
    # NOTE: each one of these arguments that determine which command will be run must be stored in a variable
    #   that starts with 'cmd_', otherwise odd behavior may ensue.
    commandgroup = p.add_argument_group()
    #commandgroup = p.add_argument_group('Procedures Available', 'Each of these options describes a different subroutine to '
    #                                                            'run. Only one can be given and if none are, defaults to '
    #                                                            'querying a taxon ID against the containment file (i.e. -QRY)')
    # 1) cmd_query_taxids
    help_cmd_query_taxid = 'query one or more taxids against the containment file. Report back which DBs contain the taxid ' \
                           '(adjusted to the species level). (Requires \'-t/--taxids\')'
    commandgroup.add_argument('-test', '-testing', action='store_true', help=argparse.SUPPRESS,
                              default=False)

    # 2) cmd_inspect_filelist
    help_cmd_filelist = 'Parses the roster of database sources to be added to the containment_dict.json file, either from ' \
                        'the soure_file_list file or from the config file (or both). Prints the results to the console ' \
                        '(readably), and then exits. Primarily for checking accuracy of source file roster before building ' \
                        'a new containment_dict.json file.'
    commandgroup.add_argument('-IFL', '--cmd_inspect_filelist', action='store_true', help=argparse.SUPPRESS, default=False)

    help_cmd_inspect_contain = 'Prints some summary data about the existing containment_dict.json file to the console and ' \
                               'then exits. Primarily for inspecting contents of the file.'
    commandgroup.add_argument('-ICD', '--cmd_inspect_contain', action='store_true', help=argparse.SUPPRESS, default=False)
    help_cmd_show_build_plan = 'Runs procedures to inspect and generate a roster of database sources, as well as to inspect' \
                               'the contaiment_dict.p file. Compares the two and identifies the plan for which files ' \
                               'to be added, ignored or replaced. This procedure is run automatically prior to building ' \
                               'a new containment_dict.json file. (Optional: \'--clober\')'
    commandgroup.add_argument('-CMO', '--cmd_compare_sources', action='store_true', help=argparse.SUPPRESS,
                              default=False)
    help_cmd_build_containment = 'Build a new containment dictionary. Requires doing just about every step along ' \
                                 'the way: 1) parses db_import_manifest, 2) opens old containment dict, 3) parses ' \
                                 'each individual database file, 4) gently replaces containment_dict.json and saves ' \
                                 'new stuff elsewhere.  (Optional: \'--clober\')'
    commandgroup.add_argument('-BCD', '--cmd_build_containment', action='store_true', help=argparse.SUPPRESS, default=False)
    commandgroup.add_argument('--print_debug_args_help', action='store_true', default = False, dest='cmd_print_debug_args_help',
                              help=argparse.SUPPRESS)
                              #help = 'Prints a help message for some additional command-line arguments. Most of thiese '
                              #       'are intended for debugging only and are not especially interesting.')
    help_cmd_download_ncbi_tax = 'Download the the NCBI reference taxonomy from NCBI and extract the file ' \
                                 '\'nodes.dmp\' so it can be used in the DQT. Attempts to pull the zip ' \
                                 'file from \'ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip\'.'
    commandgroup.add_argument('--download_ncbi_taxonomy', action='store_true', default = False,
                              dest='cmd_download_ncbi_taxonomy', help=argparse.SUPPRESS)

    #
    # Misc Args
    #
    miscgroup = p.add_argument_group('Miscellaneous Arguments',
                                        'These arguments are mostly optional and in many cases only operate with certain'
                                        'of the commands, and are ignored otherwise.')
    miscgroup.add_argument('--clobber', action='store_true', help='If provided, previous containment_dict.json is removed and'
                           'rebuilt from scratch based on the source files. (If given along with the \'--setup\' argument, '
                           'the existing containment json file will be overwritten by re-extracting the packaged ' 
                           '`containment_dict.json.gz`).',default=False)
    #
    # Hidden arguments
    #
#    commandgroup.add_argument('--cmd_random_taxon_sample', action='store_true', default=False, help=argparse.SUPPRESS)
#    hidden_args_help_strings['cmd_random_taxon_sample'] = 'Makes a quick random sample of taxids to file, for testing. ' \
#                                                          '(requires: -o/--output, --num_taxa)'
#    p.add_argument('--num_taxa', type=int, default=25, help=argparse.SUPPRESS)
#    hidden_args_help_strings['num_taxa'] = '(Integer, used with --cmd_random_taxon_sample) Number of taxa to be sampled. (default: 25)'
#    commandgroup.add_argument('--print_db_import_manifest_specs', action='store_true', default=False, help=argparse.SUPPRESS,
#                              dest = 'cmd_print_db_import_manifest_specs')
#    hidden_args_help_strings['cmd_print_db_import_manifest_specs'] = 'Prints a description of the specs for specifying a ' \
#                                                               'database roster in a text file.'
#    commandgroup.add_argument('--cmd_update_all_md5s', action='store_true', default=False, help=argparse.SUPPRESS)
#    hidden_args_help_strings['cmd_update_all_md5s'] = 'Runs through the existing containment_dict.json and updates all the ' \
#                                                      'md5 values, then saves the result and exits.'
#    commandgroup.add_argument('--cmd_parseargs_report', action='store_true', default=False, help=argparse.SUPPRESS)
#    hidden_args_help_strings['cmd_parseargs_report'] = 'Parses config and commandline arguments and reports some of the ' \
#                                                       'values, then closes.'
    # TODO: delete me
    commandgroup.add_argument('--show_args_only', action='store_true', default=False, help=argparse.SUPPRESS)

    # Go in the following order:
    #   1) parse the command line arguments, 2) run sub below to define required config settings,
    #   3) post-process the arguments and config, 4) verify that the command argument has what's needed
    p.parse_args(namespace=options)         # (1)
    # This will terminate after the setup if that is called for  # (2)
    run_initial_setup() if options.cmd_setup else define_command_argument_requirements()

    options.parser_store = p
    command_args_postprocess()              # (3)
    verify_alg_params_present()             # (4)`
    if options.show_args_only:
        run_print_argparse_results()
        sys.exit(1)

def define_command_argument_requirements():
    '''
    populates the dictionary of arguments required for each algorithm, where:
        1: 'refseq_folder',
        2: 'containment_metadata_json_path',
        3: 'fpath_ncbi_tax_nodes',
        4: 'db_import_manifest',
        5: 'output',
        6: 'taxids',
        7: 'num_taxa'
    (5/15/20: Scratch that, no numbers used, just actual strings...)

        (...from cfg_parameter_short_ids above...)
    '''
    options.command_arg_parameter_reqs['cmd_query_taxids'] = ['containment_metadata_json_path', 'fpath_ncbi_tax_nodes']
    options.command_arg_parameter_reqs['cmd_inspect_filelist'] = []
    options.command_arg_parameter_reqs['cmd_inspect_contain'] = ['containment_metadata_json_path']
    options.command_arg_parameter_reqs['cmd_compare_sources'] = ['containment_metadata_json_path']
    options.command_arg_parameter_reqs['cmd_build_containment'] = ['containment_metadata_json_path']
    options.command_arg_parameter_reqs['cmd_print_debug_args_help'] = []
    options.command_arg_parameter_reqs['cmd_download_ncbi_taxonomy'] = ['fpath_ncbi_tax_nodes']
    options.command_arg_parameter_reqs['cmd_random_taxon_sample'] = ['fpath_ncbi_tax_nodes',]
    options.command_arg_parameter_reqs['cmd_print_db_import_manifest_specs'] = []
    options.command_arg_parameter_reqs['cmd_update_all_md5s'] = ['containment_metadata_json_path']
    options.command_arg_parameter_reqs['cmd_parseargs_report'] = []
    options.command_arg_parameter_reqs['cmd_setup'] = []

    cmds = [i for i in vars(options).keys() if i[:4] == 'cmd_']
    for c in cmds:
        if c not in options.command_arg_parameter_reqs:
            logging.warning('command argument \'%s\' does not have config requirements defined for it in the '
                            'function \'define_command_argument_requirements()\'')
            options.command_arg_parameter_reqs[c] = []

def run_initial_setup():
    '''

    :return:
    '''
    rich_format = "[%(filename)s (%(lineno)d)] %(levelname)s: %(message)s"
    logging.basicConfig(format=rich_format, level=logging.CRITICAL)
    endmsg = ''

    # Set the first config value to be the scripts folder
    set_config_workingfolder_to_thisone()
    import time
    time.sleep(1)
    endmsg = endmsg + 'Changing working_folder done...\n'

    # Parse the config for real
    c_json, fpathncbi, refseq_fo, sfl, workfold = parse_dbqt_config_interpolated()
    options.working_folder = workfold
    options.containment_metadata_json_path = c_json
    options.fpath_ncbi_tax_nodes = fpathncbi

    # Download and Extract NCBI
    if os.path.isfile(options.fpath_ncbi_tax_nodes) and (options.cmd_download_ncbi_taxonomy is False): # and os.stat(options.fpath_ncbi_tax_nodes).st_size==154065274:
        print('...skipping NCBI download, file already there. To force a re-download, use the argument ')
        print('    --download_ncbi_taxonomy.')
    else:
        ncbi_taxonomy_download_taxdmp()
    endmsg = endmsg + 'Downloading/Extracting NCBI Taxonomy done....\n'
    print(endmsg)

    # Extract gzipped JSON file:
    import gzip
    if os.path.isfile(options.containment_metadata_json_path) and (options.clobber is False):
        print('...skipping containment_dict.json.gz extraction because the given path already exists. To ')
        print('    force a re-extraction of the packaged containment file, use the option \'--clobber\'.')
    else:
        with open(os.path.join(options.working_folder, 'containment_dict.json.gz'), 'rb') as cdgz:
            with open(options.containment_metadata_json_path, 'wb') as cd:
                bct=cd.write(gzip.decompress(cdgz.read()))
    sys.exit(1)

def command_args_postprocess():
    '''
    This is a routine to take certain logical actions based on the command line arguments. It is called ONLY by
    the parsing function (above), but is intended to separate out the logic from the definitions. It does several
    specific things:
        1) Sets the properties of the logger based on command line arguments
        2) Reads the config file and merges that with the command line arguments with appropriate priority
            and handling warnings properly.
        3) Identifies which routine to run based on the 'cmd' flag
    '''
    # READ GLOBAL VARIABLES FROM CONFIG FILE
    # global working_folder, refseq_folder, containment_metadata_json_path, fpath_ncbi_tax_nodes, db_import_manifest
    global options


    containment_metadata_json_path_cfg, fpath_ncbi_tax_nodes_cfg, refseq_folder_cfg, db_import_manifest_cfg, working_folder_cfg = parse_dbqt_config_interpolated()
    options.db_import_manifest_cfg = db_import_manifest_cfg
    options.refseq_folder_cfg = refseq_folder_cfg

    # CONFIGURE THE LOGGER
    mylvl = logging.INFO
    if options.MY_DEBUG:
        mylvl = logging.DEBUG
    if options.debug:
        mylvl = logging.DEBUG
    if options.quiet:
        mylvl = logging.WARNING
    if options.veryquiet:
        mylvl = logging.CRITICAL

    rich_format = "[%(filename)s (%(lineno)d)] %(levelname)s: %(message)s"
    to_file = False
    if options.logfile is not None:
        try:
            myf = open(os.path.expanduser(options.logfile), 'a')
            myf.close()
            to_file = True
        except:
            to_file = False

    if to_file:
        logging.basicConfig(format=rich_format, level=mylvl, filename=options.logfile)
    else:
        logging.basicConfig(format=rich_format, level=mylvl)
        if options.logfile is not None:
            logging.error('--logfile %s encountered a file error when I tried to open it' % options.logfile)

    verify_algorithm_argument()

    #
    # OVERRIDE GLOBAL VALUES IF GIVEN IN COMMAND LINE
    #
    options.source_containment = 'NONE'; options.source_refseq = 'NONE'; options.source_db_import_manifest = 'NONE'
    options.source_ncbitax = 'config'; options.source_working_folder = '(default)'

    # a) working folder: try CMD, then CFG, default to scripts folder
    options.working_folder = os.path.abspath('.')


    if os.path.isdir(working_folder_cfg):
        options.working_folder = os.path.abspath(working_folder_cfg)
        options.source_working_folder = 'config'
    else:
        logging.warning('Config parameter \'working_folder\' is not a valid folder: %s' % working_folder_cfg)
    if options.workdir is not None:
        if os.path.isdir(options.workdir):
            options.working_folder = os.path.abspath(options.workdir)
            options.source_working_folder = 'cmd_line'
        else:
            logging.warning('commandline argument \'workdir\' is not a valid folder %s' % options.workdir)

    # b) Containment Path: (first try CFG, over-write if in CMD, default to being in working dir)
    if containment_metadata_json_path_cfg is not None:
        if os.path.isfile(containment_metadata_json_path_cfg):
            options.containment_metadata_json_path = containment_metadata_json_path_cfg
            options.source_containment = 'config'
        else:
            logging.warning('Config parameter path_to_containment_file is not a valid file path: %s' % containment_metadata_json_path_cfg)
    if options.containment_json is not None:
        if os.path.isfile(options.containment_json):
            options.containment_metadata_json_path = options.containment_json
            options.source_containment = 'cmd_line'
        else:
            logging.warning('Command-line provided pickle_file is not a valid file path: %s' % options.containment_json)
    if options.containment_metadata_json_path is None:
        options.containment_metadata_json_path = os.path.join(options.working_folder, 'containment_dict.json')
        options.source_containment = '(default)'

    # command_args_postprocess_db_import()

    # NCBI nodes file
    if fpath_ncbi_tax_nodes_cfg is not None:
        if os.path.isfile(fpath_ncbi_tax_nodes_cfg) or options.command_arg_selected in ['cmd_setup','cmd_download_ncbi_taxonomy']:
            options.fpath_ncbi_tax_nodes = fpath_ncbi_tax_nodes_cfg
            options.source_ncbitax = 'config'
        else:
            options.fpath_ncbi_tax_nodes = None
            options.source_ncbitax = 'NONE'
            logging.warning('Config parameter fpath_ncbi_tax_nodes is not a valid file path. This must be fixed before ')
            logging.warning('   this tool can be used to query a database. To download and extract this file to the ')
            logging.warning('   path specific in the config file, use the argument --download_ncbi_taxonomy at the ')
            logging.warning('   command line.')
            logging.warning('   -> fpath_ncbi_tax_nodes from config: %s' % fpath_ncbi_tax_nodes_cfg)

    # READ THE FORMAT LIST INTO A DICT:
    for k in dbqt_config['formats'].keys():
        fmt = None
        # logging.debug('format %8s\t%s' % (k, dbqt_config.get('formats',k)))
        fmt=eval(dbqt_config.get('formats',k))
        # logging.debug('fmt is now: %s' % str(fmt))
        options.delimited_format_parse_specs[k]=fmt


def command_args_postprocess_db_import():
    '''
    Looks at the values for the manifest file given at the command line and/or in the config file for
    the db_import_manifest and refseq_folder paths. Assesses if they are valid paths and prints warnings
    accordingly.
    :return:
    '''
    # Source File List: (first try CFG, over-write if in CMD, default to being in working dir)
    global options
    if options.db_import_manifest_cfg is not None:
        if os.path.isfile(options.db_import_manifest_cfg):
            options.db_import_manifest = options.db_import_manifest_cfg
            options.source_db_import_manifest = 'config'
        else:
            logging.warning(
                'Config parameter path_to_db_import_manifest is not a valid file path: %s' % options.db_import_manifest_cfg)
    if options.db_import_manifest is not None:
        if os.path.isfile(options.db_import_manifest):
            options.db_import_manifest = options.db_import_manifest
            options.source_db_import_manifest = 'cmd_line'
        else:
            logging.warning(
                'Command-line parameter --db_import_manifest is not a valid file path: %s' % options.db_import_manifest)
    if options.db_import_manifest is None:
        db_import_manifest_wd = os.path.join(options.working_folder, 'db_import_manifest.txt')
        if os.path.isfile(db_import_manifest_wd):
            options.db_import_manifest = db_import_manifest_wd
            options.source_db_import_manifest = '(default)'
            # logging.info('Found a valid DB source file list file at: %s' % db_import_manifest)
    # RefSeq folder
    if options.refseq_folder_cfg is not None:
        if os.path.isdir(options.refseq_folder_cfg):
            options.refseq_folder = options.refseq_folder_cfg
            options.source_refseq = 'config'
        else:
            options.refseq_folder = None
            logging.warning('Config parameter refseq_folder is not a valid folder: %s' % options.refseq_folder_cfg)

def parse_dbqt_config_interpolated():
    '''
    Parses the dbqt_config file using interpolition. If a config file is specified at the command line, options
    specified therein will override the default dbqt_config where duplicated.
    :return:
    '''
    if os.path.isfile('dbqt_config'):
        dbqt_config.read('dbqt_config')
    else:
        logging.warning('File `dbqt_config` has not been created, it is possible that setup has not been run. If this is the '
                        'case, please run the DQT with the `--setup` option first, or perform the equivalent steps manually.')
        logging.warning('Making a copy of the config found in the `doc` subfolder and using the query_tool.py folder '
                        'as the working_folder.')
        config_check_exists_else_copy()
        dbqt_config.read('dbqt_config')

    # set default working_folder to be the current one if missing
    if dbqt_config.get('paths','working_folder').strip() == '':
        scriptsfold = os.path.split(__file__)[0]
        dbqt_config.set('paths','working_folder', scriptsfold)

    if hasattr(options, 'config') and options.config is not None:
        if os.path.isfile(os.path.expanduser(options.config)):
            dbqt_config.read(options.config)
            logging.debug('Reading config file: %s' % options.config)
        else:
            logging.error('Config file given at command line does not exist (file: %s)' % options.config)

    # Fetch results
    working_folder_cfg = dbqt_config['paths'].get('working_folder', fallback=None)
    containment_metadata_json_path_cfg = dbqt_config['paths'].get('path_to_containment_file', fallback=None)
    fpath_ncbi_tax_nodes_cfg = dbqt_config['paths'].get('path_to_ncbi_taxonomy_nodes', fallback=None)
    db_import_manifest_cfg = dbqt_config['import_locs'].get('path_to_db_import_manifest', fallback=None)
    refseq_folder_cfg = dbqt_config['import_locs'].get('refseq_folder', fallback=None)

    # Expand User Character on paths:
    EUorNone = lambda x: None if x is None else os.path.expanduser(x)
    working_folder_cfg = EUorNone(working_folder_cfg)
    refseq_folder_cfg = EUorNone(refseq_folder_cfg)
    containment_metadata_json_path_cfg = EUorNone(containment_metadata_json_path_cfg)
    fpath_ncbi_tax_nodes_cfg = EUorNone(fpath_ncbi_tax_nodes_cfg)
    db_import_manifest_cfg = EUorNone(db_import_manifest_cfg)
    return containment_metadata_json_path_cfg, fpath_ncbi_tax_nodes_cfg, refseq_folder_cfg, db_import_manifest_cfg, working_folder_cfg


def run_print_argparse_results(config_params=True, alg_params=False):
    '''
    This is mostly a debugging function. This has some weird reciprocal calls to verify_alg_params_present() so
    the arguments are mostly control-flow measures to avoid errors.
    :param config_params:
    :param alg_params:
    :return:
    '''
    if config_params:
        print('CONFIGURATION FILE/FOLDER PATHS:')
        print('working_folder =              %s' % options.working_folder)
        print('path_to_containment_file =    %s' % options.containment_metadata_json_path)
        print('path_to_ncbi_taxonomy_nodes = %s' % options.fpath_ncbi_tax_nodes)
        print('refseq_folder =               %s' % options.refseq_folder)
        print('path_to_db_import_manifest =    %s' % options.db_import_manifest)
        print('source_working_folder =       %s' % options.source_working_folder)
        print('source_containment =          %s' % options.source_containment)
        print('source_ncbitax =              %s' % options.source_ncbitax)
        print('source_refseq =               %s' % options.source_refseq)
        print('source_db_import_manifest =           %s\n' % options.source_db_import_manifest)

    if alg_params:
        print('VERIFYING ALGORITHM ARGUMENT:')
        verify_algorithm_argument(print_cmd_list=True)
        verify_alg_params_present(custom_list=[2,3,4], from_print_argparse=True)

def command_args_print_hidden_args_help():
    '''
    Several arguments are available at the command line for debugging but are not included in the default help menu.
    This function prints a special help menu for the hidden options. None of these are especially interesting.
    :return:
    '''
    import textwrap
    print('\nHelp menu for hidden (debugging only) arguments:\n\n', end='')

    for k in hidden_args_help_strings:
        print('  --%s')
        hstr = textwrap.wrap(hidden_args_help_strings[k], 55)
        for ln in hstr:
            print(' '*25, end='')
            print(ln)

def make_tuple_with_metadata(path, dbname, format):
    '''minor utility that takes three inputs and returns a tuple with the three inputs plus the file size and mod_time.
    '''
    s = os.stat(path)
    return (dbname, path, format, s.st_size, s.st_mtime)

def pad_str(inp, total_chars=30, left_justify=True, margin=1):
    instr = str(inp)
    slen = len(instr)
    if slen > total_chars:
        return instr

    long_space = ' '*(total_chars - slen - margin)
    marg_space = ' '*margin
    if left_justify:
        return long_space + instr + marg_space
    else:
        return marg_space + instr + long_space

def get_file_md5_digest(file_path):
    import hashlib
    with open(file_path,'rb') as fb:
        hd=hashlib.md5(fb.read()).hexdigest()
    return hd

def util_filter_out_main_dbnames(db_iterable):
    '''
    takes an iterable of db names and returns a list containing a subset that includes only the
    latest version of refseq.
    '''
    out = []
    latest_refseq_ver = -1
    latest_refseq_name = ''

    for nm in db_iterable:
        if nm[:6].lower()=='refseq':
            v = int(nm[8:])
            if v > latest_refseq_ver:
                latest_refseq_ver = v
                latest_refseq_name = nm
        else:
            out.append(nm)
    out.append(latest_refseq_name)
    return out

def db_import_manifest_read(skip_refseq = False, from_config = True, from_file_if_exists = True):
    '''
    Reads a config file containing a list of databases to be imported, including relevant information. If from_config
    is True, it will look for the relevant file paths and formats in the config file 'dbqt_config'. Specifically it will
    look in the category "db_source_files" for all keys present. Each key is treated as a database name, and the value
    is a path to the file to be parsed. Likewise it looks in "db_source_formats" for every database name and reads a
    value. If the value  is defined, it parses the value as a space-delimited string. The first item is the format, and
    the second item is a 1/0 value indicating whether the db should be imported or not (0 --> skip, 1 or missing =
    proceed). If the format is not defined in the [formats] section, the db is skipped and the event is sent to the
    logger as a warning (same if there is an error parsing the space-delimited string).

    If 'from_file_if_exists' is True, it will look for the same information in a text file. The file it looks
    through must be tab-delimited, with a single header row. The fields it expects are:
        DB_Name: simple string identifying the database (e.g. 'RefSeq_v90' or 'kaiju_db_nr_euk')
        Path: path to the file. If this is not an absolute path it will be considered relative to the working folder.
        Format: the name of the format spec (from the config file) to use.
        Import: Set to 0 if the row should be skipped during processing, 1 otherwise.

    If both arguments are True, duplicates will be prioritized from the text file.
    :return:
    '''
    global options #.refseq_folder, db_import_manifest, dbqt_config
    logging.debug('Function: db_import_manifest_read()...')

    command_args_postprocess_db_import()

    db_import_manifest_output = []
    db_import_manifest_parsed = {}
    no_file_errors = []
    not_to_import = []
    refseq_ct = 0
    line_no = 1
    refseq_in_source_list = False

    #
    # 1) Get the databases specified in the config file
    #
    if from_config:
        for dbnm in dbqt_config['db_source_files'].keys():
            db_name = dbnm
            db_filepath = dbqt_config['db_source_files'][dbnm]
            # verify that a format has been specified
            if db_name not in dbqt_config['db_source_formats'].keys():  # No Format Specified --> SKIP
                logging.warning('In config: database name \'%s\' was found in the config file under [db_source_files] but does not have'
                                'a format defined in [db_source_formats]. (Skipping)' % dbnm)
                db_format = ''
                db_to_import = 0
            else:                                                       # Format Specified --> OK
                db_fmt_val = dbqt_config['db_source_formats'][dbnm]
                db_fmt_tup = db_fmt_val.strip().split(' ')
                db_format = db_fmt_tup[0]
                if len(db_fmt_tup)>=2:
                    try:
                        db_to_import = int(db_fmt_tup[1])
                    except:
                        logging.warning('In config: database format string for \'%s\' contains a second space-delimited value that '
                                        'could not be read as either a 0 or 1 (treating as 1). (Read: %s)' % (dbnm, db_fmt_tup[1]))
                        db_to_import = 1
                    if len(db_fmt_tup) > 2:
                        logging.warning('In config: Database format string for \'%s\' contains more than one space. Using only the '
                                        'first two values. (string: \'%s\')' % (dbnm, db_fmt_val))
                else:
                    logging.warning('In config: Database format string for \'%s\' does not contain a space: assuming final value of 1 (proceeding to import). (string: \'%s\')' % (dbnm, db_fmt_val))
                    db_to_import = 1
            db_import_manifest_parsed[dbnm] = [db_name, db_filepath, db_format, str(db_to_import), 'config']

    #
    # 2) Get the databases specified in a manifest (if appropriate):
    #
    if options.db_import_manifest is not None and from_file_if_exists:
        sf = open(options.db_import_manifest, 'r')
        sf.readline()  # skip header

        lno = 1
        for ln in sf:
            if len(ln.strip())<=1:
                continue
            f = ln.strip().split('\t')
            if len(f)<3:
                logging.warning('In Manifest: line %d cannot be parsed (fewer than 3 tab-delimited fields). Line as read: \n\t%s' % (lno, ln.strip()))
            if f[0] in db_import_manifest_parsed:
                logging.info('Database %s was given in both the config and manifest file. Manifest will be used.')
            db_import_manifest_parsed[f[0]] = [f[0], f[1], f[2], f[3], 'manifest']
            lno += 1

    for flds in db_import_manifest_parsed.values():
        # logging.debug(str(flds))
        db_name = flds[0]
        db_filepath = os.path.abspath(os.path.expanduser( flds[1] ))
        # db_filepath = os.path.join(flds[1], flds[2])
        db_format = flds[2]
        db_to_import = bool(int(flds[3]))
        db_spec_source = flds[4]
        if db_to_import:
            if db_name.lower()=='refseq' and not skip_refseq:   # If the line is for RefSeq, do it differently...
                new_refseq_dir = os.path.abspath(os.path.expanduser( flds[1] ))
                if os.path.isdir(new_refseq_dir):
                    logging.debug('found RefSeq in the manifest list. Replacing config refseq folder with:\n\t%s' % new_refseq_dir)
                    options.refseq_folder = new_refseq_dir
                    refseq_in_source_list = True
                else:
                    logging.warning(' - RefSeq (line %s) has path column that is not a valid folder:\n\t%s' % (line_no, new_refseq_dir))

            else:  # ...otherwise send it to the text parser
                if os.path.isfile(db_filepath):
                    db_tuple = make_tuple_with_metadata(db_filepath, db_name, db_format)
                    db_tuple += (db_spec_source,)
                    db_import_manifest_output.append(db_tuple)
                else:
                    logging.debug(' - File in source list does not exist (line %s, db=%s)\n\t%s' % (line_no, db_name, db_filepath))
                    no_file_errors.append((db_filepath, db_name, db_format, db_spec_source))
        else:   # Add to the skips list
            not_to_import.append((db_filepath, db_name, db_format, db_spec_source))
        line_no += 1

    if not skip_refseq:
        if options.refseq_folder is not None:
            refseq_file_list = db_import_search_refseq_dir(options.refseq_folder)
            refseq_ct = len(refseq_file_list)
            for ftup in refseq_file_list:
                db_import_manifest_output.append(ftup)

    # Print some info about what we found:
    total_ct = len(db_import_manifest_output)
    other_ct = total_ct - refseq_ct
    logging.debug(' - db_import_manifest (including config) yielded the following to be imported:')
    logging.debug('     %s RefSeq database files' % refseq_ct)
    logging.debug('     %s other database files' % other_ct)
    return db_import_manifest_output, no_file_errors, not_to_import

def db_import_manifest_print_specs():
    '''
    Prints the help description for the specs of the database source roster (i.e. db_import_manifest).
    :return:
    '''
    mydesc = 'A roster of new databases can be specified using a tab-delimited text file. In order to use this format, ' \
           'a file path must be specified either at the command line (using the flag \'-dbs <PATH>\') or in the config ' \
           'file (under the [paths] section, named \'path_to_db_import_manifest\').'

    hstr='''
%s
 
The specified file must be tab-delimited text, with a single header row. Each database is given in a single row, with the following fields (in order):
    DB_Name:  Simple string identifying the database (e.g. 'RefSeq_v90' or 'kaiju_db_nr_euk')
    Path:     Path to the file. If this is not an absolute path it will be considered relative to the working folder.
    Format:   The name of the format spec (from the config file) to use.
    Import:   Set to 0 if the row should be skipped during processing, 1 otherwise.''' % mydesc
    print(mydesc)
    if options.logfile is not None:
        logging.info(mydesc)

def db_import_search_refseq_dir(custom_refseq_dir = None):
    '''
    Combs through the folder pointed to by the "options.refseq_folder" parameter for files matching '*release*.*' and
    returns the file-info-tuples associated with them.
    TODO: Changes this to use a glob instead of os.walk
    :return:
    '''
    refseq_tuple_list = []
    refseqfiles = []
    if custom_refseq_dir is None:
        refseq_dir_abs = os.path.abspath(options.refseq_folder)
    else:
        refseq_dir_abs = os.path.abspath(os.path.expanduser(custom_refseq_dir))

    for r, d, f in os.walk(refseq_dir_abs):
        for refseqfile in f:
            refseqfiles.append(os.path.join(refseq_dir_abs, r, refseqfile))

    for fpath in refseqfiles:
        fp, fn = os.path.split(fpath)
        if fn[-3:] != '.gz':
            try:
                version = fn.split(".")[0].split("release")[-1]
            except:
                continue
            refseq_tuple_list.append(make_tuple_with_metadata(fpath, 'RefSeq_v' + version, 'refseq') + ('refseq_folder',))
    return refseq_tuple_list

def parse_delimited_text_general(file_path, delimiter='\t', keycol_index = 0, header_rows = 0, valcol_index = None,
                                 convert_key_col_to_int = True, result_as_set = False):
    '''
    For a delimited text data file, converts specified columns into a dictionary where the (K,V) pairs are taken from
    the items in each row of the specified columsn. So the dict is:
        { <row_1_key_column>: <row_1_val_column>,
          <row_2_key_column>: <row_2_val_column>, ... }
    :param file_path:   absolute path to the target text file
    :param delimiter:   text data delimiter (default: '\t')
    :param keycol_index:  column index to be the key (default: 0)
    :param valcol_index: column index to be the value. If omitted, values default to 1. If result_as_set is True, this
                            argument is ignored (default = None)
    :param header_rows: number of rows to skip as a header (default = 0)
    :param convert_key_col_to_int: if True, coerces keys to be integer (default: True)
    :param result_as_set: if True, only key column is returned, as a set object (default: False)
    :return:
    '''
    kci = int(keycol_index)
    file_open = open(file_path, 'r')
    for i in range(header_rows):
        file_open.readline()

    def int_if_possible(nstr):
        try:
            return int(nstr)
        except:
            return nstr

    keyval_list = []  # can be just a list of keys if valcol_index is None
    if valcol_index is None:
        for ln in file_open:
            ln_key = ln.strip().split(delimiter)[kci]
            keyval_list.append(ln_key)
    else:
        vci = int(valcol_index)
        for ln in file_open:
            cols = ln.strip().split(delimiter)
            keyval_list.append((cols[kci], cols[vci]))
    file_open.close()

    if result_as_set:
        if valcol_index is None:
            if convert_key_col_to_int:
                return set(map(int_if_possible, keyval_list))
            else:
                return set(keyval_list)
        else:
            if convert_key_col_to_int:
                return set(map(lambda x: int_if_possible(x[0]), keyval_list))
            else:
                return set(map(lambda x: x[0], keyval_list))
    else:
        if valcol_index is None:
            keyval_list = list(map(lambda x: (x,1), keyval_list))
        if convert_key_col_to_int:
            return dict(map(lambda x: (int_if_possible(x[0]),x[1]), keyval_list))
        else:
            return dict(keyval_list)
    return False

def parse_generic_file_by_format(file_path, format):
    '''
    This is an intermediate function to take a general file path and its format and figure out how to parse it. Mostly
    it just looks up the format in the delimited-file specs, but this function is also a placeholder in case
    more exotic file parsing is required (as it apparently was in the old version). Returns taxon IDs as a set.
    :param file_path:
    :param format:
    :return:
    '''
    if format not in options.delimited_format_parse_specs:
        return False
    spec = options.delimited_format_parse_specs[format]
    delim = spec[0]
    taxcol = spec[1]
    headskip = spec[2]
    return parse_delimited_text_general(file_path, delim, taxcol, headskip, result_as_set=True)

def containment_dict_build(source_file_tuples, clobber_old = False, save_replaced = True, save_backup = False):
    '''
    Takes a list of file-metadata tuples and builds up a containment dictionary from them. Unless clobber_old is
    specified it will build upon the existing containment file. It will replace any where the name already exists
    but the file is different for some reason.
    :param source_file_tuples:
    :param clobber_old:
    :return:
    '''
    logging.info('Function: containment_dict_build()...')
    my_time_fmt_str = '%Y-%m-%d %H:%M:%S'
    file_time_fmt_str = '%Y%m%d_%H%M%S'
    if save_backup:
        logging.info(' - Saving backup containment file to: %s')
        backup_filename = containment_dict_backup()
        logging.info(' - Saving backup containment file to: %s' % backup_filename)

    # Read old containment_dict and take inventory
    if not clobber_old:
        if os.path.isfile(options.containment_metadata_json_path):
            logging.info(' - Reading previous containment file')
            contain = containment_dict_read_previous()
        else:
            logging.info(' - containment file does not exist: %s' % options.containment_metadata_json_path)
            contain = {}
    else:
        contain = {}
    contain_replaced = {}

    isrefseq = list(map(lambda x: 1 if x[0][:6].lower()=='refseq' else 0, source_file_tuples))
    refseq_ct = sum(isrefseq)
    other_ct = len(isrefseq) - refseq_ct

    logging.info(' - Parsing databases ( %s RefSeq, %s other )' % (refseq_ct, other_ct))

    import_file_tuple_list = containment_dict_show_build_plan(source_file_tuples, contain, clobber_old=clobber_old)

    for ft in import_file_tuple_list:
        db = {
            'name': ft[0],
            'file_path': ft[1],
            'format': ft[2],
            'file_size': ft[3],
            'file_mod_time': ft[4],
            'file_mod_time_str': '%s' % datetime.datetime.fromtimestamp(int(ft[4])),
            'comments': ''
        }
        fo, fn = os.path.split(db['file_path'])
        logging.debug(' - Database %s, (file=%s, format=%s)' % (db['name'], fn, ft[2]))
        # If it already exists in the contain file, check if it came from the same original file (first by file
        #   properties, then by md5 hash if not sure).
        status_str =  '     '
        db['md5'] = get_file_md5_digest(db['file_path'])

        if db['name'] in contain:
            contain_replaced[db['name']] = contain.pop(db['name'])
            contain_replaced[db['name']]['comments'] +=  'replaced on: %s, ' % datetime.datetime.now().strftime(my_time_fmt_str)

        db['taxid_set']=parse_generic_file_by_format(db['file_path'], db['format'])
        setlen = len(db['taxid_set'])
        db['num_taxa']=setlen
        status_str = status_str + (' %9s taxa |' % str(setlen))

        db['date_parsed']=datetime.datetime.now().strftime(my_time_fmt_str)
        contain[db['name']] = db
        logging.debug(status_str)

    if save_replaced and len(contain_replaced)>0:
        logging.debug(' - Saving replaced dictionaries...')
        contain_rep_filename = options.containment_metadata_json_path + '.replaced.' + datetime.datetime.now().strftime(file_time_fmt_str)
        with open(contain_rep_filename, 'wb') as contrep:
            pickle.dump(contain_replaced, contrep)

    return contain

def containment_dict_show_build_plan(source_file_tuples, contain, hide_older_refseq=True, quiet = False, clobber_old = False):
    '''
    Compares the contents of the source file list and the containment_dict, showing status for eventual
    build command.
    :param source_file_tuples: list of tuples as (name, path, format, size, mtime)
    :param contain:
    :return:
    '''
    #column widths:
    max_name_width = 60
    insources_width = 12
    incontain_width = 7
    status_width = 10

    source_file_tuples_dict = {}
    for ft in source_file_tuples:
        source_file_tuples_dict[ft[0]]=ft

    #combine the names
    all_db_names = list(set(source_file_tuples_dict.keys()).union(set(contain.keys())))

    #define output formatter
    name_width = min(max_name_width, max(map(len, all_db_names)))
    def makeline(nm, insrc, incon, statwid):
        templt = ' %s | %s | %s | %s'
        return templt % (nm[:name_width].ljust(name_width), insrc[:insources_width].ljust(insources_width),
                         incon[:incontain_width].ljust(incontain_width), statwid)

    if not clobber_old:
        print('Comparison of containment_dict and source files to be added:\n\n')
        print(makeline('Database', 'In', 'In', 'Action'))
        print(makeline('Name', 'Manifest', 'Contain', 'to be Taken'))
        print(makeline('-'*name_width, '-'*insources_width, '-'*incontain_width, '-'*status_width))
    else:
        print('No comparison to be done, \'--clobber\' was specified...')
        print('-------------------------------------------------------')

    import_list_file_tuples = []

    if clobber_old:
        import_list_file_tuples = source_file_tuples
    else:
        #compare the sources and the containment_dict
        for nm in all_db_names:
            rpt_nm = nm; rpt_incon = ''; rpt_insrc = ''; rpt_status = '';

            if not nm in source_file_tuples_dict:   # name in containment_dict.json, not in source_list
                rpt_insrc = 'no'
                if not nm in contain:
                    rpt_incon = 'no'
                    rpt_status = '(strange...this shouldn\'t happen)'
                else:
                    rpt_incon = 'YES'
                    rpt_status = '(leave in)'
            else:
                rpt_insrc = 'YES (' + source_file_tuples_dict[nm][5] + ')'

                if not nm in contain:       # in sources, not in containment_dict.json
                    rpt_incon = 'no'
                    rpt_status = 'IMPORT'
                    import_list_file_tuples.append(source_file_tuples_dict[nm])
                else:                       # in both
                    rpt_incon = 'YES'
                    sf_tup = source_file_tuples_dict[nm]
                    old_ver = contain[nm]
                    if old_ver['file_path']==sf_tup[1] and old_ver['file_size']==sf_tup[3] and old_ver['file_mod_time']==sf_tup[4]:
                        rpt_status = '(unchanged, leave in)'
                        if not quiet:
                            print(makeline(rpt_nm, rpt_insrc, rpt_incon, rpt_status))
                        continue
                    if not quiet:
                        logging.debug('getting md5 of %s' % sf_tup[1])
                    if 'md5' in old_ver.keys():
                        new_md5 = get_file_md5_digest(sf_tup[1])
                        if new_md5==old_ver.get('md5',None):
                            rpt_status = '(same md5, leave in)'
                            if not quiet:
                                print(makeline(rpt_nm, rpt_insrc, rpt_incon, rpt_status))
                            continue
                    import_list_file_tuples.append(sf_tup)
                    rpt_status = 'REPLACE (new file)'
            if not quiet:
                print(makeline(rpt_nm, rpt_insrc, rpt_incon, rpt_status))

    # print final list of actions:
    print('\nSummary of sources to be imported: (count = %d)' % len(import_list_file_tuples))
    for ift in import_list_file_tuples:
        print('   %s\t%s' % (ift[0], ift[1]))

    return import_list_file_tuples

def containment_dict_summary(contain, all_refseq = False, print_to_console = False):
    '''
    Generates a multi-line string summarizing the contents of the containment dictionary.
    :param contain: containment dictionary object
    :param all_refseq: if False, only print info for the latest refseq
    :param print_to_console: if True, prints the value using 'print()' as well as returning it.
    :return:
    '''
    summ_str = 'Containment Dictionary Summary (all_refseq = %s)\n   ***   \n' % all_refseq
    mainkeys = []
    refseq_keys = []
    refseq_vers = []
    latest_ver_num = 0
    latest_ver_key = ''
    for k in contain.keys():
        if k[:8].lower() == 'refseq_v':
            refseq_keys.append(k)
            rsv = int(k[8:])
            refseq_vers.append(rsv)
            if rsv > latest_ver_num:
                latest_ver_num = rsv
                latest_ver_key = k
        else:
            mainkeys.append(k)
    tot_db_ct = len(mainkeys) + len(refseq_keys)
    summ_str = summ_str + '    # Databases: %d (%d RefSeq, %d other)\n' % (tot_db_ct, len(refseq_keys), len(mainkeys))
    summ_str = summ_str + '  Latest RefSeq: v%d\n\n' % latest_ver_num
    if not all_refseq:
        mainkeys.append(latest_ver_key)
    else:
        for rsk in refseq_keys:
            mainkeys.append(rsk)
    # make the summary string:
    longest_key_len = max(map(len, mainkeys))
    dbname_width_max = 60
    numtaxa_width = 8
    dtparsed_width = 20
    dbname_width = min(dbname_width_max, longest_key_len+1)
    makeline = lambda dbn, nt, dt: ' %s  %s  %s\n' % (dbn[:dbname_width].ljust(dbname_width), nt.rjust(numtaxa_width), dt)

    summ_str = summ_str + "Main Databases:\n"
    summ_str = summ_str + makeline('Database Name', '# Taxa', 'Date Parsed')
    summ_str = summ_str + makeline('-'*dbname_width, '-'*numtaxa_width, '-'*dtparsed_width)
    # summ_str = summ_str + "  %s   %9s taxa    %s\n" % (lp_key('Database Name'), '# of', 'Date Parsed')
    # summ_str = summ_str + "  %s   %9s-----    %s\n" % (lp_key('-------------'), '----', '-----------')
    for mk in mainkeys:
        summ_str = summ_str + makeline(mk, str(contain[mk]['num_taxa']), contain[mk]['date_parsed'])
        # summ_str = summ_str + "  %s:  %9s taxa    %s\n" % (lp_key(mk), str(contain[mk]['num_taxa']), contain[mk]['date_parsed'])
    summ_str = summ_str + '\n'

    if print_to_console:
        print(summ_str)
    return summ_str

def containment_dict_backup():
    '''
    Makes a copy of the containment_dict.json file called 'containment_dict.json.backup' in the same folder. If a file
    by that name already exists, it tacks on a 1 and tries, then a 2, etc... to 1000.
    :return:
    '''
    if options.containment_metadata_json_path is None:
        logging.error('cannot backup containment file: options.containment_metadata_json_path is None')
        return
    backup_path = options.containment_metadata_json_path + '.backup'
    if os.path.isfile(backup_path):
        ct = 1
        while True:
            backup_path2 = backup_path + ct
            if not os.path.isfile(backup_path2):
                backup_path = backup_path2
                break
            else:
                ct += 1
                if ct > 1000:
                    break
    bfp, bfn = os.path.split(backup_path)
    shutil.copyfile(options.containment_metadata_json_path, backup_path)
    return bfn

def containment_dict_update_all_md5s():
    '''helper routine to refresh all the md5s, for debugging.'''
    contain = containment_dict_read_previous()
    for k in contain.keys():
        fp = contain[k]['file_path']
        nm = contain[k]['name']
        if os.path.isfile(fp):
            logging.debug('getting md5 for %s (%s)' % (nm, fp))
            mdfive = get_file_md5_digest(fp)
            contain[k]['md5']=mdfive
        else:
            logging.debug('file path for %s does not exist (%s)' % (nm, fp))
            contain[k]['md5']=''
    containment_dict_save(contain)

def containment_dict_save(contain, as_json=True):
    if options.containment_metadata_json_path is None:
        logging.error('cannot save containment file: options.containment_metadata_json_path is None')
        return

    if not as_json:
        logging.info('Saving containment dictionary to %s' % options.containment_metadata_json_path)
        with open(options.containment_metadata_json_path, 'wb') as contpick:
            pickle.dump(contain, contpick)
    else:
        # to save it as a json we have to convert the sets to lists. we'll keep them in a separate
        #   dictionary so that it stores at the end of the file. That way the metadata at the start
        #   will be human-readable
        fpcjson = os.path.splitext(options.containment_metadata_json_path)[0] + '.json'
        logging.info('Saving containment dictionary to %s' % fpcjson)
        contain_dcpy = copy.deepcopy(contain)
        contain_taxid_lists = {}
        for k in contain_dcpy.keys():
            contain_taxid_lists[k] = list(contain_dcpy[k].pop('taxid_set'))
        jsf = open(fpcjson, 'w')
        json.dump({'metadata': contain_dcpy, 'taxid_lists': contain_taxid_lists}, jsf, indent=2)
        jsf.close()

def containment_dict_read_previous(as_json=True):
    '''
    Reads the previously written containment dictionary if the file exists. If it does not, returns an empty
    python dictionary.
    :return:
    '''
    if options.containment_metadata_json_path is None:
        logging.error('cannot read containment file: options.containment_metadata_json_path is None')
        return {}
    if not as_json:
        if not os.path.isfile(options.containment_metadata_json_path):
            logging.error('cannot read containment file: options.containment_metadata_json_path %s is not a valid file path' % options.containment_metadata_json_path)
            return {}
        with open(options.containment_metadata_json_path, 'rb') as cf:
            cfold = pickle.load(cf)
        return cfold
    else:
        fpcjson = os.path.splitext(options.containment_metadata_json_path)[0] + '.json'
        if not os.path.isfile(fpcjson):
            logging.error('cannot read containment file in json form: options.containment_metadata_json_path (as json) %s is not a valid file path' % fpcjson)
            return {}
        with open(fpcjson, 'r') as jsf:
            cf_tmp = json.load(jsf)
        # convert the lists at the end back to sets in the main object:
        for k in cf_tmp['metadata'].keys():
            cf_tmp['metadata'][k]['taxid_set'] = set(cf_tmp['taxid_lists'][k])
        return cf_tmp['metadata']

def ncbi_taxonomy_parse_file():
    '''
    Opens the NCBI nodes.dmp file from the taxdump FTP site. Parses it into a dictionary with
    key/vals in the form:
        { <taxon_id>: (<parent_taxon_id>, <level>, <assigned_at_species>), ...}
    :return:
    '''
    if options.fpath_ncbi_tax_nodes is not None:
        if not os.path.isfile(options.fpath_ncbi_tax_nodes):
            logging.error('The path specified in the config file for the ncbi taxonomy file could not be opened. Either ')
            logging.error('  check that the path is correct in the config file or use the command line argument ')
            logging.error('  \'--download_ncbi_taxonomy\' to download and extract a fresh copy.')
            logging.error('   -> nodes.dmp path from config: %s' % options.fpath_ncbi_tax_nodes)
            return
    ncbi_f = open(options.fpath_ncbi_tax_nodes, 'r')
    # ncbi_dict = dict(map(lambda x: (int(x[0]), (int(x[2]), x[4], int(x[30]))), map(lambda x: x.strip().split('\t'), ncbi_f.readlines())))
    ncbi_dict = dict(map(lambda x: (int(x[0]), (int(x[2]), x[4])),
                         map(lambda x: x.strip().split('\t'), ncbi_f.readlines())))
    return ncbi_dict

def ncbi_taxonid_to_lineage_vector(taxid, ncbi_dict):
    '''
    takes a taxon ID and returns a length-33 vector containing all the taxon IDs at every higher level of the
    lineage. For levels where there is no taxon in the lineage, default value is -1. Fills in the levels of
    the lineage by recursively lookup up the parents and parent-ranks until taxon_id 1 (root) is reached.
    :param taxid: (int) Taxon ID to construct the lineage for.
    :param ncbi_dict:  (dict) NCBI Taxonomy Nodes Dictionary:
            {
                <taxon_id>: (<parent_taxon_id>, <level>, <assigned_at_species>),
                ...
            }
    :return: returns a 33-tuple where each entry represents one of the taxonomic levels. If the entry is -1, then
            the lineage for <taxid> is not assigned at that level. If it is a different number, that is the taxon
            in that level of the lineage.
    '''
    lineage = [-1,]*len(ncbi_tax_levels)

    tdata = ncbi_dict[taxid]
    lineage[rank2index(tdata[1])] = taxid
    next = tdata[0]
    level_ct = 1
    while next > 1:
        tdata = ncbi_dict[next]
        lineage[rank2index(tdata[1])] = next
        next = tdata[0]
        level_ct += 1
        if level_ct > 100:
            print ("taxid %s has a lineage that is supposedly 100+ levels")
            break
    return lineage

def ncbi_taxonomy_make_full_vector_lookup(ncbi_dict):
    '''
    Makes a dictionary where the values are full-lineage vectors instead of the recursive lookup
    :param ncbi_dict:
    :return:
    '''
    ncbi_tax_fullvec = {}
    for k in ncbi_dict.keys():
        ncbi_tax_fullvec[k] = ncbi_taxonid_to_lineage_vector(k, ncbi_dict)
    return ncbi_tax_fullvec

def ncbi_taxonomy_download_taxdmp():
    '''
    This is a utility function to download and extract the required nodes.dmp file with the relevant
    details of the NCBI taxonomy, if that has not already been done. If the containing folder of the
    option 'fpath_ncbi_tax_nodes' does not exist, but is a subfolder of the working_folder, then
    it is created first. Otherwise an error is raised.
    :return:
    '''
    ncbi_fold, taxdmp_fn = os.path.split(options.fpath_ncbi_tax_nodes)
    ncbi_fold_par, ncbi_foldname = os.path.split(ncbi_fold)
    logging.debug('taxdmp_fn = %s' % taxdmp_fn)
    logging.debug('ncbi_fold = %s' % ncbi_fold)
    logging.debug('ncbi_foldname = %s' % ncbi_foldname)
    logging.debug('ncbi_fold_par = %s' % ncbi_fold_par)

    if not os.path.isdir(ncbi_fold):
        if os.path.abspath(ncbi_fold_par)==options.working_folder:
            os.mkdir(ncbi_fold)
        else:
            logging.error('The folder attached to the path_to_ncbi_taxonomy_nodes is not a valid folder ')
            logging.error('and would not be a subfolder of the specified work folder, so it cannot be   ')
            logging.error('created:')
            logging.error('     options.fpath_to_ncbi_tax_nodes: %s' % options.fpath_ncbi_tax_nodes)
            logging.error('     folder split from path above: %s' % ncbi_fold)
            logging.error('     work folder: %s' % options.working_folder)
            return
    # download the taxdmp.zip file from NCBI:
    taxdmp_dest_path = os.path.join(ncbi_fold, 'taxdmp.zip')
    logging.debug('taxdmp_dest_path = %s' % taxdmp_dest_path)

    import urllib.request, zipfile, time
    if options.MY_DEBUG and os.path.isfile(taxdmp_dest_path) and os.stat(taxdmp_dest_path).st_size==51998231:
        print('(...skipping the re-download during debug...)')
    else:
        ncbi_taxdmp_url = 'ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip'
        logging.debug('downloading taxdmp.zip from FTP site:')
        urq = urllib.request.Request(ncbi_taxdmp_url)
        with urllib.request.urlopen(urq) as resp:
            with open(taxdmp_dest_path,'wb') as taxdmp_f:
                shutil.copyfileobj(resp, taxdmp_f)

    # wait 5 seconds to avoid file conflicts:
    for i in range(1,6):
        print('\rDone downloading. Waiting 5 Seconds: %d' % i, end='')
        time.sleep(1)
    print('')

    # extract the 'nodes.dmp' file only:
    tdzip = zipfile.ZipFile(taxdmp_dest_path)
    assert 'nodes.dmp' in tdzip.namelist(), 'The archive downloaded does not contain a file called \'nodes.dmp\'.'
    # print(tdzip.namelist())
    td_norm_path=tdzip.extract('nodes.dmp', ncbi_fold)

    logging.info('Success! The file \'nodes.dmp\' from the NCBI taxonomy was successfully downloaded ')
    logging.info('  and extracted to the following path:')
    logging.info('      %s' % td_norm_path)
    if td_norm_path != options.fpath_ncbi_tax_nodes:
        logging.warning('  NOTE that the saved path is different from the path specified in the config, ')
        logging.warning('  probably due to pathname normalization. This run will proceed but the config ')
        logging.warning('  must be corrected for the DBQT to function properly in the future.')
        logging.warning('      path in config file: %s' % options.fpath_ncbi_tax_nodes)
        # options.fpath_ncbi_tax_nodes = td_norm_path


def run_inspect_previous_containment_dict():
    '''
    Simple routine to open the previous containment_dict.json file and print a description of what
    it contains.
    :return:
    '''
    pcd = containment_dict_read_previous()
    pcd_sum = containment_dict_summary(pcd)
    print(pcd_sum)

def run_recruit_sources_print_report():
    '''
    Simple routine to check the DB sources that will be found when the sources and/or refseq
    folder is parsed. Prints a report to the logger.
    :return:
    '''
    rpt = '\n'
    sft, nfe, skips = db_import_manifest_read()
    refseq_list = []
    main_list = []
    latest_refseq_version = -1
    latest_refseq_index = None
    config_db_source_count = 0
    manifest_db_source_count = 0
    refseqfold_db_source_count = 0
    for db_ind in range(len(sft)):
        db = sft[db_ind]
        if db[0][:6].lower()=='refseq':
            refseq_list.append(db)
            ver = int(db[0][8:])
            if ver > latest_refseq_version:
                latest_refseq_version = ver
                latest_refseq_index = db_ind
        else:
            if db[4] == 'config':
                config_db_source_count += 1
            elif db[4] == 'manifest':
                manifest_db_source_count += 1
            elif db[4] == 'refseq_folder':
                refseqfold_db_source_count += 1
            main_list.append(db)

    if len(refseq_list)>0:
        main_list.append(sft[latest_refseq_index])

    rpt = rpt + 'Checking for Manifest & Refseq paths...\n'
    rpt = rpt + '    Manifest File: %s\n' % options.db_import_manifest
    rpt = rpt + '          (source): %s\n' % options.source_db_import_manifest
    rpt = rpt + '    RefSeq folder: %s\n' % options.refseq_folder
    rpt = rpt + '          (source): %s\n' % options.source_refseq
    rpt = rpt + '\n'
    rpt = rpt + 'Config/Manifest/Refseq_folder Data Source Counts:'
    rpt = rpt + '       Config File: %s\n' % config_db_source_count
    rpt = rpt + '          Manifest: %s\n' % manifest_db_source_count
    rpt = rpt + '     Refseq Folder: %s\n' % refseqfold_db_source_count
    rpt = rpt + '\n'
    rpt = rpt + 'Data Sources to be Imported:\n'
    for db in main_list:
        rpt = rpt + '   %s\t%s\n' % (db[0], db[1])
    if len(refseq_list)>1:
        rpt = rpt + '   (...%s other RefSeq versions not shown)\n' % (len(refseq_list)-1)

    logging.info(rpt)

def config_check_exists_else_copy():
    '''
    Checks whether the file 'dbqt_config' exists in the \scripts folder. If not, makes a copy of the version
    packaged in the 'doc' folder (considered a default).
    :return:
    '''
    scripts_fold = os.path.split(os.path.abspath(__file__))[0]
    dbqt_config_path = os.path.join(scripts_fold, 'dbqt_config')
    dbqt_config_doc_path = os.path.join(scripts_fold, 'doc', 'dbqt_config_doc')
    if not os.path.isfile(dbqt_config_path):
        shutil.copy(dbqt_config_doc_path, dbqt_config_path)

def set_config_workingfolder_to_thisone():
    '''
    Changes the value of the working_folder field of the dbqt_config to be the current folder
    :return:
    '''
    config_check_exists_else_copy()
    scripts_fold = os.path.split(os.path.abspath(__file__))[0]
    logging.debug('Updating working_folder in dbqt_config to be %s' % scripts_fold)
    cfggen = configparser.ConfigParser()
    cfggen.read('dbqt_config')
    wfcur = cfggen.get('paths','working_folder')
    cfggen.set('paths','working_folder',scripts_fold)
    with open('dbqt_config','w') as dc:
        cfggen.write(dc)

def util_query_taxid_in_contain(taxid, contain, main_list, taxid_species_ancestor):
    '''
    Returns a vector indicating the results. 1 = present, 2 = not present but species-level ancestor is, 0 = neither.
    :param taxid:
    :param contain:
    :param main_list:
    :return:
    '''
    out = []
    for nm in main_list:
        if taxid in contain[nm]['taxid_set']:
            out.append(1)
        elif taxid_species_ancestor in contain[nm]['taxid_set']:
            out.append(2)
        else:
            out.append(0)
    return out

def run_query_taxids_against_containment():
    '''
    Runs the same function as the old query tool. Takes taxon IDs and outputs which of them are in which db.
    :return:
    '''
    # PARSE TAXON ID LIST
    taxids = []
    if options.taxid_list is None:
        options.parser_store.print_help()
        sys.exit(1)
    elif options.taxid_list == 'stdin':
        # while True:
        #     foo = input()
        for foo in sys.stdin:
            if len(foo.strip())==0:
                break
            taxids.append(int(foo.strip()))
    elif os.path.isfile(options.taxid_list):
        tf = open(options.taxid_list, 'r')
        tfl = tf.readlines()
        taxids = list(map(lambda x: int(x.strip()), tfl))
    else:
        try:
            taxids.append(int(options.taxid_list))
        except:
            logging.error('The taxonID list argument \'-t\' must be either a single integer string, or \'stdin\', or'
                          'a valid file path')
            options.parser_store.print_help()
            sys.exit(1)

    # OPEN CONTAINMENT FILE AND NCBI TAXONOMY REFERENCE
    contain = containment_dict_read_previous()
    if options.all_refseq_versions:
        main_keys = list(contain.keys())
    else:
        main_keys = util_filter_out_main_dbnames(contain.keys())

    max_key_len = max(map(len, main_keys))
    ncbi_d = ncbi_taxonomy_parse_file()
    species_ind = rank2index('species')
    results = {}

    # RUN THE CHECKS:
    for taxid in taxids:
        taxid_spec = ncbi_taxonid_to_lineage_vector(taxid, ncbi_d)[30] #will be -1 if taxid is above species, but that's fine
        results[taxid] = tuple([taxid, ncbi_d[taxid][1],] + util_query_taxid_in_contain(taxid, contain, main_keys, taxid_spec))

    results = list(results.values())
    if len(results)==1:
        rpt = '\n'
        rpt = rpt + 'Taxon ID: %10s (rank: %s)\nDB results:\n' % (results[0][0], ncbi_d[results[0][0]][1])
        for mki in range(len(main_keys)):
            mk = main_keys[mki]
            if results[0][mki+2] ==0:
                mystr = '--'
            elif results[0][mki+2]==1:
                mystr = 'Yes'
            elif results[0][mki+2]==2:
                mystr = '(contains parent species)'
            rpt = rpt + (('%' + str(max_key_len+1) + 's') % mk) + ': ' + mystr + '\n'
        print(rpt)
    else:
        rpt = '\nDB Column Names:\n'
        for mki in range(len(main_keys)):
            rpt = rpt + ' %3s: ' % (mki+1) + main_keys[mki] + '\n'

        rpt = rpt + '\n'
        rpt = rpt + ('%9s' % 'taxid') + ' ' + ('%9s' % 'rank') + ' '
        rpt = rpt + ' '.join(map(str,range(len(main_keys)))) + '\n'
        for r in results:
            rpt = rpt + '%9s %9s ' % (r[0], r[1])
            mystr = ' '.join(map(str,r[2:]))
            rpt = rpt + mystr.replace('0', '-') + '\n'
        print(rpt)

def run_random_taxon_sample_to_file():
    '''
    Just creates a file with a list of randomly selected taxon IDs. For testing
    :param filepath:
    :param numtaxa:
    :return:
    '''
    if options.output_path is None:
        logging.error('output path must be specified to do the random taxon dump.')
    outf = open(options.output_path, 'w')
    nd = ncbi_taxonomy_parse_file()
    alltax = list(nd.keys())
    import random
    sometax = random.sample(alltax, options.num_taxa)
    for t in sometax:
        c=outf.write('%s\n' % t)
    outf.close()
    logging.info('wrote %s randomly selected taxon IDs to the file %s' % (options.num_taxa, options.output_path))

def verify_alg_params_present(custom_list = None, from_print_argparse = False):
    '''
    Checks to make sure all the necessary parameters for a given algorithm are provided.
    :return:
    '''
    if options.command_arg_selected is None:
        logging.error('Command argument not identified...this shouldn\'t happen')
        sys.exit(1)
    else:
        mycmd = options.command_arg_selected

    reqlist = options.command_arg_parameter_reqs[mycmd]
    if custom_list is not None:
        reqlist += custom_list

    for req in reqlist:
        # reqname = options.cfg_parameter_short_ids[req]
        reqname = req
        reqval = getattr(options, reqname, None)
        if reqval is None:
            logging.error('Command argument \'%s\' requires that %s be set, but it is currently None. Printing config diagnostics:' % (mycmd, reqval))
            if not from_print_argparse:
                run_print_argparse_results()
            sys.exit(1)
        if options.MY_DEBUG:
            logging.debug('requirement = %s, value = %s' % (reqname, reqval))

def verify_algorithm_argument(print_cmd_list=False, return_cmd_list=False):
    '''
    Goes through the option list to make sure at most one procedure argument was given. Sets default if omitted.
    NOTE: in order for this function to work, command arguments in long form MUST start with 'cmd_'
    :return:
    '''
    cmds = [i for i in vars(options).keys() if i[:4]=='cmd_']
    if print_cmd_list:
        print('')
        for c in cmds:
            print('%s' % c)
        print('')
    if return_cmd_list:
        return cmds

    cmd_ct = 0
    for c in cmds:
        if vars(options)[c]:
            cmd_ct += 1
            options.command_arg_selected = c
    if cmd_ct > 1:
        options.parser_store.print_help()
        sys.exit(1)
    elif cmd_ct == 0:
        options.cmd_query_taxids = True
        options.command_arg_selected = 'cmd_query_taxids'


def main():
    command_args_parse()
    if options.cmd_setup:
        ncbi_taxonomy_download_taxdmp()
        return

    if options.cmd_inspect_filelist:
        run_recruit_sources_print_report()
        return
    elif options.cmd_inspect_contain:
        run_inspect_previous_containment_dict()
        return
    elif options.cmd_compare_sources:
        sft, nfe, skips = db_import_manifest_read()
        contain = containment_dict_read_previous()
        imp_list = containment_dict_show_build_plan(sft, contain, clobber_old=options.clobber)
    elif options.cmd_build_containment:
        sft, nfe, skips = db_import_manifest_read()
        cd = containment_dict_build(sft, clobber_old=options.clobber)
        cd_sum = containment_dict_summary(cd)
        logging.info(cd_sum)
        containment_dict_save(cd)
    elif options.cmd_query_taxids:
        run_query_taxids_against_containment()
    elif options.cmd_random_taxon_sample:
        run_random_taxon_sample_to_file()
    elif options.cmd_print_db_import_manifest_specs:
        db_import_manifest_print_specs()
    elif options.cmd_print_debug_args_help:
        command_args_print_hidden_args_help()
    elif options.cmd_update_all_md5s:
        containment_dict_update_all_md5s()
    elif options.cmd_download_ncbi_taxonomy:
        ncbi_taxonomy_download_taxdmp()
    elif options.cmd_parseargs_report:
        run_print_argparse_results()

if __name__=='__main__':
    main()

