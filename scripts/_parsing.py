#! usr/bin/python3
import shutil, argparse, configparser, gzip, os, logging, sys, urllib.request, zipfile, time, textwrap


# Specifies how to parse file types that are just delimited text. Each entry is:
#   ( <Delimiter>, <Taxon ID Column>, <# Header Rows to Skip> )
#   NOTE: moved to the config file.
taxid_dict = {}
hidden_args_help_strings = {}


def set_config_workingfolder_to_thisone(options=None):
    '''
    Changes the value of the working_folder field of the dbqt_config to be the current folder
    :return:
    '''

    def config_check_exists_else_copy(options=None):
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

    config_check_exists_else_copy(options)
    scripts_fold = os.path.split(os.path.abspath(__file__))[0]
    logging.debug('Updating working_folder in dbqt_config to be %s' % scripts_fold)
    cfggen = configparser.ConfigParser()
    cfggen.read('dbqt_config')
    wfcur = cfggen.get('paths','working_folder')
    cfggen.set('paths','working_folder',scripts_fold)
    with open('dbqt_config','w') as dc:
        cfggen.write(dc)

def command_args_parse(options=None, dbqt_config=None):
    '''
    Separate function set up to create the argument parser and define all the arguments. Also executes parse_args at
    the very end.
    :return:
    '''

    dbqt_config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    dbqt_config.optionxform = lambda option: option

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
#                                                       'values, then closes.' \
#

    # TODO: delete me
    commandgroup.add_argument('--show_args_only', action='store_true', default=False, help=argparse.SUPPRESS)

    # Go in the following order:
    #   1) parse the command line arguments, 2) run sub below to define required config settings,
    #   3) post-process the arguments and config, 4) verify that the command argument has what's needed
    p.parse_args(namespace=options)         # (1)
    # This will terminate after the setup if that is called for  # (2)
    run_initial_setup(options=options, dbqt_config=dbqt_config) if options.cmd_setup else define_command_argument_requirements(options=options)

    options.parser_store = p
    command_args_postprocess(options=options, dbqt_config=dbqt_config)              # (3)
    verify_alg_params_present(options=options)             # (4)`
    if options.show_args_only:
        run_print_argparse_results(options=options)
        sys.exit(1)


def define_command_argument_requirements(options=None):
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

def verify_algorithm_argument(print_cmd_list=False, return_cmd_list=False, options=None):
    '''
    Goes through the option list to make sure at most one procedure argument was given. Sets default if omitted.
    NOTE: in order for this function to work, command arguments in long form MUST start with 'cmd_'
    :return:
    '''
    cmds = [i for i in vars(options).keys() if i[:4] == 'cmd_']
    if print_cmd_list:
        print('')
        for c in cmds:
            print('%s' % c)
        print('')
    if return_cmd_list:
        return cmds

def command_args_postprocess(options=None, dbqt_config=None):
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

    # global options
    containment_metadata_json_path_cfg, fpath_ncbi_tax_nodes_cfg, refseq_folder_cfg, db_import_manifest_cfg, working_folder_cfg = parse_dbqt_config_interpolated(options=options)
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

    verify_algorithm_argument(options=options)

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
    print(dbqt_config)
    for k in dbqt_config['formats'].keys():
        fmt = None
        # logging.debug('format %8s\t%s' % (k, dbqt_config.get('formats',k)))
        fmt=eval(dbqt_config.get('formats',k))
        # logging.debug('fmt is now: %s' % str(fmt))
        options.delimited_format_parse_specs[k]=fmt

def parse_dbqt_config_interpolated(options=None, dbqt_config=None):
    '''
    Parses the dbqt_config file using interpolition. If a config file is specified at the command line, options
    specified therein will override the default dbqt_config where duplicated.
    :return:
    '''

    def config_check_exists_else_copy(options=None, dbqt_config=None):
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

    dbqt_config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    dbqt_config.optionxform = lambda option: option

    if os.path.isfile('dbqt_config'):
        dbqt_config.read('dbqt_config')
    else:
        logging.warning('File `dbqt_config` has not been created, it is possible that setup has not been run. If this is the '
                        'case, please run the DQT with the `--setup` option first, or perform the equivalent steps manually.')
        logging.warning('Making a copy of the config found in the `doc` subfolder and using the query_tool.py folder '
                        'as the working_folder.')
        config_check_exists_else_copy(options=options)
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

