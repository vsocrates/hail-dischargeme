#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --requeue
#SBATCH --job-name=bhc_gpt_inference
#SBATCH --out="%x-%j.out"
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=70G
#SBATCH --gpus=a100:1
#SBATCH --nodes=1
#SBATCH --time=00-17:00:00
#SBATCH --mail-type=ALL

# do something
echo "I'm echoing to stdout"
echo "I'm echoing to stderr" 1>&2
echo "My JobID is ${SLURM_JOBID}"
echo "I have ${SLURM_CPUS_ON_NODE} CPUs on node $(hostname -s)"

module load miniconda
source activate peft_finetune_env
cd /home/vs428/Documents/DischargeMe/hail-dischargeme/notebooks/brief_hospital_course

date=$(date '+%Y-%m-%d-%H%M%S')

SPLIT="valid"
echo "The split being processed: ${SPLIT}..."

python 2_BART_Generate_BHC.py --split $SPLIT --version v3

#other SBATCH --constraint="a5000|a100|rtx3090"
