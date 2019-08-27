#! usr/bin/python
# Author: Dreycey Albin
# Update(s):07/12/2019 

import sys
import pickle

# purpose of this script
"""
This will be used as a query tool. The user should input a particular tax id, and the output will be the databases which contain that tax id. The input query is a file containing the organism tax ids seperated by new lines. 
"""

#Help message for using repeatmaker.py
if str(sys.argv[1]) in ('-h', '--help') or str(sys.argv[1]) == '':
    print ("\n")
    print ("#####################################################");
    print ("#                   ---DB-QUERY TOOL---             #");
    print ("#####################################################");
    print ("\n"*3)
    print ("USAGE: python query_tool.py <PATH TO PICKLE FILE> <QUERY FILE>")
    print ("EXAMPLE: python query_tool.py pickle_dir/containment_dict.p query_file.txt")
    print ("\n"*2)
    sys.exit()

# import the dictionary

containment_dict = pickle.load( open( sys.argv[1], "r" ) )

# import user query 

user_query_file = open(sys.argv[2])
user_query_file_read = user_query_file.readlines()

# read the lines of the query file
list1 = []
refseq_dict = {}
for taxid in user_query_file_read:
    taxid = int(taxid.split("\n")[0])
    list1 = []    
    if taxid in containment_dict:

        for db in containment_dict[taxid]:
            if "RefSeq" in db:
                list1.append(int(db.split("RefSeq")[-1].split("_v")[-1]))
                refseq_dict[int(db.split("RefSeq")[-1].split("_v")[-1])] = "RefSeq"
            else:
                list1.append(db)
        list1.sort()
        print "taxon["+str(taxid)+"]:",
        
        for item in list1:
            try:
                refseq_dict[item]
                print "RefSeq"+str(item),
            except KeyError:
                print str(item),
        print "===="
