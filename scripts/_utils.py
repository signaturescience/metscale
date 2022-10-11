#! usr/bin/python3
import os, logging, sys, shutil, configparser
from _parsing import run_print_argparse_results
from _containment import containment_dict_read_previous, containment_dict_summary
from _db_import import db_import_manifest_read
from _ncbi_taxonomy import ncbi_taxonomy_parse_file, ncbi_taxonid_to_lineage_vector


def run_inspect_previous_containment_dict(options=None):
    '''
    Simple routine to open the previous containment_dict.json file and print a description of what
    it contains.
    :return:
    '''
    pcd = containment_dict_read_previous(options=options)
    pcd_sum = containment_dict_summary(pcd)
    print(pcd_sum)

def run_recruit_sources_print_report(options=None, dbqt_config=None):
    '''
    Simple routine to check the DB sources that will be found when the sources and/or refseq
    folder is parsed. Prints a report to the logger.
    :return:
    '''
    rpt = '\n'
    sft, nfe, skips = db_import_manifest_read(options=options, dbqt_config=dbqt_config)
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

def run_query_taxids_against_containment(options=None):
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
    contain = containment_dict_read_previous(options=options)
    if options.all_refseq_versions:
        main_keys = list(contain.keys())
    else:
        main_keys = util_filter_out_main_dbnames(contain.keys())

    max_key_len = max(map(len, main_keys))
    ncbi_d = ncbi_taxonomy_parse_file(options=options)
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
        rpt = rpt + ' '.join(map(str, range(1,len(main_keys)+1) )) + '\n'
        for r in results:
            rpt = rpt + '%9s %9s ' % (r[0], r[1])
            mystr = ' '.join(map(str,r[2:]))
            rpt = rpt + mystr.replace('0', '-') + '\n'
        print(rpt)

def run_random_taxon_sample_to_file(options=None):
    '''
    Just creates a file with a list of randomly selected taxon IDs. For testing
    :param filepath:
    :param numtaxa:
    :return:
    '''
    if options.output_path is None:
        logging.error('output path must be specified to do the random taxon dump.')
    outf = open(options.output_path, 'w')
    nd = ncbi_taxonomy_parse_file(options=options)
    alltax = list(nd.keys())
    import random
    sometax = random.sample(alltax, options.num_taxa)
    for t in sometax:
        c=outf.write('%s\n' % t)
    outf.close()
    logging.info('wrote %s randomly selected taxon IDs to the file %s' % (options.num_taxa, options.output_path))

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
                run_print_argparse_results(options=options)
            sys.exit(1)
        if options.MY_DEBUG:
            logging.debug('requirement = %s, value = %s' % (reqname, reqval))

def verify_algorithm_argument(print_cmd_list=False, return_cmd_list=False, options=None):
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

