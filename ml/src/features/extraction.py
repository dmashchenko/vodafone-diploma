import sys
from sklearn.cluster import KMeans
import numpy as np
import pandas as pd

STATISTICS_POSTFIXES = ['mea_mnt', 'max_mnt', 'min_mnt', 'std_mnt', 'td_mnt', 'mea_wk']


def statistic_columns(columns):
    result = []
    for c in columns:
        for mask in STATISTICS_POSTFIXES:
            if mask in c:
                result.append(c)
                break
    return result


def extract(X):
    distortions = []
    for i in range(2, 100):
        kmeans = KMeans(n_clusters=i, n_init=10, max_iter=300, random_state=0).fit(X)
        # print(kmeans.inertia_)
        distortions.append(kmeans.inertia_)
        # kmeans.labels_
    return distortions


def add_traff_features(df):
    traff_df = df[['traff_m1', 'traff_m2', 'traff_m3', 'traff_m4', 'traff_m5']]
    df['traff_mean'] = traff_df.mean(axis=1)
    df['traff_median'] = traff_df.median(axis=1)
    df['traff_min'] = traff_df.min(axis=1)
    df['traff_max'] = traff_df.max(axis=1)
    df['traff_std'] = traff_df.std(axis=1)
    df['traff_td'] = df \
        .apply(
        lambda x: np.round(
            linear_regression([1, 2, 3, 4, 5], [x.traff_m5, x.traff_m4, x.traff_m3, x.traff_m2, x.traff_m1])[1],
            decimals=1),
        axis=1)
    return df


def add_real_lon_lat(df, geodf):
    guessed_geodf = pd.DataFrame(data={'city': ['Odesa', 'Chernivtsi', 'Kyiv', 'Kharkiv', 'Sumy', 'Dnipro', 'Mykolaiv'],
                                       'loc_lon': [11.75, 10.6, 11.75, 12.85, 12.5, 12.55, 12.05],
                                       'loc_lat': [14.74, 15.04, 15.36, 15.32, 15.49, 15.08, 14.85]}).set_index('city')

    geo = pd.merge(guessed_geodf, geodf, left_index=True, right_index=True)

    lon_coeff = linear_regression(geo.loc_lon_x, geo.loc_lon_y)
    lat_coeff = linear_regression(geo.loc_lat_x, geo.loc_lat_y)

    df['loc_lon'] = df['loc_lon'].apply(lambda x: np.round(lon_coeff[0] + x * lon_coeff[1], decimals=4))
    df['loc_lat'] = df['loc_lat'].apply(lambda x: np.round(lat_coeff[0] + x * lat_coeff[1], decimals=4))
    return df


def linear_regression(X, y):
    X = np.asarray(list(zip([1] * len(X), X)))
    X_transp = np.transpose(X)
    inverted_matrix = np.linalg.inv(np.dot(X_transp, X))
    return np.dot(inverted_matrix, np.dot(X_transp, np.transpose(y)))


def get_city_by_geo(lat, lon, geo_df):
    point = np.array((lat, lon))
    min_distance = [sys.float_info.max, 'City']
    for index, row in geo_df.iterrows():
        d = np.linalg.norm(np.array((row['loc_lat'], row['loc_lon'])) - point)
        if min_distance[0] > d:
            min_distance[0] = d
            min_distance[1] = index
    return min_distance[1]


def get_station_by_geo(lat, lon, station_dict):
    point = (lat, lon)
    min_distance = [sys.float_info.max, 'station']
    if point in station_dict:
        return station_dict[point]
    else:
        for key in station_dict.keys():
            d = np.linalg.norm(np.array(key) - np.array(point))
            if min_distance[0] > d:
                min_distance[0] = d
                min_distance[1] = station_dict[key]
    return min_distance[1]


def add_city_feature(df, geodf):
    geo_city_dict = {}

    for index, row in df.groupby(['loc_lon', 'loc_lat']).size().reset_index().iterrows():
        lat_ = row['loc_lat']
        lon_ = row['loc_lon']
        geo_city_dict[(lat_, lon_)] = get_city_by_geo(lat_, lon_, geodf)

    df['city'] = df[['loc_lat', 'loc_lon']].dropna().apply(lambda x: geo_city_dict[(x.loc_lat, x.loc_lon)], axis=1)
    df.city.fillna('Other_cities', inplace=True)
    return df


