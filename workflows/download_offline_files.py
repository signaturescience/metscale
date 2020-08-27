import json
import subprocess
import requests
from shutil import copyfile
from distutils.dir_util import copy_tree
import urllib.request
import urllib
from urllib.parse import urlparse
import os
import sys
import argparse
import time
from socket import error as SocketError
from snakemake.io import expand


workflows=['read_filtering', 'test_files', 'assembly', 'comparison', 'sourmash_db', 'kaiju_db', 'taxonomic_classification', 'functional_inference', 'mtsv_db', 'all']  #keep all at the end of the list


CHOCOPLAN_DIR = "chocophlan_plus_viral"
UNIREF_DIR ="uniref90"
BRACKEN_DIR = "Bracken_Kraken2_DB"


def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)



def reporthook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    percent = min(int(count*block_size*100/total_size),100)
    sys.stdout.write("\r...%d%%, %d MB, %d KB/s, %d seconds passed" %
                    (percent, progress_size / (1024 * 1024), speed, duration))
    sys.stdout.flush()

#certain files want special attention Needs to be installed in certain subdir inside data folder
def download_extract_targz_file(file_name, install_sub_dir, install_dir, url_string):
    if not os.path.isdir(os.path.join(install_dir, install_sub_dir)):
        print("\nDownloading " + file_name)
        try:
            urllib.request.urlretrieve(url_string, install_dir+ "/"+ file_name, reporthook)
            mkdir_command = "mkdir " + install_dir + "/" +  install_sub_dir
            subprocess.run([mkdir_command], shell =True)
            gunzip_command = "gunzip " + install_dir + "/" + file_name
            subprocess.run([gunzip_command], shell =True)
            file_name = file_name.replace('.gz','')
            untar_command =  "tar -xvf " + install_dir + "/" + file_name + " -C " + install_dir + "/" +  install_sub_dir
            subprocess.run([untar_command], shell =True)
        except SocketError as e:
            print("Error downloading/extracting file " + file_name + "Retry script.")
            print(e)
        try:
            os.remove(install_dir+ "/"+file_name)
        except OSError:
            pass
    

def download_sourmash_files(data, workflow, install_dir):   
    tar_file = data[workflow]['sbttar']
    db = data[workflow]['databases']
    kv = data[workflow]['kvalue']
    sbturl = data[workflow]['sbturl']
    sourmash_files = expand(tar_file, database=db, kvalue=kv)
    for file in sourmash_files:
        if not (os.path.isfile(install_dir+"/"+file)):
            print("\nDownloading " + file +" from " +sbturl)
            try:
                urllib.request.urlretrieve("http://" +sbturl + '/' +file, install_dir +"/" +file, reporthook)
            except SocketError as e:
                print("Error downloading file " + file + "Retry script.")
                print(e)
#            try:
#                os.remove(install_dir+ "/"+file)
#            except OSError:
#                pass 

def download_kmer_files(file_name, install_sub_dir, install_dir, url_string):
    if not (os.path.isdir(install_dir + "/" + install_sub_dir)):
        mkdir_command = "mkdir " + install_dir + "/" + install_sub_dir
        subprocess.run([mkdir_command], shell =True)
    urllib.request.urlretrieve(url_string, install_dir+ "/" + install_sub_dir+ "/" +file_name, reporthook)              
                
