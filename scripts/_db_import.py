#! usr/bin/python3
import os, logging


def make_tuple_with_metadata(path, dbname, format):
    '''minor utility that takes three inputs and returns a tuple with the three inputs plus the file size and mod_time.
    '''
    s = os.stat(path)
    return (dbname, path, format, s.st_size, s.st_mtime)

def command_args_postprocess_db_import(options=None):
    '''
    Looks at the values for the manifest file given at the command line and/or in the config file for
    the db_import_manifest and refseq_folder paths. Assesses if they are valid paths and prints warnings
    accordingly.
    :return:
    '''
    # Source File List: (first try CFG, over-write if in CMD, default to being in working dir)
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

def db_import_manifest_read(skip_refseq=False, from_config=True, from_file_if_exists=True, options=None, dbqt_config=None):
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
    # global options  # .refseq_folder, db_import_manifest, dbqt_config
    logging.debug('Function: db_import_manifest_read()...')

    command_args_postprocess_db_import(options=options)

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
                logging.warning(
                    'In config: database name \'%s\' was found in the config file under [db_source_files] but does not have'
                    'a format defined in [db_source_formats]. (Skipping)' % dbnm)
                db_format = ''
                db_to_import = 0
            else:  # Format Specified --> OK
                db_fmt_val = dbqt_config['db_source_formats'][dbnm]
                db_fmt_tup = db_fmt_val.strip().split(' ')
                db_format = db_fmt_tup[0]
                if len(db_fmt_tup) >= 2:
                    try:
                        db_to_import = int(db_fmt_tup[1])
                    except:
                        logging.warning(
                            'In config: database format string for \'%s\' contains a second space-delimited value that '
                            'could not be read as either a 0 or 1 (treating as 1). (Read: %s)' % (dbnm, db_fmt_tup[1]))
                        db_to_import = 1
                    if len(db_fmt_tup) > 2:
                        logging.warning(
                            'In config: Database format string for \'%s\' contains more than one space. Using only the '
                            'first two values. (string: \'%s\')' % (dbnm, db_fmt_val))
                else:
                    logging.warning(
                        'In config: Database format string for \'%s\' does not contain a space: assuming final value of 1 (proceeding to import). (string: \'%s\')' % (
                        dbnm, db_fmt_val))
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
            if len(ln.strip()) <= 1:
                continue
            f = ln.strip().split('\t')
            if len(f) < 3:
                logging.warning(
                    'In Manifest: line %d cannot be parsed (fewer than 3 tab-delimited fields). Line as read: \n\t%s' % (
                    lno, ln.strip()))
        # if f[0] in db_import_manifest_parsed:
        #     logging.info('Database %s was given in both the config and manifest file. Manifest will be used.')
        # print(f[0])
        # db_import_manifest_parsed[f[0]] = [f[0], f[1], f[2], f[3], 'manifest']
        # lno += 1

    for flds in db_import_manifest_parsed.values():
        # logging.debug(str(flds))
        db_name = flds[0]
        db_filepath = os.path.abspath(os.path.expanduser(flds[1]))
        # db_filepath = os.path.join(flds[1], flds[2])
        db_format = flds[2]
        db_to_import = bool(int(flds[3]))
        db_spec_source = flds[4]
        if db_to_import:
            if db_name.lower() == 'refseq' and not skip_refseq:  # If the line is for RefSeq, do it differently...
                new_refseq_dir = os.path.abspath(os.path.expanduser(flds[1]))
                if os.path.isdir(new_refseq_dir):
                    logging.debug(
                        'found RefSeq in the manifest list. Replacing config refseq folder with:\n\t%s' % new_refseq_dir)
                    options.refseq_folder = new_refseq_dir
                    refseq_in_source_list = True
                else:
                    logging.warning(' - RefSeq (line %s) has path column that is not a valid folder:\n\t%s' % (
                    line_no, new_refseq_dir))

            else:  # ...otherwise send it to the text parser
                if os.path.isfile(db_filepath):
                    db_tuple = make_tuple_with_metadata(db_filepath, db_name, db_format)
                    db_tuple += (db_spec_source,)
                    db_import_manifest_output.append(db_tuple)
                else:
                    logging.debug(' - File in source list does not exist (line %s, db=%s)\n\t%s' % (
                    line_no, db_name, db_filepath))
                    no_file_errors.append((db_filepath, db_name, db_format, db_spec_source))
        else:  # Add to the skips list
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

def db_import_manifest_print_specs(options=None):
    '''
    Prints the help description for the specs of the database source roster (i.e. db_import_manifest).
    :return:
    '''
    mydesc = 'A roster of new databases can be specified using a tab-delimited text file. In order to use this format, ' \
             'a file path must be specified either at the command line (using the flag \'-dbs <PATH>\') or in the config ' \
             'file (under the [paths] section, named \'path_to_db_import_manifest\').'

    hstr = '''
%s

The specified file must be tab-delimited text, with a single header row. Each database is given in a single row, with the following fields (in order):
    DB_Name:  Simple string identifying the database (e.g. 'RefSeq_v90' or 'kaiju_db_nr_euk')
    Path:     Path to the file. If this is not an absolute path it will be considered relative to the working folder.
    Format:   The name of the format spec (from the config file) to use.
    Import:   Set to 0 if the row should be skipped during processing, 1 otherwise.''' % mydesc
    print(mydesc)
    if options.logfile is not None:
        logging.info(mydesc)

def db_import_search_refseq_dir(custom_refseq_dir=None, options=None):
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
            refseq_tuple_list.append(
                make_tuple_with_metadata(fpath, 'RefSeq_v' + version, 'refseq') + ('refseq_folder',))
    return refseq_tuple_list


