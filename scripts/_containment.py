#! usr/bin/python3
import pickle, copy, datetime, shutil, os, logging, json, hashlib

def get_file_md5_digest(file_path):
    with open(file_path,'rb') as fb:
        hd=hashlib.md5(fb.read()).hexdigest()
    return hd

def containment_dict_backup(options=None):
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

def containment_dict_read_previous(as_json=True, options=None):
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
            logging.error(
                'cannot read containment file: options.containment_metadata_json_path %s is not a valid file path' % options.containment_metadata_json_path)
            return {}
        with open(options.containment_metadata_json_path, 'rb') as cf:
            cfold = pickle.load(cf)
        return cfold
    else:
        fpcjson = os.path.splitext(options.containment_metadata_json_path)[0] + '.json'
        if not os.path.isfile(fpcjson):
            logging.error(
                'cannot read containment file in json form: options.containment_metadata_json_path (as json) %s is not a valid file path' % fpcjson)
            return {}
        with open(fpcjson, 'r') as jsf:
            cf_tmp = json.load(jsf)
        # convert the lists at the end back to sets in the main object:
        for k in cf_tmp['metadata'].keys():
            cf_tmp['metadata'][k]['taxid_set'] = set(cf_tmp['taxid_lists'][k])
        return cf_tmp['metadata']


def parse_delimited_text_general(file_path, delimiter='\t', keycol_index=0, header_rows=0, valcol_index=None,
                                 convert_key_col_to_int=True, result_as_set=False):
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
            keyval_list = list(map(lambda x: (x, 1), keyval_list))
        if convert_key_col_to_int:
            return dict(map(lambda x: (int_if_possible(x[0]), x[1]), keyval_list))
        else:
            return dict(keyval_list)
    return False


def parse_generic_file_by_format(file_path, format, options=None):
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

def containment_dict_show_build_plan(source_file_tuples, contain, quiet=False,   # hide_older_refseq=True
                                     clobber_old=False):
    '''
    Compares the contents of the source file list and the containment_dict, showing status for eventual
    build command.
    :param source_file_tuples: list of tuples as (name, path, format, size, mtime)
    :param contain:
    :return:
    '''
    # column widths:
    max_name_width = 60
    insources_width = 12
    incontain_width = 7
    status_width = 10

    source_file_tuples_dict = {}
    for ft in source_file_tuples:
        source_file_tuples_dict[ft[0]] = ft

    # combine the names
    all_db_names = list(set(source_file_tuples_dict.keys()).union(set(contain.keys())))

    # define output formatter
    name_width = min(max_name_width, max(map(len, all_db_names)))

    def makeline(nm, insrc, incon, statwid):
        templt = ' %s | %s | %s | %s'
        return templt % (nm[:name_width].ljust(name_width), insrc[:insources_width].ljust(insources_width),
                         incon[:incontain_width].ljust(incontain_width), statwid)

    if not clobber_old:
        print('Comparison of containment_dict and source files to be added:\n\n')
        print(makeline('Database', 'In', 'In', 'Action'))
        print(makeline('Name', 'Config', 'Contain', 'to be Taken'))
        print(makeline('-' * name_width, '-' * insources_width, '-' * incontain_width, '-' * status_width))
    else:
        print('No comparison to be done, \'--clobber\' was specified...')
        print('-------------------------------------------------------')

    import_list_file_tuples = []

    if clobber_old:
        import_list_file_tuples = source_file_tuples
    else:
        # compare the sources and the containment_dict
        sort_all_db_names_1 = list(filter(lambda x: x.lower()[0:6] != "refseq", all_db_names))
        sort_all_db_names_1.sort(key=lambda x: x.lower())
        sort_all_db_names_2 = list(filter(lambda x: x.lower()[0:6] == "refseq", all_db_names))
        sort_all_db_names_2 = sorted(sort_all_db_names_2, key=lambda x: int(x.lower().replace("refseq_v", "")),
                                     reverse=True)
        sort_all_db_names = sort_all_db_names_1 + sort_all_db_names_2

        for nm in sort_all_db_names:
            rpt_nm = nm;
            rpt_incon = '';
            rpt_insrc = '';
            rpt_status = '';

            if not nm in source_file_tuples_dict:  # name in containment_dict.json, not in source_list
                rpt_insrc = 'no'
                if not nm in contain:
                    rpt_incon = 'no'
                    rpt_status = '(strange...this shouldn\'t happen)'
                else:
                    rpt_incon = 'YES'
                    rpt_status = '(leave in)'
            else:
                rpt_insrc = 'YES (' + source_file_tuples_dict[nm][5] + ')'

                if not nm in contain:  # in sources, not in containment_dict.json
                    rpt_incon = 'no'
                    rpt_status = 'IMPORT'
                    import_list_file_tuples.append(source_file_tuples_dict[nm])
                else:  # in both
                    rpt_incon = 'YES'
                    sf_tup = source_file_tuples_dict[nm]
                    old_ver = contain[nm]
                    if old_ver['file_path'] == sf_tup[1] and old_ver['file_size'] == sf_tup[3] and old_ver[
                        'file_mod_time'] == sf_tup[4]:
                        rpt_status = '(unchanged, leave in)'
                        if not quiet:
                            print(makeline(rpt_nm, rpt_insrc, rpt_incon, rpt_status))
                        continue
                    if not quiet:
                        logging.debug('getting md5 of %s' % sf_tup[1])
                    if 'md5' in old_ver.keys():
                        new_md5 = get_file_md5_digest(sf_tup[1])
                        if new_md5 == old_ver.get('md5', None):
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

