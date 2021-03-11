import json
import argparse
import pandas as pd
import os
import matplotlib.patches as mpatches
import numpy as np
import matplotlib.pyplot as plt


RED = [255,0,0]
ORANGE = [255,165,0]
YELLOW = [255,255,0]
GREEN = [0,128,0]
BLUE = [0,0,255]
GREY = [128,128,128]
WHITE = [255,255,255]
NUM_SPECIES_ROWS = 16


def get_bracken_color(val):
    if val > 100000:
        return RED
    elif val > 30000:
        return ORANGE
    elif val > 10000:
        return YELLOW
    elif val > 1000:
        return GREEN
    elif val > 100:
        return BLUE
    elif val > 0:
        return GREY
    else:
        return WHITE

def get_krakenuniq_color(val):
    if val > 10000:
        return RED
    elif val > 5000:
        return ORANGE
    elif val > 2000:
        return YELLOW
    elif val > 1000:
        return GREEN
    elif val > 500:
        return BLUE
    elif val > 0:
        return GREY
    else:
        return WHITE

def get_kaiju_color(val):
    if val > 100000:
        return RED
    elif val > 30000:
        return ORANGE
    elif val > 10000:
        return YELLOW
    elif val > 1000:
        return GREEN
    elif val > 100:
        return BLUE
    elif val > 0:
        return GREY
    else:
        return WHITE

def get_mash_color(val):
    if val > .95:
        return RED
    elif val > .90:
        return ORANGE
    elif val > .85:
        return YELLOW
    elif val > .80:
        return GREEN
    elif val > .75:
        return BLUE
    elif val > 0:
        return GREY
    else:
        return WHITE

def get_kraken2_color(val):
    if val > 100000:
        return RED
    elif val > 30000:
        return ORANGE
    elif val > 10000:
        return YELLOW
    elif val > 1000:
        return GREEN
    elif val > 100:
        return BLUE
    elif val > 0:
        return GREY
    else:
        return WHITE

def get_sourmash_color(val):
    if val > .6:
        return RED
    elif val >.2:
        return ORANGE
    elif val > .15:
        return YELLOW
    elif val > .1:
        return GREEN
    elif val > .05:
        return BLUE
    elif val > 0:
        return GREY
    else:
        return WHITE

#create large dataset
def create_abundance_df(data):
    #create dict of id -> tool
    files_out_id = data.get('files').get('out_id')
    files_out_id = [int(x) for x in files_out_id]
    files_tool = data.get('files').get('tool')
    tools_dict = dict(zip(files_out_id, files_tool))

    #create a dict of id -> trim
    files_trim = data.get('files').get('trim')
    trim_dict = dict(zip(files_out_id, files_trim))

    species_id = data.get('variables').get('species_id')
    species_name = get_species_name(species_id, data)
    var_name = data.get('variables').get('var_name')
    var_value = data.get('variables').get('var_value')
    var_value = [float(x) for x in var_value]
    out_id = data.get('variables').get('out_id')
    out_id = [int(x) for x in out_id]
    tool = []
    for id in out_id:  #slow refactor
        tool.append(tools_dict[id])
    trim = []
    for id in out_id:  #slow refactor
        trim.append(trim_dict[id])

    vars_df = pd.DataFrame(list(zip(species_name, var_name, var_value, tool, trim)), columns=['SpeciesName', 'Measure', 'Score', 'Tool', 'Trim'])
    vars_df['Species_Trim'] = vars_df['SpeciesName'] + " Trim:" + vars_df['Trim']
    vars_df = vars_df.drop(['SpeciesName', 'Trim'], axis=1)
    vars_df.set_index('Species_Trim', inplace=True)
    #vars_df.to_csv("var_df_large.csv")

    #Create smailler dataset that we will use
    bracken_df = vars_df[(vars_df['Tool']=='Bracken')&(vars_df['Measure']=='new_est_reads')]
    bracken_df = bracken_df.drop(columns=['Measure','Tool'])
    bracken_df = bracken_df.rename(columns={"Score": "Bracken"})

    kaiju_df = vars_df[(vars_df['Tool']=='Kaiju')&(vars_df['Measure']=='read_count')]
    kaiju_df = kaiju_df.drop(columns=['Measure','Tool'])
    kaiju_df = kaiju_df.rename(columns={"Score": "Kaiju"})

    kraken2_df = vars_df[(vars_df['Tool']=='Kraken2')&(vars_df['Measure']=='fragments')]
    kraken2_df = kraken2_df.drop(columns=['Measure','Tool'])
    kraken2_df = kraken2_df.rename(columns={"Score": "Kraken2"})

    krakenuniq_df = vars_df[(vars_df['Tool']=='KrakenUniq')&(vars_df['Measure']=='kmers')]
    krakenuniq_df = krakenuniq_df.drop(columns=['Measure','Tool'])
    krakenuniq_df = krakenuniq_df.rename(columns={"Score": "KrakenUniq"})

    sourmash_df = vars_df[(vars_df['Tool']=='Sourmash')&(vars_df['Measure']=='f_match')]
    sourmash_df = sourmash_df.groupby(['Species_Trim']).max()
    sourmash_df = sourmash_df.drop(columns=['Measure','Tool'])
    sourmash_df = sourmash_df.rename(columns={"Score": "Sourmash"})

    mash_df = vars_df[(vars_df['Tool']=='Mash Screen')&(vars_df['Measure']=='identity')]
    mash_df = mash_df.groupby(['Species_Trim']).max()  #slow refactor
    mash_df = mash_df.drop(columns=['Measure','Tool'])
    mash_df = mash_df.rename(columns={"Score": "Mash"})

    #Only use ![] df's, create df
    populated_workflows_df = []
    workflow_cols = []
    if (not bracken_df.empty):
        populated_workflows_df.append(bracken_df)
        workflow_cols.append("Bracken")
    if (not kaiju_df.empty):
        populated_workflows_df.append(kaiju_df)
        workflow_cols.append("Kaiju")
    if (not krakenuniq_df.empty):
        populated_workflows_df.append(krakenuniq_df)
        workflow_cols.append("KrakenUniq")
    if (not kraken2_df.empty):
        populated_workflows_df.append(kraken2_df)
        workflow_cols.append("Kraken2")
    if (not mash_df.empty):
        populated_workflows_df.append(mash_df)
        workflow_cols.append("Mash")
    if (not sourmash_df.empty):
        populated_workflows_df.append(sourmash_df)
        workflow_cols.append("Sourmash")
    abundance_df = pd.concat(populated_workflows_df, sort=True)
    for workflow in workflow_cols:
        abundance_df[workflow] = abundance_df[workflow].fillna(0)
    abundance_df = abundance_df.groupby(['Species_Trim']).sum()
    return abundance_df, workflow_cols


