#! usr/bin/python3
import pickle, copy, datetime, shutil, argparse, configparser
import os, logging, sys
import glob
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

# define some global variables
class Opts:
    dir_working = None
    dir_refseq = None
    fpath_containment = None
    fpath_ncbi_tax_nodes = None
    source_file_list = None  # special, defies naming convention
    delimited_format_parse_specs = {
        # 'accn2taxid':       ('\t', 2, 1),
        # 'kraken2_inspect':  ('\t', 4, 0),
        # 'first_col':        ('\t', 0, 0),
        # 'refseq':           ('\t', 0, 0),
        # 'seqid2taxid':      ('\t', 1, 0)
    }
    MY_DEBUG = True
    parser_store = None

options = Opts()


# Specifies how to parse file types that are just delimited text. Each entry is:
#   ( <Delimiter>, <Taxon ID Column>, <# Header Rows to Skip> )
#   NOTE: moved to the config file.


taxid_dict = {}
ncbi_tax_levels = ['no rank', 'superkingdom', 'kingdom', 'subkingdom', 'superphylum', 'phylum', 'subphylum',
                   'superclass', 'class', 'subclass', 'infraclass', 'cohort', 'subcohort', 'superorder', 'order',
                   'suborder', 'infraorder', 'parvorder', 'superfamily', 'family', 'subfamily', 'tribe', 'subtribe',
                   'genus', 'subgenus', 'section', 'subsection', 'series', 'species group', 'species subgroup',
                   'species', 'subspecies', 'varietas', 'forma']
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
    p = argparse.ArgumentParser(description='Module to build and manipulate the Taxon ID metadata and the database'
                                            ' containment_dict.p')

    help_taxid_list = 'The NCBI taxonomy ID(s) to query against the containment_dict metadatabase. Can be in one of ' \
                      'three forms: a) a single integer, which will be queried and the results output, b) a valid path' \
                      'to a text file containing one taxon ID per line, all of which will be queried and the results ' \
                      'output as tab-delimited text, or c) \'stdin\' in which case a list of taxon_ids is pulled from ' \
                      'standard input and processed as with a file.'
    p.add_argument('-t', '--taxids', dest='taxid_list', type=str, default=None, help=help_taxid_list)
    p.add_argument('-o', '--output', dest='output_path', type=str, default=None, help='output file path')
    p.add_argument('--all_refseq_versions', action='store_true', default=False,
                   help='Prints whatever results are called for including all versions of RefSeq, not just the latest '
                        'version (default).')


    configgroup = p.add_argument_group('Configuration Options',
                                       'Paths to key locations and files required by the tool. Arguments not supplied '
                                       'will be pulled from the default config file \'dbqt_config\' and if needed will '
                                       'be assigned their default values (where applicable).')
    configgroup.add_argument('-wd', '--workdir', type=str, default=None,
                   help='The working folder in which we assume the script \'prepare_taxid_metadata.sh\' has run. '
                        '(default: current directory)')
    configgroup.add_argument('-pf', '--pickle_file', type=str, default=None,
                             help='Path to the pickled containment_dict.p file.')
    configgroup.add_argument('-dbs', '--db_source_list_file', type=str, default=None,
                   help='Path to the file containing the Source File List. Typically named \'source_file_list.txt\'. '
                        'This is a specifically formatted text file (tab-delimited) containing the target DBs and '
                        'metadata files.')
    configgroup.add_argument('-c', '--config', type=str, default=None,
                             help='Optional config file (overrides default file path: \'dbqt_config\'')


    logginggroup = p.add_argument_group('Logging Options', 'Options related to how much information the program prints '
                                                           'while running (to stdout by default, but optioanlly to a logfile.')
    logginggroup.add_argument('-qt', '--quiet', action='store_true', default=False,
                   help='If given, disables logging to the console except for warnings or errors (overrides --debug)')
    logginggroup.add_argument('-vqt', '--veryquiet', action='store_true', default=False,
                   help='If given, disables logging to the console (overrides --quiet and --debug)')
    logginggroup.add_argument('--debug', action='store_true', default=False,
                   help='If given, enables more detailed logging useful in debugging.')
    logginggroup.add_argument('-lf', '--logfile', type=str, default=None,
                   help='If given, sends logging messages to a file instead of the console. Note that if the path'
                        'given is not a valid path to open a new file, the behavior is undefined.')

    commandgroup = p.add_argument_group('Procedures Available', 'Each of these options describes a different subroutine to '
                                                                'run. Only one can be given and if none are, defaults to '
                                                                'querying a taxon ID against the containment file (i.e. -QRY)')
    help_cmd_query_taxid = 'query one or more taxids against the containment file. Report back which DBs contain the taxid ' \
                           '(adjusted to the species level). (Requires \'-t/--taxids\', \'-o/--output\')'
    commandgroup.add_argument('-QRY', '--cmd_query_taxids', action='store_true', help=help_cmd_query_taxid,
                              default=False)
    help_cmd_filelist = 'Parses the roster of database sources to be added to the containment_dict.p file, either from ' \
                        'the soure_file_list file or from the config file (or both). Prints the results to the console ' \
                        '(readably), and then exits. Primarily for checking accuracy of source file roster before building ' \
                        'a new containment_dict.p file.'
    commandgroup.add_argument('-IFL', '--cmd_inspect_filelist', action='store_true', help=help_cmd_filelist, default=False)
    help_cmd_inspect_contain = 'Prints some summary data about the existing containment_dict.p file to the console and ' \
                               'then exits. Primarily for inspecting contents of the file.'
    commandgroup.add_argument('-ICD', '--cmd_inspect_contain', action='store_true', help=help_cmd_inspect_contain, default=False)
    help_cmd_show_build_plan = 'Runs procedures to inspect and generate a roster of database sources, as well as to inspect' \
                               'the contaiment_dict.p file. Compares the two and identifies the plan for which files ' \
                               'to be added, ignored or replaced. This procedure is run automatically prior to building ' \
                               'a new containment_dict.p file. (Optional: \'--clober\')'
    commandgroup.add_argument('-CMO', '--cmd_compare_sources', action='store_true', help=help_cmd_show_build_plan,
                              default=False)
    help_cmd_build_containment = 'Build a new containment dictionary. Requires doing just about every step along ' \
                                 'the way: 1) parses source_file_list, 2) opens old containment dict, 3) parses ' \
                                 'each individual database file, 4) gently replaces containment_dict.p and saves ' \
                                 'new stuff elsewhere.  (Optional: \'--clober\')'
    commandgroup.add_argument('-BCD', '--cmd_build_containment', action='store_true', help=help_cmd_build_containment, default=False)
    commandgroup.add_argument('--print_debug_args_help', action='store_true', default = False,
                              help = 'Prints a help message for some additional command-line arguments. Most of thiese '
                                     'are intended for debugging only and are not especially interesting.')

    #
    # Misc Args
    #
    miscgroup = p.add_argument_group('Miscellaneous Arguments',
                                        'These arguments are mostly optional and in many cases only operate with certain'
                                        'of the commands, and are ignored otherwise.')
    miscgroup.add_argument('--clobber', action='store_true', help='If provided, previous containment_dict.p is removed and'
                                                                  'rebuilt from scratch based on the source files.',default=False)
    #
    # Hidden arguments
    #
    commandgroup.add_argument('--cmd_random_taxon_sample', action='store_true', default=False, help=argparse.SUPPRESS)
    hidden_args_help_strings['cmd_random_taxon_sample'] = 'Makes a quick random sample of taxids to file, for testing. ' \
                                                          '(requires: -o/--output, --num_taxa)'
    p.add_argument('--num_taxa', type=int, default=25, help=argparse.SUPPRESS)
    hidden_args_help_strings['num_taxa'] = '(Integer, used with --cmd_random_taxon_sample) Number of taxa to be sampled. (default: 25)'
    commandgroup.add_argument('--print_source_file_list_specs', action='store_true', default=False, help=argparse.SUPPRESS)
    hidden_args_help_strings['print_source_file_list_specs'] = 'Prints a description of the specs for specifying a ' \
                                                               'database roster in a text file.'
    commandgroup.add_argument('--cmd_update_all_md5s', action='store_true', default=False, help=argparse.SUPPRESS)
    hidden_args_help_strings['cmd_update_all_md5s'] = 'Runs through the existing containment_dict.p and updates all the ' \
                                                      'md5 values, then saves the result and exits.'

    p.parse_args(namespace=options)
    options.parser_store = p
    command_args_postprocess()

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
    # global dir_working, dir_refseq, fpath_containment, fpath_ncbi_tax_nodes, source_file_list
    global options
    if hasattr(options,'config') and options.config is not None:
        if os.path.isfile(os.path.expanduser(options.config)):
            dbqt_config.read(options.config)
            logging.debug('Reading config file: %s' % options.config)
        else:
            logging.error('Config file given at command line does not exist (file: %s)' % options.config)
    else:
        dbqt_config.read('dbqt_config')

    dir_working_cfg = os.path.expanduser(dbqt_config['paths'].get('working_folder', fallback=None))
    dir_refseq_cfg = os.path.expanduser(dbqt_config['paths'].get('refseq_folder', fallback=None))
    fpath_containment_cfg = os.path.expanduser(dbqt_config['paths'].get('path_to_pickle_file', fallback=None))
    fpath_ncbi_tax_nodes_cfg = os.path.expanduser(dbqt_config['paths'].get('path_to_ncbi_taxonomy_nodes', fallback=None))
    source_file_list_cfg = os.path.expanduser(dbqt_config['paths'].get('path_to_source_file_list', fallback=None))

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


    rich_format = "%(levelname) 8s [%(filename)s (line %(lineno)d)]: %(message)s"
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

    # logging.debug('dir_refseq_cfg: %s' % dir_refseq_cfg)
    # logging.debug('fpath_containment_cfg: %s' % fpath_containment_cfg)
    # logging.debug('fpath_ncbi_tax_nodes_cfg: %s' % fpath_ncbi_tax_nodes_cfg)
    # logging.debug('source_file_list_cfg: %s' % source_file_list_cfg)
    verify_algorithm_argument()

    # OVERRIDE GLOBAL VALUES IF GIVEN IN COMMAND LINE
    # working folder: try CMD, then CFG, default to scripts folder
    options.dir_working = os.path.abspath('.')
    # logging.debug('First version of working folder: current path (%s)' % options.dir_working)
    if os.path.isdir(dir_working_cfg):
        options.dir_working = os.path.abspath(dir_working_cfg)
        # logging.debug('Second version of working folder: config path (%s)' % options.dir_working)
    else:
        logging.warning('Config parameter working_folder is not a valid folder: %s' % dir_working_cfg)
    if options.workdir is not None:
        if os.path.isdir(options.workdir):
            # logging.debug('Last version of working folder: command-line path (%s)' % options.dir_working)
            options.dir_working = os.path.abspath(options.workdir)
        else:
            logging.warning('CMD workdir is not a valid folder %s' % options.workdir)

    # Containment Path: (first try CFG, over-write if in CMD, default to being in working dir)
    if fpath_containment_cfg is not None:
        if os.path.isfile(fpath_containment_cfg):
            options.fpath_containment = fpath_containment_cfg
        else:
            logging.warning('Config parameter path_to_pickle_file is not a valid file path: %s' % fpath_containment_cfg)
    if options.pickle_file is not None:
        if os.path.isfile(options.pickle_file):
            options.fpath_containment = options.pickle_file
        else:
            logging.warning('Command-line provided pickle_file is not a valid file path: %s' % options.pickle_file)
    if options.fpath_containment is None:
        options.fpath_containment = os.path.join(options.dir_working, 'containment_dict.p')

    # Source File List: (first try CFG, over-write if in CMD, default to being in working dir)
    if source_file_list_cfg is not None:
        if os.path.isfile(source_file_list_cfg):
            options.source_file_list = source_file_list_cfg
        else:
            logging.warning('Config parameter source_file_list_cfg is not a valid file path: %s' % source_file_list_cfg)
    if options.db_source_list_file is not None:
        if os.path.isfile(options.db_source_list_file):
            options.source_file_list = options.db_source_list_file
        else:
            logging.warning('Command-line parameter --db_source_list_file is not a valid file path: %s' % options.db_source_list_file)
    if options.source_file_list is None:
        source_file_list_wd = os.path.join(options.dir_working, 'source_file_list.txt')
        if os.path.isfile(source_file_list_wd):
            source_file_list = source_file_list_wd
            logging.info('Found a valid DB source file list file at: %s' % source_file_list)

    # RefSeq folder
    if dir_refseq_cfg is not None:
        if os.path.isdir(dir_refseq_cfg):
            options.dir_refseq = dir_refseq_cfg
        else:
            options.dir_refseq = None
            logging.warning('Config parameter refseq_folder is not a valid folder: %s' % dir_refseq_cfg)

    # NCBI nodes file
    if fpath_ncbi_tax_nodes_cfg is not None:
        if os.path.isfile(fpath_ncbi_tax_nodes_cfg):
            options.fpath_ncbi_tax_nodes = fpath_ncbi_tax_nodes_cfg
        else:
            options.fpath_ncbi_tax_nodes = None
            logging.warning('Config parameter fpath_ncbi_tax_nodes_cfg is not a valid file: %s' % fpath_ncbi_tax_nodes_cfg)

    # log important parameter values at start of run:
    param_vals_msg = '''Parameter values after parsing:
        working_folder:                %s
        path_to_pickle_file:           %s
        path_to_source_file_list:      %s
        path_to_ncbi_taxonomy_nodes:   %s
        refseq_folder:                 %s
    ''' % (options.dir_working, options.fpath_containment, options.source_file_list, options.fpath_ncbi_tax_nodes, options.dir_refseq)
    logging.debug(param_vals_msg)

    # READ THE FORMAT LIST INTO A DICT:
    for k in dbqt_config['formats'].keys():
        fmt = None
        # logging.debug('format %8s\t%s' % (k, dbqt_config.get('formats',k)))
        fmt=eval(dbqt_config.get('formats',k))
        # logging.debug('fmt is now: %s' % str(fmt))
        options.delimited_format_parse_specs[k]=fmt

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