def containment_dict_build(source_file_tuples, clobber_old=False, save_replaced=True, save_backup=False, options=None):
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
        backup_filename = containment_dict_backup(options=options)
        logging.info(' - Saving backup containment file to: %s' % backup_filename)

    # Read old containment_dict and take inventory
    if not clobber_old:
        if os.path.isfile(options.containment_metadata_json_path):
            logging.info(' - Reading previous containment file')
            contain = containment_dict_read_previous(options=options)
        else:
            logging.info(' - containment file does not exist: %s' % options.containment_metadata_json_path)
            contain = {}
    else:
        contain = {}
    contain_replaced = {}

    isrefseq = list(map(lambda x: 1 if x[0][:6].lower() == 'refseq' else 0, source_file_tuples))
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
        status_str = '     '
        db['md5'] = get_file_md5_digest(db['file_path'])

        if db['name'] in contain:
            contain_replaced[db['name']] = contain.pop(db['name'])
            contain_replaced[db['name']]['comments'] += 'replaced on: %s, ' % datetime.datetime.now().strftime(
                my_time_fmt_str)

        db['taxid_set'] = parse_generic_file_by_format(db['file_path'], db['format'], options=options)
        setlen = len(db['taxid_set'])
        db['num_taxa'] = setlen
        status_str = status_str + (' %9s taxa |' % str(setlen))

        db['date_parsed'] = datetime.datetime.now().strftime(my_time_fmt_str)
        contain[db['name']] = db
        logging.debug(status_str)

    if save_replaced and len(contain_replaced) > 0:
        logging.debug(' - Saving replaced dictionaries...')
        contain_rep_filename = options.containment_metadata_json_path + '.replaced.' + datetime.datetime.now().strftime(
            file_time_fmt_str)
        with open(contain_rep_filename, 'wb') as contrep:
            pickle.dump(contain_replaced, contrep)

    return contain

def containment_dict_summary(contain, all_refseq=False, print_to_console=False):
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
    dbname_width = min(dbname_width_max, longest_key_len + 1)
    makeline = lambda dbn, nt, dt: ' %s  %s  %s\n' % (
    dbn[:dbname_width].ljust(dbname_width), nt.rjust(numtaxa_width), dt)

    summ_str = summ_str + "Main Databases:\n"
    summ_str = summ_str + makeline('Database Name', '# Taxa', 'Date Parsed')
    summ_str = summ_str + makeline('-' * dbname_width, '-' * numtaxa_width, '-' * dtparsed_width)
    # summ_str = summ_str + "  %s   %9s taxa    %s\n" % (lp_key('Database Name'), '# of', 'Date Parsed')
    # summ_str = summ_str + "  %s   %9s-----    %s\n" % (lp_key('-------------'), '----', '-----------')
    for mk in mainkeys:
        summ_str = summ_str + makeline(mk, str(contain[mk]['num_taxa']), contain[mk]['date_parsed'])
        # summ_str = summ_str + "  %s:  %9s taxa    %s\n" % (lp_key(mk), str(contain[mk]['num_taxa']), contain[mk]['date_parsed'])
    summ_str = summ_str + '\n'

    if print_to_console:
        print(summ_str)
    return summ_str

def containment_dict_save(contain, as_json=True, options=None):
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

def containment_dict_update_all_md5s(options=None):
    '''helper routine to refresh all the md5s, for debugging.'''
    contain = containment_dict_read_previous(options=options)
    for k in contain.keys():
        fp = contain[k]['file_path']
        nm = contain[k]['name']
        if os.path.isfile(fp):
            logging.debug('getting md5 for %s (%s)' % (nm, fp))
            mdfive = get_file_md5_digest(fp)
            contain[k]['md5'] = mdfive
        else:
            logging.debug('file path for %s does not exist (%s)' % (nm, fp))
            contain[k]['md5'] = ''
    containment_dict_save(contain, options=options)