def get_color(name, val):
    if name == 'Bracken':
        return get_bracken_color(val)
    elif name == 'Kaiju':
        return get_kaiju_color(val)
    elif name == 'KrakenUniq' :
        return get_krakenuniq_color(val)
    elif name == 'Kraken2':
        return get_kraken2_color(val)
    elif name == 'Mash':
        return get_mash_color(val)
    else:
        return get_sourmash_color(val)


def create_graph(sorted_data, workflow_cols, data_dir):
    c = []
    for _, row in sorted_data.iterrows():
        c_row = []
        for idx, val in enumerate(row):
            c_row.append(get_color(sorted_data.columns[idx], val))
        c.append(c_row)
    n_row, n_col = sorted_data.shape
    np_c = np.asarray(c, dtype=np.int)
    y_tuple, x = np.array([(i,j) for i in sorted_data.index for j in workflow_cols]).T   #for explore_json.py
    y = [' '.join(el) for el in y_tuple]
    # Scatter does not expect a 3D array of uints but a 2D array of RGB floats
    c1 = (np_c/255.0).reshape(n_row*n_col,3)
    plt.scatter(x, y, c=c1, s=500, edgecolors='b')
    for species in y:
        plt.axhline(y = species, color ="green", linestyle =":")
    figure = plt.gcf()
    figure.set_size_inches(16,8)
    plt.title("Signal Plot v3")
    red_patch = mpatches.Patch(color='red', label='Very strong species signal')
    orange_patch = mpatches.Patch(color='orange', label='Strong species signal')
    yellow_patch = mpatches.Patch(color='yellow', label='Moderately strong species signal')
    green_patch = mpatches.Patch(color='green', label='Moderate species signal')
    blue_patch = mpatches.Patch(color='blue', label='Weak species signal')
    grey_patch = mpatches.Patch(color='grey', label='Very weak species signal')
    white_patch = mpatches.Patch(color='white', label='No species signal')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0., handles=[red_patch, orange_patch, yellow_patch, green_patch, blue_patch, grey_patch, white_patch])
    signal_path = os.path.join(data_dir, "signal_plot.png")
    plt.savefig(signal_path, dpi=100, bbox_inches='tight')


def get_species_name(ids, data):
    s = data.get('taxa').get('species_id')
    id = data.get('taxa').get('id')
    r = data.get('taxa').get('rank')
    n = data.get('taxa').get('name')
    species_name = {z[0]:list(z[1:]) for z in zip(s, r, n, id)}
    names_list = []
    for id in ids:
        if id != 'NA':
            id = int(id)
        names_list.append(species_name[id][1])
    return names_list


def get_all_rows_with_values(abundance_df):
    sorted_abundance_df = pd.DataFrame(columns = abundance_df.columns)
    for _, row in abundance_df.iterrows():
        if (row > 0).all():
            sorted_abundance_df = sorted_abundance_df.append(row)
    return sorted_abundance_df


def sorted_values(abundance_df):
    df = abundance_df.sort_values(by=list(abundance_df.columns), ascending=False)
    df = df.head(NUM_SPECIES_ROWS)
    return df


if __name__ == '__main__':
    #parser = argparse.ArgumentParser()
    #parser.add_argument("--data", help="data dir",default="/data/home/")
    #parser.add_argument("--post", help="post processing dir")
    #args = parser.parse_args()
    #data_path = args.data

    data_path = snakemake.params[0]  

    combined_output_path = os.path.join(data_path, "combined_output.json")
    with open(combined_output_path) as json_file:
        data = json.load(json_file)

    #create abundance dataframe from the json file
    abundance_df, workflow_cols = create_abundance_df(data)
    sorted_abundance_df = sorted_values(abundance_df)
    abundance_filepath = os.path.join(data_path, 'signal_plot.tsv')
    abundance_df.to_csv(abundance_filepath, sep='\t')
    create_graph(sorted_abundance_df, workflow_cols, data_path)  
