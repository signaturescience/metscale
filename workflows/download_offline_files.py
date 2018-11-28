import json
import subprocess
import urllib.request
import os
import sys
import argparse
import time
from socket import error as SocketError
from snakemake.io import expand

workflows=['read_filtering', 'test_files', 'assembly', 'comparison', 'classification', 'inference', 'all']  #keep all at the end of the list

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
    
def download_file(workflow):
    if workflow in data.keys():
        for file_name, url in data[workflow].items():
            if (file_name == 'sbttar'):     #sourmash files from the taxonomic classification workflow.
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
                            try:
                                os.remove(install_dir+ "/"+file)
                            except OSError:
                                pass
            elif (':' in url):      #Normal files to DL
                file_type = url.partition(":")[0] 
                if (file_type == 'https' or file_type == 'http'):
                    if not (os.path.isfile(install_dir+"/"+file_name)):
                        print("Downloading " +file_name + " from " + url)
                        try:
                            urllib.request.urlretrieve(url, install_dir+ "/"+file_name, reporthook)
                        except SocketError as e:
                            print("Error downloading file " + file_name + " Retry script.")
                            print(e)
                            try:
                                os.remove(install_dir+ "/"+file_name)
                            except OSError:
                                pass
                elif (file_type == 'docker'):
                    if not (os.path.isfile("../container_images/"+file_name)):
                        print("Downloading singularity image " +file_name)
                        sing_command = "singularity pull "+url
                        subprocess.run([sing_command], shell=True)   #TODO: Error handling for sing pull
                        os.rename(file_name, "../container_images/"+file_name)    
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script to download data required for offline processing of Dahak software. Requires config/offline_downloads.json")
    parser.add_argument("--workflow", help="Download databases/images for inputed workflow", choices=workflows, type=str.lower, required=True)
    parser.add_argument("--data_dir", help="directory to copy non image files to", default="data")
    args = parser.parse_args()
    install_dir = args.data_dir
    user_input = args.workflow
    
    try:
        with open('config/offline_downloads.json')as f:
            data = json.load(f)
    except IOError:
        print("Error: config/offline_downloads.json is missing. Exiting")
        sys.exit(1)
         
    try:
        if not os.path.isdir("data"):
            os.mkdir("data")
    except IOError:
        print("Error: can't create data directory")     
    if (user_input == 'all'):
        user_input = workflows[0:-1]
        for workflow in user_input:     
            download_file(workflow)
    else:
        download_file(user_input)


