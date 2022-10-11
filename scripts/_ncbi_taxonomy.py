#! usr/bin/python3
import shutil, urllib.request, zipfile, time, os, logging


ncbi_tax_levels = ['no rank', 'superkingdom', 'kingdom', 'subkingdom', 'superphylum', 'phylum', 'subphylum',
                   'superclass', 'class', 'subclass', 'infraclass', 'cohort', 'subcohort', 'superorder', 'order',
                   'suborder', 'infraorder', 'parvorder', 'superfamily', 'family', 'subfamily', 'tribe', 'subtribe',
                   'genus', 'subgenus', 'section', 'subsection', 'series', 'species group', 'species subgroup',
                   'species', 'subspecies', 'varietas', 'forma','strain', 'clade']
rank2index = lambda x: ncbi_tax_levels.index(x)


def ncbi_taxonomy_parse_file(options=None):
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

