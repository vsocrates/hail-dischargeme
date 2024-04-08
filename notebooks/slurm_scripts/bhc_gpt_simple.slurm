#!/bin/bash
#SBATCH --partition=gpu,day,week
#SBATCH --requeue
#SBATCH --job-name=bhc_gpt_simple
#SBATCH --out="%x-%j.out"
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=70G
#SBATCH --gpus=1
#SBATCH --nodes=1
#SBATCH --time=00-12:00:00
#SBATCH --mail-type=ALL

# do something
echo "I'm echoing to stdout"
echo "I'm echoing to stderr" 1>&2
echo "My JobID is ${SLURM_JOBID}"
echo "I have ${SLURM_CPUS_ON_NODE} CPUs on node $(hostname -s)"

module load miniconda
source activate openai
cd /home/vs428/Documents/DischargeMe/hail-dischargeme/notebooks/brief_hospital_course

date=$(date '+%Y-%m-%d-%H%M%S')

papermill GPT4_Simple_runv1.ipynb GPT4_Simple_runv1.ipynb --log-output -p N 1000