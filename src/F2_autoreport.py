# This script generates a report of the simulation automatically, with all the important data.

# Importing necessary packages
import dash
import dash_html_components as html
import time
import pandas as pd
import reverse_geocoder as rg
import json
import dash_table
import base64

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

# Determining the geographical location of the project
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

df_simsettings = pd.DataFrame(list(dict_simsettings.items()), columns=['Setting', 'Value'])

projectName = 'Harbor Norway'
scenarioName = '100% self-generation'
releaseDesign = '0.0x'
branchID = 'xcdd5eg004'
simDate = time.strftime("%Y-%m-%d")

# Reading images

pv_dem_ts = base64.b64encode(open('../MVS_outputs/input_timeseries_Habor_kW.png', 'rb').read())
pv_inp_ts = base64.b64encode(open('../MVS_outputs/input_timeseries_PV plant (mono)_kW.png', 'rb').read())
el_flows_14 = base64.b64encode(open('../MVS_outputs/Electricity_flows_14_days.png', 'rb').read())
el_flows_365 = base64.b64encode(open('../MVS_outputs/Electricity_flows_365_days.png', 'rb').read())
op_add_caps = base64.b64encode(open('../MVS_outputs/optimal_additional_capacities.png', 'rb').read())
pv_inv_flow = base64.b64encode(open('../MVS_outputs/PV plant (mono) bus flows.png', 'rb').read())

# Determining the sectors which were simulated

with open('../MVS_outputs/json_input_processed.json') as f:
    data = json.load(f)
sectors = list(data['project_data']['sectors'].keys())
sec_list = """"""
for sec in sectors:
    sec_list += "\n" + f'\u2022 {sec.upper()}'

# Creating a dataframe for the demands
with open('../MVS_outputs/json_with_results.json') as gf:
    data1 = json.load(gf)

demands = data1['energyConsumption']

del demands['DSO_feedin']
del demands['Electricity excess']

dem_keys = list(demands.keys())

demand_data = {}

for dem in dem_keys:
    demand_data.update({dem: [demands[dem]['timeseries_peak']["value"],
                              demands[dem]['timeseries_average']["value"],
                              demands[dem]['timeseries_total']["value"]]})

df_dem = pd.DataFrame.from_dict(demand_data, orient='index',
                                columns=['Peak Demand (kW)', 'Mean Demand (kW)', 'Total Demand per annum (kW)'])
df_dem.index.name = 'Demands'
df_dem = df_dem.reset_index()
df_dem = df_dem.round(2)

# Creating a DF for the components table

with open('../MVS_outputs/json_input_processed.json') as bf:
    data2 = json.load(bf)

components1 = data2['energyProduction']
components2 = data2['energyConversion']

del components1['DSO_consumption_period_1']
del components1['DSO_consumption_period_2']

comp1_keys = list(components1.keys())
comp2_keys = list(components2.keys())

components = {}

for comps in comp1_keys:
    components.update({comps: [components1[comps]['type_oemof'],
                               components1[comps]['installedCap']['value'],
                               components1[comps]['optimizeCap']['value']]})
for comps in comp2_keys:
    components.update({comps: [components2[comps]['type_oemof'],
                               components2[comps]['installedCap']['value'],
                               components2[comps]['optimizeCap']['value']]})

df_comp = pd.DataFrame.from_dict(components, orient='index',
                                 columns=['Type of Component', 'Installed Capcity', 'Optimization'])
df_comp.index.name = 'Component'
df_comp = df_comp.reset_index()

for i in range(len(df_comp)):
    if df_comp.at[i, 'Optimization']:
        df_comp.iloc[i, df_comp.columns.get_loc('Optimization')] = 'Yes'
    else:
        df_comp.iloc[i, df_comp.columns.get_loc('Optimization')] = 'No'

# Creating a Pandas dataframe for the components optimization results table

df_scalars = pd.read_excel('../MVS_outputs/scalars.xlsx', sheet_name='scalar_matrix')
df_scalars = df_scalars.drop(['Unnamed: 0', 'total_flow', 'peak_flow', 'average_flow'], axis=1)
df_scalars = df_scalars.rename(columns={'label': 'Component/Parameter', 'optimizedAddCap': 'CAP',
                                        'annual_total_flow': 'Aggregated Flow'})
df_scalars = df_scalars.round(2)

# Creating a Pandas dataframe for the costs' results

df_costs1 = pd.read_excel('../MVS_outputs/scalars.xlsx', sheet_name='cost_matrix')
df_costs1 = df_costs1.round(2)
df_costs = df_costs1[['label', 'costs_total', 'costs_upfront', 'annuity_total', 'annuity_om']].copy()
df_costs = df_costs.rename(columns={'label': 'Component', 'costs_total': 'CAP',
                                    'costs_upfront': 'Upfront Investment Costs'})


# # Function that creates a HTML table from a Pandas dataframe
# def make_dash_table(df):
#     """ Return a dash definition of an HTML table for a Pandas dataframe """
#     table = []
#     for index, row in df.iterrows():
#         html_row = []
#         for i in range(len(row)):
#             html_row.append(html.Td([row[i]]))
#         table.append(html.Tr(html_row))
#     return table


# Function that creates a Dash DataTable from a Pandas dataframe
def make_dash_data_table(df):
    """"""
    return (dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        style_cell={'padding': '5px',
                    'height': 'auto',
                    'width': 'auto',
                    'textAlign': 'center'},
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }],
        style_header={
            'fontWeight': 'bold',
            'color': '#8c3604'
        },
        style_table={
            'margin': '30px',
            'fontSize': '40px'
        }
    ))


