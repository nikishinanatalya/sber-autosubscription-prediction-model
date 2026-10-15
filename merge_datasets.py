import pandas as pd

def merge_datasets(ga_csv, ga_hits_csv):
    ga = pd.read_csv(ga_csv, low_memory=False)
    ga_hits = pd.read_csv(ga_hits_csv)

    target_action = ['sub_car_claim_click', 'sub_car_claim_submit_click', 'sub_open_dialog_click',
                     'sub_custom_question_submit_click', 'sub_call_number_click', 'sub_callback_submit_click',
                     'sub_submit_success', 'sub_car_request_submit_click']

    ga_hits.event_value = ga_hits.event_action.apply(lambda x: 1 if x in target_action else 0)

    ga_hits_agr = ga_hits.groupby(['session_id'])[['event_value']].max()

    ga['event_session_target'] = ga.session_id.apply(lambda x: ga_hits_agr.loc[x, 'event_value']
    if x in ga_hits_agr.index else -1)

    ga_tg = ga[ga.event_session_target != -1]

    ga_tg = ga_tg.drop_duplicates()

    ga_tg_event_dict =  ga_tg[['session_id', 'event_session_target']]

    return ga_tg, ga_tg_event_dict