def verify_alg_params_present(custom_list = None, from_print_argparse = False, options=None):
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

def run_print_argparse_results(config_params=True, alg_params=False, options=None):
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

def run_initial_setup(options=None, dbqt_config=None):
    '''
    :return:
    '''

    def ncbi_taxonomy_download_taxdmp(options=None):
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
            if os.path.abspath(ncbi_fold_par) == options.working_folder:
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

        if options.MY_DEBUG and os.path.isfile(taxdmp_dest_path) and os.stat(taxdmp_dest_path).st_size == 51998231:
            print('(...skipping the re-download during debug...)')
        else:
            ncbi_taxdmp_url = 'ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip'
            logging.debug('downloading taxdmp.zip from FTP site:')
            urq = urllib.request.Request(ncbi_taxdmp_url)
            with urllib.request.urlopen(urq) as resp:
                with open(taxdmp_dest_path, 'wb') as taxdmp_f:
                    shutil.copyfileobj(resp, taxdmp_f)

        # wait 5 seconds to avoid file conflicts:
        for i in range(1, 6):
            print('\rDone downloading. Waiting 5 Seconds: %d' % i, end='')
            time.sleep(1)
        print('')

        # extract the 'nodes.dmp' file only:
        tdzip = zipfile.ZipFile(taxdmp_dest_path)
        assert 'nodes.dmp' in tdzip.namelist(), 'The archive downloaded does not contain a file called \'nodes.dmp\'.'
        # print(tdzip.namelist())
        td_norm_path = tdzip.extract('nodes.dmp', ncbi_fold)

        logging.info('Success! The file \'nodes.dmp\' from the NCBI taxonomy was successfully downloaded ')
        logging.info('  and extracted to the following path:')
        logging.info('      %s' % td_norm_path)
        if td_norm_path != options.fpath_ncbi_tax_nodes:
            logging.warning('  NOTE that the saved path is different from the path specified in the config, ')
            logging.warning('  probably due to pathname normalization. This run will proceed but the config ')
            logging.warning('  must be corrected for the DBQT to function properly in the future.')
            logging.warning('      path in config file: %s' % options.fpath_ncbi_tax_nodes)
            # options.fpath_ncbi_tax_nodes = td_norm_path

    rich_format = "[%(filename)s (%(lineno)d)] %(levelname)s: %(message)s"
    logging.basicConfig(format=rich_format, level=logging.CRITICAL)
    endmsg = ''

    # Set the first config value to be the scripts folder
    set_config_workingfolder_to_thisone()
    time.sleep(1)
    endmsg = endmsg + 'Changing working_folder done...\n'

    # Parse the config for real
    c_json, fpathncbi, refseq_fo, sfl, workfold = parse_dbqt_config_interpolated(options=options, dbqt_config=dbqt_config)
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
    if os.path.isfile(options.containment_metadata_json_path) and (options.clobber is False):
        print('...skipping containment_dict.json.gz extraction because the given path already exists. To ')
        print('    force a re-extraction of the packaged containment file, use the option \'--clobber\'.')
    else:
        with open(os.path.join(options.working_folder, 'containment_dict.json.gz'), 'rb') as cdgz:
            with open(options.containment_metadata_json_path, 'wb') as cd:
                bct=cd.write(gzip.decompress(cdgz.read()))
    sys.exit(1)

def command_args_print_hidden_args_help():
    '''
    Several arguments are available at the command line for debugging but are not included in the default help menu.
    This function prints a special help menu for the hidden options. None of these are especially interesting.
    :return:
    '''
    print('\nHelp menu for hidden (debugging only) arguments:\n\n', end='')

    for k in hidden_args_help_strings:
        print('  --%s')
        hstr = textwrap.wrap(hidden_args_help_strings[k], 55)
        for ln in hstr:
            print(' '*25, end='')
            print(ln)
