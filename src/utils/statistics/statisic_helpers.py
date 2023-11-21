import json
from typing import List

import numpy as np

with open('config/model_thresholds_and_scaling.json', 'r') as f:
    scaling_info = json.load(f)


def find_best_threshold_separate_distributions(values1: List[float], values2: List[float]):
    values1 = np.array(values1)
    values2 = np.array(values2)

    if values1.mean() < values2.mean():
        left_values = values1
        right_values = values2
    else:
        left_values = values2
        right_values = values1

    # Define a range of possible thresholds
    thresholds = np.linspace(right_values.mean(), left_values.mean(), num=100)

    best_threshold = None
    best_accuracy = 0

    # Collect empty space for non-overlapping distributions to cut inbetween later
    perfect_accuracy_thresholds = []

    # Test each threshold
    for threshold in thresholds:
        predictions = np.concatenate((right_values >= threshold, left_values < threshold))
        accuracy = predictions.sum() / len(predictions)

        if accuracy >= best_accuracy:
            if accuracy == 1:
                perfect_accuracy_thresholds.append(threshold)
            best_accuracy = accuracy
            best_threshold = threshold

    if perfect_accuracy_thresholds:
        best_threshold = np.mean(perfect_accuracy_thresholds)

    return best_threshold


def scale_model_similarity(value, model_number: int):
    min_value = scaling_info["scaling_values"][f"low_similarity_value_model{model_number}"]
    max_value = scaling_info["scaling_values"][f"high_similarity_value_model{model_number}"]
    return (value - min_value) / (max_value - min_value)


def is_question_valid(top_matching_similarity, model_number: int):
    threshold = scaling_info["valid_question_thresholds"][f"valid_predictions_threshold_model{model_number}"]
    return top_matching_similarity >= threshold
