import argparse
import os
import json


def wrap_dict(path, content):
    return {path[0]: wrap_dict(path[1:], content)} if path else content

def get_files(path):
    all_files_list = os.popen(f"find {path} -type f").read().splitlines()
    return all_files_list

def get_files_with_ext(path,extlist):
    all_files = get_files(path)
    specific_files ={}
    for ext in extlist:
        specific_files[ext]=[]
        for file in all_files:
            if file.split(".")[-1] ==ext:
                specific_files[ext].append(file)
    return specific_files

def get_sub_folders(path):
    all_sub_directories_list = os.popen(f"find {path} -type d").read().splitlines()
    return all_sub_directories_list

def LastNlines(fname, N):
    assert N >= 0
    pos = N + 1
    lines = []
    with open(fname) as f:
        while len(lines) <= N:
            try:
                f.seek(-pos, 2)
            except IOError:
                f.seek(0)
                break
            finally:
                lines = list(f)
            pos *= 2
    return lines[-N:]


def merge_dict(dict1, dict2):
    for key, val in dict1.items():
        if type(val) == dict:
            if key in dict2 and type(dict2[key] == dict):
                merge_dict(dict1[key], dict2[key])
        else:
            if key in dict2:
                dict1[key] = dict2[key]

    for key, val in dict2.items():
        if not key in dict1:
            dict1[key] = val

    return dict1

parser = argparse.ArgumentParser(description='')

parser.add_argument('-parent',
                    help='The parent directory to parse.', required=True)

parser.add_argument("-log", action='store_true', help="parse output log files")


args = parser.parse_args()


files = get_files_with_ext(args.parent,["py","log"])
subdir = get_sub_folders("weak/patch-32-3/RK300")
del subdir[0]
print(subdir)
if args.log:
    data = []
    for path in subdir:
        path_as_list = path.split('/')
        file_path =path+"/out.log"

        lines = LastNlines(file_path, 2)
        core_data = {}
        if lines[-1] == "Sus: going down successfully":
            print("Successful")
            core_data["successful"] = True
        else:
            raise Exception("Corrupt out.log")

        ncore = path.split("/")[-1]
        integ = path.split("/")[-2]
        # print(integ)
        # print(path)
        patchsize = path.split("/")[-3].split("-")[1]

        last_timestep = lines[-2]
        core_data["timestep"] = int(last_timestep.split("Timestep ")[1].split(" ")[0])
        core_data["time"] = float(last_timestep.split("Time=")[1].split(" ")[0])
        core_data["walltime"] = float(last_timestep.split("Wall Time=")[1].split(" ")[0])
        core_data["EMA"] = float(last_timestep.split("EMA=")[1].split(" ")[0])
        core_data["Memory"] = float(last_timestep.split("Memory Used=")[1].split(" ")[0])
        core_data["Memory units"] = last_timestep.split("Memory Used=")[1].split(" ")[1]
        core_data["ncores"] = int(ncore)
        core_data["patchsize"]=int(patchsize)
        core_data["integrator"] = integ
        # print(wrap_dict(path_as_list,core_data))
        data.append(wrap_dict(path_as_list,core_data))

    all_data = {}
    for dic in data:
        all_data=merge_dict(all_data,dic)

    with open('out.json', 'w+') as f:
        # this would place the entire output on one line
        # use json.dump(lista_items, f, indent=4) to "pretty-print" with four spaces per indent
        json.dump(all_data, f, indent=4)
    # print(all_data)