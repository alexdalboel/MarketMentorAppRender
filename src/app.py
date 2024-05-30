import dash
from dash import html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from newsapi import NewsApiClient
from googleapiclient.discovery import build
import requests
from datetime import date
import json

#Initializing my two APIs that require keys
newsapi = NewsApiClient(api_key='c57b23e74bb1410fa4bbd751013c38bd')
youtube = build('youtube', 'v3', developerKey='AIzaSyB6iaReakVUQZcdIJwDm9zLjCat0zT-WKU')

#Loading my local faq.json file I made for the FAQ section
with open('faq.json', 'r') as f:
    faq_data = json.load(f)
faq_list = faq_data['faq']

#Loading my local finance_lit_byCountry.json file I made from the OECD data
with open('finance_lit_byCountry.json', 'r') as json_file:
    scores_data = json.load(json_file)

# Create bar plot from finance_lit_byCountry.json to display financial literacy scores by country
bar_plot = dcc.Graph(
    id='financial-literacy-bar-plot',
    figure={
        'data': [
            go.Bar(
                x=list(scores_data.keys()),
                y=list(scores_data.values()),
                marker_color='rgb(64, 210, 255)',
                name='Financial Literacy Scores',
                text=list(scores_data.keys()), 
            )
        ],
        'layout': go.Layout(
            title='Financial Literacy Scores by Country',
            xaxis={'title': 'Country or Economy', 'tickvals': [], 'ticktext': []},
            yaxis={'title': 'Scores financial literacy'},
            margin={'l': 40, 'b': 40, 't': 50, 'r': 10},
            height=350,
            hovermode='closest'
        )
    }
)

#Function for YouTube API call to make my html.Iframe elements 
def get_initial_videos():
    request = youtube.search().list(
        q='Learn about the stock market',
        part='snippet',
        type='video',
        maxResults=7
    )
    response = request.execute()

    videos_list = []
    for item in response['items']:
        video_title = item['snippet']['title']
        video_url = f"https://www.youtube.com/embed/{item['id']['videoId']}"
        video_item = html.Div([
            html.H5(video_title),
            html.Iframe(src=video_url, width="100%", height="236", style={'border': 'none'})
        ])
        videos_list.append(video_item)

    return html.Div(videos_list, style={'height': '400px', 'overflowY': 'auto'})

#Function for Open Library API call to get my book data used for table in 'Learn More' tab
def get_stock_trading_books():
    #The url where I specify which title words I'm searching for and setting the response limit = 7
    url = "http://openlibrary.org/search.json?q=learn+stock+trading+investing&limit=7"
    response = requests.get(url)
    if response.status_code == 200:
        books_data = response.json()
        books = []
        for work in books_data.get("docs", []):
            title = work.get("title", "Title not available")
            authors = ", ".join(work.get("author_name", ["Author not available"]))
            published_date = work.get("first_publish_year", "Publication year not available")
            books.append({"Title": title, "Authors": authors, "Published Date": published_date})
        return books
    else:
        return []


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR])
server = app.server
app.title = "MarketMentor"


#Welcome tab
tab1_content = dbc.Row(
    [
        dbc.Col(
            html.Div(
                [
                    html.P("Welcome to MarketMentor. This is a dashboard style web application which is designed \
                       to help you learn about the stock market. Navigating through the menu above, you'll \
                       be able to learn about:"),
                    html.H6("- Basic terminology"),
                    html.H6("- Stock price movement"),
                    html.H6("- Stock market news"),
                    html.H6("- Calculating simulated loss/gain"),
                    html.P("To your right you'll notice a barplot made from OECD data on financial \
                           literacy in different countries. The aim of MarketMentor is to make \
                           a small part of financial learning accessible to you and \
                           help facilitate your journey towards financial literacy. Happy exploring!")
                ],
                style={"margin": "20px"}
            ),
            width=5,
            lg=5
        ),
        dbc.Col(
            [
                bar_plot,
                html.P("Source: https://www.oecd.org/financial/education/international-survey-of-adult-financial-literacy-2023.htm")
            ],
            width=7,
            lg=7
        )
    ],
    justify="center",
    style={"margin": "20px"}
)

