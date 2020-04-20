# This script generates a report of the simulation automatically, with all the important data.

# Importing necessary packages
import dash
import dash_html_components as html
import time
import pandas as pd
import reverse_geocoder as rg
import json

# Initialize the app
app = dash.Dash(__name__)

colors = {
    'bg-head': '#9ae6db',
    'text-head': '#000000',
    'text-body': '#000000',
    'inp-box': '#03034f',
    'font-inpbox': '#FFFFFF'
}
# Reading the relevant user-inputs from the csv files into Pandas dataframes
dfprojectData = pd.read_csv('../inputs/csv_elements/project_data.csv')
dfeconomicData = pd.read_csv('../inputs/csv_elements/economic_data.csv')
dfsimSettíngs = pd.read_csv('../inputs/csv_elements/simulation_settings.csv')

# Obtaining the coordinates of the project location
coordinates = (float(dfprojectData['project_data'][2]), float(dfprojectData['project_data'][3]))

# Determining the location of the project
geoList = rg.search(coordinates)
geoDict = geoList[0]
location = geoDict['name']

dict_projectdata = {'Country': dfprojectData.at[0, 'project_data'],
                    'Project ID': dfprojectData.at[4, 'project_data'],
                    'Scenario ID': dfprojectData.at[6, 'project_data'],
                    'Currency': dfeconomicData.at[0, 'economic_data'],
                    'Project Location': location,
                    'Discount Factor': dfeconomicData.at[1, 'economic_data'],
                    'Tax': dfeconomicData.at[4, 'economic_data']}

df_projectData = pd.DataFrame(list(dict_projectdata.items()), columns=['Label', 'Value'])

dict_simsettings = {'Evaluated period': dfsimSettíngs.at[0, 'simulation_settings'],
                    'Start date': dfsimSettíngs.at[5, 'simulation_settings'],
                    'Timestep length': dfsimSettíngs.at[7, 'simulation_settings']}

df_simsettings = pd.DataFrame(list(dict_simsettings.items()))

projectName = 'Harbor Norway'
scenarioName = '100% self-generation'
releaseDesign = '0.0x'
branchID = 'xcdd5eg004'
simDate = time.strftime("%Y-%m-%d")

# Determining the sectors which were simulated

with open('../MVS_outputs/json_input_processed.json') as f:
    data = json.load(f)
sectors = list(data['project_data']['sectors'].keys())
sec_list = """"""
for sec in sectors:
    sec_list += "\n" + f'\u2022 {sec.upper()}'


# Function that creates a HTML table from a Pandas dataframe
def make_dash_table(df):
    """ Return a dash definition of an HTML table for a Pandas dataframe """
    table = []
    for index, row in df.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append(html.Td([row[i]]))
        table.append(html.Tr(html_row))
    return table


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
        html.Br([]),
        html.Div([html.Span('Scenario name  : ', style={'fontWeight': 'bold'}), f'{scenarioName}']),
    ],
             style={
                 'textAlign': 'left',
                 'fontSize': '40px',
                 'margin': '30px'
             }),

    html.Div(className='blockoftext1', children=[
        html.Div(['The energy system with the ', html.Span(f'{projectName}', style={'fontStyle': 'italic'}),
                  ' for the scenario ', html.Span(f'{scenarioName}',
                                                  style={'fontStyle': 'italic'}),
                  ' was simulated with the Multi-Vector simulation tool MVS 0.0x developed from the E-LAND toolbox '
                  'developed in the scope of the Horizon 2020 European research project. The tool was developed by '
                  'Reiner Lemoine Institute and utilizes the OEMOF framework.'])],

             style={
                 'textAlign': 'justify',
                 'fontSize': '40px',
                 'margin': '30px'
             }
             ),

    html.Br([]),

    html.Div(className='inpdatabox', children=[html.H2('Input Data')],
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
    html.Br([]),

    html.Div(className='heading1', children=[html.H2('Project Data',
                                                     style={
                                                         'textAlign': 'left',
                                                         'margin': '30px',
                                                         'fontSize': '60px',
                                                         'color': '#8c3604',
                                                     }),
                                             html.Hr(
                                                 style={
                                                     'color': '#000000',
                                                     'margin': '30px',
                                                 })]),

    html.Div(className='blockoftext2', children=[html.P('The most important simulation data will be presented below. '
                                                        'Detailed settings, costs, and technological parameters can '
                                                        'be found in the appendix.',
                                                        style={
                                                            'textAlign': 'justify',
                                                            'fontSize': '40px',
                                                            'margin': '30px'
                                                        }
                                                        )]),

    html.Div(
        [
            html.Div([
                html.H4(
                    ['Project Location'], className="projdataheading",
                    style={'position': 'relative',
                           'left': '0',
                           'height': '20%',
                           'borderLeft': '20px solid #8c3604',
                           'background': '#ffffff',
                           'paddingTop': '1px',
                           'paddingBottom': '1px',
                           'paddingLeft': '30px',
                           'paddingRight': '60px',
                           'fontSize': '40px',
                           }),

                html.Img(className='locationimage', src='https://i.imgur.com/lJAwIzc.png', alt='Project location map',
                         title='Project location',
                         style={
                             'align': 'left',

                         })
            ],
                style={
                    'margin': '30px', 'width': '48%'
                }

            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H4(
                                ['Project Data'], className="projdataheading",
                                style={'position': 'relative',
                                       'left': '0',
                                       'height': '20%',
                                       'margin': '0mm',
                                       'borderLeft': '20px solid #8c3604',
                                       'background': '#ffffff',
                                       'paddingTop': '1px',
                                       'paddingBottom': '1px',
                                       'paddingLeft': '30px',
                                       'paddingRight': '60px'
                                       }
                            ),

                            html.Br([]),

                            html.Table(make_dash_table(df_projectData)),
                        ],
                        className="projdata",
                        style={
                            'width': '48%',
                            'margin': '30px',
                            'fontSize': '40px',

                        }
                    )
                ]

            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H4(
                                ['Simulation Settings'], className="projdataheading",
                                style={'position': 'relative',
                                       'left': '0',
                                       'height': '20%',
                                       'margin': '0mm',
                                       'borderLeft': '20px solid #8c3604',
                                       'background': '#ffffff',
                                       'paddingTop': '1px',
                                       'paddingBottom': '1px',
                                       'paddingLeft': '30px',
                                       'paddingRight': '60px'
                                       }
                            ),
                            html.Br([]),
                            html.Table(make_dash_table(df_simsettings))
                        ],
                        className="projdata",
                        style={
                            'width': '48%',
                            'margin': '30px',
                            'fontSize': '40px'}

                    )
                ])
        ]
    ),
    html.Br(),
    html.Div(className='heading1', children=[html.H2('Energy Demand',
                                                     style={
                                                         'textAlign': 'left',
                                                         'margin': '30px',
                                                         'fontSize': '60px',
                                                         'color': '#8c3604',
                                                     }),
                                             html.Hr(
                                                 style={
                                                     'color': '#000000',
                                                     'margin': '30px',
                                                 })]),

    html.Div(className='blockoftext2', children=[html.P('The simulation was performed for the energy system '
                                                        'covering the following sectors:'),
                                                 html.P(f'{sec_list}')
                                                 ],
             style={
                 'textAlign': 'justify',
                 'fontSize': '40px',
                 'margin': '30px'
             })

])

if __name__ == '__main__':
    app.run_server(debug=True)
