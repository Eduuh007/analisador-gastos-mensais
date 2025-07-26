import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px

app = dash.Dash(__name__)
app.title = "Analisador de Gastos Mensais"

app.layout = html.Div([
    html.H1("Analisador de Gastos Mensais", style={'textAlign': 'center'}),

    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Arraste ou selecione um arquivo CSV'
        ]),
        style={
            'width': '100%',
            'height': '80px',
            'lineHeight': '80px',
            'borderWidth': '2px',
            'borderStyle': 'dashed',
            'borderRadius': '10px',
            'textAlign': 'center',
            'margin': '20px'
        },
        multiple=False
    ),

    html.Div(id='output-data-upload')
])

def parse_contents(contents, filename):
    import base64
    import io

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        else:
            return html.Div(['Formato de arquivo não suportado. Envie um CSV.'])
    except Exception as e:
        return html.Div([f'Ocorreu um erro ao processar o arquivo: {e}'])

    # Conversão de data, se possível
    if 'Data' in df.columns:
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')

    # Gráfico por categoria
    if 'Categoria' in df.columns and 'Valor' in df.columns:
        fig = px.pie(df, names='Categoria', values='Valor', title='Distribuição de Gastos por Categoria')
    else:
        fig = None

    return html.Div([
        html.H5(filename),
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_table={'overflowX': 'auto'},
            page_size=10,
            style_cell={'textAlign': 'left'}
        ),
        html.Br(),
        html.Div([
            dcc.Graph(figure=fig) if fig else html.Div('Colunas "Categoria" e "Valor" não encontradas.')
        ])
    ])

@app.callback(
    Output('output-data-upload', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_output(contents, filename):
    if contents is not None:
        return parse_contents(contents, filename)
    return None

if __name__ == '__main__':
    app.run(debug=True)

