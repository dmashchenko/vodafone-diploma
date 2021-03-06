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


def add_city_feature(df, geodf):
    geo_city_dict = {}

    for index, row in df.groupby(['loc_lon', 'loc_lat']).size().reset_index().iterrows():
        lat_ = row['loc_lat']
        lon_ = row['loc_lon']
        geo_city_dict[(lat_, lon_)] = get_city_by_geo(lat_, lon_, geodf)

    df['city'] = df[['loc_lat', 'loc_lon']].dropna().apply(lambda x: geo_city_dict[(x.loc_lat, x.loc_lon)], axis=1)
    df.city.fillna('NoGeo', inplace=True)
    return df
