import dash
import dash_html_components as html

app = dash.Dash(__name__)

colors = {
    'bg-head': '#9ae6db',
    'text-head': '#000000',
    'text-body': '#000000',
    'inp-box': '#03034f',
    'font-inpbox': '#FFFFFF'
}

projectName = 'Harbor Norway'
scenarioName = '100% self-generation'
releaseDesign = '0.0x'
branchID = 'xcdd5eg004'
simDate = 'DD – MM – 20YY'

# Header section with logo and the title of the report, and CSS styling. Work in progress...

app.layout = html.Div([

    html.Div(className='header_title_logo',
             children=[html.Img(id='mvslogo', src='https://elandh2020.eu/wp-content/themes/netron/libs/images/logo'
                                                  '/logo-eland-original.svg', width='370px'),
                       html.H1('MULTI VECTOR SIMULATION - REPORT SHEET')],
             style={
                 'textAlign': 'center',
                 'color': colors['text-head'],
                 'borderStyle': 'solid',
                 'borderWidth': 'thin',
                 'padding': '10px',
                 'margin': '30px',
                 'fontSize': '225%'
             }),

    html.Div(className='imp-info', children=[
        html.P(f"MVS Release: {releaseDesign}"),
        html.P(f"Branch-id: {branchID}"),
        html.P(f"Simulation date: {simDate}")

    ],
             style={
                 'textAlign': 'right',
                 'padding': '5px',
                 'fontSize': '22px',
                 'margin': '30px'

             }),

    html.Div(className='imp_info2', children=[
        html.Div([html.Span('Project name   : ', style={'fontWeight': 'bold'}), f'{projectName}']),
        html.P(''),
        html.Div([html.Span('Scenario name  : ', style={'fontWeight': 'bold'}), f'{scenarioName}']),
    ],
             style={
                 'textAlign': 'left',
                 'fontSize': '40px',
                 'margin': '30px'
             }),

    html.Div(className='blockoftext1', children=[
        html.Div(['The energy system with the ', html.Span(f'{projectName}', style={'fontStyle': 'italic'}),
                  ' for the scenario ', html.Span(f'{scenarioName}', style={'fontStyle': 'italic'}), ' was simulated '
                                                                                                     'with the '
                                                                                                     'Multi-Vector '
                                                                                                     'simulation tool '
                                                                                                     'MVS 0.0x '
                                                                                                     'developed from '
                                                                                                     'the E-LAND '
                                                                                                     'toolbox '
                                                                                                     'developed in '
                                                                                                     'the scope of '
                                                                                                     'the Horizon '
                                                                                                     '2020 '
                                                                                                     'European '
                                                                                                     'research '
                                                                                                     'project. The '
                                                                                                     'tool was '
                                                                                                     'developed by '
                                                                                                     'Reiner Lemoine '
                                                                                                     'Institute and '
                                                                                                     'utilizes the '
                                                                                                     'OEMOF '
                                                                                                     'framework.'])],

             style={
                 'textAlign': 'justify',
                 'fontSize': '40px',
                 'margin': '30px'
             }
             ),

    html.Br(),

    html.Div(className='inpdatabox', children=[html.H2('INPUT DATA')],
             style={
                 'textAlign': 'center',
                 'borderStyle': 'solid',
                 'borderWidth': 'thin',
                 'padding': '0.5px',
                 'margin': '30px',
                 'fontSize': '250%',
                 'width': '3000px',
                 'margin-left': 'auto',
                 'margin-right': 'auto',
                 'background': colors['inp-box'],
                 'color': colors['font-inpbox'],
                 'verticalAlign': 'middle'

             }),
    html.Br(),
    html.Div()

])
if __name__ == '__main__':
    app.run_server(debug=True)
