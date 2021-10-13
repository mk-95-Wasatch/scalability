from xml.dom import minidom
from shutil import copyfile
import os

class UPS:
    def __init__(self,filename):
        self.__root_file_name = filename

        # load the ups file
        self.__root_ups_obj = minidom.parse(self.__root_file_name)

    @property
    def new_ups_obj(self):
        return self.__new_ups_obj

    def create_new_ups_file(self,new_file_name):
        self.__new_file_name = new_file_name
        copyfile(self.__root_file_name, self.__new_file_name)
        self.__new_ups_obj = minidom.parse(self.__new_file_name)

    def write_changes(self):
        f = open(self.__new_file_name, 'w')
        self.__new_ups_obj.writexml(f)
        f.close()

    def set_viscosity(self,new_value):
        # set the value of the viscosity mu = U h/Reh; h = 1/res
        for node in self.__new_ups_obj.getElementsByTagName('BasicExpression'):
            for subnode in node.getElementsByTagName('NameTag'):
                tagName = subnode.getAttribute("name")

            if tagName == "viscosity":
                for subnode in node.getElementsByTagName("Constant"):
                    subnode.firstChild.replaceWholeText(new_value)

    def set_max_time(self,new_value):
        for node in self.__new_ups_obj.getElementsByTagName('maxTime'):
            node.firstChild.replaceWholeText(new_value)

    def set_dt(self,new_value):
        for node in self.__new_ups_obj.getElementsByTagName('delt_min'):
            node.firstChild.replaceWholeText(new_value)

        for node in self.__new_ups_obj.getElementsByTagName('delt_max'):
            node.firstChild.replaceWholeText(new_value)

    def set_uda_name(self, new_basename):
        for node in self.__new_ups_obj.getElementsByTagName('filebase'):
            node.firstChild.replaceWholeText(new_basename + '.uda')

    def set_upper_box(self,u0,u1,u2):
        for node in self.__new_ups_obj.getElementsByTagName('upper'):
            upper = '[{},{},{}]'.format(u0, u1, u2)
            node.firstChild.replaceWholeText(upper)

    def set_lower_box(self,l0,l1,l2):
        for node in self.__new_ups_obj.getElementsByTagName('lower'):
            lower = '[{},{},{}]'.format(l0, l1, l2)
            node.firstChild.replaceWholeText(lower)

    def set_resolution(self,nx,ny,nz):
        for node in self.__new_ups_obj.getElementsByTagName('resolution'):
            Resolution = '[{},{},{}]'.format(nx, ny, nz)
            node.firstChild.replaceWholeText(Resolution)

    def set_patches(self,p0,p1,p2):
        for node in self.__new_ups_obj.getElementsByTagName('patches'):
            P = '[{},{},{}]'.format(p0, p1, p2)
            node.firstChild.replaceWholeText(P)


def get_patches(highest=9):
    total_processors = [2**i for i in range(0,highest+1)]
    p0 = 1
    smallest = [p0,p0,p0/2]
    patches = []
    counter = 1
    for i in range(len(total_processors)):
        if counter==4:
            counter=1
        smallest[-counter] = int(smallest[-counter]*2)
        patches.append(smallest.copy())
        counter+=1
    return patches,total_processors

def workload(case,patches, resolution):
    if case=="weak":
        resolutions = []
        for patch in patches:
            resol = [pi*resolution for pi in patch]
            resolutions.append(resol)
        return resolutions
    elif case=="strong":
        resolutions = []
        for patch in patches:
            resol = [resolution for pi in patch]
            resolutions.append(resol)
        return resolutions

def upper_box(patches):
    upper = []
    for patch in patches:
        upper.append([pi for pi in patch])
    return upper

def get_viscosity(uppers,resolutions,Reh,U):
    viscosities = []
    for upper,resolution in zip(uppers,resolutions):
        viscosities.append(U*upper[0]/Reh/resolution[0])
    return viscosities

def get_dt(h,U,Courant):
    return Courant*h/U

def working_dir_tree(case, processors, prepath=None):
    paths =[]
    if case =="weak":
        parent = case
    elif case =="strong":
        parent = case
    for num in processors:
        if prepath!=None:
            path = "./{}/{}/{}".format(parent,prepath,num)
        else:
            path = "./{}/{}".format(parent,num)
        os.makedirs(name=path)
        paths.append(path)
    return paths
