#! usr/bin/python
# Author: Dreycey Albin
# Update(s):07/11/2019, 10/31/2019, 11/01/2019 

import pickle, copy, datetime, shutil, argparse, configparser
import os, logging
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
dbqt_config = configparser.ConfigParser()

# define some global variables
dir_working = None
dir_refseq = None
fpath_containment = None
fpath_ncbi_tax_nodes = None
source_file_list = None  # special, defies naming convention
MY_DEBUG = True


# Specifies how to parse file types that are just delimited text. Each entry is:
#   ( <Delimiter>, <Taxon ID Column>, <# Header Rows to Skip> )
delimited_format_parse_specs = {
    'accn2taxid':       ('\t', 2, 1),
    'kraken2_inspect':  ('\t', 4, 0),
    'first_col':        ('\t', 0, 0),
    'refseq':           ('\t', 0, 0),
    'seqid2taxid':      ('\t', 1, 0)
}

taxid_dict = {}
ncbi_tax_levels = ['no rank', 'superkingdom', 'kingdom', 'subkingdom', 'superphylum', 'phylum', 'subphylum',
                   'superclass', 'class', 'subclass', 'infraclass', 'cohort', 'subcohort', 'superorder', 'order',
                   'suborder', 'infraorder', 'parvorder', 'superfamily', 'family', 'subfamily', 'tribe', 'subtribe',
                   'genus', 'subgenus', 'section', 'subsection', 'series', 'species group', 'species subgroup',
                   'species', 'subspecies', 'varietas', 'forma']


#
# Utility Functions First:
#
def command_args_parse():
    p = argparse.ArgumentParser(description='Module to build and manipulate the Taxon ID metadata and the database'
                                            ' containment_dict.p')
    p.add_argument('-wd', '--workdir', type=str, default=None,
                   help='The working folder in which we assume the script \'prepare_taxid_metadata.sh\' has run. '
                        '(default: current directory)')
    p.add_argument('-sfl', '--source_file_list',type=str, default=None,
                   help='Path to the file containing the Source File List. Typically named \'source_file_list.txt\'. '
                        'This is a specifically formatted text file (tab-delimited) containing the target DBs and '
                        'metadata files.')
    p.add_argument('-pf', '--pickle_file', type=str, default=None, help='path to the pickled containment_dict.p file')
    p.add_argument('-q', '--quiet', action='store_true', default=False,
                   help='If given, disables logging to the console except for warnings or errors (overrides --debug)')
    p.add_argument('-vq', '--veryquiet', action='store_true', default=False,
                   help='If given, disables logging to the console (overrides --quiet and --debug)')
    p.add_argument('--debug', action='store_true', default=False,
                   help='If given, enables more detailed logging useful in debugging.')
    p.add_argument('-lf', '--logfile', type=str, default=None,
                   help = 'If given, sends logging messages to a file instead of the console. Note that if the path'
                          'given is not a valid path to open a new file, the behavior is undefined.')

    commandgroup = p.add_mutually_exclusive_group()
    help_cmd_filelist = 'Parses the Source File List, prints the results to the console (readably), and then exits.'
    commandgroup.add_argument('-IFL', '--cmd_inspect_filelist', action='store_true', help=help_cmd_filelist, default=False)
    help_cmd_inspect_contain = 'Opens the existing containment_dict.p file and gets some summary data about it. Prints' + \
                               'it to the console and then exits.'
    commandgroup.add_argument('-ICD', '--cmd_inspect_contain', action='store_true', help=help_cmd_inspect_contain, default=False)
    help_cmd_build_containment = 'Build a new containment dictionary. Requires doing just about every step along' \
                                 'the way: 1) parses source_file_list, 2) opens old containment dict, 3) parses' \
                                 'each individual database file, 4) gently replaces containment_dict.p and saves' \
                                 'new stuff elsewhere.'
    commandgroup.add_argument('-BCD', '--cmd_build_containment', action='store_true', help=help_cmd_build_containment, default=False)

    args = p.parse_args()
    command_args_postprocess(args)
    return args