def source_file_list_read(skip_refseq = False, from_config = True, from_file_if_exists = True):
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
    global options #.dir_refseq, source_file_list, dbqt_config
    logging.debug('Function: source_file_list_read()...')

    source_file_list_output = []
    source_file_list_parsed = {}
    no_file_errors = []
    not_to_import = []
    refseq_ct = 0
    line_no = 1
    refseq_in_source_list = False

    #
    # 1) Get the raw values from the config (or text file)
    #
    if from_config:
        for dbnm in dbqt_config['db_source_files'].keys():
            db_name = dbnm
            db_filepath = dbqt_config['db_source_files'][dbnm]
            if db_name not in dbqt_config['db_source_formats'].keys():
                logging.warning('In config: database name \'%s\' was found in the config file under [db_source_files] but does not have'
                                'a format defined in [db_source_formats]. (Skipping)' % dbnm)
                db_format = ''
                db_to_import = 0
            else:
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
                    logging.warning('In config: Database format string for \'%s\' does not contain a space: assuming final value of 1 (proceeding). (string: \'%s\')' % (dbnm, db_fmt_val))
                    db_to_import = 1
            source_file_list_parsed[dbnm] = [db_name, db_filepath, db_format, str(db_to_import)]

    if options.source_file_list is not None and from_file_if_exists:
        sf = open(options.source_file_list, 'r')
        sf.readline()  # skip header

        for ln in sf:
            if len(ln.strip())<=1:
                continue
            flds = ln.strip().split('\t')
            source_file_list_parsed[flds[0]] = flds

    for flds in source_file_list_parsed.values():
        # logging.debug(str(flds))
        db_name = flds[0]
        db_filepath = os.path.abspath(os.path.expanduser( flds[1] ))
        # db_filepath = os.path.join(flds[1], flds[2])
        db_format = flds[2]
        db_to_import = bool(int(flds[3]))
        if db_to_import:
            if db_name.lower()=='refseq' and not skip_refseq:   # If the line is for RefSeq, do it differently...
                new_refseq_dir = os.path.abspath(os.path.expanduser( flds[1] ))
                if os.path.isdir(new_refseq_dir):
                    logging.debug('found RefSeq in the source list. Replacing config refseq folder with:\n\t%s' % new_refseq_dir)
                    options.dir_refseq = new_refseq_dir
                    refseq_in_source_list = True
                else:
                    logging.warning(' - RefSeq (line %s) has path column that is not a valid folder:\n\t%s' % (line_no, new_refseq_dir))

            else:  # ...otherwise send it to the text parser
                if os.path.isfile(db_filepath):
                    db_tuple = make_tuple_with_metadata(db_filepath, db_name, db_format)
                    source_file_list_output.append(db_tuple)
                else:
                    logging.debug(' - File in source list does not exist (line %s, db=%s)\n\t%s' % (line_no, db_name, db_filepath))
                    no_file_errors.append((db_filepath, db_name, db_format))
        else:   # Add to the skips list
            not_to_import.append((db_filepath, db_name, db_format))
        line_no += 1

    if not skip_refseq:
        if options.dir_refseq is not None:
            refseq_file_list = search_refseq_dir(options.dir_refseq)
            refseq_ct = len(refseq_file_list)
            for ftup in refseq_file_list:
                source_file_list_output.append(ftup)

    # Print some info about what we found:
    total_ct = len(source_file_list_output)
    other_ct = total_ct - refseq_ct
    logging.debug(' - source_file_list (including config) yielded the following to be imported:')
    logging.debug('     %s RefSeq database files' % refseq_ct)
    logging.debug('     %s other database files' % other_ct)
    return source_file_list_output, no_file_errors, not_to_import

