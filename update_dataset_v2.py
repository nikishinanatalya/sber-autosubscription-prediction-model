import pandas as pd

def fill_nan_devices(ga_tg, update_dictionary):

    ga_tg = ga_tg.copy()

    # Обновление device_os на уровне информации о клиенте

    ga_tg['device_key'] = (ga_tg.client_id.fillna('_none_') + '_' +
                           ga_tg.device_category.fillna('_none_') + '_' +
                           ga_tg.device_brand.fillna('_none_') + '_' +
                           ga_tg.device_browser.fillna('_none_') + '_' +
                           ga_tg.device_screen_resolution.fillna('_none_'))

    if update_dictionary['created_device_dictionaries'] == 0:

        ga_tg_agg = ga_tg.groupby([
            'client_id', 'device_category', 'device_brand', 'device_os', 'device_browser', 'device_screen_resolution'],
            as_index=False).agg(count_session=('session_id', 'count'))
        ga_tg_agg_max_for_os = ga_tg_agg.groupby(
            ['client_id', 'device_category', 'device_brand', 'device_browser', 'device_screen_resolution'])['count_session'].idxmax()
        ga_tg_agg_dict_for_os = ga_tg_agg.loc[ga_tg_agg_max_for_os]
        ga_tg_agg_dict_for_os['device_key'] = (ga_tg_agg_dict_for_os.client_id + '_' +
                                               ga_tg_agg_dict_for_os.device_category + '_' +
                                               ga_tg_agg_dict_for_os.device_brand + '_' +
                                               ga_tg_agg_dict_for_os.device_browser + '_' +
                                               ga_tg_agg_dict_for_os.device_screen_resolution)

        ga_tg_agg_dict_for_os_series = pd.Series(ga_tg_agg_dict_for_os['device_os'].values, index=ga_tg_agg_dict_for_os['device_key'])

        update_dictionary['ga_tg_agg_dict_for_os_series'] = ga_tg_agg_dict_for_os_series


    ga_tg['device_os'] = ga_tg['device_os'].fillna(ga_tg['device_key'].map(update_dictionary['ga_tg_agg_dict_for_os_series']))

    ga_tg.drop(['device_key'], axis=1, inplace=True)


    #Заполнение колонок device_os и device_brand для устройств Apple

    ga_tg.loc[
        (ga_tg.device_category == 'desktop') &
        (ga_tg.device_brand == 'Apple') &
        (ga_tg.device_os.isna()), 'device_os'] = 'Macintosh'

    ga_tg.loc[
        (ga_tg.device_category == 'desktop') &
        (ga_tg.device_brand.isna()) &
        (ga_tg.device_os == 'Macintosh'), 'device_brand'] = 'Apple'

    ga_tg.loc[
        (ga_tg.device_category == 'desktop') &
        (ga_tg.device_os.isna()) &
        (ga_tg.device_brand.isna()) &
        (ga_tg.device_browser == 'Safari'), ['device_brand', 'device_os']] = ['Apple', 'Macintosh']

    ga_tg.loc[
        (ga_tg.device_category.isin(['mobile', 'tablet'])) &
        (ga_tg.device_os == 'iOS') &
        (ga_tg.device_brand.isna()), 'device_brand'] = 'Apple'

    ga_tg.loc[
        (ga_tg.device_category.isin(['mobile', 'tablet'])) &
        (ga_tg.device_os.isna()) &
        (ga_tg.device_brand == 'Apple'), 'device_os'] = 'iOS'

    ga_tg.loc[
        (ga_tg.device_category.isin(['mobile', 'tablet'])) &
        (ga_tg.device_os.isna()) &
        (ga_tg.device_brand.isna()) &
        (ga_tg.device_browser.isin(['Safari', 'Safari (in-app)'])), ['device_brand', 'device_os']] = ['Apple', 'iOS']


    # Заполнение колонки device_os по бренду

    ga_tg['device_key'] = (ga_tg.device_category.fillna('_none_') + '_' +
                           ga_tg.device_brand.fillna('_none_'))

    if update_dictionary['created_device_dictionaries'] == 0:

        ga_tg_agg_os_by_brand = ga_tg[~ga_tg.device_brand.isin(['Apple', '(not set)'])].groupby(
            ['device_category', 'device_brand', 'device_os'], as_index=False).agg(count_sessions = ('session_id', 'count'))

        ga_tg_agg_os_by_brand_max = ga_tg_agg_os_by_brand.groupby([
            'device_category', 'device_brand'])['count_sessions'].idxmax()
        ga_tg_agg_os_by_brand_dict = ga_tg_agg_os_by_brand.loc[ga_tg_agg_os_by_brand_max]
        ga_tg_agg_os_by_brand_dict['device_key'] = (ga_tg_agg_os_by_brand_dict.device_category + '_' +
                                                    ga_tg_agg_os_by_brand_dict.device_brand)

        ga_tg_agg_os_by_brand_dict_series = pd.Series(ga_tg_agg_os_by_brand_dict['device_os'].values, index=ga_tg_agg_os_by_brand_dict['device_key'])

        update_dictionary['ga_tg_agg_os_by_brand_dict_series'] = ga_tg_agg_os_by_brand_dict_series

    ga_tg['device_os'] = ga_tg['device_os'].fillna(ga_tg['device_key'].map(update_dictionary['ga_tg_agg_os_by_brand_dict_series']))

    ga_tg.drop(['device_key'], axis=1, inplace=True)

    # Одновременное заполнение колонок device_os и device_brand по клиенту

    ga_tg['device_key'] = (ga_tg.client_id.fillna('_none_') + '_' +
                           ga_tg.device_category.fillna('_none_') + '_' +
                           ga_tg.device_screen_resolution.fillna('_none_'))

    if update_dictionary['created_device_dictionaries'] == 0:

        ga_tg_na_brand_os = ga_tg[(ga_tg.device_brand.isna()) & (ga_tg.device_os.isna())
                                  ].groupby(
            ['device_category', 'client_id', 'device_brand', 'device_os', 'device_screen_resolution'],
            dropna=False, as_index=False).agg(count_session=('session_id', 'count'))

        ga_tg_na_brand_os_client = ga_tg[
            (ga_tg.device_category + ' ' + ga_tg.client_id + ' ' + ga_tg.device_screen_resolution).isin(
                ga_tg_na_brand_os.device_category + ' ' +
                ga_tg_na_brand_os.client_id + ' ' +
                ga_tg_na_brand_os.device_screen_resolution)
        ].groupby(['device_category', 'client_id', 'device_brand', 'device_os', 'device_screen_resolution'],
                  as_index=False).agg(count_session=('session_id', 'count'))

        ga_tg_na_brand_os_client_max = ga_tg_na_brand_os_client.groupby([
            'device_category', 'client_id', 'device_screen_resolution'])['count_session'].idxmax()
        ga_tg_na_brand_os_client_dict = ga_tg_na_brand_os_client.loc[ga_tg_na_brand_os_client_max]

        ga_tg_na_brand_os_client_dict['device_key'] = (ga_tg_na_brand_os_client_dict.client_id + '_' +
                                                       ga_tg_na_brand_os_client_dict.device_category + '_' +
                                                       ga_tg_na_brand_os_client_dict.device_screen_resolution)

        ga_tg_na_brand_os_client_dict_series_brand = pd.Series(ga_tg_na_brand_os_client_dict['device_brand'].values,
                                                               index=ga_tg_na_brand_os_client_dict['device_key'])

        ga_tg_na_brand_os_client_dict_series_os = pd.Series(ga_tg_na_brand_os_client_dict['device_os'].values,
                                                            index=ga_tg_na_brand_os_client_dict['device_key'])

        update_dictionary['ga_tg_na_brand_os_client_dict_series_brand'] = ga_tg_na_brand_os_client_dict_series_brand
        update_dictionary['ga_tg_na_brand_os_client_dict_series_os'] = ga_tg_na_brand_os_client_dict_series_os

    ga_tg[['device_brand_nan', 'device_os_nan']] = ga_tg[['device_brand', 'device_os']]

    ga_tg.loc[(ga_tg.device_brand_nan.isna()) & (ga_tg.device_os_nan.isna()), 'device_os'] = ga_tg.loc[
        (ga_tg.device_brand_nan.isna()) & (ga_tg.device_os_nan.isna()), 'device_key'].map(update_dictionary['ga_tg_na_brand_os_client_dict_series_os'])

    ga_tg.loc[(ga_tg.device_brand_nan.isna()) & (ga_tg.device_os_nan.isna()), 'device_brand'] = ga_tg.loc[
        (ga_tg.device_brand_nan.isna()) & (ga_tg.device_os_nan.isna()), 'device_key'].map(update_dictionary['ga_tg_na_brand_os_client_dict_series_brand'])

    ga_tg.drop(['device_key', 'device_brand_nan', 'device_os_nan'], axis=1, inplace=True)


     # Заполнение колонки device_os

    ga_tg['device_key'] = (ga_tg.client_id.fillna('_none_') + '_' +
                           ga_tg.device_category.fillna('_none_') + '_' +
                           ga_tg.device_screen_resolution.fillna('_none_'))

    if update_dictionary['created_device_dictionaries'] == 0:

        ga_tg_na_brand_os_os = ga_tg[(ga_tg.device_brand.isna()) & (ga_tg.device_os.isna())
                                     ].groupby(
            ['device_category', 'client_id', 'device_brand', 'device_os', 'device_screen_resolution'],
            dropna=False, as_index=False).agg(count_session=('session_id', 'count'))

        ga_tg_na_brand_os_os_client = ga_tg[
            (~ga_tg.device_os.isna()) &
            (ga_tg.device_brand.isna()) &
            ((ga_tg.device_category + ' ' + ga_tg.client_id).isin(
                ga_tg_na_brand_os_os.device_category + ' ' + ga_tg_na_brand_os_os.client_id))
            ].groupby(['device_category', 'client_id', 'device_os', 'device_screen_resolution'],
                      as_index=False).agg(count_session_3=('session_id', 'count'))

        ga_tg_na_brand_os_os_client_max = ga_tg_na_brand_os_os_client.groupby([
            'device_category', 'client_id', 'device_screen_resolution'])['count_session_3'].idxmax()
        ga_tg_na_brand_os_os_client_dict = ga_tg_na_brand_os_os_client.loc[ga_tg_na_brand_os_os_client_max]
        ga_tg_na_brand_os_os_client_dict['device_key'] = (ga_tg_na_brand_os_os_client_dict.client_id + '_' +
                                                          ga_tg_na_brand_os_os_client_dict.device_category + '_' +
                                                          ga_tg_na_brand_os_os_client_dict.device_screen_resolution)
        ga_tg_na_brand_os_os_client_dict_series = pd.Series(ga_tg_na_brand_os_os_client_dict['device_os'].values,
                                                             index=ga_tg_na_brand_os_os_client_dict['device_key'])

        update_dictionary['ga_tg_na_brand_os_os_client_dict_series'] = ga_tg_na_brand_os_os_client_dict_series

    ga_tg['device_os'] = ga_tg['device_os'].fillna(ga_tg['device_key'].map(update_dictionary['ga_tg_na_brand_os_os_client_dict_series']))

    ga_tg.drop(['device_key'], axis=1, inplace=True)

    update_dictionary['created_device_dictionaries'] = 1

    return ga_tg


