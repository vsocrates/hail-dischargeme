#!/usr/bin/env python
# coding: utf-8

import argparse

parser = argparse.ArgumentParser(description='Generate BHC Summaries with Trained BART.')
parser.add_argument('--split',
                    help='split')
parser.add_argument('--version',
                    help='Version of output to output')

args = parser.parse_args()

split = args.split
version = args.version

import datasets
from transformers import pipeline
from transformers.pipelines.pt_utils import KeyDataset
from tqdm.auto import tqdm
from pathlib import Path


pipe = pipeline("text2text-generation", model="/home/vs428/Documents/DischargeMe/hail-dischargeme/notebooks/brief_hospital_course/template_code/bart-dischargeme-results_v2/checkpoint-16500", device=0)


from pynvml import *


def print_gpu_utilization():
    nvmlInit()
    handle = nvmlDeviceGetHandleByIndex(0)
    info = nvmlDeviceGetMemoryInfo(handle)
    print(f"GPU memory occupied: {info.used//1024**2} MB.", flush=True)


def print_summary(result):
    print(f"Time: {result.metrics['train_runtime']:.2f}", flush=True)
    print(f"Samples/second: {result.metrics['train_samples_per_second']:.2f}", flush=True)
    print_gpu_utilization()


import pandas as pd
from datasets import Dataset


print_gpu_utilization()

# train_data = pd.read_pickle("/gpfs/gibbs/project/rtaylor/shared/DischargeMe/public/train/discharge_target_with_preceding_text+structured_data.pickle")
# train_ds = Dataset.from_pandas(train_data[['hadm_id', "bhc_preceding_text", "brief_hospital_course"]], split="train")

if split == "valid":
    fname = "/gpfs/gibbs/project/rtaylor/shared/DischargeMe/public/valid/discharge_target_with_preceding_text+structured_data.pickle"
elif split == "test_phase_1":
    fname = "/gpfs/gibbs/project/rtaylor/shared/DischargeMe/public/test_phase_1/discharge_target_with_preceding_text+structured_data.pickle"
else:
    raise Exception("Split doesn't exist!")


data = pd.read_pickle(fname)
ds = Dataset.from_pandas(data[['hadm_id', "bhc_preceding_text", "brief_hospital_course"]], split="test")

print(data['brief_hospital_course_word_count'].describe())


BATCH_SIZE = 16

# KeyDataset (only *pt*) will simply return the item in the dict returned by the dataset item
# as we're not interested in the *target* part of the dataset. For sentence pair use KeyPairDataset
outs = []
print(ds)
ds = ds
for out in tqdm(pipe(KeyDataset(ds, "bhc_preceding_text"), 
                     batch_size=BATCH_SIZE,
                     clean_up_tokenization_spaces=True,
                     truncation=True,
                     return_text=True,
                     max_length=1024,
                     no_repeat_ngram_size=5, 
                     num_beams=3, 
                     early_stopping=True
                    ), total=len(ds)):
    outs.append(out)


print_gpu_utilization()

def flatten(xss):
    return [x for xs in xss for x in xs]

outs = flatten(outs)

pd.DataFrame.from_records(outs).to_csv(f"/gpfs/gibbs/project/rtaylor/shared/DischargeMe/BART_gen_{split}_{version}.csv")
data_out = pd.concat([data, pd.DataFrame.from_records(outs).rename({"generated_text": "brief_hospital_course_BART"}, axis=1)], axis=1)

print("Writing file to:")
print(f"/home/vs428/Documents/DischargeMe/hail-dischargeme/notebooks/brief_hospital_course/outputs/bhc_scores/{Path(fname).stem}_BART_gen_{split}_{version}.pickle")
data_out.to_pickle(f"/home/vs428/Documents/DischargeMe/hail-dischargeme/notebooks/brief_hospital_course/outputs/bhc_scores/{Path(fname).stem}_BART_gen_{split}_{version}.pickle")