def source_file_list_print_specs():
    '''
    Prints the help description for the specs of the database source roster (i.e. source_file_list).
    :return:
    '''
    mydesc = 'A roster of new databases can be specified using a tab-delimited text file. In order to use this format, ' \
           'a file path must be specified either at the command line (using the flag \'-dbs <PATH>\') or in the config ' \
           'file (under the [paths] section, named \'path_to_source_file_list\').'

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

def search_refseq_dir(custom_refseq_dir = None):
    '''
    Combs through the folder pointed to by the "options.dir_refseq" parameter for files matching '*release*.*' and
    returns the file-info-tuples associated with them.
    TODO: Changes this to use a glob instead of os.walk
    :return:
    '''
    refseq_tuple_list = []
    refseqfiles = []
    if custom_refseq_dir is None:
        refseq_dir_abs = os.path.abspath(options.dir_refseq)
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
            refseq_tuple_list.append(make_tuple_with_metadata(fpath, 'RefSeq_v' + version, 'refseq'))
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
        if os.path.isfile(options.fpath_containment):
            logging.info(' - Reading previous containment file')
            contain = containment_dict_read_previous()
        else:
            logging.info(' - containment file does not exist: %s' % options.fpath_containment)
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

        # if db['name'] in contain:
        #     status_str = status_str + 'In pickled: Yes   | Call: '
        #     old_ver = contain[db['name']]
        #     if (old_ver['file_path']==db['file_path'] and old_ver['file_size']==db['file_size'] and
        #         old_ver['file_mod_time']==db['file_mod_time']):
        #         status_str = status_str + 'unchanged (no action)'
        #         logging.debug(status_str)
        #         continue
        #
        #     db['md5']=get_file_md5_digest(db['file_path'])
        #     if db['md5']==old_ver['md5']:
        #         status_str = status_str + 'same md5 (no action)'
        #         logging.debug(status_str)
        #         continue
        #     # if we get here, make a backup copy of the old one.
        #     status_str = status_str + 'new file (parse)      |'
        #     contain_replaced[db['name']] = contain.pop(db['name'])
        #     contain_replaced[db['name']]['comments'] +=  'replaced on: %s, ' % datetime.datetime.now().strftime(my_time_fmt_str)
        # else:
        #     status_str = status_str + 'In pickled: No    | Parsing...   | '

        db['taxid_set']=parse_generic_file_by_format(db['file_path'], db['format'])
        setlen = len(db['taxid_set'])
        db['num_taxa']=setlen
        status_str = status_str + (' %9s taxa |' % str(setlen))

        db['date_parsed']=datetime.datetime.now().strftime(my_time_fmt_str)
        contain[db['name']] = db
        logging.debug(status_str)

    if save_replaced and len(contain_replaced)>0:
        logging.debug(' - Saving replaced dictionaries...')
        contain_rep_filename = options.fpath_containment + '.replaced.' + datetime.datetime.now().strftime(file_time_fmt_str)
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
    source_file_tuples_dict = {}
    for ft in source_file_tuples:
        source_file_tuples_dict[ft[0]]=ft

    all_db_names = list(set(source_file_tuples_dict.keys()).union(set(contain.keys())))

    rpt = '\n'
    rpt = rpt + 'Comparison of containment_dict and source files to be added:\n\n'
    rpt = rpt + ' Name                  Sources  Contain  Status     \n'
    rpt = rpt + '---------------------  -------  -------  -----------'
    if not clobber_old:
        logging.info(rpt)
    else:
        logging.info('No comparison to be done, \'--clobber\' was specified...')
        logging.info('-------------------------------------------------------')

    import_list_file_tuples = []

    if clobber_old:
        import_list_file_tuples = source_file_tuples
    else:
        for nm in all_db_names:
            rpt=''
            if len(nm)>21:
                rpt = rpt + nm[:21] + '  '
            else:
                rpt = rpt + nm + ' '*(23-len(nm))

            if not nm in source_file_tuples_dict:   # name in containment_dict.p, not in source
                rpt = rpt + ' ' * 9
                if not nm in contain:
                    rpt = rpt + ' '*9 + '(strange...this shouldn\'t happen)'
                else:
                    rpt = rpt + ' xxx     ---   (leave in)'
            else:
                rpt = rpt + ' xxx     '
                if not nm in contain:       # in sources, not in containment_dict.p
                    rpt = rpt + ' '*9 + '-import'
                    import_list_file_tuples.append(source_file_tuples_dict[nm])
                else:                       # in both
                    rpt = rpt + ' xxx     '
                    sf_tup = source_file_tuples_dict[nm]
                    old_ver = contain[nm]
                    if old_ver['file_path']==sf_tup[1] and old_ver['file_size']==sf_tup[3] and old_ver['file_mod_time']==sf_tup[4]:
                        rpt = rpt + '---   (unchanged)'
                        if not quiet:
                            logging.info(rpt)
                        continue
                    if not quiet:
                        logging.debug('getting md5 of %s' % sf_tup[1])
                    if 'md5' in old_ver.keys():
                        new_md5 = get_file_md5_digest(sf_tup[1])
                        if new_md5==old_ver.get('md5',None):
                            rpt = rpt + '---   (same md5)'
                            if not quiet:
                                logging.info(rpt)
                            continue
                    import_list_file_tuples.append(sf_tup)
                    rpt = rpt + '-replace (new file)'
            if not quiet:
                logging.info(rpt)
    logging.info('Summary of sources to be imported: (count = %d)' % len(import_list_file_tuples))
    for ift in import_list_file_tuples:
        logging.info('   %s\t%s' % (ift[0], ift[1]))


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
    lp_key = lambda x: ('%' + str(longest_key_len) + 's') % x
    summ_str = summ_str + "  Main Databases:\n"
    summ_str = summ_str + "  %s   %9s taxa    %s\n" % (lp_key('Database Name'), '# of', 'Date Parsed')
    summ_str = summ_str + "  %s   %9s-----    %s\n" % (lp_key('-------------'), '----', '-----------')
    for mk in mainkeys:
        summ_str = summ_str + "  %s:  %9s taxa    %s\n" % (lp_key(mk), str(contain[mk]['num_taxa']), contain[mk]['date_parsed'])
    summ_str = summ_str + '\n'

    if print_to_console:
        print(summ_str)
    return summ_str

