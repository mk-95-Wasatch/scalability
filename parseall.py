import argparse
import json
from glob import glob

def wrap_dict(path, content):
    return {path[0]: wrap_dict(path[1:], content)} if path else content

def get_sub_folders(path):
    all_sub_directories_list = glob(str(path) + '/*/')
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

# user have to set these values
patches_size_list = ['8','16','32']
integ_list = ["RK311","RK300","RK310","RK301"]
subdir =[]
for patch_size in patches_size_list:
    for integ in integ_list:
        for num,subpath in enumerate(get_sub_folders("weak/patch-{}-3/{}".format(patch_size,integ))):
            if num!=0:
                subdir.append(subpath)
print(subdir)
if args.log:
    data = []
    for path in subdir:
        path_as_list = path.split('/')
        file_path =path+"out.log"
        lines = LastNlines(file_path, 2)
        core_data = {}
        if lines[-1] == "Sus: going down successfully\n":
            print("Successful")
            core_data["successful"] = True
        else:
            raise Exception("Corrupt out.log")

        ncore = path.split("/")[-2]
        integ = path.split("/")[-3]
        patchsize = path.split("/")[-4].split("-")[1]

        last_timestep = lines[-2]
        core_data["timestep"] = int(last_timestep.split("Timestep ")[1].split(" ")[0])
        core_data["time"] = float(last_timestep.split("Time=")[1].split(" ")[0])
        core_data["walltime"] = float(last_timestep.split("Wall Time=")[1].split(" ")[0])
        core_data["EMA"] = float(last_timestep.split("EMA=")[1].split(" ")[0])
        try:
            core_data["Memory"] = float(last_timestep.split("Memory Use=")[1].split(" ")[0])
            core_data["Memory units"] = last_timestep.split("Memory Use=")[1].split(" ")[1]
        except:
            core_data["Memory"] = float(last_timestep.split("Memory Used=")[1].split(" ")[0])
            core_data["Memory units"] = last_timestep.split("Memory Used=")[1].split(" ")[1]

        core_data["ncores"] = int(ncore)
        core_data["patchsize"]=int(patchsize)
        core_data["integrator"] = integ
        data.append(wrap_dict(path_as_list[:-1],core_data))

    all_data = {}
    for dic in data:
        all_data=merge_dict(all_data,dic)

    with open('out.json', 'w+') as f:
        # this would place the entire output on one line
        # use json.dump(lista_items, f, indent=4) to "pretty-print" with four spaces per indent
        json.dump(all_data, f, indent=4)
    # print(all_data)