#Stock movement tab (graph + news)
tab2_content = html.Div(
    [
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        dbc.Button(
                            html.H6("What am I looking at?"),
                            id="collapse-button",
                            class_name="mb-3 mx-2",
                            color="primary",
                            n_clicks=0,
                        ),
                        dbc.Collapse(
                            dbc.Card(dbc.CardBody("On this page you'll find the price movement \
                                                  of a stock by entering the stock ticker in the input \
                                                  form. A stock ticker is a abbreviation or identifier for \
                                                  a company. Try to look up TSLA (Tesla) or \
                                                  GME (Gamestop). You'll see the closing price for \
                                                  that stock for the last two weeks and the news \
                                                  associated with that stock. The stock price goes up \
                                                  and down, but why? Try to look at the news and see \
                                                  if you can spot any negative news that would make \
                                                  the price drop or good news that would make it go up. \
                                                  The idea is to buy stock at a low price, and sell higher.")),
                            id="collapse",
                            is_open=False,
                        ),
                    ],
                    style={'textAlign': 'center', "margin": "10px"}
                ),
                width="auto",
            ),
            justify="center",
            align="center",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.H4("Stock price movement"),
                            dcc.Input(
                                id='stock-input',
                                type='text',
                                placeholder='Enter stock ticker',
                                style={
                                    'marginBottom': '10px',
                                    'textAlign': 'center',
                                    'width': '100%',
                                }
                            ),
                            html.Div(
                                dcc.Graph(id='stock-graph'),
                                style={'width': '100%', 'height': '40%'}
                            ),
                        ],
                        style={
                            'display': 'flex',
                            'flexDirection': 'column',
                            'justifyContent': 'center',
                            'alignItems': 'center',
                        }
                    ),
                    width=12,
                    lg=7
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.H4("Latest news related to your stock", style={'textAlign': 'center'}),
                            html.Div(id='news-titles')
                        ]
                    ),
                    width=12,
                    lg=5
                )
            ]
        )
    ]
)

#Simulate investment calculator
tab3_content = html.Div([
    dbc.Row(
        dbc.Col(
            html.Div(
                [
                    dbc.Button(
                        html.H6("What is this?"),
                        id="collapse-button-2",
                        class_name="mb-3 mx-2",
                        color="primary",
                        n_clicks=0,
                    ),
                    dbc.Collapse(
                        dbc.Card(dbc.CardBody("This a stock investment calculator. Put in a stock ticker (example: AAPL), \
                                              and choose a buy date and sell date. Remember, the market is closed on weekends. \
                                              You'll be able to see the potential gain/loss if you had purchased \
                                              the chosen amount of stock these dates. You'll also see some additional \
                                              price information for those two dates, in the infoboxes.")),
                        id="collapse-2",
                        is_open=False,
                    ),
                ],
                style={'textAlign': 'center', "margin": "10px"}
            ),
            width="auto",
        ),
        justify="center",
        align="center",
    ),
    dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H4("Stock Investment Calculator", style={'margin-top':'10px'}),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Input(
                                            id='calc-stock-input',
                                            type='text',
                                            placeholder='Enter stock ticker',
                                            style={'margin': '10px', 'width': '100%'}
                                        ),
                                        width=12,
                                        lg=6
                                    ),
                                    dbc.Col(
                                        dcc.Input(
                                            id='calc-amount-input',
                                            type='number',
                                            placeholder='Amount of shares bought',
                                            style={'margin': '10px', 'width': '100%'}
                                        ),
                                        width=12,
                                        lg=6
                                    ),
                                ],
                                justify="center",
                                align="center",
                                style={'marginBottom': '20px'}
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.DatePickerSingle(
                                            id='calc-buy-date-input',
                                            placeholder='Buy date',
                                            style={'width': '100%'}
                                        ),
                                        width=12,
                                        lg=6
                                    ),
                                    dbc.Col(
                                        dcc.DatePickerSingle(
                                            id='calc-sell-date-input',
                                            placeholder='Sell date',
                                            max_date_allowed=date.today(),
                                            style={'width': '100%'}
                                        ),
                                        width=12,
                                        lg=6
                                    ),
                                ],
                                justify="center",
                                align="center",
                                style={'marginBottom': '20px'}
                            ),
                            dbc.Button(
                                "Calculate Profit/Loss",
                                id='calc-button',
                                color='primary',
                                className='mb-3'
                            ),
                            html.Div(id='calc-result', style={'marginTop': '20px'})
                        ],
                        style={'textAlign': 'center'}
                    ),
                    style={'margin': '20px'}
                ),
                width=12,
                lg=6
            ),
            dbc.Col(
                [
                    dbc.Card(
                        [
                            dbc.CardHeader(html.H4("Buy Date Infobox")),
                            dbc.CardBody(id='buy-info')
                        ],
                        style={'margin': '20px'}
                    ),
                    dbc.Card(
                        [
                            dbc.CardHeader(html.H4("Sell Date Infobox")),
                            dbc.CardBody(id='sell-info')
                        ],
                        style={'margin': '20px'}
                    ),
                ],
                width=12,
                lg=6
            ),
        ],
        justify="center"
    )
])

