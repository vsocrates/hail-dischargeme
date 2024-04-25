#!/bin/bash
#SBATCH --partition=gpu,day,week
#SBATCH --requeue
#SBATCH --job-name=bhc_gpt_simple
#SBATCH --out="%x-%j.out"
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=70G
#SBATCH --gpus=1
#SBATCH --constraint="a5000|a100|rtx3090"
#SBATCH --nodes=1
#SBATCH --time=00-18:00:00
#SBATCH --mail-type=ALL

# do something
echo "I'm echoing to stdout"
echo "I'm echoing to stderr" 1>&2
echo "My JobID is ${SLURM_JOBID}"
echo "I have ${SLURM_CPUS_ON_NODE} CPUs on node $(hostname -s)"

module load miniconda
source activate peft_finetune_env
cd /home/vs428/Documents/DischargeMe/hail-dischargeme/notebooks/brief_hospital_course/template_code

date=$(date '+%Y-%m-%d-%H%M%S')

papermill fine_tune_bart_dischargeme.ipynb fine_tune_bart_dischargeme_output.ipynb --log-output -p version v2


# sbatch -C "a5000|a100|rtx3090" --gpus=1 --partition gpu bhc_preceding_text_bart_v1.slurm


