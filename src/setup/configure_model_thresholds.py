import json

import pandas as pd

from src.utils.statistics.statisic_helpers import find_best_threshold_separate_distributions

valid_predictions = pd.read_csv("merged_predictions.csv")
unrelated_questions_predictions = pd.read_csv("merged_random_questions.csv")


def find_thresholds_and_save_config():
    # Find valid question separation threshold
    valid_predictions_threshold_model1 = find_best_threshold_separate_distributions(valid_predictions["Chance1_model1"],
                                                                                    unrelated_questions_predictions[
                                                                                        "Chance1_model1"])
    valid_predictions_threshold_model2 = find_best_threshold_separate_distributions(valid_predictions["Chance1_model2"],
                                                                                    unrelated_questions_predictions[
                                                                                        "Chance1_model2"])

    # Find scaling for models
    col_model1 = ['Chance1_model1', 'Chance2_model1', 'Chance3_model1']
    col_model2 = ['Chance1_model2', 'Chance2_model2', 'Chance3_model2']

    low_similarity_value_model1 = valid_predictions[col_model1].quantile(0.1).mean()
    low_similarity_value_model2 = valid_predictions[col_model2].quantile(0.1).mean()
    high_similarity_value_model1 = valid_predictions[col_model1].quantile(0.9).mean()
    high_similarity_value_model2 = valid_predictions[col_model2].quantile(0.9).mean()

    json_values = {'valid_question_thresholds': {
        'valid_predictions_threshold_model1': valid_predictions_threshold_model1,
        'valid_predictions_threshold_model2': valid_predictions_threshold_model2
    },
        'scaling_values': {
            'low_similarity_value_model1': low_similarity_value_model1,
            'low_similarity_value_model2': low_similarity_value_model2,
            'high_similarity_value_model1': high_similarity_value_model1,
            'high_similarity_value_model2': high_similarity_value_model2
        }
    }

    with open('config/model_thresholds_and_scaling.json', 'w') as f:
        json.dump(json_values, f, indent=4)


if __name__ == '__main__':
    find_thresholds_and_save_config()