def containment_dict_backup():
    '''
    Makes a copy of the containment_dict.p file called 'containment_dict.p.backup' in the same folder. If a file
    by that name already exists, it tacks on a 1 and tries, then a 2, etc... to 1000.
    :return:
    '''
    if options.fpath_containment is None:
        logging.error('cannot backup containment file: options.fpath_containment is None')
        return
    backup_path = options.fpath_containment + '.backup'
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
    shutil.copyfile(options.fpath_containment, backup_path)
    return bfn

def containment_dict_save(contain):
    if options.fpath_containment is None:
        logging.error('cannot save containment file: options.fpath_containment is None')
        return
    logging.info('Saving containment dictionary to %s' % options.fpath_containment)
    with open(options.fpath_containment, 'wb') as contpick:
        pickle.dump(contain, contpick)

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

def containment_dict_read_previous():
    '''
    Reads the previously written containment dictionary if the file exists. If it does not, returns an empty
    python dictionary.
    :return:
    '''
    if options.fpath_containment is None:
        logging.error('cannot read containment file: options.fpath_containment is None')
        return {}
    if not os.path.isfile(options.fpath_containment):
        logging.error('cannot read containment file: options.fpath_containment %s is not a valid file path' % options.fpath_containment)
        return {}

    with open(options.fpath_containment, 'rb') as cf:
        cfold = pickle.load(cf)
    return cfold

