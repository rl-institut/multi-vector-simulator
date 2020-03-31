"""
This script uses Plotly and Dash to automatically generate reports of the MVS simulation results. 
"""
import dash
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash(__name__)

colors = {
    'bg-head': '#9ae6db',
    'text-head': '#000000',
    'text-body': '#000000'
}

projectName = 'Harbor Norway'
scenarioName = '100% self-generation'

# Header section with logo and the title of the report, and CSS styling. Work in progress...

app.layout = html.Div([

    html.Div(className='header_title_logo',
             children=[html.Img(id='mvslogo', src='https://elandh2020.eu/wp-content/themes/netron/libs/images/logo'
                                                  '/logo-eland-original.svg', width='350px'),
                       html.H1('MULTI VECTOR SIMULATION - REPORT SHEET')],
             style={
                 'textAlign': 'center',
                 'color': colors['text-head'],
                 'borderStyle': 'solid',
                 'borderWidth': 'thin',
                 'padding': '10px',
                 'margin': '20px',
                 'fontSize': '250%'
             }),

    html.Div(className='imp-info', children=[
        html.P('MVS Release: 0.0x'),
        html.P('Branch-id: xcdd5eg004'),
        html.P('Simulation date: DD – MM – 20YY')

        ],
             style={
                 'textAlign': 'right',
                 'padding': '5px',
                 'fontSize': '20px',
                 'margin': '20px'

             }),

    html.Div(className='imp_info2', children=[
        html.P('Project name: '),
        html.P('Scenario name: ')
    ],
             style={
                 'textAlign': 'left',
                 'fontSize': '40px',
                 'margin': '20px'
             }
             )



])


if __name__ == '__main__':
    app.run_server(debug=True)
