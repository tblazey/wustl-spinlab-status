#!/usr/bin/python

#Load libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import numpy as np

#Load in temperature data with pandas
plot_data = pd.read_csv('./temp_data.csv',
                        parse_dates=['Datetime'],
                        dtype={'Temperature': 'float64', 'Status': object})                      

#Get info about last update
last_time = plot_data['Datetime'].iloc[-1]
up_str = 'Last Updated at: %s'%(last_time.strftime('%m-%d-%Y %I:%M:%S %p'))
          
#Create scatter temperature plot
tp = px.scatter(plot_data,
                 x='Datetime',
                 y='Temperature',
                 color='Status',
                 color_discrete_sequence=['#348cc1', '#e34e21'])
                 
#Update scatter layout
tp.update_traces(marker={'size':12, 'line':{'color':'black', 'width':2}})
tp.update_xaxes(showgrid=True,
                 gridwidth = 1,
                 gridcolor = 'Black',
                 showline = True,
                 linewidth = 3,
                 linecolor = 'black',
                 tickfont = {'color' : 'black', 'size' : 14},
                 ticklen = 10,
                 tickcolor = 'black',
                 ticks = 'outside',
                 range = [last_time - timedelta(hours = 12),
                          last_time + timedelta(hours = 1)])
tp.update_yaxes(showgrid = True,
                 gridwidth = 1,
                 gridcolor = 'Black',
                 showline = True,
                 linewidth = 3,
                 linecolor = 'black',
                 tickfont = {'color':'black', 'size':14},
                 ticklen = 10,
                 tickcolor='black',
                 ticks = 'outside',
                 tick0 = 0.5,
                 nticks = 6,
                 range = [0.0, 2.5],
                 fixedrange = True)
tp.update_layout(dragmode = 'pan',
                  margin={'t':40, 'b':140},
                  autosize=True,
                  plot_bgcolor = 'white',
                  xaxis_title = '<b>Date</b>',
                  xaxis_title_font_color = 'black',
                  xaxis_title_font_size = 20,
                  yaxis_title= '<b>Temperature (K)</b>',
                  yaxis_title_font_color = 'black',
                  yaxis_title_font_size = 20,
                  legend={'y' : 0.1,
                         'title' : '<b>Status</b>',
                         'xanchor' : 'center',
                         'bgcolor' : 'rgba(255, 255, 255, 1)',
                         'bordercolor' : 'black',
                         'borderwidth' : 1.5,
                         'title_font_size' : 16,
                         'title_font_color' : 'black',
                         'font':{'color' :'black', 'size' : 14}})
                         
#Load in spectrogram data
spec_data = np.load('./spec.npz')


#Create spectogram plot
sp = px.imshow(spec_data['spec'], x=spec_data['time'], y=spec_data['freq'], aspect='auto', zmax=2000)
sp.update_xaxes(autorange = True,
                 tickfont = {'color':'black', 'size':16},
                 ticklen = 10,
                 tickcolor='black',
                 ticks = 'outside',
                 nticks = 6)
sp.update_yaxes(autorange = True,
                 tickfont = {'color':'black', 'size':16},
                 ticklen = 10,
                 tickcolor='black',
                 ticks = 'outside',
                 nticks = 6)
sp.update_layout(margin={'t':40, 'b':140},
                  autosize=True,
                  xaxis_title = '<b>Time (secs)</b>',
                  xaxis_title_font_color = 'black',
                  xaxis_title_font_size = 20,
                  yaxis_title= '<b>Frequency</b>',
                  yaxis_title_font_color = 'black',
                  yaxis_title_font_size = 20)
sp.update_coloraxes(colorbar = {'nticks':5,
                                 'len':0.6,
                                 'thickness':40,
                                 'title':{'text':'<b>Amp.</b>', 'font':{'size':16}, 'side':'bottom'}})
                                 
#Create dash app for showing plot
config = dict({'scrollZoom': True})
app = dash.Dash(__name__, title='WUSTL Spinlab Status')
server = app.server
app.layout = html.Div(
    children=[
        html.H1('WUSTL Spinlab Status', style={'text-align':'center', 'font-size':'2.25vw'}),
        html.H3(up_str, style={'color':'gray', 'text-align':'center', 'font-size':'1.25vw', 'margin-bottom':'2vw'}),
        html.Div(className='rows', style={'columnCount':1},
            children=[
                dcc.Tabs([
                    dcc.Tab(label='Latest Cyrostatus Page',
                        children=[
                            html.Img(src=app.get_asset_url('current.png'),
                                    style={'max-width': '100%',
                                           'max-height':'100%',
                                           'padding-top':'2vw',
                                           'padding-left' :'2vw'})
                        ]
                    ),
                    dcc.Tab(label='Spinlab Temperature',
                        children=[
                            dcc.Graph(figure=tp, config=config, style={'height': '60vw', 'width':'90vw'})
                        ]
                    ),
                    dcc.Tab(label='Audio Spectogram',
                        children=[
                            dcc.Graph(figure=sp, config=config, style={'height': '60vw', 'width':'90vw'})
                        ]
                    )                
                ], style={'fontWeight':'bold', 'fontSize':20}),

            ]
        )
    ],
)

#Run app
if __name__ == '__main__':
    app.run_server()