def fill_nan_utm(ga_tg, update_dictionary):

    ga_tg = ga_tg.copy()

    # Создание колонки visit_hour в качестве характкристики для заполнения пустых UTM значений и для дальнейшего анализа

    ga_tg['visit_hour'] = ga_tg.visit_time.apply(lambda x: x.split(':')[0])

    # Заполнение пустых UTM значений значением _none_ для упрощения обновления данных

    ga_tg[['utm_source', 'utm_campaign', 'utm_adcontent', 'utm_keyword']] = ga_tg[
        ['utm_source', 'utm_campaign', 'utm_adcontent', 'utm_keyword']].fillna('_none_')

    # Заполнение колонок utm_campaign и utm_adcontent по клиенту:

    # Формирование словаря на основе данных колонок client_id, visit_date, visit_hour

    ga_tg['utm_key'] = (ga_tg.client_id + '_' +
                        ga_tg.visit_date + '_' +
                        ga_tg.visit_hour + '_' +
                        ga_tg.utm_medium + '_' +
                        ga_tg.utm_source + '_' +
                        ga_tg.utm_keyword)

    if update_dictionary['created_utm_dictionaries'] == 0:

        ga_tg_utm_cl_1 = ga_tg[(ga_tg.utm_campaign == '_none_') & (ga_tg.utm_adcontent == '_none_')].groupby(
            ['client_id', 'utm_medium', 'utm_source', 'utm_keyword'], dropna=False).agg(
            count_sessions=('session_id', 'count'))

        ga_tg_ind_1 = ga_tg[(ga_tg.utm_campaign != '_none_') | (ga_tg.utm_adcontent != '_none_')
                            ].set_index(['client_id', 'utm_medium', 'utm_source', 'utm_keyword'])
        ga_tg_utm_1 = ga_tg_ind_1[ga_tg_ind_1.index.isin(ga_tg_utm_cl_1.index)]
        ga_tg_utm_1 = ga_tg_utm_1.reset_index().groupby([
            'client_id', 'visit_date', 'visit_hour', 'utm_medium', 'utm_source', 'utm_campaign', 'utm_adcontent',
            'utm_keyword'],
            as_index=False).agg(count_sesions=('session_id', 'count'))

        ga_tg_utm_1_count = ga_tg_utm_1.groupby(
            ['client_id', 'visit_date', 'visit_hour', 'utm_medium', 'utm_source', 'utm_keyword']).agg(
            count_utm=('utm_medium', 'count'))

        ga_tg_utm_1_count_one_by_one = ga_tg_utm_1_count[ga_tg_utm_1_count.count_utm == 1]

        ga_tg_utm_1 = ga_tg_utm_1.set_index(
            ['client_id', 'visit_date', 'visit_hour', 'utm_medium', 'utm_source', 'utm_keyword'])
        ga_tg_utm_1_dict = ga_tg_utm_1[ga_tg_utm_1.index.isin(ga_tg_utm_1_count_one_by_one.index)]
        ga_tg_utm_1 = ga_tg_utm_1.reset_index()
        ga_tg_utm_1_dict = ga_tg_utm_1_dict.reset_index()

        ga_tg_utm_1_dict['utm_key'] = (ga_tg_utm_1_dict.client_id + '_' +
                                       ga_tg_utm_1_dict.visit_date + '_' +
                                       ga_tg_utm_1_dict.visit_hour + '_' +
                                       ga_tg_utm_1_dict.utm_medium + '_' +
                                       ga_tg_utm_1_dict.utm_source + '_' +
                                       ga_tg_utm_1_dict.utm_keyword)

        ga_tg_utm_1_dict_series_campaign = pd.Series(ga_tg_utm_1_dict['utm_campaign'].values, index=ga_tg_utm_1_dict['utm_key'])
        ga_tg_utm_1_dict_series_adcontent= pd.Series(ga_tg_utm_1_dict['utm_adcontent'].values,
                                                     index=ga_tg_utm_1_dict['utm_key'])

        update_dictionary['ga_tg_utm_1_dict_series_campaign'] = ga_tg_utm_1_dict_series_campaign
        update_dictionary['ga_tg_utm_1_dict_series_adcontent'] = ga_tg_utm_1_dict_series_adcontent

    ga_tg[['utm_campaign_nan', 'utm_adcontent_nan']] = ga_tg[['utm_campaign', 'utm_adcontent']]

    ga_tg.loc[(ga_tg.utm_campaign_nan == '_none_') & (ga_tg.utm_adcontent_nan == '_none_'), 'utm_campaign'] = ga_tg.loc[
        (ga_tg.utm_campaign_nan == '_none_') & (ga_tg.utm_adcontent_nan == '_none_'), 'utm_key'].map(
        update_dictionary['ga_tg_utm_1_dict_series_campaign'])

    ga_tg.loc[(ga_tg.utm_campaign_nan == '_none_') & (ga_tg.utm_adcontent_nan == '_none_'), 'utm_adcontent'] = ga_tg.loc[
        (ga_tg.utm_campaign_nan == '_none_') & (ga_tg.utm_adcontent_nan == '_none_'), 'utm_key'].map(
        update_dictionary['ga_tg_utm_1_dict_series_adcontent'])

    ga_tg[['utm_campaign', 'utm_adcontent']] = ga_tg[['utm_campaign', 'utm_adcontent']].fillna('_none_')

    ga_tg.drop(['utm_key', 'utm_campaign_nan', 'utm_adcontent_nan'], axis=1, inplace=True)


    # Формирование словаря на основе данных колонок client_id, visit_date

    ga_tg['utm_key'] = (ga_tg.client_id + '_' +
                        ga_tg.visit_date + '_' +
                        ga_tg.utm_medium + '_' +
                        ga_tg.utm_source + '_' +
                        ga_tg.utm_keyword)

    if update_dictionary['created_utm_dictionaries'] == 0:

        ga_tg_utm_cl_2 = ga_tg[(ga_tg.utm_campaign == '_none_') & (ga_tg.utm_adcontent == '_none_')].groupby(
            ['client_id', 'utm_medium', 'utm_source', 'utm_keyword']).agg(count_sessions=('session_id', 'count'))

        ga_tg_ind_2 = ga_tg[(ga_tg.utm_campaign != '_none_') | (ga_tg.utm_adcontent != '_none_')
                            ].set_index(['client_id', 'utm_medium', 'utm_source', 'utm_keyword'])
        ga_tg_utm_2 = ga_tg_ind_2[ga_tg_ind_2.index.isin(ga_tg_utm_cl_2.index)]
        ga_tg_utm_2 = ga_tg_utm_2.reset_index().groupby([
            'client_id', 'visit_date', 'utm_medium', 'utm_source', 'utm_campaign', 'utm_adcontent', 'utm_keyword'],
            as_index=False).agg(count_sesions=('session_id', 'count'))

        ga_tg_utm_2_count = ga_tg_utm_2.groupby(
            ['client_id', 'visit_date', 'utm_medium', 'utm_source', 'utm_keyword']).agg(count_utm=('utm_medium', 'count'))

        ga_tg_utm_2_count_one_by_one = ga_tg_utm_2_count[ga_tg_utm_2_count.count_utm == 1]

        ga_tg_utm_2 = ga_tg_utm_2.set_index(['client_id', 'visit_date', 'utm_medium', 'utm_source', 'utm_keyword'])
        ga_tg_utm_2_dict = ga_tg_utm_2[ga_tg_utm_2.index.isin(ga_tg_utm_2_count_one_by_one.index)]
        ga_tg_utm_2_dict = ga_tg_utm_2_dict.reset_index()

        ga_tg_utm_2_dict['utm_key'] = (ga_tg_utm_2_dict.client_id + '_' +
                                       ga_tg_utm_2_dict.visit_date + '_' +
                                       ga_tg_utm_2_dict.utm_medium + '_' +
                                       ga_tg_utm_2_dict.utm_source + '_' +
                                       ga_tg_utm_2_dict.utm_keyword)

        ga_tg_utm_2_dict_series_campaign = pd.Series(ga_tg_utm_2_dict['utm_campaign'].values, index=ga_tg_utm_2_dict['utm_key'])
        ga_tg_utm_2_dict_series_adcontent= pd.Series(ga_tg_utm_2_dict['utm_adcontent'].values, index=ga_tg_utm_2_dict['utm_key'])

        update_dictionary['ga_tg_utm_2_dict_series_campaign'] = ga_tg_utm_2_dict_series_campaign
        update_dictionary['ga_tg_utm_2_dict_series_adcontent'] = ga_tg_utm_2_dict_series_adcontent

    ga_tg[['utm_campaign_nan', 'utm_adcontent_nan']] = ga_tg[['utm_campaign', 'utm_adcontent']]

    ga_tg.loc[(ga_tg.utm_campaign_nan == '_none_') & (ga_tg.utm_adcontent_nan == '_none_'), 'utm_campaign'] = ga_tg.loc[
        (ga_tg.utm_campaign_nan == '_none_') & (ga_tg.utm_adcontent_nan == '_none_'), 'utm_key'].map(
        update_dictionary['ga_tg_utm_2_dict_series_campaign'])

    ga_tg.loc[(ga_tg.utm_campaign_nan == '_none_') & (ga_tg.utm_adcontent_nan == '_none_'), 'utm_adcontent'] = ga_tg.loc[
        (ga_tg.utm_campaign_nan == '_none_') & (ga_tg.utm_adcontent_nan == '_none_'), 'utm_key'].map(
        update_dictionary['ga_tg_utm_2_dict_series_adcontent'])

    ga_tg[['utm_campaign', 'utm_adcontent']] = ga_tg[['utm_campaign', 'utm_adcontent']].fillna('_none_')

    ga_tg.drop(['utm_key', 'utm_campaign_nan', 'utm_adcontent_nan'], axis=1, inplace=True)


    # Формирование словаря на основе данных колонок client_id

    ga_tg['utm_key'] = (ga_tg.client_id + '_' +
                        ga_tg.utm_medium + '_' +
                        ga_tg.utm_source + '_' +
                        ga_tg.utm_keyword)

    if update_dictionary['created_utm_dictionaries'] == 0:

        ga_tg_utm_cl_3 = ga_tg[(ga_tg.utm_campaign == '_none_') & (ga_tg.utm_adcontent == '_none_')].groupby(
            ['client_id', 'utm_medium', 'utm_source', 'utm_keyword']).agg(count_sessions=('session_id', 'count'))

        ga_tg_ind_3 = ga_tg[(ga_tg.utm_campaign != '_none_') | (ga_tg.utm_adcontent != '_none_')
                            ].set_index(['client_id', 'utm_medium', 'utm_source', 'utm_keyword'])
        ga_tg_utm_3 = ga_tg_ind_3[ga_tg_ind_3.index.isin(ga_tg_utm_cl_3.index)]
        ga_tg_utm_3 = ga_tg_utm_3.reset_index().groupby([
            'client_id', 'utm_medium', 'utm_source', 'utm_campaign', 'utm_adcontent', 'utm_keyword'],
            as_index=False).agg(count_sesions=('session_id', 'count'))

        ga_tg_utm_3_count = ga_tg_utm_3.groupby(
            ['client_id', 'utm_medium', 'utm_source', 'utm_keyword']).agg(count_utm=('utm_medium', 'count'))

        ga_tg_utm_3_count_one_by_one = ga_tg_utm_3_count[ga_tg_utm_3_count.count_utm == 1]

        ga_tg_utm_3 = ga_tg_utm_3.set_index(['client_id', 'utm_medium', 'utm_source', 'utm_keyword'])
        ga_tg_utm_3_dict = ga_tg_utm_3[ga_tg_utm_3.index.isin(ga_tg_utm_3_count_one_by_one.index)]
        ga_tg_utm_3_dict = ga_tg_utm_3_dict.reset_index()

        ga_tg_utm_3_dict['utm_key'] = (ga_tg_utm_3_dict.client_id + '_' +
                                       ga_tg_utm_3_dict.utm_medium + '_' +
                                       ga_tg_utm_3_dict.utm_source + '_' +
                                       ga_tg_utm_3_dict.utm_keyword)

        ga_tg_utm_3_dict_series_campaign = pd.Series(ga_tg_utm_3_dict['utm_campaign'].values,
                                                     index=ga_tg_utm_3_dict['utm_key'])
        ga_tg_utm_3_dict_series_adcontent = pd.Series(ga_tg_utm_3_dict['utm_adcontent'].values,
                                                      index=ga_tg_utm_3_dict['utm_key'])

        update_dictionary['ga_tg_utm_3_dict_series_campaign'] = ga_tg_utm_3_dict_series_campaign
        update_dictionary['ga_tg_utm_3_dict_series_adcontent'] = ga_tg_utm_3_dict_series_adcontent

    ga_tg[['utm_campaign_nan', 'utm_adcontent_nan']] = ga_tg[['utm_campaign', 'utm_adcontent']]

    ga_tg.loc[(ga_tg.utm_campaign_nan == '_none_') & (ga_tg.utm_adcontent_nan == '_none_'), 'utm_campaign'] = ga_tg.loc[
        (ga_tg.utm_campaign_nan == '_none_') & (ga_tg.utm_adcontent_nan == '_none_'), 'utm_key'].map(
        update_dictionary['ga_tg_utm_3_dict_series_campaign'])

    ga_tg.loc[(ga_tg.utm_campaign_nan == '_none_') & (ga_tg.utm_adcontent_nan == '_none_'), 'utm_adcontent'] = \
    ga_tg.loc[
        (ga_tg.utm_campaign_nan == '_none_') & (ga_tg.utm_adcontent_nan == '_none_'), 'utm_key'].map(
        update_dictionary['ga_tg_utm_3_dict_series_adcontent'])

    ga_tg[['utm_campaign', 'utm_adcontent']] = ga_tg[['utm_campaign', 'utm_adcontent']].fillna('_none_')

    ga_tg.drop(['utm_key', 'utm_campaign_nan', 'utm_adcontent_nan'], axis=1, inplace=True)


    # Заполнение колонок utm_campaign и utm_adcontent по клиенту - случай разных значений данной пары у клиента

    if update_dictionary['created_utm_dictionaries'] == 0:

        ga_tg_utm_cl_4 = ga_tg[(ga_tg.utm_campaign == '_none_') & (ga_tg.utm_adcontent == '_none_')].groupby(
            ['client_id', 'utm_medium', 'utm_source', 'utm_keyword']).agg(count_sessions=('session_id', 'count'))

        ga_tg_ind_4 = ga_tg[((ga_tg.utm_campaign != '_none_') | (ga_tg.utm_adcontent != '_none_'))
        ].set_index(['client_id', 'utm_medium', 'utm_source', 'utm_keyword'])
        ga_tg_utm_4 = ga_tg_ind_4[ga_tg_ind_4.index.isin(ga_tg_utm_cl_4.index)]
        ga_tg_utm_4 = ga_tg_utm_4.reset_index()

        ga_tg_utm_cl_4_all = ga_tg_utm_4.client_id.drop_duplicates()
        ga_tg_utm_4_full = ga_tg[ga_tg.client_id.isin(ga_tg_utm_cl_4_all)]

        ga_tg_diff = ga_tg_utm_4_full

        initial_index = []
        index_for_update = []

        clients = ga_tg_diff.client_id.drop_duplicates()

        for cl_id in clients:
            ga_tg_diff_none = ga_tg_diff[
                (ga_tg_diff.client_id == cl_id) &
                (ga_tg_diff.utm_campaign == '_none_') &
                (ga_tg_diff.utm_adcontent == '_none_')
                ]
            for ind in ga_tg_diff_none.index:
                row = ga_tg_diff[ga_tg_diff.index == ind]
                ga_tg_diff_utm = ga_tg_diff[
                    ((ga_tg_diff.utm_campaign != '_none_') | (ga_tg_diff.utm_adcontent != '_none_')) &
                    (ga_tg_diff.client_id == row.client_id.loc[ind]) &
                    (ga_tg_diff.utm_medium == row.utm_medium.loc[ind]) &
                    (ga_tg_diff.utm_source == row.utm_source.loc[ind]) &
                    (ga_tg_diff.utm_keyword == row.utm_keyword.loc[ind]) &
                    (ga_tg_diff.visit_number < row.visit_number.loc[ind])
                    ]

                ga_tg_diff_upd = ga_tg_diff_utm[ga_tg_diff_utm.visit_number == ga_tg_diff_utm.visit_number.max()]

                if len(ga_tg_diff_upd) == 0:
                    ga_tg_diff_utm = ga_tg_diff[
                        ((ga_tg_diff.utm_campaign != '_none_') | (ga_tg_diff.utm_adcontent != '_none_')) &
                        (ga_tg_diff.client_id == row.client_id.loc[ind]) &
                        (ga_tg_diff.utm_medium == row.utm_medium.loc[ind]) &
                        (ga_tg_diff.utm_source == row.utm_source.loc[ind]) &
                        (ga_tg_diff.utm_keyword == row.utm_keyword.loc[ind]) &
                        (ga_tg_diff.visit_number > row.visit_number.loc[ind])
                        ]

                    ga_tg_diff_upd = ga_tg_diff_utm[ga_tg_diff_utm.visit_number == ga_tg_diff_utm.visit_number.min()]

                ind_utm = pd.NA
                if len(ga_tg_diff_upd) != 0:
                    ind_utm = int(ga_tg_diff_upd.index[0])

                initial_index.append(ind)
                index_for_update.append(ind_utm)

        df_ind = pd.DataFrame({
            'initial_index': initial_index,
            'index_for_update': index_for_update}).set_index('index_for_update')

        ga_tg.index.name = 'index_for_update'

        df_upd_dict = pd.merge(df_ind, ga_tg, on='index_for_update', how='left')
        df_upd_dict = df_upd_dict[['initial_index', 'utm_campaign', 'utm_adcontent']]
        df_upd_dict = df_upd_dict.rename(columns={'utm_campaign': 'utm_campaign_4', 'utm_adcontent': 'utm_adcontent_4'})
        df_upd_dict.set_index('initial_index')

        ga_tg.reset_index()

        ga_tg.index.name = 'initial_index'
        ga_tg = pd.merge(ga_tg, df_upd_dict, on='initial_index', how='left')

        ga_tg.loc[(~ga_tg.utm_campaign_4.isna()) & (~ga_tg.utm_adcontent_4.isna()) &
                  (ga_tg.utm_campaign == '_none_') & (ga_tg.utm_adcontent == '_none_'),
            ['utm_campaign', 'utm_adcontent']] = ga_tg.loc[(~ga_tg.utm_campaign_4.isna()) & (~ga_tg.utm_adcontent_4.isna()) &
                                                           (ga_tg.utm_campaign == '_none_') & (ga_tg.utm_adcontent == '_none_'),
            ['utm_campaign_4', 'utm_adcontent_4']].values

        ga_tg = ga_tg.drop(['initial_index', 'utm_campaign_4', 'utm_adcontent_4'], axis=1)


    # Заполнение колонки utm_campaign по клиенту

    ga_tg['utm_key'] = (ga_tg.client_id + '_' +
                        ga_tg.utm_medium + '_' +
                        ga_tg.utm_source + '_' +
                        ga_tg.utm_adcontent + '_' +
                        ga_tg.utm_keyword)

    if update_dictionary['created_utm_dictionaries'] == 0:

        ga_tg_utm_camp_cl_1 = ga_tg[(ga_tg.utm_campaign == '_none_')].groupby(
            ['client_id', 'utm_medium', 'utm_source', 'utm_adcontent', 'utm_keyword']).agg(
            count_sessions=('session_id', 'count'))

        ga_tg_ind_camp_1 = ga_tg[ga_tg.utm_campaign != '_none_'].set_index(
            ['client_id', 'utm_medium', 'utm_source', 'utm_adcontent', 'utm_keyword'])
        ga_tg_utm_camp_1 = ga_tg_ind_camp_1[ga_tg_ind_camp_1.index.isin(ga_tg_utm_camp_cl_1.index)]
        ga_tg_utm_camp_1 = ga_tg_utm_camp_1.reset_index().groupby([
            'client_id', 'utm_medium', 'utm_source', 'utm_campaign', 'utm_adcontent', 'utm_keyword'],
            as_index=False).agg(count_sessions_utm=('session_id', 'count'))

        ga_tg_utm_camp_1_count = ga_tg_utm_camp_1.groupby(
            ['client_id', 'utm_medium', 'utm_source', 'utm_adcontent', 'utm_keyword']).agg(
            count_utm=('utm_medium', 'count'))

        ga_tg_utm_camp_1_count_one_by_one = ga_tg_utm_camp_1_count[ga_tg_utm_camp_1_count.count_utm == 1]

        ga_tg_utm_camp_1 = ga_tg_utm_camp_1.set_index(
            ['client_id', 'utm_medium', 'utm_source', 'utm_adcontent', 'utm_keyword'])
        ga_tg_utm_camp_1_dict = ga_tg_utm_camp_1[ga_tg_utm_camp_1.index.isin(ga_tg_utm_camp_1_count_one_by_one.index)]
        ga_tg_utm_camp_1_dict = ga_tg_utm_camp_1_dict.reset_index()
        ga_tg_utm_camp_1_dict['utm_key'] = (ga_tg_utm_camp_1_dict.client_id + '_' +
                                            ga_tg_utm_camp_1_dict.utm_medium + '_' +
                                            ga_tg_utm_camp_1_dict.utm_source + '_' +
                                            ga_tg_utm_camp_1_dict.utm_adcontent + '_' +
                                            ga_tg_utm_camp_1_dict.utm_keyword)

        ga_tg_utm_camp_1_dict_series = pd.Series(ga_tg_utm_camp_1_dict['utm_campaign'].values, index=ga_tg_utm_camp_1_dict['utm_key'])

        update_dictionary['ga_tg_utm_camp_1_dict_series'] = ga_tg_utm_camp_1_dict_series

    ga_tg.loc[(ga_tg.utm_campaign == '_none_'), 'utm_campaign'] = ga_tg.loc[
        (ga_tg.utm_campaign == '_none_'), 'utm_key'].map(update_dictionary['ga_tg_utm_camp_1_dict_series'])

    ga_tg[['utm_campaign']] = ga_tg[['utm_campaign']].fillna('_none_')

    ga_tg.drop(['utm_key'], axis=1, inplace=True)


    # Заполнение колонки utm_campaign по клиенту - случай разных значений в данной колонке у клиента
    # Обновление основано на поиске ближайших данных по полю visit_number по каждому клиенту в сформированном датасете

    if update_dictionary['created_utm_dictionaries'] == 0:

        ga_tg_utm_camp_cl_1 = ga_tg[(ga_tg.utm_campaign == '_none_')].groupby(
            ['client_id', 'utm_medium', 'utm_source', 'utm_adcontent', 'utm_keyword']).agg(
            count_sessions=('session_id', 'count'))

        ga_tg_ind_camp_1 = ga_tg[ga_tg.utm_campaign != '_none_'].set_index(
            ['client_id', 'utm_medium', 'utm_source', 'utm_adcontent', 'utm_keyword'])
        ga_tg_utm_camp_1 = ga_tg_ind_camp_1[ga_tg_ind_camp_1.index.isin(ga_tg_utm_camp_cl_1.index)]
        ga_tg_utm_camp_1 = ga_tg_utm_camp_1.reset_index().groupby([
            'client_id', 'utm_medium', 'utm_source', 'utm_campaign', 'utm_adcontent', 'utm_keyword'],
            as_index=False).agg(count_sessions_utm=('session_id', 'count'))

        ga_tg_utm_camp_1_count = ga_tg_utm_camp_1.groupby(
            ['client_id', 'utm_medium', 'utm_source', 'utm_adcontent', 'utm_keyword']).agg(
            count_utm=('utm_medium', 'count'))

        ga_tg_utm_camp_1_count_many = ga_tg_utm_camp_1_count[ga_tg_utm_camp_1_count.count_utm > 1]
        ga_tg_utm_camp_1_count_many = ga_tg_utm_camp_1_count_many.reset_index()

        ga_tg_diff_camp = ga_tg[ga_tg.client_id.isin(ga_tg_utm_camp_1_count_many.client_id.drop_duplicates())]

        clients = ga_tg_utm_camp_1_count_many.client_id.drop_duplicates()

        for cl_id in clients:
            ga_tg_diff_camp_none = ga_tg_diff_camp[
                (ga_tg_diff_camp.client_id == cl_id) &
                (ga_tg_diff_camp.utm_campaign == '_none_')
                ]
            for row in ga_tg_diff_camp_none.itertuples():
                ga_tg_diff_camp_utm = ga_tg_diff_camp[
                    (ga_tg_diff_camp.utm_campaign != '_none_') &
                    (ga_tg_diff_camp.client_id == row.client_id) &
                    (ga_tg_diff_camp.utm_medium == row.utm_medium) &
                    (ga_tg_diff_camp.utm_source == row.utm_source) &
                    (ga_tg_diff_camp.utm_adcontent == row.utm_adcontent) &
                    (ga_tg_diff_camp.utm_keyword == row.utm_keyword) &
                    (ga_tg_diff_camp.visit_number < row.visit_number)]

                ga_tg_diff_camp_upd = ga_tg_diff_camp_utm[
                    ga_tg_diff_camp_utm.visit_number == ga_tg_diff_camp_utm.visit_number.max()]

                if len(ga_tg_diff_camp_upd) == 0:
                    ga_tg_diff_camp_utm = ga_tg_diff_camp[
                        (ga_tg_diff_camp.utm_campaign != '_none_') &
                        (ga_tg_diff_camp.client_id == row.client_id) &
                        (ga_tg_diff_camp.utm_medium == row.utm_medium) &
                        (ga_tg_diff_camp.utm_source == row.utm_source) &
                        (ga_tg_diff_camp.utm_adcontent == row.utm_adcontent) &
                        (ga_tg_diff_camp.utm_keyword == row.utm_keyword) &
                        (ga_tg_diff_camp.visit_number > row.visit_number)]

                    ga_tg_diff_camp_upd = ga_tg_diff_camp_utm[
                        ga_tg_diff_camp_utm.visit_number == ga_tg_diff_camp_utm.visit_number.min()]

                if len(ga_tg_diff_camp_upd) != 0:
                    ga_tg.loc[row.Index, 'utm_campaign'] = ga_tg_diff_camp_upd.utm_campaign.values[0]


    # Заполнение колонки utm_adcontent по клиенту

    ga_tg['utm_key'] = (ga_tg.client_id + '_' +
                        ga_tg.utm_medium + '_' +
                        ga_tg.utm_source + '_' +
                        ga_tg.utm_campaign + '_' +
                        ga_tg.utm_keyword)

    if update_dictionary['created_utm_dictionaries'] == 0:

        ga_tg_utm_adcont_cl_1 = ga_tg[(ga_tg.utm_adcontent == '_none_')].groupby(
            ['client_id', 'utm_medium', 'utm_source', 'utm_campaign', 'utm_keyword']).agg(
            count_sessions=('session_id', 'count'))

        ga_tg_ind_adcont_1 = ga_tg[ga_tg.utm_adcontent != '_none_'].set_index(
            ['client_id', 'utm_medium', 'utm_source', 'utm_campaign', 'utm_keyword'])
        ga_tg_utm_adcont_1 = ga_tg_ind_adcont_1[ga_tg_ind_adcont_1.index.isin(ga_tg_utm_adcont_cl_1.index)]
        ga_tg_utm_adcont_1 = ga_tg_utm_adcont_1.reset_index().groupby([
            'client_id', 'utm_medium', 'utm_source', 'utm_campaign', 'utm_adcontent', 'utm_keyword'],
            as_index=False).agg(count_sessions_utm=('session_id', 'count'))

        ga_tg_utm_adcont_1_count_max = ga_tg_utm_adcont_1.groupby([
            'client_id', 'utm_medium', 'utm_source', 'utm_campaign', 'utm_keyword'])['count_sessions_utm'].idxmax()

        ga_tg_utm_adcont_1_dict = ga_tg_utm_adcont_1.loc[ga_tg_utm_adcont_1_count_max]
        ga_tg_utm_adcont_1_dict['utm_key'] = (ga_tg_utm_adcont_1_dict.client_id + '_' +
                                            ga_tg_utm_adcont_1_dict.utm_medium + '_' +
                                            ga_tg_utm_adcont_1_dict.utm_source + '_' +
                                            ga_tg_utm_adcont_1_dict.utm_campaign + '_' +
                                            ga_tg_utm_adcont_1_dict.utm_keyword)

        ga_tg_utm_adcont_1_dict_series = pd.Series(ga_tg_utm_adcont_1_dict['utm_adcontent'].values,
                                                 index=ga_tg_utm_adcont_1_dict['utm_key'])

        update_dictionary['ga_tg_utm_adcont_1_dict_series'] = ga_tg_utm_adcont_1_dict_series

    ga_tg.loc[(ga_tg.utm_adcontent == '_none_'), 'utm_adcontent'] = ga_tg.loc[
        (ga_tg.utm_adcontent == '_none_'), 'utm_key'].map(update_dictionary['ga_tg_utm_adcont_1_dict_series'])

    ga_tg[['utm_adcontent']] = ga_tg[['utm_adcontent']].fillna('_none_')

    ga_tg.drop(['utm_key'], axis=1, inplace=True)


    # Заполнение колонки utm_adcontent по utm_campaign - связь один к одному

    if update_dictionary['created_utm_dictionaries'] == 0:

        ga_tg_utm_adcont_none = ga_tg[(ga_tg.utm_campaign != '_none_') & (ga_tg.utm_adcontent == '_none_')].groupby(
            ['utm_campaign']).agg(count_sessions=('session_id', 'count'))

        ga_tg_utm_adcont_no_none = ga_tg[
            (ga_tg.utm_adcontent != '_none_') &
            (ga_tg.utm_campaign.isin(ga_tg_utm_adcont_none.reset_index().utm_campaign))].groupby([
            'utm_campaign', 'utm_adcontent'], as_index=False).agg(count_sessions_utm=('session_id', 'count'))

        ga_tg_utm_adcont_no_none_count = ga_tg_utm_adcont_no_none.groupby(
            ['utm_campaign']).agg(count_adcont=('utm_adcontent', 'count'))

        ga_tg_utm_adcont_no_none_count_one_by_one = ga_tg_utm_adcont_no_none_count[
            ga_tg_utm_adcont_no_none_count.count_adcont == 1]

        ga_tg_utm_adcont_dict = ga_tg_utm_adcont_no_none[
            ga_tg_utm_adcont_no_none.utm_campaign.isin( ga_tg_utm_adcont_no_none_count_one_by_one.reset_index().utm_campaign)]

        ga_tg_utm_adcont_dict_series = pd.Series(ga_tg_utm_adcont_dict['utm_adcontent'].values,
                                                   index=ga_tg_utm_adcont_dict['utm_campaign'])

        update_dictionary['ga_tg_utm_adcont_dict_series'] = ga_tg_utm_adcont_dict_series

    ga_tg.loc[(ga_tg.utm_adcontent == '_none_'), 'utm_adcontent'] = ga_tg.loc[
        (ga_tg.utm_adcontent == '_none_'), 'utm_campaign'].map(update_dictionary['ga_tg_utm_adcont_dict_series'])

    ga_tg[['utm_adcontent']] = ga_tg[['utm_adcontent']].fillna('_none_')


    # Заполнение колонки utm_adcontent по данным колонок utm_campaign и geo_city - связь один к одному

    ga_tg['utm_key'] = (ga_tg.utm_campaign + '_' +
                        ga_tg.geo_city)

    if update_dictionary['created_utm_dictionaries'] == 0:

        ga_tg_utm_adcont_city_none = ga_tg[(ga_tg.utm_campaign != '_none_') & (ga_tg.utm_adcontent == '_none_')].groupby(
            ['utm_campaign', 'geo_city']).agg(count_sessions=('session_id', 'count'))

        ga_tg_utm_adcont_city_ind = ga_tg[(ga_tg.utm_adcontent != '_none_')].set_index(['utm_campaign', 'geo_city'])
        ga_tg_utm_adcont_city_no_none = ga_tg_utm_adcont_city_ind[
            (ga_tg_utm_adcont_city_ind.index.isin(ga_tg_utm_adcont_city_none.index))].reset_index().groupby([
            'utm_campaign', 'utm_adcontent', 'geo_city'], as_index=False).agg(
            count_sessions_utm_geo=('session_id', 'count'))

        ga_tg_utm_adcont_city_no_none_count = ga_tg_utm_adcont_city_no_none.groupby(
            ['utm_campaign', 'geo_city']).agg(count_city=('geo_city', 'count'))

        ga_tg_utm_adcont_city_no_none_count_one_by_one = ga_tg_utm_adcont_city_no_none_count[
            ga_tg_utm_adcont_city_no_none_count.count_city == 1]

        ga_tg_utm_adcont_city_no_none = ga_tg_utm_adcont_city_no_none.set_index(['utm_campaign', 'geo_city'])
        ga_tg_utm_adcont_city_dict = ga_tg_utm_adcont_city_no_none[
            ga_tg_utm_adcont_city_no_none.index.isin(ga_tg_utm_adcont_city_no_none_count_one_by_one.index)]
        ga_tg_utm_adcont_city_no_none = ga_tg_utm_adcont_city_no_none.reset_index()
        ga_tg_utm_adcont_city_dict = ga_tg_utm_adcont_city_dict.reset_index()
        ga_tg_utm_adcont_city_dict['utm_key'] = (ga_tg_utm_adcont_city_dict.utm_campaign + '_' +
                                                 ga_tg_utm_adcont_city_dict.geo_city)

        ga_tg_utm_adcont_city_dict_series = pd.Series(ga_tg_utm_adcont_city_dict['utm_adcontent'].values,
                                                   index=ga_tg_utm_adcont_city_dict['utm_key'])

        update_dictionary['ga_tg_utm_adcont_city_dict_series'] = ga_tg_utm_adcont_city_dict_series

    ga_tg.loc[(ga_tg.utm_adcontent == '_none_'), 'utm_adcontent'] = ga_tg.loc[
        (ga_tg.utm_adcontent == '_none_'), 'utm_key'].map(update_dictionary['ga_tg_utm_adcont_city_dict_series'])

    ga_tg[['utm_adcontent']] = ga_tg[['utm_adcontent']].fillna('_none_')

    ga_tg.drop(['utm_key'], axis=1, inplace=True)


    # Заполнение колонки utm_campaign по данным колонок utm_adcontent и geo_city - связь один к одному

    ga_tg['utm_key'] = (ga_tg.utm_adcontent + '_' +
                        ga_tg.geo_city)

    if update_dictionary['created_utm_dictionaries'] == 0:

        ga_tg_utm_camp_city_none = ga_tg[(ga_tg.utm_campaign == '_none_') & (ga_tg.utm_adcontent != '_none_')].groupby(
            ['utm_adcontent', 'geo_city']).agg(count_sessions=('session_id', 'count'))

        ga_tg_utm_camp_city_ind = ga_tg[(ga_tg.utm_campaign != '_none_')].set_index(['utm_adcontent', 'geo_city'])
        ga_tg_utm_camp_city_no_none = ga_tg_utm_camp_city_ind[
            (ga_tg_utm_camp_city_ind.index.isin(ga_tg_utm_camp_city_none.index))].reset_index().groupby([
            'utm_campaign', 'utm_adcontent', 'geo_city'], as_index=False).agg(count_sessions_camp=('session_id', 'count'))

        ga_tg_utm_camp_city_no_none_count = ga_tg_utm_camp_city_no_none.groupby(
            ['utm_adcontent', 'geo_city']).agg(count_city=('geo_city', 'count'))

        ga_tg_utm_camp_city_no_none_count_one_by_one = ga_tg_utm_camp_city_no_none_count[
            ga_tg_utm_camp_city_no_none_count.count_city == 1]

        ga_tg_utm_camp_city_no_none = ga_tg_utm_camp_city_no_none.set_index(['utm_adcontent', 'geo_city'])
        ga_tg_utm_camp_city_dict = ga_tg_utm_camp_city_no_none[
            ga_tg_utm_camp_city_no_none.index.isin(ga_tg_utm_camp_city_no_none_count_one_by_one.index)]
        ga_tg_utm_camp_city_no_none = ga_tg_utm_camp_city_no_none.reset_index()
        ga_tg_utm_camp_city_dict = ga_tg_utm_camp_city_dict.reset_index()
        ga_tg_utm_camp_city_dict['utm_key'] = (ga_tg_utm_camp_city_dict.utm_adcontent + '_' +
                                               ga_tg_utm_camp_city_dict.geo_city)

        ga_tg_utm_camp_city_dict_series = pd.Series(ga_tg_utm_camp_city_dict['utm_campaign'].values,
                                                   index=ga_tg_utm_camp_city_dict['utm_key'])

        update_dictionary['ga_tg_utm_camp_city_dict_series'] = ga_tg_utm_camp_city_dict_series

    ga_tg.loc[(ga_tg.utm_campaign == '_none_'), 'utm_campaign'] = ga_tg.loc[
        (ga_tg.utm_campaign == '_none_'), 'utm_key'].map(update_dictionary['ga_tg_utm_camp_city_dict_series'])

    ga_tg[['utm_campaign']] = ga_tg[['utm_campaign']].fillna('_none_')

    ga_tg.drop(['utm_key'], axis=1, inplace=True)


    # Заполнение оставшихся колонок значением _none_

    ga_tg = ga_tg.fillna('_none_')

    update_dictionary['created_utm_dictionaries'] = 1

    return ga_tg



