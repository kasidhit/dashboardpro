from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc


df_trend = pd.read_csv('dataproject/df_trend.csv')
df_s = pd.read_csv('dataproject/df_s.csv')
df_all_order_week = pd.read_csv('dataproject/df_all_order_week.csv')
df_all_order_month = pd.read_csv('dataproject/df_all_order_month.csv')
df_all_order_day = pd.read_csv('dataproject/df_all_order_day.csv')
df_all_discountday = pd.read_csv('dataproject/df_all_discountday.csv')



# Create the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.LUMEN, dbc.icons.FONT_AWESOME])
server = app.server

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("HomeHuk Dashboard", className="text-xl-center bg-info text-white"))
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='trendline-dropdown',
                         options=['Shopee', 'Lazada', 'Shopee & Lazada'],
                         value='Shopee'),
            dcc.RadioItems(id='data-radio',
                           options={
                               'order_volume': 'Order Volume',
                               'sum_purchased': 'Trend Line'
                           },
                           value='order_volume',
                           inline=True),
            dcc.Graph(id='price-graph', figure={})
        ], width={'size': 7}),
        dbc.Col([
            dcc.Dropdown(id='graph-dropdown', options=['distribution of the amount in each canceled order',
                                                       'fail_top3'],
                         value='distribution of the amount in each canceled order'),
            dcc.Dropdown(id='year-dropdown', options=[2020, 2021, 2022, 'all'],
                         value=2022),
            dcc.Dropdown(id='month-dropdown', options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 'all'],
                         value=1),
            dcc.RadioItems(id='datas-radio',
                           options={
                               'high': 'high',
                               'mid-high': 'mid-high',
                               'mid-low': 'mid-low',
                               'low': 'low'
                           },
                           value='mid-hight'),
            dcc.Graph(id='fail-graph', figure={})
        ], width={'size': 5})
    ]),
    dbc.Row([
        dbc.Col([dcc.Dropdown(id='channel-salesby', options=['Shopee', 'Lazada'],
                              value='Shopee')], width={'size': 3}),
        dbc.Col([dcc.Dropdown(id='year-salesby', options=[2020, 2021, 2022],
                              value=2020)], width={'size': 3})
    ]),
    dbc.Row([
        dbc.Col([dcc.Graph(id='sales-by-weekday', figure={})], width={'size': 4}),
        dbc.Col([dcc.Graph(id='sales-by-day', figure={})], width={'size': 4}),
        dbc.Col([dcc.Graph(id='sales-by-month', figure={})], width={'size': 4})

    ])
])


# Set up the callback function
@app.callback(
    Output(component_id='price-graph', component_property='figure'),
    Input(component_id='trendline-dropdown', component_property='value'),
    Input('data-radio', 'value')
)
def update_graph(selected_channel, select_data):
    filtered_trendline = df_trend[df_trend['channel_id'] == selected_channel]
    if selected_channel != 'Shopee & Lazada':
        line_fig = px.line(filtered_trendline,
                           x='YMD', y=select_data,
                           color='channel_id',
                           color_discrete_map={'Shopee': 'orange',
                                               'Lazada': 'royalblue'},
                           template="simple_white",
                           title=f'{select_data} in {selected_channel}')
    else:
        line_fig = px.line(df_trend,
                           x='YMD', y=select_data,
                           color='channel_id',
                           color_discrete_map={'Shopee': 'orange',
                                               'Lazada': 'royalblue'},
                           template="simple_white",
                           title=f'{select_data} in {selected_channel}')

    # line_fig.update_layout(margin={'l': 20, 'b': 30, 't': 10, 'r': 10}, hovermode='closest')
    line_fig.update_traces(mode="lines", hovertemplate=None)
    line_fig.update_layout(hovermode="x unified")
    return line_fig


@app.callback(
    Output(component_id='fail-graph', component_property='figure'),
    Input(component_id='graph-dropdown', component_property='value'),
    Input(component_id='year-dropdown', component_property='value'),
    Input(component_id='month-dropdown', component_property='value'),
    Input('datas-radio', 'value')
)
def update_graph(select_graph, selected_year, select_month, select_cat):
    if select_graph == 'distribution of the amount in each canceled order':
        if (selected_year == 'all') & (select_month == 'all'):
            df = df_s
        elif (selected_year == 'all') & (select_month != 'all'):
            df = df_s.query("month == @select_month")
        elif (selected_year != 'all') & (select_month == 'all'):
            df = df_s.query("year == @selected_year")
        elif (selected_year != 'all') & (select_month != 'all'):
            df = df_s.query("year == @selected_year").query("month == @select_month")

        fig = px.pie(df, values='Order_fail', names='price_cat',
                     title='distribution of the amount in each canceled order.'
                     )
        fig.update_traces(textposition='inside', textinfo='percent+label')
    else:
        if (selected_year == 'all') & (select_month == 'all'):
            df = df_s.query("price_cat == @select_cat")
        elif (selected_year == 'all') & (select_month != 'all'):
            df = df_s.query("month == @select_month").query("price_cat == @select_cat")
        elif (selected_year != 'all') & (select_month == 'all'):
            df = df_s.query("year == @selected_year").query("price_cat == @select_cat")
        elif (selected_year != 'all') & (select_month != 'all'):
            df = df_s.query("year == @selected_year").query("month == @select_month").query("price_cat == @select_cat")

        df2 = df[df['Order_fail'] > 50].sort_values('percent_fail', ascending=False).head(3)
        if df2.empty:
            df2 = df[df['Order_fail'] > 10].sort_values('percent_fail', ascending=False).head(3)
        # df['item_namenew'] = df['item_name'].apply(lambda x: x[12:x.index(' ',25)])
        fig = px.bar(df2, x="item_id", y="Order_fail", hover_data=['item_name', 'percent_fail'],
                     color='channel_id',
                     height=400,
                     template="simple_white")

    return fig


@app.callback(
    Output(component_id='sales-by-weekday', component_property='figure'),
    Input(component_id='channel-salesby', component_property='value'),
    Input(component_id='year-salesby', component_property='value'),
)
def update_graph(channel_salesby, year_salesby):
    df = df_all_order_week.query("channel_id == @channel_salesby").query("year == @year_salesby")
    fig = px.line(df, x='weekday', y='order_volume', color='year',
                  color_discrete_map={2020: 'orange', 2021: 'royalblue', 2022: 'pink'},
                  template="simple_white",
                  height=270)

    return fig


@app.callback(
    Output(component_id='sales-by-day', component_property='figure'),
    Input(component_id='channel-salesby', component_property='value'),
    Input(component_id='year-salesby', component_property='value'),
)
def update_graph(channel_salesby, year_salesby):
    df = df_all_order_day.query("channel_id == @channel_salesby").query("year == @year_salesby")
    fig = px.line(df, x='day', y='order_volume', color='year',
                  color_discrete_map={2020: 'orange', 2021: 'royalblue', 2022: 'pink'},
                  template="simple_white",
                  height=270)

    return fig


@app.callback(
    Output(component_id='sales-by-month', component_property='figure'),
    Input(component_id='channel-salesby', component_property='value'),
    Input(component_id='year-salesby', component_property='value'),
)
def update_graph(channel_salesby, year_salesby):
    df = df_all_order_month.query("channel_id == @channel_salesby").query("year == @year_salesby")
    fig = px.line(df, x='month', y='order_volume', color='year',
                  color_discrete_map={2020: 'orange', 2021: 'royalblue', 2022: 'pink'},
                  template="simple_white",
                  height=270)

    return fig


if __name__=='__main__':
    app.run(debug=True)