# Header section with logo and the title of the report, and CSS styling. Work in progress...

app.layout = html.Div([

    html.Div(className='header_title_logo',
             children=[html.Img(id='mvslogo', src='assets/logo-eland-original.jpg', width='370px'),
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
                            html.Br([]),
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

                            html.Div(className='tableplay', children=[make_dash_data_table(df_projectData)]),
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
                            html.Br([]),
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

                            html.Div(className='tableplay', children=[make_dash_data_table(df_simsettings)])
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
                                                 html.P(f'{sec_list}', style={'borderStyle': 'solid',
                                                                              'borderWidth': 'thick',
                                                                              'width': 'auto',
                                                                              'padding': '20px',
                                                                              'textAlign': 'center'})
                                                 ],
             style={
                 'textAlign': 'justify',
                 'fontSize': '40px',
                 'margin': '30px'
             }),

    html.Div(className='demandmatter', children=[html.H4('Electricity Demand', style={'position': 'relative',
                                                                                      'left': '0',
                                                                                      'height': '20%',
                                                                                      'margin': '0mm',
                                                                                      'borderLeft': '20px solid #8c3604',
                                                                                      'background': '#ffffff',
                                                                                      'paddingTop': '1px',
                                                                                      'paddingBottom': '1px',
                                                                                      'paddingLeft': '30px',
                                                                                      'paddingRight': '60px'
                                                                                      }),
                                                 html.P('Electricity demands that have to be supplied are: ')], style={
        'textAlign': 'left',
        'fontSize': '40px',
        'margin': '30px'}),

    html.Div(children=[make_dash_data_table(df_dem)]),

    html.Div(className='timeseriesplots',
             children=[
                 html.Img(src='data:image/png;base64,{}'.format(pv_dem_ts.decode()), width='1500px'),
                 html.Br([]),
                 html.H4('PV System Input Time Series', style={
                     'textAlign': 'left',
                     'fontSize': '40px',
                     'position': 'relative',
                     'left': '0',
                     'height': '20%',
                     'margin': '0mm',
                     'borderLeft': '20px solid #8c3604',
                     'background': '#ffffff',
                     'paddingTop': '1px',
                     'paddingBottom': '1px',
                     'paddingLeft': '30px',
                     'paddingRight': '60px'
                 }),
                 html.Br([]),
                 html.Img(src='data:image/png;base64,{}'.format(pv_inp_ts.decode()), width='1500px')
             ],
             style={
                 'margin': '30px'
             }),

    html.Div(),

    html.Br(),

    html.Div(className='heading1', children=[html.H2('Energy System Components',
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

    html.Div(className='blockoftext2', children=[
        html.P('The energy system is comprised of the following components:')
    ],
             style={
                 'textAlign': 'justify',
                 'fontSize': '40px',
                 'margin': '30px'
             }),

    html.Div(children=[make_dash_data_table(df_comp)]),

    html.Br([]),

    html.Div(className='simresultsbox', children=[html.H2('SIMULATION RESULTS')],
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

    html.Div(className='heading1', children=[html.H2('Dispatch & Energy Flows',
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

    html.Div(className='blockoftext2', children=[
        html.P('The capacity optimization of components that were to be used resulted in:')
    ],
             style={
                 'textAlign': 'justify',
                 'fontSize': '40px',
                 'margin': '30px'
             }),

    html.Div(children=[make_dash_data_table(df_scalars)]),
    html.Div(className='blockoftext2', children=[
        html.P('With this, the demands are met with the following dispatch schedules:'),
        html.P('a. Flows in the system for a duration of 14 days', style={'marginLeft': '20px'})
    ],
             style={
                 'textAlign': 'justify',
                 'fontSize': '40px',
                 'margin': '30px'
             }),

    html.Img(src='data:image/png;base64,{}'.format(el_flows_14.decode()),
             style={'display': 'block',
                    'marginLeft': '50px',
                    'maxWidth': '100%',
                    'height': 'auto'
                    }),

    html.P('b. Flows in the system for the whole year', style={'marginLeft': '50px',
                                                               'textAlign': 'justify',
                                                               'fontSize': '40px',
                                                               }),
    html.Img(src='data:image/png;base64,{}'.format(el_flows_365.decode()),
             style={'display': 'block',
                    'marginLeft': '50px',
                    'maxWidth': '100%',
                    'height': 'auto'
                    }),

    html.Br(style={'marginBottom': '5px'}),

    html.Div(className='res_images', children=[
        html.Img(src='data:image/png;base64,{}'.format(op_add_caps.decode())),
        html.Img(src='data:image/png;base64,{}'.format(pv_inv_flow.decode()))
    ],
             style={'display': 'block',
                    'marginLeft': '50px',
                    'maxWidth': '100%',
                    'height': 'auto',
                    'marginBottom': '5px'
                    }
             ),

    html.P('This results in the following KPI of the dispatch:', style={'marginLeft': '50px',
                                                                        'textAlign': 'justify',
                                                                        'fontSize': '40px',
                                                                        }),
    html.Div(className='heading1', children=[html.H2('Economic Evaluation',
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

    html.P('The following installation and operation costs result from capacity and dispatch optimization:',
           style={'margin': '30px',
                  'textAlign': 'justify',
                  'fontSize': '40px',
                  }),

    html.Div(children=[make_dash_data_table(df_costs)])

])

if __name__ == '__main__':
    app.run_server(debug=True)
