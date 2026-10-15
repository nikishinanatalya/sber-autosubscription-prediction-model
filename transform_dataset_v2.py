import pandas as pd

def create_features(ga_tg, transform_dictionary, ga_tg_dict=None):

    ga_tg = ga_tg.copy()

    # Добавление в датасет целевой переменной, необходимой для группировки значений у атрибутов

    if transform_dictionary['merged_datasets'] == 0:

        ga_tg = pd.merge(left=ga_tg, right=ga_tg_dict, on=['session_id'], how='left')

    # Создание признака неинформативных строк

    ga_tg['uninformative_session'] = 0
    ga_tg.loc[(ga_tg == '_none_').sum(axis=1) / 18 * 100 > 30, 'uninformative_session'] = 1

    # Создание дополнительных атрибутов времени

    ga_tg['visit_month'] = pd.to_datetime(ga_tg.visit_date).dt.month.astype(str)
    ga_tg['visit_day'] = pd.to_datetime(ga_tg.visit_date).dt.day.astype(str)
    ga_tg['visit_week_day'] = pd.to_datetime(ga_tg.visit_date).dt.weekday.astype(str)

    # Разбиение значений атрибута device_browser на группы

    not_browsers_apps_contains = ['Instagram', 'Threads', 'com.vk', 'com.zhiliaoapp', 'FBAN']
    not_browsers_web_agents = ['Android Webview', 'Safari (in-app)', 'MRCHROME']
    not_browsers_system_agents = ['Android', 'Android Runtime', 'Mozilla', 'Mozilla Compatible Agent']
    not_browsers_stuff = ['MT6735_TD', 'MyApp', 'NokiaX2-02', 'Nokia501', 'helloworld', '(not set)']

    ga_tg.loc[ga_tg.device_browser.str.contains('|'.join(not_browsers_apps_contains), case=False, na=False),
    'device_app_category'] = 'Apps'
    ga_tg.loc[ga_tg.device_browser.isin(not_browsers_web_agents), 'device_app_category'] = 'Web Agents'
    ga_tg.loc[ga_tg.device_browser.isin(not_browsers_system_agents), 'device_app_category'] = 'System Agents'
    ga_tg.loc[ga_tg.device_browser.isin(not_browsers_stuff), 'device_app_category'] = 'Stuff'
    ga_tg.loc[ga_tg.device_app_category.isna(), 'device_app_category'] = 'Browsers'

    # Создание атрибута признака органического трафика

    ga_tg['organic_traffic'] = ga_tg.utm_medium.apply(lambda x: 1 if x in (['organic', 'referral', '(none)']) else 0)

    # Создание атрибута признака рекламы в социальных сетях

    ga_tg['social_network'] = ga_tg.utm_source.apply(
        lambda x: 1 if x in ['QxAxdyPLuQMEcrdZWdWb', 'MvfHsxITijuriZxsqZqt', 'ISrKoXQCxqqYvAZICvjs',
                             'IZEXUFLARCUMynmHNBGo', 'PlbkrSYoHuZBWfYjYnfw', 'gVRrcxiDQubJiljoTbGm'] else 0)

    # Создание атрибута признака аномалии характеристик устройств

    ga_tg['device_anomaly'] = 0

    ga_tg.loc[
        (ga_tg.device_category == 'desktop') &
        (ga_tg.device_os == 'iOS'), 'device_anomaly'] = 1

    ga_tg.loc[
        (ga_tg.device_category == 'desktop') &
        (ga_tg.device_os != 'Macintosh') &
        (~ga_tg.device_os.isna()) &
        (ga_tg.device_browser == 'Safari'), 'device_anomaly'] = 1

    ga_tg.loc[
        (ga_tg.device_category.isin(['mobile', 'tablet'])) &
        (ga_tg.device_brand != 'Apple') &
        (~ga_tg.device_brand.isna()) &
        (ga_tg.device_brand != '(not set)') &
        (ga_tg.device_browser == 'Safari'), 'device_anomaly'] = 1

    ga_tg.loc[
        (ga_tg.device_category.isin(['mobile', 'tablet'])) &
        (ga_tg.device_os == 'Macintosh'), 'device_anomaly'] = 1

    # Устройства с одинаковой шириной и длиной экрана

    ga_tg['device_anomaly'] = ga_tg.device_screen_resolution.apply(
        lambda x: 1 if x.split('x')[0] == x.split('x')[1] else 0)

    ga_tg.loc[(ga_tg.device_app_category == 'Stuff'), 'device_anomaly'] = 1

    # Создание атрибута со сгруппированными по целевому событию значениями для атрибута utm_source

    if transform_dictionary['created_grouped_utm_dictionaries'] == 0:

        ga_tg_utm_source_piv = ga_tg.groupby(['utm_source'], as_index=False).agg(targeted=('event_session_target', 'sum'))

        ga_tg_utm_source_piv['utm_source_target_frequency'] = ga_tg_utm_source_piv.apply(
            lambda x: 'high' if x.targeted > 22 and x.targeted <= 100
            else ('medium' if x.targeted > 11 and x.targeted <= 22
                  else ('low' if x.targeted > 3 and x.targeted <= 11
                        else ('too low' if x.targeted > 1 and x.targeted <= 3
                              else ('once' if x.targeted == 1
                                    else ('zero' if x.targeted == 0
                                          else x.utm_source))))), axis=1)

        ga_tg_utm_source_piv_dict = ga_tg_utm_source_piv.set_index('utm_source')[ 'utm_source_target_frequency']

        transform_dictionary['ga_tg_utm_source_piv_dict'] = ga_tg_utm_source_piv_dict

    ga_tg['utm_source_target_frequency'] = ga_tg['utm_source'].map(transform_dictionary['ga_tg_utm_source_piv_dict'])

    ga_tg[['utm_source_target_frequency']] = ga_tg[['utm_source_target_frequency']].fillna('other')


    # Создание атрибута со сгруппированными по целевому событию значениями для атрибута utm_medium

    if transform_dictionary['created_grouped_utm_dictionaries'] == 0:

        ga_tg_utm_medium_piv = ga_tg.groupby(['utm_medium'], as_index=False).agg(targeted=('event_session_target', 'sum'))

        ga_tg_utm_medium_piv['utm_medium_target_frequency'] = ga_tg_utm_medium_piv.apply(
            lambda x: 'too low' if x.targeted > 1 and x.targeted <= 3
            else ('once' if x.targeted == 1
                  else ('zero' if x.targeted == 0
                        else x.utm_medium)), axis=1)

        ga_tg_utm_medium_piv_dict = ga_tg_utm_medium_piv.set_index('utm_medium')['utm_medium_target_frequency']

        transform_dictionary['ga_tg_utm_medium_piv_dict'] = ga_tg_utm_medium_piv_dict

    ga_tg['utm_medium_target_frequency'] = ga_tg['utm_medium'].map(transform_dictionary['ga_tg_utm_medium_piv_dict'])

    ga_tg[['utm_medium_target_frequency']] = ga_tg[['utm_medium_target_frequency']].fillna('other')


    # Создание атрибута со сгруппированными по целевому событию значениями для атрибута utm_campaign

    if transform_dictionary['created_grouped_utm_dictionaries'] == 0:

        ga_tg_utm_campaign_piv = ga_tg.groupby(['utm_campaign'], as_index=False).agg(targeted=('event_session_target', 'sum'))

        ga_tg_utm_campaign_piv['utm_campaign_target_frequency'] = ga_tg_utm_campaign_piv.apply(
            lambda x: 'high' if x.targeted > 100 and x.targeted <= 170
            else ('medium' if x.targeted > 26 and x.targeted <= 100
                  else ('medium to low' if x.targeted > 10 and x.targeted <= 26
                        else ('low' if x.targeted > 3 and x.targeted <= 10
                              else ('too low' if x.targeted > 1 and x.targeted <= 3
                                    else ('once' if x.targeted == 1
                                          else ('zero' if x.targeted == 0
                                                else x.utm_campaign)))))), axis=1)

        ga_tg_utm_campaign_piv_dict = ga_tg_utm_campaign_piv.set_index('utm_campaign')['utm_campaign_target_frequency']

        transform_dictionary['ga_tg_utm_campaign_piv_dict'] = ga_tg_utm_campaign_piv_dict

    ga_tg['utm_campaign_target_frequency'] = ga_tg['utm_campaign'].map(transform_dictionary['ga_tg_utm_campaign_piv_dict'])

    ga_tg[['utm_campaign_target_frequency']] = ga_tg[['utm_campaign_target_frequency']].fillna('other')


    # Создание атрибута со сгруппированными по целевому событию значениями для атрибута utm_adcontent

    if transform_dictionary['created_grouped_utm_dictionaries'] == 0:

        ga_tg_utm_adcontent_piv = ga_tg.groupby(['utm_adcontent'], as_index=False).agg(targeted=('event_session_target', 'sum'))

        ga_tg_utm_adcontent_piv['utm_adcontent_target_frequency'] = ga_tg_utm_adcontent_piv.apply(
            lambda x: 'medium' if x.targeted > 18 and x.targeted <= 100
            else ('low' if x.targeted > 4 and x.targeted <= 18
                  else ('too low' if x.targeted > 1 and x.targeted <= 4
                        else ('once' if x.targeted == 1
                              else ('zero' if x.targeted == 0
                                    else x.utm_adcontent)))), axis=1)

        ga_tg_utm_adcontent_piv_dict = ga_tg_utm_adcontent_piv.set_index('utm_adcontent')['utm_adcontent_target_frequency']

        transform_dictionary['ga_tg_utm_adcontent_piv_dict'] = ga_tg_utm_adcontent_piv_dict

    ga_tg['utm_adcontent_target_frequency'] = ga_tg['utm_adcontent'].map(transform_dictionary['ga_tg_utm_adcontent_piv_dict'])

    ga_tg[['utm_adcontent_target_frequency']] = ga_tg[['utm_adcontent_target_frequency']].fillna('other')


    # Создание атрибута со сгруппированными по целевому событию значениями для атрибута utm_keyword

    if transform_dictionary['created_grouped_utm_dictionaries'] == 0:

        ga_tg_utm_keyword_piv = ga_tg.groupby(['utm_keyword'], as_index=False).agg(targeted=('event_session_target', 'sum'))

        ga_tg_utm_keyword_piv['utm_keyword_target_frequency'] = ga_tg_utm_keyword_piv.apply(
            lambda x: 'high' if x.targeted > 20 and x.targeted < 90
            else ('medium' if x.targeted > 9 and x.targeted <= 20
                  else ('low' if x.targeted > 3 and x.targeted <= 9
                        else ('too low' if x.targeted > 1 and x.targeted <= 3
                              else ('once' if x.targeted == 1
                                    else ('zero' if x.targeted == 0
                                          else x.utm_keyword))))), axis=1)

        ga_tg_utm_keyword_piv_dict = ga_tg_utm_keyword_piv.set_index('utm_keyword')['utm_keyword_target_frequency']

        transform_dictionary['ga_tg_utm_keyword_piv_dict'] = ga_tg_utm_keyword_piv_dict

    ga_tg['utm_keyword_target_frequency'] = ga_tg['utm_keyword'].map(transform_dictionary['ga_tg_utm_keyword_piv_dict'])

    ga_tg[['utm_keyword_target_frequency']] = ga_tg[['utm_keyword_target_frequency']].fillna('other')


    # Создание атрибута со сгруппированными по целевому событию значениями для атрибута device_os

    if transform_dictionary['created_grouped_device_dictionaries'] == 0:

        ga_tg_device_os_piv = ga_tg.groupby(['device_os'], as_index=False).agg(targeted=('event_session_target', 'sum'))

        ga_tg_device_os_piv['device_os_target_frequency'] = ga_tg_device_os_piv.apply(
            lambda x: 'zero' if x.targeted == 0 else x.device_os, axis=1)

        ga_tg_device_os_piv_dict = ga_tg_device_os_piv.set_index('device_os')['device_os_target_frequency']

        transform_dictionary['ga_tg_device_os_piv_dict'] = ga_tg_device_os_piv_dict

    ga_tg['device_os_target_frequency'] = ga_tg['device_os'].map(transform_dictionary['ga_tg_device_os_piv_dict'])

    ga_tg[['device_os_target_frequency']] = ga_tg[['device_os_target_frequency']].fillna('other')


    # Создание атрибута со сгруппированными по целевому событию значениями для атрибута device_brand

    if transform_dictionary['created_grouped_device_dictionaries'] == 0:

        ga_tg_device_brand_piv = ga_tg.groupby(['device_brand'], as_index=False).agg(targeted=('event_session_target', 'sum'))

        ga_tg_device_brand_piv['device_brand_target_frequency'] = ga_tg_device_brand_piv.apply(
            lambda x: 'medium' if x.targeted > 7 and x.targeted <= 25
            else ('low' if x.targeted > 1 and x.targeted <= 7
                  else ('once' if x.targeted == 1
                        else ('zero' if x.targeted == 0
                              else x.device_brand))), axis=1)

        ga_tg_device_brand_piv_dict = ga_tg_device_brand_piv.set_index('device_brand')['device_brand_target_frequency']

        transform_dictionary['ga_tg_device_brand_piv_dict'] = ga_tg_device_brand_piv_dict

    ga_tg['device_brand_target_frequency'] = ga_tg['device_brand'].map(transform_dictionary['ga_tg_device_brand_piv_dict'])

    ga_tg[['device_brand_target_frequency']] = ga_tg[['device_brand_target_frequency']].fillna('other')


    # Создание атрибута со сгруппированными по целевому событию значениями для атрибута device_screen_resolution

    ga_tg['device_key'] = (ga_tg.device_category + '_' +
                           ga_tg.device_screen_resolution)

    if transform_dictionary['created_grouped_device_dictionaries'] == 0:

        # По категории desktop

        ga_tg_device_screen_desc_piv = ga_tg[ga_tg.device_category == 'desktop'].groupby(
            ['device_category', 'device_screen_resolution'], as_index=False).agg(targeted=('event_session_target', 'sum'))

        ga_tg_device_screen_desc_piv['device_screen_target_frequency'] = ga_tg_device_screen_desc_piv.apply(
            lambda x: 'desktop - high' if x.targeted > 90 and x.targeted <= 600
            else ('desktop - medium' if x.targeted > 15 and x.targeted <= 90
                  else ('desktop - medium to low' if x.targeted > 8 and x.targeted <= 15
                        else ('desktop - low' if x.targeted > 3 and x.targeted <= 8
                              else ('desktop - too low' if x.targeted > 1 and x.targeted <= 3
                                    else ('desktop - once' if x.targeted == 1
                                          else ('desktop - zero' if x.targeted == 0
                                                else x.device_category + ' ' + x.device_screen_resolution)))))), axis=1)

        ga_tg_device_screen_desc_piv['device_key'] = (ga_tg_device_screen_desc_piv.device_category + '_' +
                                                      ga_tg_device_screen_desc_piv.device_screen_resolution)

        # По категории mobile

        ga_tg_device_screen_mobile_piv = ga_tg[ga_tg.device_category == 'mobile'].groupby(
            ['device_category', 'device_screen_resolution'], as_index=False).agg(targeted=('event_session_target', 'sum'))

        ga_tg_device_screen_mobile_piv['device_screen_target_frequency'] = ga_tg_device_screen_mobile_piv.apply(
            lambda x: 'mobile - high' if x.targeted > 150 and x.targeted <= 600
            else ('mobile - medium' if x.targeted > 26 and x.targeted <= 150
                  else ('mobile - medium to low' if x.targeted > 11 and x.targeted <= 26
                        else ('mobile - low' if x.targeted > 6 and x.targeted <= 11
                              else ('mobile - too low' if x.targeted > 1 and x.targeted <= 6
                                    else ('mobile - once' if x.targeted == 1
                                          else ('mobile - zero' if x.targeted == 0
                                                else x.device_category + ' ' + x.device_screen_resolution)))))), axis=1)

        ga_tg_device_screen_mobile_piv['device_key'] = (ga_tg_device_screen_mobile_piv.device_category + '_' +
                                                        ga_tg_device_screen_mobile_piv.device_screen_resolution)

        # По категории tablet

        ga_tg_device_screen_tablet_piv = ga_tg[ga_tg.device_category == 'tablet'].groupby(
            ['device_category', 'device_screen_resolution'], as_index=False).agg(targeted=('event_session_target', 'sum'))

        ga_tg_device_screen_tablet_piv['device_screen_target_frequency'] = ga_tg_device_screen_tablet_piv.apply(
            lambda x: 'tablet - medium' if x.targeted > 6 and x.targeted <= 20
            else ('tablet - low' if x.targeted > 3 and x.targeted <= 6
                  else ('tablet - too low' if x.targeted > 1 and x.targeted <= 3
                        else ('tablet - once' if x.targeted == 1
                              else ('tablet - zero' if x.targeted == 0
                                    else x.device_category + ' ' + x.device_screen_resolution)))), axis=1)

        ga_tg_device_screen_tablet_piv['device_key'] = (ga_tg_device_screen_tablet_piv.device_category + '_' +
                                                        ga_tg_device_screen_tablet_piv.device_screen_resolution)

        ga_tg_device_screen_piv = pd.concat([ga_tg_device_screen_desc_piv,
                                                  ga_tg_device_screen_mobile_piv,
                                                  ga_tg_device_screen_tablet_piv], axis=0, ignore_index=True)

        ga_tg_device_screen_piv_dict = ga_tg_device_screen_piv.set_index(['device_key'])[ 'device_screen_target_frequency']

        transform_dictionary['ga_tg_device_screen_piv_dict'] = ga_tg_device_screen_piv_dict

    ga_tg['device_screen_target_frequency'] = ga_tg['device_key'].map(transform_dictionary['ga_tg_device_screen_piv_dict'])

    ga_tg[['device_screen_target_frequency']] = ga_tg[['device_screen_target_frequency']].fillna('other')

    ga_tg.drop(['device_key'], axis=1, inplace=True)

    # Создание атрибута со сгруппированными по целевому событию значениями для атрибута device_browser

    if transform_dictionary['created_grouped_device_dictionaries'] == 0:

        ga_tg_device_browser_piv = ga_tg.groupby(['device_browser'], as_index=False).agg(targeted=('event_session_target', 'sum'))

        ga_tg_device_browser_piv['device_browser_target_frequency'] = ga_tg_device_browser_piv.apply(
            lambda x: 'too low' if x.targeted >= 1 and x.targeted < 14
            else ('zero' if x.targeted == 0
                  else x.device_browser), axis=1)

        ga_tg_device_browser_piv_dict = ga_tg_device_browser_piv.set_index('device_browser')['device_browser_target_frequency']

        transform_dictionary['ga_tg_device_browser_piv_dict'] = ga_tg_device_browser_piv_dict

    ga_tg['device_browser_target_frequency'] = ga_tg['device_browser'].map(transform_dictionary['ga_tg_device_browser_piv_dict'])

    ga_tg[['device_browser_target_frequency']] = ga_tg[['device_browser_target_frequency']].fillna('other')


    # Создание атрибута со сгруппированными по целевому событию значениями для атрибутов geo_country и geo_city

    # Создание вспомогательного атрибута geo
    ga_tg['geo'] = ga_tg.apply(lambda x: x.geo_country + ' - ' + x.geo_city, axis=1)

    if transform_dictionary['created_grouped_device_dictionaries'] == 0:

        ga_tg_geo_piv = ga_tg.groupby(['geo'], as_index=False).agg(targeted=('event_session_target', 'sum'))

        ga_tg_geo_piv['geo_target_frequency'] = ga_tg_geo_piv.apply(lambda x: 'high' if x.targeted > 73 and x.targeted < 200
        else ('medium' if x.targeted > 37 and x.targeted <= 73
              else ('medium to low' if x.targeted > 9 and x.targeted <= 37
                    else ('low' if x.targeted > 3 and x.targeted <= 9
                          else ('too low' if x.targeted > 1 and x.targeted <= 3
                                else ('once' if x.targeted == 1
                                      else ('zero' if x.targeted == 0
                                            else x.geo)))))), axis=1)

        ga_tg_geo_piv_dict = ga_tg_geo_piv.set_index('geo')['geo_target_frequency']

        transform_dictionary['ga_tg_geo_piv_dict'] = ga_tg_geo_piv_dict

    ga_tg['geo_target_frequency'] = ga_tg['geo'].map(transform_dictionary['ga_tg_geo_piv_dict'])

    ga_tg[['geo_target_frequency']] = ga_tg[['geo_target_frequency']].fillna('other')

    # Удаление атрибута device_model, т.к. много пропущенных значений и среди существующих маленькая конверсия

    ga_tg.drop('device_model', axis=1, inplace=True)

    # Удаление колонок, которые не будут участвовать в обучении

    if transform_dictionary['created_grouped_device_dictionaries'] == 0:
        ga_tg.drop('event_session_target', axis=1, inplace=True)

    ga_tg.drop(columns=['session_id', 'client_id', 'visit_date', 'visit_time', 'visit_number',
                                   'utm_source', 'utm_medium', 'utm_campaign', 'utm_adcontent', 'utm_keyword',
                                   'device_os', 'device_brand', 'device_screen_resolution', 'device_browser',
                                   'geo_country', 'geo_city', 'geo'], inplace=True)

    transform_dictionary['merged_datasets'] = 1
    transform_dictionary['created_grouped_utm_dictionaries'] = 1
    transform_dictionary['created_grouped_device_dictionaries'] = 1

    return ga_tg