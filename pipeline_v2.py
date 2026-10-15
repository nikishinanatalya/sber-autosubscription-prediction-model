import pandas as pd
import dill
import datetime

from sklearn.pipeline import Pipeline
from sklearn.compose import make_column_selector
from sklearn.preprocessing import FunctionTransformer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

from merge_datasets import merge_datasets
from update_dataset_v2 import fill_nan_devices
from update_dataset_v2 import fill_nan_utm
from transform_dataset_v2 import create_features

def main():
    print('Car Rent Prediction Pipeline')

    ga = 'data/ga_sessions.csv'
    ga_hits = 'data/ga_hits-001.csv'

    ga_tg, ga_tg_event_dict = merge_datasets(ga, ga_hits)

    update_dictionary = {'created_device_dictionaries': 0,
                         'created_utm_dictionaries': 0}

    transform_dictionary = {'merged_datasets': 0,
                            'created_grouped_utm_dictionaries': 0,
                            'created_grouped_device_dictionaries': 0}

    X = ga_tg.drop(['event_session_target'], axis=1)
    Y = ga_tg['event_session_target']

    dataframe_transformer = Pipeline(steps=[
        ('fill_nan_devices', FunctionTransformer(fill_nan_devices, kw_args={'update_dictionary': update_dictionary})),
        ('fill_nan_utm', FunctionTransformer(fill_nan_utm, kw_args={'update_dictionary': update_dictionary})),
        ('create_features', FunctionTransformer(create_features, kw_args={'transform_dictionary': transform_dictionary, 'ga_tg_dict': ga_tg_event_dict}))
    ])

    categorical_transformer = Pipeline(steps=[
        ('encoder', OneHotEncoder(handle_unknown='ignore'))
    ])

    features_transformer = ColumnTransformer(transformers=[
        ('categorical', categorical_transformer, make_column_selector(dtype_include=object)),
        ('numerical', 'passthrough', make_column_selector(dtype_include=['int64'])),
    ])

    preprocessor = Pipeline(steps=[
        ('dataframe_transformer', dataframe_transformer),
        ('features_transformer', features_transformer)
    ])

    model = LogisticRegression(C=2, max_iter=500, random_state=42, class_weight='balanced')

    pipe = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', model)
    ])

    pipe.fit(X, Y)
    score = roc_auc_score(Y, pipe.predict_proba(X)[:, 1])
    print(f'model: {type(pipe.named_steps["classifier"]).__name__}, roc_auc: {score:.4f}')

    with open('Cars_rent_pipe_v2.pkl', 'wb') as file:
        dill.dump({
            'model': pipe,
            'metadata': {
                'name': 'Car rent prediction model',
                'author': 'Natalia Nikishina',
                'version': 2,
                'date': datetime.datetime.now(),
                'type': type(pipe.named_steps["classifier"]).__name__,
                'roc_auc': score
            }
        }, file)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
