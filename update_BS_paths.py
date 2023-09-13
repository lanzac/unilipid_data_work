#!/usr/bin/env python3

import subprocess
import os
import argparse
import shutil

BS_RPATH="../unilipid_data/software/Biospring/biospring_binaries_MacOS/bin/biospring"
PDB2SPN_RPATH="../unilipid_data/software/Biospring/biospring_binaries_MacOS/bin/pdb2spn"
LIB_RPATH="../unilipid_data/software/Biospring/biospring_binaries_MacOS/lib"

def get_dependencies_paths(input_path):

    # Exécute la commande otool -L et capture la sortie
    try:
        output = subprocess.check_output(["otool", "-L", input_path], universal_newlines=True)
    except:
        print("otool: An exception occurred")
        return

    # Splits output into lines
    lines = output.splitlines()

    # Initializes a list to store library paths
    library_paths = []

    # Loop on output lines to extract paths
        # Ignores the first line because it contains the name of the binary itself
    for line in lines[1:]:
        library_path = line.strip().split(" ")[0]
        library_paths.append(library_path)

    return library_paths

def explore_dependencies(explored_path):

    # print("-"*20)
    # print(f"expored_path: {explored_path}")

    if explored_path in all_dependencies_path:
        # print("It is already explored.")
        return
    else:

        # if explored_path.startswith("@executable_path"):
        #     print("This path is already a relative path. We store it and going to check its dependencies.")
        #     # We recover its relative path
        #     lib_rpath = os.path.join(LIB_RPATH, os.path.basename(explored_path))
        #     explored_path = os.path.join(LIB_RPATH, os.path.basename(explored_path))
        
        all_dependencies_path.append(explored_path)
        
        
        new_dependencies_paths = get_dependencies_paths(explored_path)
        # print(f"Its dependencies: {new_dependencies_paths}")
        if new_dependencies_paths is not None:
            for path in new_dependencies_paths:
                explore_dependencies(path)

# https://www.tutorialspoint.com/How-to-delete-all-files-in-a-directory-with-Python      
def delete_files_in_directory(directory_path):
   try:
     files = os.listdir(directory_path)
     for file in files:
       file_path = os.path.join(directory_path, file)
       if os.path.isfile(file_path):
         os.remove(file_path)
     print("All files deleted successfully.")
   except OSError:
     print("Error occurred while deleting files.")

def print_dir_files(directory_path):
    files = os.listdir(directory_path)
    for file in files:
        print(file)

def run_subprocess(arguments_list, print_output=True):
    try:
        # Run the locate command and capture the output
        output = subprocess.check_output(arguments_list, universal_newlines=True)

        # Print the output
        if print_output:
            print(f"Output of {arguments_list[0]} command:")
            print(output)
    except subprocess.CalledProcessError as e:
        print(f"Error of {arguments_list[0]} command: {e}")

def change_bin_dependency_path(old, new, bin_path):
    run_subprocess(["install_name_tool", "-change", old, new, bin_path], print_output=False)

def copy_file(source_file, destination_directory):
    # Use shutil.copy() to copy the file
    try:
        shutil.copy(source_file, destination_directory)
        # print(f"File '{source_file}' copied to '{destination_directory}'.")
    except FileNotFoundError:
        print(f"Source file '{source_file}' not found.")
        return False
    except PermissionError:
        print(f"Permission denied. You may not have the required permissions to copy the file.")
        return False
    except shutil.Error as e:
        print(f"Error copying the file: {e}")
        return False
    return True


# all_dependencies_path = []
# explore_dependencies(BS_RPATH)
# all_dependencies_path.remove(BS_RPATH)

# print(all_dependencies_path)



# copied_dep = []

# for lib_path in all_dependencies_path:
#     try:
#         subprocess.check_output(["cp", lib_path, LIB_RPATH])
#         copied_dep.append(lib_path)
#     except:
#         print(f"cp {lib_path} to {LIB_RPATH} failed. Try to run script with sudo.")

# # install_name_tool -change /usr/local/lib/libomp.dylib @executable_path/../lib/libomp.dylib pdb2spn

# bs_main_dependencies = get_dependencies_paths(BS_RPATH)