def ncbi_taxonomy_parse_file():
    '''
    Opens the NCBI nodes.dmp file from the taxdump FTP site. Parses it into a dictionary with
    key/vals in the form:
        { <taxon_id>: (<parent_taxon_id>, <level>, <assigned_at_species>), ...}
    :return:
    '''
    if not os.path.isfile(options.fpath_ncbi_tax_nodes):
        logging.error('cannot open NCBI nodes file %s' % options.fpath_ncbi_tax_nodes)
        return
    ncbi_f = open(options.fpath_ncbi_tax_nodes, 'r')
    ncbi_dict = dict(map(lambda x: (int(x[0]), (int(x[2]), x[4], int(x[30]))), map(lambda x: x.strip().split('\t'), ncbi_f.readlines())))
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
    lineage = [-1,]*34

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

def run_inspect_previous_containment_dict():
    '''
    Simple routine to open the previous containment_dict.p file and print a description of what
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
    sft, nfe, skips = source_file_list_read()
    refseq_list = []
    main_list = []
    latest_refseq_version = -1
    latest_refseq_index = None
    for db_ind in range(len(sft)):
        db = sft[db_ind]
        if db[0][:6].lower()=='refseq':
            refseq_list.append(db)
            ver = int(db[0][8:])
            if ver > latest_refseq_version:
                latest_refseq_version = ver
                latest_refseq_index = db_ind
        else:
            main_list.append(db)

    if len(refseq_list)>0:
        main_list.append(sft[latest_refseq_index])

    rpt = rpt + 'Searching for data sources...\n'
    rpt = rpt + '    RefSeq folder: %s\n' % options.dir_refseq
    rpt = rpt + '    Source List File: %s\n' % options.source_file_list
    rpt = rpt + 'Data Sources to be Imported:\n'
    for db in main_list:
        rpt = rpt + '   %s\t%s\n' % (db[0], db[1])
    if len(refseq_list)>1:
        rpt = rpt + '   (...%s other RefSeq versions not shown)\n' % (len(refseq_list)-1)

    logging.info(rpt)

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
        while True:
            foo = input()
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


def verify_algorithm_argument():
    '''
    Goes through the option list to make sure at most one procedure argument was given. Sets default if omitted.
    :return:
    '''
    cmds = [i for i in vars(options).keys() if i[:4]=='cmd_']
    cmd_ct = 0
    for c in cmds:
        if vars(options)[c]:
            cmd_ct += 1
    if cmd_ct > 1:
        options.parser_store.print_help()
        sys.exit(1)
    elif cmd_ct == 0:
        options.cmd_query_taxids = True

def main():
    command_args_parse()
    if options.cmd_inspect_filelist:
        run_recruit_sources_print_report()
        return
    elif options.cmd_inspect_contain:
        run_inspect_previous_containment_dict()
        return
    elif options.cmd_compare_sources:
        sft, nfe, skips = source_file_list_read()
        contain = containment_dict_read_previous()
        imp_list = containment_dict_show_build_plan(sft, contain, clobber_old=options.clobber)
    elif options.cmd_build_containment:
        sft, nfe, skips = source_file_list_read()
        cd = containment_dict_build(sft, clobber_old=options.clobber)
        cd_sum = containment_dict_summary(cd)
        logging.info(cd_sum)
        containment_dict_save(cd)
    elif options.cmd_query_taxids:
        run_query_taxids_against_containment()
    elif options.cmd_random_taxon_sample:
        run_random_taxon_sample_to_file()
    elif options.print_source_file_list_specs:
        source_file_list_print_specs()
    elif options.print_debug_args_help:
        command_args_print_hidden_args_help()
    elif options.cmd_update_all_md5s:
        containment_dict_update_all_md5s()

if __name__=='__main__':
    main()