def command_args_postprocess(cargs):
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
    global dir_working, dir_refseq, fpath_containment, fpath_ncbi_tax_nodes, source_file_list
    dbqt_config.read('dbqt_config')
    dir_working_cfg = dbqt_config['paths'].get('working_folder', fallback=None)
    dir_refseq_cfg = dbqt_config['paths'].get('refseq_folder', fallback=None)
    fpath_containment_cfg = dbqt_config['paths'].get('path_to_pickle_file', fallback=None)
    fpath_ncbi_tax_nodes_cfg = dbqt_config['paths'].get('path_to_ncbi_taxonomy_nodes', fallback=None)
    source_file_list_cfg = dbqt_config['paths'].get('path_to_source_file_list', fallback=None)

    # CONFIGURE THE LOGGER
    mylvl = logging.INFO
    if cargs.debug:
        mylvl = logging.DEBUG
    if cargs.quiet:
        mylvl = logging.WARNING
    if cargs.veryquiet:
        mylvl = logging.CRITICAL
    if MY_DEBUG:
        mylvl = logging.DEBUG

    rich_format = "%(levelname) 8s [%(filename)s (line %(lineno)d)]: %(message)s"
    to_file = False
    if cargs.logfile is not None:
        try:
            myf = open(cargs.logfile, 'a')
            myf.close()
            to_file = True
        except:
            to_file = False

    if to_file:
        logging.basicConfig(format=rich_format, level=mylvl, filename=cargs.logfile)
    else:
        logging.basicConfig(format=rich_format, level=mylvl)
        if cargs.logfile is not None:
            logging.error('--logfile %s encountered a file error when I tried to open it' % cargs.logfile)

    # OVERRIDE GLOBAL VALUES IF GIVEN IN COMMAND LINE
    # working folder: try CMD, then CFG, default to scripts folder
    dir_working = os.path.abspath('.')
    if os.path.isdir(dir_working_cfg):
        dir_working = os.path.abspath(dir_working_cfg)
    else:
        logging.warning('CFG workdir is not a valid folder: %s' % dir_working_cfg)
    if cargs.workdir is not None:
        if os.path.isdir(cargs.workdir):
            dir_working = os.path.abspath(cargs.workdir)
        else:
            logging.warning('CMD workdir is not a valid folder %s' % cargs.workdir)

    # Containment Path: (first try CFG, over-write if in CMD, default to being in working dir)
    if fpath_containment_cfg is not None:
        if os.path.isfile(fpath_containment_cfg):
            fpath_containment = fpath_containment_cfg
        else:
            logging.warning('CFG path_to_pickle_file is not a valid file path: %s' % fpath_containment_cfg)
    if cargs.pickle_file is not None:
        if os.path.isfile(cargs.pickle_file):
            fpath_containment = cargs.pickle_file
        else:
            logging.warning('CMD pickle_file is not a valid file path: %s' % cargs.pickle_file)
    if fpath_containment is None:
        fpath_containment = os.path.join(dir_working, 'containment_dict.p')

    # Source File List: (first try CFG, over-write if in CMD, default to being in working dir)
    if source_file_list_cfg is not None:
        if os.path.isfile(source_file_list_cfg):
            source_file_list = source_file_list_cfg
        else:
            logging.warning('CFG source_file_list_cfg is not a valid file path: %s' % source_file_list_cfg)
    if cargs.source_file_list is not None:
        if os.path.isfile(cargs.source_file_list):
            source_file_list = cargs.source_file_list
        else:
            logging.warning('CMD source_file_list is not a valid file path: %s' % cargs.source_file_list)
    if source_file_list is None:
        source_file_list_wd = os.path.join(dir_working, 'source_file_list.txt')
        if os.path.isfile(source_file_list_wd):
            source_file_list = source_file_list_wd

    # RefSeq folder
    if dir_refseq_cfg is not None:
        if os.path.isdir(dir_refseq_cfg):
            dir_refseq = dir_refseq_cfg
        else:
            dir_refseq = None
            logging.warning('CFG refseq_folder is not a valid folder: %s' % dir_refseq_cfg)

    # NCBI nodes file
    if fpath_ncbi_tax_nodes_cfg is not None:
        if os.path.isfile(fpath_ncbi_tax_nodes_cfg):
            fpath_ncbi_tax_nodes = fpath_ncbi_tax_nodes_cfg
        else:
            fpath_ncbi_tax_nodes = None
            logging.warning('CFG fpath_ncbi_tax_nodes_cfg is not a valid file: %s' % fpath_ncbi_tax_nodes_cfg)

    # log important parameter values at start of run:
    param_vals_msg = '''Parameter values after parsing:
        working_folder:                %s
        path_to_pickle_file:           %s
        path_to_source_file_list:      %s
        path_to_ncbi_taxonomy_nodes:   %s
        refseq_folder:                 %s
    ''' % (dir_working, fpath_containment, source_file_list, fpath_ncbi_tax_nodes, dir_refseq)
    logging.info(param_vals_msg)

    # IDENTIFIES WHICH ROUTINE TO RUN:
    # todo: build this out later.

