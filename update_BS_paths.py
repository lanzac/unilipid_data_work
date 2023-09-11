#!/usr/bin/env python3

import subprocess

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

    print(f"expored_path: {explored_path}")

    if explored_path in bs_dependencies_path:
        print("It is already explored.")
        return
    else:
        print("This path is new, with store it.")
        bs_dependencies_path.append(explored_path)

        new_dependencies_paths = get_dependencies_paths(explored_path)
        print(f"Its dependencies: {new_dependencies_paths}")
        if new_dependencies_paths is not None:
            for path in new_dependencies_paths:
                explore_dependencies(path)


bs_dependencies_path = []
explore_dependencies(BS_RPATH)

bs_dependencies_path.remove(BS_RPATH)

print(bs_dependencies_path)

for lib_path in bs_dependencies_path:
    try:
        subprocess.check_output(["cp", lib_path, LIB_RPATH])
    except:
        print(f"cp {lib_path} to {LIB_RPATH} failed. Try to run script with sudo.")

quit()

