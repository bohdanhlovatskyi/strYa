import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app
from app import server

# Connect to your app pages
from apps import simple_examples, real_life
# from apps import

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dcc.Link('Simple examples|', href='/apps/simple_examples'),
        dcc.Link('Real life', href='/apps/real_life'),
    ], className="row"),
    html.Div(id='page-content', children=[])
], style={"background": 'white'})


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/simple_examples':
        return simple_examples.layout
    if pathname == '/apps/real_life':
        return real_life.layout
    else:
        return simple_examples.layout


if __name__ == '__main__':
    app.run_server(debug=True)
