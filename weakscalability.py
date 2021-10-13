from upsfileobj import *
import math
from pathlib import Path
from shutil import copyfile

patch_size_list = [8,16,32,64]
integrators = ["RK311","RK301","RK310","RK300"]
patches, total_processors_num = get_patches(8)
h = 0.001
Umax = 2/math.sqrt(3)
Courrant = 0.2
Reh = 1.0

slurm_runs = []
for integ in integrators:
    slurm_runs.append('')
    for patch_size in patch_size_list:
        resolutions = workload("weak",patches,patch_size)
        uppers = upper_box(patches)
        viscosities = get_viscosity(uppers,resolutions,Reh=Reh,U=Umax)
        dt = get_dt(h=h,U=Umax,Courant=Courrant)
        dir_paths = working_dir_tree("weak",total_processors_num,prepath="patch-{}-3/{}".format(patch_size,integ))
        print(total_processors_num)
        print(patches)
        print(resolutions)

        for path,patch,resolution,upper,viscosity, core_num in zip(dir_paths,patches,resolutions,uppers,viscosities,total_processors_num):
            ups_obj = UPS("{}/taylor-green-vortex-3d.ups".format(integ))
            new_file_name = path+"/taylor-green-vortex-3d.ups"
            ups_obj.create_new_ups_file(new_file_name)

            ups_obj.set_dt(dt)
            ups_obj.set_lower_box(0,0,0)
            ups_obj.set_patches(patch[0],patch[1],patch[2])
            ups_obj.set_upper_box(upper[0],upper[1],upper[2])
            ups_obj.set_resolution(resolution[0],resolution[1],resolution[2])
            ups_obj.set_viscosity(viscosity)
            ups_obj.write_changes()

            abs_file_path = str(Path(new_file_name).absolute())
            mpi_command = 'mpirun -np {} $SUS {} > out.log'.format(core_num,abs_file_path)
            slurm_runs.append(mpi_command)
            # print(mpi_command)

print(slurm_runs)
slurm_file = "slurm_weak.script"
copyfile("slurm_base.script", slurm_file)
MyFile=open(slurm_file,'a')

for element in slurm_runs:
     MyFile.write(element)
     MyFile.write('\n')
MyFile.close()
