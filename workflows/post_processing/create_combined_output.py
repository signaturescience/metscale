import argparse
import subprocess



#create combined_output.json
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="input/data dir")
    parser.add_argument("--post", help="post_processing dir")
    args = parser.parse_args()
    print(args)

    #process_str = "process_output.R " + args.input + " " + args.post
    subprocess.call (["Rscript", "process_output.R", args.input, args.post])
    input_str = args.post + "/combined_output.json"
    output_str = args.input + "/combined_output.json"
    subprocess.call(["mv", input_str, output_str])