#Learn more tab (YouTube videos and books)
tab4_content = html.Div(
    [
    dbc.Row(
        dbc.Col(
            html.Div(
                [
                    dbc.Button(
                        html.H6("Learn more on your own"),
                        id="collapse-button-3",
                        class_name="mb-3 mx-2",
                        color="primary",
                        n_clicks=0,
                    ),
                    dbc.Collapse(
                        dbc.Card(dbc.CardBody("Lucky for you, the internet is filled with \
                                              free knowledge that you can use for your stock market learning. \
                                              Here's some content MarketMentor has found for you!")),
                        id="collapse-3",
                        is_open=False,
                    ),
                ],
                style={'textAlign': 'center', "margin": "10px"}
            ),
            width="auto",
        ),
        justify="center",
        align="center",
    ),

    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        html.H4("Learn from videos", style={'margin-top':'10px'}),
                        get_initial_videos()
                    ],
                    style={
                        'padding':'10px',
                        'height':'90%',
                        'overflowY':'scroll'                    
                    }
                ),
                width=12,
                lg=5
            ),
            dbc.Col(
                html.Div(
                    [
                        html.H4("Stock Trading Books", style={'margin-top':'10px'}),
                        dash_table.DataTable(
                            id='stock-books-table',
                            columns=[
                                {"name": "Title", "id": "Title"},
                                {"name": "Authors", "id": "Authors"},
                                {"name": "Published Date", "id": "Published Date"}
                            ],
                            data=get_stock_trading_books(),
                            style_cell={
                                'whiteSpace': 'normal',
                                'height': 'auto',
                                'minWidth': '0px',
                                'width': 'auto',
                                'maxWidth': '200px',
                            },
                            style_table={'margin':'20px'}
                        )
                    ],
                    style={'margin':'20px'}
                ),
                width=12,
                lg=6
                
            )
        ]
    )
    ]
)

#Frequently Asked Questions (FAQ) tab
tab5_content = html.Div(
    dbc.Container(
        dbc.Row(
            dbc.Col(
                dash_table.DataTable(
                    id='faq-table',
                    columns=[
                        {"name": "Question", "id": "question"},
                        {"name": "Answer", "id": "answer"}
                    ],
                    data=faq_list,
                    style_table={'width': '100%'},
                    style_cell={
                        'textAlign': 'left', 
                        'padding': '5px', 
                        'whiteSpace': 'normal',  
                        'height': 'auto'  
                    },
                    style_header={
                        'backgroundColor': 'lightgrey', 
                        'fontWeight': 'bold'
                    }
                ),
                width={"size": 8, "offset": 2}  
            )
        ),
        fluid=True  
    ),
    style={'paddingTop': '20px', 'paddingBottom': '20px'}
)

#Organizing the different tab contents in the app layout
app.layout = html.Div(
    [
        dbc.Navbar(
            dbc.Container(
                [
                    dbc.Row(
                        [
                            
                            dbc.Col(
                                html.Div(
                                    [
                                        html.H2(
                                            "MarketMentor",
                                            style={'color': 'grey', 'margin-bottom': '0'}
                                        ),
                                        html.H6(
                                            "Your stock info dashboard!",
                                            style={'color': 'grey', 'margin-top': '0'}
                                        )
                                    ],
                                    style={'display': 'flex', 'flex-direction': 'column', 'justify-content': 'center'}
                                ),
                                width="auto"
                            ),
                        ],
                        align="center",
                        className="g-0",
                        justify="center"
                    ),
                ],
                fluid=True,
            ),
        ),
        dbc.Tabs(
            [
                dbc.Tab(tab1_content, label="Welcome"),
                dbc.Tab(tab5_content, label="FAQ"),
                dbc.Tab(tab2_content, label="Stock movement"),
                dbc.Tab(tab3_content, label="Stock potential"),
                dbc.Tab(tab4_content, label="Learn more"),
            ]
        )
    ]
)

#Callback function for button collapse
@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

#Callback function for button collapse
@app.callback(
    Output("collapse-2", "is_open"),
    [Input("collapse-button-2", "n_clicks")],
    [State("collapse-2", "is_open")],
)
def toggle_collapse_2(n, is_open):
    if n:
        return not is_open
    return is_open

#Callback function for button collapse
@app.callback(
    Output("collapse-3", "is_open"),
    [Input("collapse-button-3", "n_clicks")],
    [State("collapse-3", "is_open")],
)
def toggle_collapse_3(n, is_open):
    if n:
        return not is_open
    return is_open

