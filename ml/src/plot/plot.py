import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import math


def scatter_against_target_fig(df, cols=4, sample=2000):
    plotdf = df.sample(sample)

    columns = plotdf.columns.drop('target')
    features_count = len(columns)
    rows = math.ceil(features_count / cols)
    col_index = _get_col_index_list(cols, rows)
    row_index = np.repeat(list(range(1, rows + 1, 1)), cols)

    result_fig = make_subplots(rows=rows, cols=cols, subplot_titles=columns, shared_yaxes=True)

    for i, feature in zip(range(features_count), columns):
        result_fig.add_trace(
            go.Scatter(x=plotdf[feature], y=plotdf.target, mode='markers'),
            row=row_index[i], col=col_index[i]
        )

    return result_fig


def _get_col_index_list(cols, rows):
    list_to_repeat = list(range(1, cols + 1, 1))
    col_index = []
    for _ in range(rows):
        col_index += list_to_repeat
    return col_index
