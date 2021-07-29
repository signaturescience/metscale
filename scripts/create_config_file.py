#!/bin/env python
## Created by Matthew Scholz for Signature Science 11/15/2020

import json
import glob
import argparse

def get_input_required_options(text,required_options):
    print(text)
    option_string = ""

    while True:
        ok = ""
        intake = input()
        if intake == "":
            print("you must choose an option:",required_options)
            continue
        if "," in intake:
            for splits in intake.split(","):
                if splits not in required_options:
                    print(splits,"not allowed")
                    ok = "no"
            if ok != "no":
                return intake
            else:
                print("you must enter one of the following:", required_options)
        else:
            if intake in required_options:
                return intake
            else:
                print("you must enter one of the following:",required_options)




assembler_labels = ['assembler', 'multiqc_assembler']
assembler_type = ""
default_qual = ["2","30"]
default_kvalue = ["21","31","51"]
config_internals = ['pre_trimming_pattern','pre_trimming_pattern','pre_trimming_pattern', 'reverse_pe_pattern_replace','sample_file_ext']
with open("config/my_custom_config_strict.json", "r") as f:
    data = json.load(f)

from datetime import datetime

day = str(datetime.now().day)
month = str(datetime.now().month)
year = str(datetime.now().year)

date_string = "".join([day,month,year])

keep = get_input_required_options("Custom config file will be named 'custom_config_"+date_string+".json  OK? (y/n):", ['y', 'n'])

if keep == 'n':
    print("enter string for filename")
    out_file_name = input()
else:
    out_file_name = "custom_config_"+date_string+".json"


read_info_template = {
    'metscale':{
        "read_patterns" : {
            "pre_trimming_pattern"  : "{sample}_{direction}_reads",
            "pre_trimming_glob_pattern"  : "*_1_reads.fq.gz",
            "reverse_pe_pattern_search"  : "1_",
            "reverse_pe_pattern_replace" : "2_"
        },
        "quality_trimming" : {
            "sample_file_ext" : ".fq.gz"
        }
    },
    'illumina':{
        "read_patterns" : {
            "pre_trimming_pattern"  : "{sample}_{direction}_reads",
            "pre_trimming_glob_pattern"  : "*_S*_L*_R1_001.fastq.gz",
            "reverse_pe_pattern_search"  : "R1",
            "reverse_pe_pattern_replace" : "R2",
        },
        "quality_trimming" : {
            "sample_file_ext" : ".fastq.gz"
        },
    }
}

read_info = read_info_template['metscale']
quals=[]
qual_range = []
for i in range(2,39):
    qual_range.append(str(i))
keep = get_input_required_options("keep default quality trimming at"+str(default_qual)+"? (y/n)",['y', 'n'] )
if keep == 'n':
    qual_list = get_input_required_options("select quality to trim at, extra qualities separate by (,):", qual_range)
    if len(qual_list) == 0:
        quals = default_qual
    else:
        if "," in qual_list:
            quals = qual_list.split(",")
        else:
            quals.extend(qual_list)
else:
    quals.extend(default_qual)

print("default is to use the following kmers:",default_kvalue)
keep = get_input_required_options("accept? y/n", ['y', 'n'])
if "y" in keep:
    print("kept")
else:
    default_kvalue=[]
    new_kmers = []
    kmer_range = []
    for i in range(5,121,2):
        kmer_range.append(str(i))
    values = get_input_required_options("enter comma separated K values to use", kmer_range)
    if "," in values:
        new_kmers = values.split(",")
    else:
        new_kmers.append(values)
    for entry in new_kmers:
        if not int(entry):
            print(entry,"is not a digit, please try again")
            quit()
        else:
            default_kvalue.append(entry)


print("define patterns:")

while True:
    keep = get_input_required_options("You may select 'illumina' , 'metscale', or 'custom' parameters for input patterns:", ['illumina', 'metscale', 'custom'])
    if (keep == 'custom'):
        for topLevel in read_info:
            print(topLevel)
            for values in read_info[topLevel]:
                take = input(values+"= (default ="+read_info[topLevel][values]+"), blank to keep the same:")
                if len(take) > 0:
                    manual_values = ",".split(take)
                    read_info[topLevel][values] = manual_values
                else:
                    print("keeping",read_info[topLevel][values])
    else:
        read_info = read_info_template[keep]
    print("current patterns:", read_info)

    file_list = glob.glob("data/"+read_info['read_patterns']['pre_trimming_glob_pattern'])
    data_list = []
    for name in file_list:
        pattern = read_info['read_patterns']['pre_trimming_glob_pattern'].replace("*", "")
        print(pattern)
        name = name.replace(pattern, "")
    #replace with \/ when porting to unix
        name = name.replace("data/", "")
        data_list.append(name)
    print("patterns will result in list:" ,data_list)
    if 'y' in get_input_required_options("approve? (y/n)", ["y", "n"]):
        print("OK")
        file_list = data_list
        break
    else:
        if get_input_required_options("Change file patterns?(y/n)", ['y','n']) == 'y':
            continue
        elif get_input_required_options("manually enter patterns? (y/n)", ['y', 'n']) == 'y':
            file_list = input("Enter the desired patterns:\n")
            if "," in file_list:
                file_list = file_list.split(",")
            break
        elif get_input_required_options("Leave blank?(y/n)",['y','n']) == y:
            file_list = []
            break
        else:
            print("cannot find file pattern, stopping")
            exit(1)

customize = get_input_required_options("Do you want to customize databases or other values? (y/n)\n(Select no unless you know what you're doing):", ['y', 'n'])
if customize == 'y':
    assembler_type=get_input_required_options("Please select your assemblers: ('megahit', 'metaspades', or 'megahit,metaspades'):", ['megahit', 'metaspades', 'megahit,metaspades'])
comment = ""
for level1 in data:
    if level1 == "read_patterns":
        data[level1] = read_info
        continue
    for subs in data[level1]:
        if subs == "samples_input_workflow":
            data[level1][subs]['samples'] = file_list
            continue
        for values in data[level1][subs]:

            if values == "qual":
                data[level1][subs][values] = quals
            elif values == "kvalue":
                data[level1][subs][values] = default_kvalue
            elif values == 'kmers':
                data[level1][subs][values] = default_kvalue
            elif "y" in customize:
                if values in assembler_labels:
                    #print("you previously selected",assembler_type,"for:", values)
                    data[level1][subs][values] = assembler_type
                    comment = ""
                    continue
                elif values in config_internals:
                    comment = "__\n"
                    continue
                elif "comment" in values:
                    comment = comment+" ".join([subs, level1, data[level1][subs][values]])
                else:
                    print(comment)
                    comment = "--\n"
                    print("select value for",level1,values,", leave blank to keep:\n", data[level1][subs][values])
                    take = input()
                    if len(take) == 0:
                        take = data[level1][subs][values]
                        print("you selected",take,"for:" , values, "\n--\n")
                    data[level1][subs][values] = take
            else:
                continue

out = open(out_file_name, "w")
out.write(json.dumps(data, indent=4))