#Callback function for creating and changing graph based on user input (Yahoo finance API)
@app.callback(
    Output('stock-graph', 'figure'),
    [Input('stock-input', 'value')]
)
def update_graph(ticker):
    if not ticker:
        return go.Figure()

    try:
        stock_data = yf.download(ticker, period='14d')
        print(stock_data.index)
    except KeyError:
        return go.Figure(go.Scatter(), layout={'title': f'Stock Data for {ticker} Not Found'})

    fig = go.Figure()

    # Add closing price data
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'], 
                             mode='lines+markers', name='Close Price'))

    # Add opening price data
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Open'], 
                             mode='lines+markers', name='Open Price', line=dict(color='red')))

    fig.update_layout(
        title=f'Closing and Opening Prices for {ticker.upper()} (Last 14 Days)',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        xaxis=dict(
            tickformat='%d-%m-%Y',
            dtick='D1',
            tickangle=30
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig

#Callback function to change displayed news based on user input (same input as graph) (News API)
@app.callback(
    Output('news-titles', 'children'),
    [Input('stock-input', 'value')]
)
def update_news(ticker):
    if not ticker:
        return html.Div()

    articles = newsapi.get_everything(q=ticker, language='en', sort_by='publishedAt', page_size=7)
    news_list = []
    for article in articles['articles']:
        title = article['title']
        source = article['source']['name']
        snippet = article['description']
        url = article['url']
        news_item = html.Div([
            html.H5(title),
            html.P(f"Source: {source}"),
            html.P(snippet),
            html.A("Read More", href=url, target='_blank')
        ])
        news_list.append(news_item)

    return html.Div(news_list, style={'overflowY': 'scroll', 'height': '400px'})

#Callback function to use Yahoo finance to fetch prices, and do some simple calculations
#as well as displaying some general information about the input stock.
@app.callback(
    [Output('calc-result', 'children'),
     Output('buy-info', 'children'),
     Output('sell-info', 'children')],
    [Input('calc-button', 'n_clicks')],
    [State('calc-stock-input', 'value'), State('calc-amount-input', 'value'),
     State('calc-buy-date-input', 'date'), State('calc-sell-date-input', 'date')]
)
def calculate_profit_loss(n_clicks, ticker, amount, buy_date, sell_date):
    if not (ticker and amount and buy_date and sell_date):
        return "Please provide all inputs.", None, None

    try:
        stock_data = yf.download(ticker, start=buy_date, end=sell_date)
        
        buy_date = pd.to_datetime(buy_date)
        sell_date = pd.to_datetime(sell_date)
        
        buy_date_available = stock_data.index.asof(buy_date)
        sell_date_available = stock_data.index.asof(sell_date)

        if pd.isna(buy_date_available):
            return f"Buy date {buy_date.date()} is not available in the stock data.", None, None
        if pd.isna(sell_date_available):
            return f"Sell date {sell_date.date()} is not available in the stock data.", None, None

        buy_info = stock_data.loc[buy_date_available]
        sell_info = stock_data.loc[sell_date_available]

    except Exception as e:
        return f"Error fetching data for {ticker}: {e}", None, None

    profit_loss = (sell_info['Close'] - buy_info['Close']) * amount
    result = f"Profit/Loss: ${profit_loss:.2f}"

    # Buy Date Information
    buy_info_card = [
        html.Div([
            html.Div(f"Open Price: ${buy_info['Open']:.2f}", style={'float': 'left', 'width': '50%'}),
            html.Div(f"Lowest Price: ${buy_info['Low']:.2f}", style={'float': 'right', 'width': '50%'})
        ]),
        html.Div([
            html.Div(f"Close Price: ${buy_info['Close']:.2f}", style={'float': 'left', 'width': '50%'}),
            html.Div(f"Highest Price: ${buy_info['High']:.2f}", style={'float': 'right', 'width': '50%'})
        ])
    ]

    # Sell Date Information
    sell_info_card = [
        html.Div([
            html.Div(f"Open Price: ${sell_info['Open']:.2f}", style={'float': 'left', 'width': '50%'}),
            html.Div(f"Lowest Price: ${sell_info['Low']:.2f}", style={'float': 'right', 'width': '50%'})
        ]),
        html.Div([
            html.Div(f"Close Price: ${sell_info['Close']:.2f}", style={'float': 'left', 'width': '50%'}),
            html.Div(f"Highest Price: ${sell_info['High']:.2f}", style={'float': 'right', 'width': '50%'})
        ])
    ]

    return result, buy_info_card, sell_info_card

if __name__ == "__main__":
    app.run_server(debug=False)
