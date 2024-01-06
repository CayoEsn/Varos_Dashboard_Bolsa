import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import requests
from bs4 import BeautifulSoup
import yfinance as yf

external_stylesheets = [dbc.themes.BOOTSTRAP, 'assets/style.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = dbc.Container(fluid=True, children=[
    dbc.Row([
        dbc.Col([
            dbc.Col([
                dcc.Dropdown(
                    id='dropdown',
                    options=[
                        {'label': 'WEGE3', 'value': 'WEGE3'},
                        {'label': 'PETR4', 'value': 'PETR4'},
                        {'label': 'CEAB3', 'value': 'CEAB3'},
                    ],
                    value='PETR4',
                    className='dropdown-stocks'
                ), html.Div(id='output-div')
            ]),
            dbc.Col([
                dcc.Graph(id='grafico-candlestick', style={'display': 'none'}),
            ]),
        ], width=6, style={'marginTop': '200px'}),
        dbc.Col([
            html.H2('Notícias', className='text-center',
                    style={'fontSize': 'calc(1.425rem + 2.1vw)'}),

            html.Div(id='noticias')
        ], width=6, style={'marginTop': '140px'}),
    ]),
], style={'height': '100vh', 'padding': '25px 25px 0px', 'backgroundColor': 'rgb(19, 21, 22)', 'width': '100%', 'color': 'white', 'fontFamily': 'Lato,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol"'})


@app.callback(
    Output('noticias', 'children'),
    [Input('dropdown', 'value')]
)
def update_output(selected_option):
    elementos_noticias = []

    if (selected_option):
        url = f'https://braziljournal.com/?s={selected_option.lower()}'
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            allnews_element = soup.find(class_='allnews-list')

            if allnews_element:
                divs = allnews_element.find_all(['div'])

                for element in divs:
                    titulo = element.find_all('p')[0].text.strip()
                    subtitulo = element.find_all('h2')[0].text.strip()
                    link = element.find_all('a')[1]['href']

                    div = html.Div([
                        dcc.Link([
                            html.H3(titulo, style={
                                    'color': '#B0B7BE', 'fontSize': '16px', 'fontWeight': '500'}),
                            html.H5(subtitulo, style={
                                    'color': '#F2F4F8', 'fontSize': '24px', 'fontWeight': '700'})
                        ], href=link, target='_blank', style={'textDecoration': 'none'})
                    ], style={'margin': '30px 0px'})

                    elementos_noticias.append(div)
        else:
            print(
                f'Erro ao fazer a solicitação. Código de status: {response.status_code}')

    return elementos_noticias


@app.callback(
    Output('grafico-candlestick', 'figure'),
    Output('grafico-candlestick', 'style'),
    [Input('dropdown', 'value')]
)
def grafico_candlestick(selected_option):
    if (selected_option):
        dados = yf.download(selected_option + '.SA', period='1y')

        if dados is not None and not dados.empty:
            figura = go.Figure(data=[go.Candlestick(x=dados.index,
                                                    open=dados['Open'],
                                                    high=dados['High'],
                                                    low=dados['Low'],
                                                    close=dados['Close'])])
            figura.update_layout(
                paper_bgcolor='rgb(19, 21, 22)',
                plot_bgcolor='rgb(19, 21, 22)',
                font=dict(color='white'),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False, dtick=2),
                xaxis_rangeslider=dict(visible=False),
            )
            return figura, ({'display': 'block'})
        else:
            return go.Figure()
    else:
        return go.Figure()


if __name__ == '__main__':
    app.run_server(debug=True)
