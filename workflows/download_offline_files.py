import json
import urllib.request
import subprocess
import os
import sys
import argparse


selections=['read_filtering', 'test_files', 'all']  #keep all at the end of the list

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script to download data required for offline processing of Dahak software")
    parser.add_argument("--workflow", help="Download databases/images for inputed workflow", choices=selections, type=str.lower, required=True)
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
    
    if (user_input == 'all'):
        user_input = selections[0:-1]
    for selection in user_input:     
        if selection in data.keys():
            for file_name,url in data[selection].items():
                file_type = url.partition(":")[0] 
                if (file_type == 'https' or file_type == 'http'):
                    print("Downloading " +file_name)
                    urllib.request.urlretrieve(url, install_dir+"/"+file_name)
                elif (file_type == 'docker'):
                    print("Downloading singularity image " +file_name)
                    sing_command = "singularity pull "+url
                    subprocess.run([sing_command], shell=True)
                    os.rename(file_name, "../container_images/"+file_name)