# for path in bs_main_dependencies:
#     if path in copied_dep:
#         print(f"install_name_tool -change {path} @executable_path/../lib/{os.path.basename(path)} {BS_RPATH}")
#         # subprocess.check_output(["install_name_tool", "-change", path, f"@executable_path/../lib/{os.path.basename(path)}", {BS_RPATH}])



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Recursive exploration and local packaging of binary dependencies in a ../lib directory.")
    parser.add_argument('binary_path', type=str, help='Binary path')
    args = parser.parse_args()

    # Check if the file given in "binary_path" exists
    if os.path.isfile(args.binary_path):
        BIN_PATH = os.path.abspath(args.binary_path)
    else:
        print(f"The file {args.binary_path} does not exist.")
        quit()
    
    # Check if binary is in bin directory
    if os.path.dirname(BIN_PATH).endswith("bin"):
        BIN_DIR = os.path.dirname(BIN_PATH)
    else:
        print(f"The file {args.binary_path} should be in bin directory.")
        quit()
    
    # Check if ../lib directy exists, create it if this is not the case
    tmp_lib_rpath = os.path.join(BIN_DIR, "..", "lib")
    if not os.path.exists(tmp_lib_rpath):
        user_input = input(f"The '../lib' directory does not exist. Do you want to create it? (y/n): ").strip().lower()
        if user_input == 'y':
            os.makedirs(tmp_lib_rpath)
        else:
            print("Ok goodbye then.")
            quit()
        
    LIB_DIR = os.path.abspath(tmp_lib_rpath)

    # Check if there are files in lib directory
    # User need to clean all directory to continue
    # libdir_contents = os.listdir(LIB_DIR)
    # if libdir_contents:
    #     print("-"*20)
    #     print_dir_files(LIB_DIR)
    #     user_input = input(f"There are {len(libdir_contents)} file(s) in the lib directory. Do you want to remove them ? Script stops if No. (y/n)").strip().lower()
    #     if user_input == 'y':
    #         delete_files_in_directory(LIB_DIR)
    #     else:
    #         print("Keep files in lib directory. End of script.")
    #         quit()

    # Try to find existing lib directory associated with binary


    all_dependencies_path = []
    explore_dependencies(BIN_PATH)
    all_dependencies_path.remove(BIN_PATH)
    print(all_dependencies_path)

    all_lib_names = []
    for dep_path in all_dependencies_path:
        print(f"Try to copy '{dep_path}' to library directory")
        if copy_file(dep_path, LIB_DIR):
            lib_name = os.path.basename(dep_path)
            all_lib_names.append(lib_name)
    
    print(all_lib_names)

    # Get binary dependencies
    print("-"*20)
    # Change dependencies paths of binary
    print("First level dependencies:")
    bin_dependencies_paths = get_dependencies_paths(BIN_PATH)
    for path in bin_dependencies_paths:
        lib_name = os.path.basename(path)
        if lib_name in all_lib_names:
            change_bin_dependency_path(path, os.path.join("@executable_path/../lib", lib_name), BIN_PATH)

    # Change dependencies paths of libraries in ../lib
    for lib_name_main in all_lib_names:
        lib_dependencies_paths = get_dependencies_paths(os.path.join(LIB_DIR, lib_name_main))
        print(lib_name_main)

        for path in lib_dependencies_paths:
            lib_name_sub = os.path.basename(path)
            if lib_name_sub in all_lib_names:
                change_bin_dependency_path(path, os.path.join("@executable_path/../lib", lib_name_sub), os.path.join(LIB_DIR, lib_name_main))
    


    # Check if all paths point to existing file and are absolute and not in "@executable_path/../" form.
    # for path in bin_dependencies_paths:
    #     if not os.path.isfile(path):
    #         if path.startswith("@executable_path"):
    #             print(f"ERROR: {path} is in relative path form. We should first have only absolute paths. End of script.")
    #             quit()
    #         print(f"WARNING: {path} does not exist.")
    #     else:
    #         print(f"File '{path}' copied to library directory")
    #         copy_file(path, LIB_DIR)
    #         print("Change to relative path ../lib")
    #         lib_name = os.path.basename(path)
    #         change_bin_dependency_path(path, os.path.join("@executable_path/../lib", lib_name), BIN_PATH)



    # for path in bin_dependencies_paths:
    #     if path.startswith("@executable_path"):
    #         # Check if it's a valid format
    #         lib_name = os.path.basename(path)
    #         valid_lib_path = os.path.join("@executable_path/../lib", lib_name)
    #         if path != valid_lib_path:
    #             print(f"{path} is not in a valid format! It should be: {valid_lib_path}")

    #         # This path is a valid relative path, check if the corresponding lib exists in LIB_DIR
    #         if not os.path.exists(os.path.join(LIB_DIR, lib_name)):
    #             user_input = input(f"{lib_name} does not exist in lib directory! Try to locate this lib ? (y/n)")
    #             if user_input == 'y':
    #                 run_subprocess(["locate", lib_name])
    #                 # Propose to change the path of dependency
    #                 user_input = input(f"Enter new path for {lib_name}: ")
    #                 # Check user_input file path
    #                 if os.path.isfile(user_input):
    #                     change_bin_dependency_path(path, user_input, BIN_PATH)
    #             else:
    #                 print("Keep this path.")
                
    #         print(f"{path} is a valid relative path and {lib_name} exists in lib directory.")

    #     else:
    #         print(path)
    
    # print(bin_dependencies_paths)

    quit()