def add_station_feature(df, train_station_dict=None):
    if len(train_station_dict) == 0:
        for index, row in df.groupby(['loc_lon', 'loc_lat']).size().reset_index().iterrows():
            lat_ = row['loc_lat']
            lon_ = row['loc_lon']
            train_station_dict[(lat_, lon_)] = f'station-{index}'

        df['station'] = df[['loc_lat', 'loc_lon']].dropna().apply(lambda x: train_station_dict[(x.loc_lat, x.loc_lon)],
                                                                  axis=1)
    else:
        test_station_dict = {}
        for index, row in df.groupby(['loc_lon', 'loc_lat']).size().reset_index().iterrows():
            lat_ = row['loc_lat']
            lon_ = row['loc_lon']
            if (lat_, lon_) in test_station_dict:
                continue
            test_station_dict[(lat_, lon_)] = get_station_by_geo(lat_, lon_, train_station_dict)

        df['station'] = df[['loc_lat', 'loc_lon']].dropna().apply(lambda x: test_station_dict[(x.loc_lat, x.loc_lon)],
                                                                  axis=1)

    df.station.fillna('Other_stations', inplace=True)
    return df, train_station_dict


def _calc_traff_stats(df):
    result = {}
    for cluster in df.columns:
        cluster_col = df[cluster]
        result[cluster] = [np.round(cluster_col.min(), decimals=3),
                           np.round(cluster_col.max(), decimals=3),
                           np.round(cluster_col.median(), decimals=3),
                           np.round(cluster_col.mean(), decimals=3),
                           np.round(cluster_col.std(), decimals=3)]

    return result


def _cluster_traffic_by_month(cluster_stats):
    result = {}
    for cluster in cluster_stats['traff_m1']:
        result[cluster] = []
        for i in range(5, 0, -1):
            traff_month = f'traff_m{i}'
            cluster_ = cluster_stats[traff_month][cluster]
            result[cluster].append([cluster_[2], cluster_[3]])

    return result


def calculate_statistics_by_cluster(df, cluster_feature):
    cluster_stats = {}
    for i in range(5, 0, -1):
        col_name = f'traff_m{i}'
        print(f'working on {col_name}')
        traffic_by_cluster_df = df[[cluster_feature, col_name]].pivot(values=col_name, columns=cluster_feature)
        cluster_traffic_statistics = _calc_traff_stats(traffic_by_cluster_df)
        print(f'cluster stats for: {col_name} is complete')
        cluster_stats[col_name] = cluster_traffic_statistics

    cluster_median_trends = {}
    cluster_mean_trends = {}
    cluster_traffic_by_month = _cluster_traffic_by_month(cluster_stats)
    for cluster in cluster_traffic_by_month:
        regr_median_result = linear_regression([1, 2, 3, 4, 5],
                                               [cluster_traffic_by_month[cluster][0][0],
                                                cluster_traffic_by_month[cluster][1][0],
                                                cluster_traffic_by_month[cluster][2][0],
                                                cluster_traffic_by_month[cluster][3][0],
                                                cluster_traffic_by_month[cluster][4][0]])
        cluster_median_trends[cluster] = np.round(regr_median_result[1], decimals=3)

        regr_mean_result = linear_regression([1, 2, 3, 4, 5],
                                             [cluster_traffic_by_month[cluster][0][1],
                                              cluster_traffic_by_month[cluster][1][1],
                                              cluster_traffic_by_month[cluster][2][1],
                                              cluster_traffic_by_month[cluster][3][1],
                                              cluster_traffic_by_month[cluster][4][1]])
        cluster_mean_trends[cluster] = np.round(regr_mean_result[1], decimals=3)

    return cluster_stats, cluster_median_trends, cluster_mean_trends


def apply_cluster_statistics(df, cluster, cluster_median_trends, cluster_mean_trends, cluster_stats):
    df[f'{cluster}_cluster_median_td'] = df[cluster].apply(lambda x: cluster_median_trends[x])
    df[f'{cluster}_cluster_mean_td'] = df[cluster].apply(lambda x: cluster_mean_trends[x])
    df[f'{cluster}_cluster_last_month_min'] = df[cluster].apply(lambda x: cluster_stats['traff_m1'][x][0])
    df[f'{cluster}_cluster_last_month_max'] = df[cluster].apply(lambda x: cluster_stats['traff_m1'][x][1])
    df[f'{cluster}_cluster_last_month_median'] = df[cluster].apply(lambda x: cluster_stats['traff_m1'][x][2])
    df[f'{cluster}_cluster_last_month_mean'] = df[cluster].apply(lambda x: cluster_stats['traff_m1'][x][3])
    df[f'{cluster}_cluster_last_month_std'] = df[cluster].apply(lambda x: cluster_stats['traff_m1'][x][4])