def make_tuple_with_metadata(path, dbname, format):
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

def read_source_file_list():
    '''
    Reads a config file containing a list of databases to be imported, including relevant information
    :return:
    '''
    logging.info('Function: read_source_file_list()...')
    sf = open(source_file_list, 'r')
    sf.readline() #skip header
    source_file_list_output = []
    refseq_ct = 0

    for ln in sf:
        if len(ln.strip())<=1:
            continue
        flds = ln.strip().split('\t')
        db_name = flds[0]
        db_filepath = os.path.join(flds[1], flds[2])
        db_format = flds[3]
        db_to_import = bool(int(flds[4]))
        if db_to_import:
            # If the line is for RefSeq, do it differently:
            if db_name.lower()=='refseq':
                refseq_dir = flds[1]
                if os.path.isdir(refseq_dir):
                    refseq_file_list = search_refseq_dir(refseq_dir)
                else:
                    logging.warning(' - RefSeq line has folder column that is not a valid path:')
                    logging.warning('       %s' % refseq_dir)
                    logging.warning('   ...skipping RefSeq search')
                    refseq_file_list = []
                refseq_ct = len(refseq_file_list)
                for ftup in refseq_file_list:
                    source_file_list_output.append(ftup)
            else:
                db_tuple = make_tuple_with_metadata(db_filepath, db_name, db_format)
                source_file_list_output.append(db_tuple)

    # Print some info about what we found:
    total_ct = len(source_file_list_output)
    other_ct = total_ct - refseq_ct
    logging.debug(' - source_file_list yielded the following to be imported:')
    logging.debug('     %s RefSeq database files' % refseq_ct)
    logging.debug('     %s other database files' % other_ct)
    return source_file_list_output

def search_refseq_dir(custom_refseq_dir = None):
    '''
    Combs through the folder pointed to by the "dir_refseq" parameter for files matching '*release*.*' and
    returns the file-info-tuples associated with them.
    TODO: Changes this to use a glob instead of os.walk
    :return:
    '''
    refseq_tuple_list = []
    refseqfiles = []
    if custom_refseq_dir is None:
        refseq_dir_abs = os.path.abspath(dir_refseq)
    else:
        refseq_dir_abs = os.path.abspath(custom_refseq_dir)

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
    if format not in delimited_format_parse_specs:
        return False
    spec = delimited_format_parse_specs[format]
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

    if not clobber_old:
        if os.path.isfile(fpath_containment):
            logging.info(' - Reading previous containment file')
            contain = containment_dict_read_previous()
        else:
            logging.info(' - containment file does not exist: %s' % fpath_containment)
            contain = {}
    else:
        contain = {}
    contain_replaced = {}

    isrefseq = list(map(lambda x: 1 if x[0][:6].lower()=='refseq' else 0, source_file_tuples))
    refseq_ct = sum(isrefseq)
    other_ct = len(isrefseq) - refseq_ct

    logging.info(' - Parsing databases ( %s RefSeq, %s other )' % (refseq_ct, other_ct))
    print_ct = 0
    for ft in source_file_tuples:
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

        if db['name'] in contain:
            status_str = status_str + 'In pickled: Yes   | Call: '
            old_ver = contain[db['name']]
            if (old_ver['file_path']==db['file_path'] and old_ver['file_size']==db['file_size'] and
                old_ver['file_mod_time']==db['file_mod_time']):
                status_str = status_str + 'unchanged (no action)'
                logging.debug(status_str)
                continue

            db['md5']=get_file_md5_digest(db['file_path'])
            if db['md5']==old_ver['md5']:
                status_str = status_str + 'same md5 (no action)'
                logging.debug(status_str)
                continue
            # if we get here, make a backup copy of the old one.
            status_str = status_str + 'new file (parse)      |'
            contain_replaced[db['name']] = contain.pop(db['name'])
            contain_replaced[db['name']]['comments'] +=  'replaced on: %s, ' % datetime.datetime.now().strftime(my_time_fmt_str)
        else:
            status_str = status_str + 'In pickled: No    | Parsing...   | '

        db['taxid_set']=parse_generic_file_by_format(db['file_path'], db['format'])
        setlen = len(db['taxid_set'])
        db['num_taxa']=setlen
        status_str = status_str + (' %9s taxa |' % str(setlen))

        db['date_parsed']=datetime.datetime.now().strftime(my_time_fmt_str)
        contain[db['name']] = db
        logging.debug(status_str)

    if save_replaced and len(contain_replaced)>0:
        logging.debug(' - Saving replaced dictionaries...')
        contain_rep_filename = fpath_containment + '.replaced.' + datetime.datetime.now().strftime(file_time_fmt_str)
        with open(contain_rep_filename, 'wb') as contrep:
            pickle.dump(contain_replaced, contrep)

    return contain

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
    summ_str = summ_str + '  Size: %d (%d RefSeq, %d other)\n' % (tot_db_ct, len(refseq_keys), len(mainkeys))
    summ_str = summ_str + '  Latest RefSeq: v%d\n' % latest_ver_num
    if not all_refseq:
        mainkeys.append(latest_ver_key)
    else:
        for rsk in refseq_keys:
            mainkeys.append(rsk)
    # make the summary string:
    longest_key_len = max(map(len, mainkeys))
    lp_key = lambda x: ('%' + str(longest_key_len) + 's') % x
    summ_str = summ_str + "  Main Databases: (Name, # Taxa, Date Parsed)\n"
    for mk in mainkeys:
        summ_str = summ_str + "  %s: %9s taxa, %s\n" % (lp_key(mk), str(contain[mk]['num_taxa']), contain[mk]['date_parsed'])
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
    if fpath_containment is None:
        logging.error('cannot backup containment file: fpath_containment is None')
        return
    backup_path = fpath_containment + '.backup'
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
    shutil.copyfile(fpath_containment, backup_path)
    return bfn

