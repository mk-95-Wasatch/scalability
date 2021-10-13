#!/bin/bash
#SBATCH --time=48:00:00 # walltime, abbreviated by -t
#SBATCH --job-name=100OADC-v2
#SBATCH -e slurm-%j.err-%n
#SBATCH -o slurm-%j.out-%n
#SBATCH --ntasks=1024 # number of MPI tasks, abbreviated by -n # additional information for allocated clusters
#SBATCH --account=smithp-guest
#SBATCH --partition=ash-guest
##SBATCH-C "c12"
#SBATCH --mail-user=karammokbel@gmail.com

#export WORKDIR=/scratch/general/lustre/u1148465/ash-cases/Arrangement-0/100ADC-A0-version-2
export SUS=/uufs/chpc.utah.edu/common/home/u0945696/development/builds/uintah-ash/opt/StandAlone/sus
#export INPUT_FILE="$WORKDIR/FullStage_Original.ups"
module load python/3.5.2
module load gcc/6.4
module load openmpi/4.0.4
 # run the program
 # see above for other MPI distributions