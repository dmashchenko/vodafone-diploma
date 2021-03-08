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


def traffic_parallel_coords(df, max_value=50000, range=[0.8, 1]):
    df = df[df.target < max_value]
    dimensions = []

    for col in ['traff_m5', 'traff_m4', 'traff_m3', 'traff_m2', 'traff_m1', 'target']:
        dimensions.append(dict(range=[0, max_value],
                               tickvals=[0, 20, max_value * 0.5, 120, max_value],
                               label=col, values=df[col]))
        if col == 'target':
            dimensions[-1]['constraintrange'] = [max_value * range[0], max_value * range[1]]

    fig = go.Figure(data=
    go.Parcoords(
        line=dict(color=df['target'],
                  colorscale=px.colors.sequential.Rainbow,
                  showscale=True,
                  cmin=0,
                  cmax=max_value),
        dimensions=list(dimensions)
    )
    )
    # fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
    #                   plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white", size=18, ), width=1100, height=600)
    return fig
