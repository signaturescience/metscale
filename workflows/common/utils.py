from os.path import join
import re, glob

def container_image_is_external(biocontainers, app):
    """
    Return a boolean: is this container going to be run
    using an external URL (quay.io/biocontainers),
    or is it going to use a local, named Docker image?
    """
    try:
        d = biocontainers[app]
        if (('use_local' in d) and (d['use_local'] is True)):
            # This container does not use an external url
            return False
        else:
            # This container uses a quay.io url
            return True

    except KeyError:
        # No "biocontainers" key specified in params.
        # 
        # We can either crash here,
        # or hope the user knows what
        # they're doing.
        # 
        return True 


def container_image_name(biocontainers, app):
    """
    Get the name of a container image for app,
    using params dictionary biocontainers.

    Verification:
    - Check that the user provides 'local' if 'use_local' is True
    - Check that the user provides both 'quayurl' and 'version'
    """
    if container_image_is_external(biocontainers,app):
        try:
            qurl  = biocontainers[app]['quayurl']
            qvers = biocontainers[app]['version']
            quayurl = "docker://" + qurl + ":" + qvers
            return quayurl
        except KeyError:
            err = "Error: quay.io URL for %s biocontainer "%(app)
            err += "could not be determined"
            raise Exception(err)

    else:
        try:
            dir_loc = biocontainers[app]['location']
            file_name =  biocontainers[app]['filename']
            full_path = "file:"+dir_loc+file_name
            return full_path
        except KeyError:
            err = "Error: the parameters provided specify a local "
            err += "container image should be used for %s, but none "%(app)
            err += "was specified using the 'local' key."
            raise Exception(err)

'''
def get_sample_inputs(all_sample_names, read_glob_pattern, read_file_ext, data_dir):
    ###################################
    # Code to get samples input files based on sample name and glob file pattern

    #Using user defined params get input file list
    #workflows = config['workflows']
    #all_sample_names = workflows['samples_input_workflow']['samples']
    sample_input_files = []
    for sample in all_sample_names:
        input_file_pattern = read_glob_pattern #readfilt['read_patterns']['pre_trimming_glob_pattern']
        input_file_pattern = re.sub(r"\*", sample, input_file_pattern, 1)
        input_file_pattern = join(data_dir, input_file_pattern)
        print("input_file_pattern: "+str(input_file_pattern))
        sample_input_files.extend(glob.glob(input_file_pattern))

    #now we need to remove file extension and data_dir
    file_names = []
    for file in sample_input_files:
        file_path_no_dir = file.replace(data_dir+'/','')
        #file_names.append(file_path_no_dir.replace(readfilt["quality_trimming"]["sample_file_ext"],''))
        file_names.append(file_path_no_dir.replace(read_file_ext,''))
    sample_input_files = file_names
    return sample_input_files
'''

def get_samples_filenames(workflows, readfilt, post_processing, data_dir):
    # Code to get samples input files based on sample name and glob file pattern
    #Using user defined params get input file list
    
    all_sample_names = workflows['samples_input_workflow']['samples']
    sample_input_files = []
    sample_finished_folders = [] # Also checking for data subfolders with '_finished' appended
    for sample in all_sample_names:
        input_file_pattern = readfilt['read_patterns']['pre_trimming_glob_pattern']
        input_file_pattern = re.sub(r"\*", sample, input_file_pattern, 1)
        input_file_pattern = join(data_dir, input_file_pattern)
        finished_folder_output_pattern = post_processing['move_samples_to_dir']['output_pattern'].replace('{sample}','')
        finished_folder_pattern = input_file_pattern.replace(readfilt["quality_trimming"]["sample_file_ext"], finished_folder_output_pattern) 
        sample_input_files.extend(glob.glob(input_file_pattern))
        sample_finished_folders.extend(glob.glob(finished_folder_pattern))

    #now we need to remove file extension and data_dir
    file_names = []
    for file in sample_input_files:
        file_path_no_dir = file.replace(data_dir+'/','')
        file_names.append(file_path_no_dir.replace(readfilt["quality_trimming"]["sample_file_ext"],''))
    sample_input_files = file_names
    if (sample_input_files == [] and sample_finished_folders == []):
        print("Warning: No input files found!")
    return sample_input_files, sample_finished_folders