def download_file(workflow, data, install_dir):
    if workflow in data.keys():
        if (workflow == "post_processing"):
            install_dir = "post_processing/"
        for file_name, url_string in data[workflow].items():   
            try:
                url = urlparse(url_string)
            except Exception as e:  #we don't care since some of the JSONS are not URL's
                pass
            if (file_name == 'sbttar'):     #sourmash files from the taxonomic classification workflow.
                download_sourmash_files(data, workflow, install_dir)
            elif (file_name == 'full_chocophlan_plus_viral.v0.1.1.tar.gz'):
                download_extract_targz_file(file_name, CHOCOPLAN_DIR, install_dir, url_string)
            elif (file_name == 'uniref90_annotated_1_1.tar.gz'):
                download_extract_targz_file(file_name, UNIREF_DIR, install_dir, url_string)
            elif (file_name.endswith("kmer_distrib")):
                download_kmer_files(file_name, BRACKEN_DIR, install_dir, url_string)
            elif (url.scheme == "http" or url.scheme == "https" or url.scheme == "ftp"):      #download via http, ftp
                if not  (os.path.isfile(os.path.join(install_dir, file_name)) ):
                    print("Downloading " +file_name + " from " + url_string)
                    try:
                        opener = urllib.request.build_opener()
                        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                        urllib.request.install_opener(opener)
                        urllib.request.urlretrieve(url_string, install_dir+ "/"+ file_name, reporthook)
                        if (file_name.endswith('.tgz') or file_name.endswith('.tar.gz')):
                            untar_command = "tar -zxvf " + install_dir+"/" + file_name + " -C " + install_dir + " && rm -f " + install_dir+"/" + file_name
                            subprocess.run([untar_command], shell=True) 
                        elif (file_name.endswith('.gz') and not file_name.endswith('fq.gz')):
                            unzip_command = "gunzip -c " + install_dir+"/" + file_name + " > " + install_dir + "/" + os.path.splitext(file_name)[0] + " && rm -f " + install_dir+"/" + file_name
                            subprocess.run([unzip_command], shell=True)
                    except SocketError as e:
                        print("Error downloading file " + file_name + " Retry script.")
                        print(e)
                        try:
                            os.remove(install_dir+ "/"+file_name)
                        except OSError:
                            print("Error unable to delete  " + file_name)
            elif (url.scheme == 'docker'):    #download singularity image
                if not (os.path.isfile("../container_images/"+file_name)):
                    print("Downloading singularity image " +file_name)
                    sing_command = "singularity pull "+url_string
                    try:
                        subprocess.run([sing_command], shell=True)   
                        os.rename(file_name, "../container_images/"+file_name)
                    except OSError as e:
                            print("OS Error  " + file_name)
                            print(e)
            elif (url.scheme == "dir"):  #copy dir
                if not (os.path.isdir(os.path.join(install_dir, file_name))):
                    print("Copying "+ file_name)
                    try:
                        copy_tree(".."+ url.path, install_dir+"/"+file_name)
                    except OSError as e:
                        print('Directory not copied. Error: ' +str(e))
            elif (url.scheme == "file"):         #copy file from local location
                if not (os.path.isfile(os.path.join(install_dir, file_name))):
                    print("Copying "+ file_name)
                    if (file_name.endswith('.tgz')):
                        untar_command = "tar -zxvf " + ".." + url.path + " -C " + install_dir + " && rm -f " + install_dir+"/" + file_name
                        try:
                            subprocess.run([untar_command], shell=True)
                        except OSError as e:
                            print('OS Error: ' +str(e))   
                    else: 
                        try: 
                            copyfile(".."+ url.path, install_dir+ "/"+ file_name)
                        except OSError as e:
                            print('File not copied. Error: ' +str(e))
            elif (url.scheme == "gdrive"):
                if not (os.path.isfile(os.path.join(install_dir, file_name))):
                    print("Downloading "+ file_name)
                    destination = os.path.join(install_dir, file_name)
                    try:
                        download_file_from_google_drive(url.netloc, destination)
                    except OSError as e:
                        print("Failed download from GDrive for " + file_name)
                         
    
def main_func(user_input, install_dir, file_list='config/offline_downloads.json'):   
    try:
        with open(file_list)as f:
            data = json.load(f)
    except IOError:
        print("Error: offline_downloads.json is missing. Exiting")
        sys.exit(1)
         
    try:
        if not os.path.isdir("data"):
            os.mkdir("data")
    except IOError:
        print("Error: can't create data directory")     
    if ('all' in user_input):
        user_input = workflows[0:-1]
        for workflow in user_input:     
            download_file(workflow, data, install_dir)
    else:
        for workflow in user_input:
            download_file(workflow, data, install_dir)

        
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script to download data required for offline processing of Dahak software. Requires config/offline_downloads.json")
    parser.add_argument("--workflow", nargs='+', help="Download databases/images for inputed workflow", choices=workflows, type=str.lower, required=True)
    parser.add_argument("--data_dir", help="directory to copy non image files to", default="data")
    args = parser.parse_args()
    install_dir = args.data_dir
    user_input = args.workflow
    main_func(user_input, install_dir)
    