def containment_dict_save(contain):
    if fpath_containment is None:
        logging.error('cannot save containment file: fpath_containment is None')
        return
    logging.info('Saving containment dictionary to %s' % fpath_containment)
    with open(fpath_containment, 'wb') as contpick:
        pickle.dump(contain, contpick)

def containment_dict_read_previous():
    '''
    Reads the previously written containment dictionary if the file exists. If it does not, returns an empty
    python dictionary.
    :return:
    '''
    if fpath_containment is None:
        logging.error('cannot read containment file: fpath_containment is None')
        return {}
    if not os.path.isfile(fpath_containment):
        logging.error('cannot read containment file: fpath_containment %s is not a valid file path' % fpath_containment)
        return {}

    with open(fpath_containment, 'rb') as cf:
        cfold = pickle.load(cf)
    return cfold

def run_inspect_previous_containment_dict():
    pcd = containment_dict_read_previous()
    pcd_sum = containment_dict_summary(pcd)
    print(pcd_sum)

def parse_ncbi_taxonomy_file():
    '''
    Opens the NCBI nodes.dmp file from the taxdump FTP site. Parses it into a dictionary with
    key/vals in the form:
        { <taxon_id>: (<parent_taxon_id>, <level>, <assigned_at_species>), ...}
    :return:
    '''
    if not os.path.isfile(fpath_ncbi_tax_nodes):
        logging.error('cannot open NCBI nodes file %s' % fpath_ncbi_tax_nodes)
        return
    ncbi_f = open(fpath_ncbi_tax_nodes, 'r')
    ncbi_dict = dict(map(lambda x: (int(x[0]), (int(x[2]), x[4], int(x[30]))), map(lambda x: x.strip().split('\t'), ncbi_f.readlines())))
    return ncbi_dict

def taxonid_to_lineage_vector(taxid, ncbi_dict):
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
    lineage = [-1,]*33
    r2i = lambda x: ncbi_tax_levels.index(x)-1

    tdata = ncbi_dict[taxid]
    lineage[r2i[tdata[1]]] = taxid
    next = tdata[0]
    level_ct = 1
    while next > 1:
        tdata = ncbi_dict[next]
        lineage[r2i[tdata[1]]] = next
        next = tdata[0]
        level_ct += 1
        if level_ct > 100:
            print ("taxid %s has a lineage that is supposedly 100+ levels")
            break

def make_ncbi_taxonomy_full_vector_lookup(ncbi_dict):
    '''
    Makes a dictionary where the values are full-lineage vectors instead of the recursive lookup
    :param ncbi_dict:
    :return:
    '''
    ncbi_tax_fullvec = {}
    for k in ncbi_dict.keys():
        ncbi_tax_fullvec[k] = taxonid_to_lineage_vector(k, ncbi_dict)
    return ncbi_tax_fullvec

def main():
    args = command_args_parse()
    sft = read_source_file_list()
    cd = containment_dict_build(sft)
    cd_sum = containment_dict_summary(cd)
    print (cd_sum)
    containment_dict_save(cd)

if __name__=='__main__':
    main()