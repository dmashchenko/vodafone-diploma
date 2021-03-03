from sklearn.cluster import KMeans

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
