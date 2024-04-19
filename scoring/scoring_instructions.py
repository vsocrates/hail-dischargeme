import os
import json
import numpy as np
import pandas as pd

import evaluate

from bleu import Bleu
from rouge import Rouge
from bertscore import BertScore  #


def calculate_scores_instructions(generated, reference, metrics):
    if not metrics:
        raise ValueError("No metrics specified for scoring.")
    print("Beginning scoring...")

    scores = {}
    for metric in metrics:
        scores[metric] = {"discharge_instructions": []}

    # initialize scorers
    if "bleu" in metrics:
        bleuScorer = Bleu()
        print("bleuScorer initialized")
    if "rouge" in metrics:
        scores["rouge"]["discharge_instructions"] = [[], [], []]
        rougeScorer = Rouge(["rouge1", "rouge2", "rougeL"])
        print("rougeScorer initialized")
    if "bertscore" in metrics:
        bertScorer = BertScore()
        print("bertScorer initialized")
    if "meteor" in metrics:
        meteorScorer = evaluate.load("meteor")
        print("meteorScorer initialized")

    def calculate_scores(rows_ref, rows_gen):
        if "bleu" in metrics:
            temp = bleuScorer(
                refs=rows_ref["discharge_instructions"].tolist(),
                hyps=rows_gen["discharge_instructions"].tolist(),
            )
            scores["bleu"]["discharge_instructions"].extend(temp)
        if "rouge" in metrics:
            temp = rougeScorer(
                refs=rows_ref["discharge_instructions"].tolist(),
                hyps=rows_gen["discharge_instructions"].tolist(),
            )
            scores["rouge"]["discharge_instructions"][0].extend(
                    temp['rouge1'],
            )
            scores["rouge"]["discharge_instructions"][1].extend(
                    temp['rouge2'],
            )
            scores["rouge"]["discharge_instructions"][2].extend(
                    temp['rougeL'],
            )
        if "bertscore" in metrics:
            temp = bertScorer(
                refs=rows_ref["discharge_instructions"].tolist(),
                hyps=rows_gen["discharge_instructions"].tolist(),
            )
            scores["bertscore"]["discharge_instructions"].extend(temp)
        if "meteor" in metrics:
            temp = meteorScorer.compute(
                references=rows_ref["discharge_instructions"].tolist(),
                predictions=rows_gen["discharge_instructions"].tolist(),
            )
            scores["meteor"]["discharge_instructions"].append(temp["meteor"])

        # print progress
        current_row = i + 128
        if current_row % 128 == 0:
            print(f"Processed {current_row}/{len(generated)} samples.", flush=True)

    reference.set_index("hadm_id", drop=False, inplace=True)
    generated.set_index("hadm_id", drop=False, inplace=True)

    batch_size = 128
    for i in range(0, len(generated), batch_size):
        rows_ref = reference[i : i + batch_size]
        rows_gen = generated[i : i + batch_size]
        calculate_scores(rows_ref=rows_ref, rows_gen=rows_gen)

    print(f"Processed {len(generated)}/{len(generated)} samples.", flush=True)
    print("Done.")
    return scores


def compute_overall_score_instructions(scores):
    print("Computing overall score...")
    leaderboard = {}

    metrics = list(scores.keys())

    if "bleu" in metrics:
        bleu_discharge_instructions = np.mean(scores["bleu"]["discharge_instructions"])
        leaderboard["bleu"] = np.mean(
            [bleu_discharge_instructions]
        )
    if "rouge" in metrics:
        rouge_1_discharge_instructions = np.mean(
            scores["rouge"]["discharge_instructions"][0]
        )
        rouge_2_discharge_instructions = np.mean(
            scores["rouge"]["discharge_instructions"][1]
        )
        rouge_l_discharge_instructions = np.mean(
            scores["rouge"]["discharge_instructions"][2]
        )

        leaderboard["rouge1"] = np.mean(
            [rouge_1_discharge_instructions]
        )
        leaderboard["rouge2"] = np.mean(
            [rouge_2_discharge_instructions]
        )
        leaderboard["rougel"] = np.mean(
            [rouge_l_discharge_instructions]
        )
    if "bertscore" in metrics:
        bertscore_discharge_instructions = np.mean(
            scores["bertscore"]["discharge_instructions"]
        )
        leaderboard["bertscore"] = np.mean(
            [bertscore_discharge_instructions]
        )
    if "meteor" in metrics:
        meteor_discharge_instructions = np.mean(
            scores["meteor"]["discharge_instructions"]
        )
        leaderboard["meteor"] = np.mean(
            [meteor_discharge_instructions]
        )

    # normalize sacrebleu to be between 0 and 1
    for key in leaderboard.keys():
        if key == "sacrebleu":
            leaderboard[key] = leaderboard[key] / 100

    overall_score = np.mean(list(leaderboard.values()))
    leaderboard["overall"] = overall_score

    print("Done.")
    return leaderboard
