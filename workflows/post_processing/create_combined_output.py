import argparse
import subprocess
import os



#create combined_output.json
if __name__ == '__main__':
#    parser = argparse.ArgumentParser()
#    parser.add_argument("--input", help="input/data dir")
#    parser.add_argument("--post", help="post_processing dir")
#    args = parser.parse_args()
#   subprocess.call (["Rscript", "process_output.R", args.input, args.post])
    input = snakemake.params[0]
    post_processing = snakemake.params[1]
    os.chdir(post_processing)
    
    path_to_script = os.path.join(post_processing, "process_output.R")
    subprocess.call (["Rscript", "process_output.R", input, post_processing])
    input_str = post_processing + "/combined_output.json"
    output_str = input + "/combined_output.json"
    subprocess.call(["mv", input_str, output_str])
