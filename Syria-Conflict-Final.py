import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import codecs
import plotly.io as pio
from array import array
from pandas.io.json import json_normalize

##SETTINGS
pd.set_option('display.max_rows', 200)
pd.options.display.max_rows = 999

##MAPBOX TOKEN
mapboxt = 'pk.eyJ1IjoiemJvbiIsImEiOiJja2hkMHhtNzAwMG1tMnJwamZwZGo0ZW04In0.TIkHu0roG9CvRbnx6B9N9Q'

##TOGGLES FOR MAP DESIGN
country_toggle = True #toggle for world or specific countries
city_toggle = True # toggle to display cities
subnat_toggle = False #toggle sub-national borders on or off
subnat_labels = False #toggle sub-national labels on or off
highlight_subnat_toggle = False #toggle for a highlighted region
h_subnat_label = False #toggle labeling of hilighted subnats
h_nat_label = True #toggle labeling of states
river_toggle = False #display rivers and lakes
irregular_toggle = True #toggle mapping of irregular points (ports, airports)
add_feature_toggle = True #toggle for mapping additional geo data via gejson lat/lon crunching
px_chloro_toggle = False # toggle inclusion of CSV data for a chloropleth map

#SET TOGGLES FOR STYLE ELEMENTS
background_color = '#ede7f1' ##fbf9fc
highlighted_subnat_color = '#f6e0cf' #'#eab68f'
highlighted_subnat_border_width = 0.25
highlighted_subnat_border_opacity = 0.5
highlighted_subnat_label_opacity = 0.5
nat_border_color = '#282828'
nat_border_width = 1
nat_border_opacity = 0.75
subnat_border_width = 0.25
subnat_border_color = '#282828'
subnat_border_opacity = 0.25
marker_size = 13
marker_color = '#282828'
city_text_color = '#282828'
city_text_opacity = 0.75
city_text_size = 17
irregular_text_color = '#282828'
irregular_text_size = 15
irregular_text_opacity = 1
subnat_label_size = 19
subnat_label_opacity = 0.25
subnat_label_color = '#282828'
nat_label_size = 75
nat_label_opacity = 0.3
nat_label_color = '#282828'
optional_feature_line_width = 2
optional_feature_opacity = 0.75
operational_feature_line_color = '#282828'
optional_feature_color = '#d186b6'

chlorocheck = 'toself' if px_chloro_toggle == False else 'none'
externalcheck = 'toself' if subnat_toggle == False else 'none'

##SET NAT/SUBNAT/CITY/FEATURE DETAILS
### Input the countries and cities to be mapped, along with the orientation of the labels for cities
country_list = ['Syria','Turkey']
city_list = [['Damascus', 'middle right'], ['Aleppo', 'bottom center'], ['Manbij', 'bottom center'], ['Idlib', 'bottom center']]
subnat_list = ['Idlib']

### Additional features to be included in the map (roads, provinces, etc)
additional_feature_counter = 1
feature_1_path = 'syrialivemap.geojson' #Syria provinces
feature_2_path = 'Syria_highway_trunk_line.geojson'

##BASE GEOJSON DATA IMPORT
#Natural Earth geographic data
with open('naturalearth.geojson', 'r', encoding='utf-8') as geojson_file:
    countries = json.load(geojson_file)

with open('naturalearth_countries.geojson', 'r', encoding='utf-8') as geojson_file:
    borders = json.load(geojson_file)

##CUSTOM CSV CONSTRUCTION
###Use this to input data manually
csv_countries = []
csv_totals = []
csv_list = [['Fujian', 5], ['Beijing', 3], ['Yunnan', 10], ['Hunan', 15], ['Hubei', 9], ['Shandong', 8], ['Henan', 3], ['Jiangsu', 38], ['Shanghai', 2], ['Zhejiang', 2], ['Liaoning', 1], ['Tianjin', 1], ['Shanxi', 1]]
for i in csv_list:
    csv_countries.append(i[0])
    csv_totals.append(i[1])
csv_dict = {'Name':csv_countries, 'Total':csv_totals}
csv_data = pd.DataFrame(csv_dict)


##ISO CODE COUNTRY LIST FOR CITY IMPORTS
### Loads a list of ISO codes to be used for mapping cities and notable locations (city_list)
iso_list = pd.read_csv('G:\\My Drive\\Python\\Maps\\CityDB\\data_csv.csv', encoding='utf-8')
iso_codes = []

##PREPARE ANY IRREGULAR/MANUAL MAP POINTS - PORTS, AIRPORTS, ATTACKS, ETC
### A custom dictionary used to manually input notable points on the map (ie, attacks that occur outside populated areas)
irregular_dict = {
        'name':['Tell Rifaat'],#, 'Port Qasim'],
        'latitude':[36.4733],# 24.7854],
        'longitude':[37.0972],#, 67.3695],
        'position':['bottom center'],#, 'middle right'],
        'type':['circle']}#, 'industry']} #list of irregular adds
irregular_slice = pd.DataFrame.from_dict(irregular_dict)

##LOAD CITIES ON A COUNTRY-BY-COUNTRY BASIS (SAVES LOADING A COMPLETE LIST) - https://download.geonames.org/export/dump/
###Use ISO codes to load geographic data from the target countries (country_list)
if city_toggle == True and country_toggle == True:
    for column, row in iso_list.iterrows():
        if row['Name'] in country_list:
            iso_codes.append(row['Code'])
#LOAD CORRESPONDING CITY FILES
    paths = {}
    frames = []
    columns = ['geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude', 'feature class',
        'feature code', 'country code', 'cc2', 'admin1 code', 'admin2 code', 'admin3 code', 'admin4 code',
        'population', 'elevation', 'dem', 'timezone', 'modification date']
    for i in range(0, len(iso_codes)):
        paths['City_{0}'.format(i)] = 'G:\\My Drive\\Python\\Maps\\CityDB\\' + iso_codes[i] + '\\' + iso_codes[i] + '.csv'
    for keys, values in paths.items():
        imported_slice = pd.read_csv(values, encoding='utf-8', sep='\t', names=columns, low_memory=False)
        frames.append(imported_slice) #make a list of dataframe slices and eventually concat them
    city_df = pd.concat(frames)
    city_df['position'] = 'top right'
    city_df['type'] = 'city'
else:
    pass

##LOAD ADDITIONAL FEATURES
#FIRST FEATURE
if add_feature_toggle == True:
    with open(feature_1_path, 'r', encoding='utf-8', errors='replace') as geojson_file:
        feature_1 = json.load(geojson_file)
else: pass

#SECOND FEATURE
if add_feature_toggle == True:
    with open(feature_2_path, 'r', encoding='utf-8', errors='replace') as geojson_file:
        feature_2 = json.load(geojson_file)
else: pass

##NARROW DOWN FEATURES
### Narrow down imported feature to find what you're looking for. Often includes sifting through various labels of JSON data
#Afrin Province
output_list = []
revised_latlon = [] #lat always comes first
old_feature_1 = feature_1
for feature in feature_1['features']:
    if feature['properties']['fill'] == 'Afrin' or feature['properties']['fill'] == 'Peacespring':
        # old_list = feature['geometry']['coordinates']
        # for x in feature['geometry']['coordinates']: #SHIFTING ON THE LAT/LON DUE TO MISALIGNED BORDERS
        #     for y in x:
        #         new_pair = [(y[0] - 0.035), (y[1] + 0.007)]
        #         revised_latlon.append(new_pair)
        # feature_slice = feature
        # feature_slice['geometry']['coordinates'] = [revised_latlon]
        output_list.append(feature)
        output_list = output_list
feature_1 = {'type':'FeatureCollection', 'features':output_list}

#M4 Highway in northern Syria
features_slice = []
for i in feature_2['features']:
    if i['properties']['ref'] == 'M4' or i['properties']['full_id'] == 'w24872291':  # set a condition as-needed
        if i['properties']['int_ref'] != 'M10':
            features_slice.append(i)
            continue
        elif i['properties']['int_ref'] == 'M10':
            if i['properties']['name'] == 'Syria Road':
                features_slice.append(i)
                continue
        else:
            pass
feature_2 = {'type': 'FeatureCollection', 'features': features_slice}

#Kurdish-controlled territory (same source file as Afrin)
output_list = []
for feature in old_feature_1['features']:
    if feature['properties']['fill'] == 'kurds':
        print(feature)
        output_list.append(feature)
        output_list = output_list
feature_3 = {'type':'FeatureCollection', 'features':output_list}

#Idlib (same source file as Afrin)
output_list = []
for feature in old_feature_1['features']:
    if feature['properties']['fill'] == 'idlib':
        output_list.append(feature)
        output_list = output_list
feature_4 = {'type':'FeatureCollection', 'features':output_list}

#Government-controlled territory
output_list = []
for feature in old_feature_1['features']:
    if feature['properties']['fill'] == 'government':
        output_list.append(feature)
        output_list = output_list
feature_5 = {'type':'FeatureCollection', 'features':output_list}

##NAME CONVERSION LIST (if needed in future)##
subnat_conversions = {
    'na':'na'}

subnat_check_list = []
for key, value in subnat_conversions.items():
    subnat_check_list.append(key)

###FUNCTIONS###
def ip_cruncher(input): #convert geojson to list of lon/lat
    points = []
    out_list = []
    for feature in input['features']:
        if feature['geometry']['type'] == 'Polygon':
            points.extend(feature['geometry']['coordinates'][0])
            points.append([None, None]) # mark the end of a polygon
        elif feature['geometry']['type'] == 'MultiPolygon':
            for polyg in feature['geometry']['coordinates']:
                points.extend(polyg[0])
                points.append([None, None]) #end of polygon
        elif feature['geometry']['type'] == 'MultiLineString':
            points.extend(feature['geometry']['coordinates'])
            points.append([None, None])
        elif feature['geometry']['type'] == 'LineString':
            points.extend(feature['geometry']['coordinates'])
            points.append([None, None])
        else: pass
    prov_lons, prov_lats = zip(*points)
    out_list = [prov_lons, prov_lats]
    return out_list

def get_centroid(input, target, national=True): #find center point in a polygon
    #SUBNAT
    if national==False:
        highlighted_data = []
        cleaned_list = []
        for i in input['features']:
            if i['properties']['admin'] in country_list:
                cleaned_list.append(i)
        cleaned_input = {'type':'FeatureCollection', 'features':cleaned_list}
        gpd_df = gpd.GeoDataFrame.from_features(cleaned_input['features'])
        gpd_slice = gpd_df.loc[gpd_df['name'].str.contains(target, na=False)]
        lon = gpd_slice.centroid.x
        lat = gpd_slice.centroid.y
        points = [lon, lat]
        return points
    #NAT
    elif national==True:
        highlighted_data = []
        cleaned_list = []
        for i in input['features']:
            if i['properties']['ADMIN'] == target:
                cleaned_list.append(i)
        cleaned_input = {'type':'FeatureCollection', 'features':cleaned_list}
        gpd_slice = gpd.GeoDataFrame.from_features(cleaned_input['features'])
            #    gpd_slice = gpd_df.loc[gpd_df['ADMIN'].str.contains(target, na=False)]
        lon = gpd_slice.centroid.x
        lat = gpd_slice.centroid.y
        points = [lon, lat]
        return points

def marker_plot(df, irregular=True): #for plotting markers, toggle for city DB or irregular (manually inputed)
    if irregular==False:
        for i, row in df.iterrows():
            lat = [row['latitude']]
            lon = [row['longitude']]
            marker_output = go.scattermapbox.Marker(
                    size=marker_size,
                    symbol='circle',#row['type'],
                    allowoverlap=True,
                    color=marker_color)
        return  {
            "type": "scattermapbox",
            "lat":  lat,
            "lon":  lon,
            "text": row['name'],
            "mode": "markers+text",
            "textposition":row['position'],
            "textfont":{
            "size":city_text_size,
            "color":city_text_color}, # BLACK #241f20"},
            "marker": marker_output}
    elif irregular==True:
        for i, row in df.iterrows():
            marker_output = go.scattermapbox.Marker(
                    size=marker_size,
                    symbol=row['type'],
                    allowoverlap=True,
                    color=marker_color)
            lat = [row['latitude']]
            lon = [row['longitude']]
        return  {
            "type": "scattermapbox",
            "lat":  lat,
            "lon":  lon,
            "text": row['name'],
            "mode": "markers+text",
            'marker':marker_output,
            "textposition":row['position'],
            "textfont":{
            "size":city_text_size,
            "color":city_text_color}}

def label_adjuster(input, direction, degree): #shift the labels / same direction options as textposition
    in_lat = input[1]
    in_lon = input[0]
    if direction == 'top':
        in_lat += degree
    elif direction == 'top-left':
        in_lat += (degree / 2)
        in_lon -= (degree / 2)
    elif direction == 'top-right':
        in_lat += (degree / 2)
        in_lon += (degree / 2)
    elif direction == 'bottom':
        in_lat -= degree
    elif direction == 'bottom-left':
        in_lat -= (degree / 2)
        in_lon -= (degree / 2)
    elif direction == 'bottom-right':
        in_lat -= (degree / 2)
        in_lon += (degree / 2)
    elif direction == 'right':
        in_lon += degree
    elif direction == 'left':
        in_lon -= degree
    out_list = [in_lon, in_lat]
    return out_list

def list_check(list, term):
    for x in list:
        if term in x[0]:
            return True
        else: return False

##OFFSET LABELS FOR CITIES AND IRREGULAR PLOTS
def label_offsetter(input, direction, distance):
    #DIRECTION ADJUSTMENT
    if direction == 'top':
        input['lat'][0] += distance
    elif direction == 'top-left':
        input['lat'][0] += (distance / 2)
        input['lon'][0] -= (distance / 2)
    elif direction == 'top-right':
        input['lat'][0] += (distance / 2)
        input['lon'][0] += (distance / 2)
    elif direction == 'bottom':
        input['lat'][0] -= distance
    elif direction == 'bottom-left':
        input['lat'][0] -= (distance / 2)
        input['lon'][0] -= (distance / 2)
    elif direction == 'bottom-right':
        input['lat'][0] -= (distance / 2)
        input['lon'][0] += (distance / 2)
    elif direction == 'right':
        input['lon'][0] += distance
    elif direction == 'left':
        input['lon'][0] -= distance
    else: pass
    del input['marker']
    input['mode'] = 'text'
    return input

##CRUNCH INTERNAL BORDERS
### Applies ip_cruncher to sub-national geographic data to get the appropriate lon/lat
if country_toggle == True and subnat_toggle == True:
    i_countries_slice = []
    province_list = []
    for i in countries['features']:
        if i['properties']['admin'] in country_list:
            i['id'] = i['properties']['name']
            province_list.append(i['properties']['name'])
            i_countries_slice.append(i)
    i_countries_slice_out = {'type':'FeatureCollection', 'features':i_countries_slice}
    internal_border_list = ip_cruncher(i_countries_slice_out)
else:
    internal_border_list = ip_cruncher(countries)

if highlight_subnat_toggle == True:
    highlighted_slice = []
    for i in countries['features']:
        if i['properties']['name'] in subnat_list and i['properties']['admin'] in country_list:
            highlighted_slice.append(i)
    highlighted_slice_out = {'type':'FeatureCollection', 'features':highlighted_slice}
    internal_highlight_list = ip_cruncher(highlighted_slice_out)

##CRUNCH EXTERNAL BORDERS
### Applies ip_cruncher to national geographic data to get the appropriate lon/lat
if country_toggle == True:
    x_countries_slice = []
    x_countries_slice_out = []
    for i in borders['features']:
        if i['properties']['ADMIN'] in country_list:
            i['id'] = i['properties']['ADMIN']
            x_countries_slice.append(i)
    x_countries_slice_out = {'type':'FeatureCollection', 'features':x_countries_slice}
    external_border_list = ip_cruncher(x_countries_slice_out)
else:
    external_border_list = ip_cruncher(borders)

##CRUNCH ADDITIONAL FEATURES
### Applies ip_cruncher to external feature geographic data to get the appropriate lon/lat
#FIRST FEATURE
if add_feature_toggle == True:
    feature_1_list = ip_cruncher(feature_1)

#SECOND FEATURE
# if add_feature_toggle == True:
    features_slice = []
    features_slice_out = []
    feature_2_list = ip_cruncher(feature_2)

#THIRD FEATURE
# if add_feature_toggle == True:
    features_slice = []
    features_slice_out = []
    feature_3_list = ip_cruncher(feature_3)

#FOURTH FEATURE
# if add_feature_toggle == True:
    features_slice = []
    features_slice_out = []
    feature_4_list = ip_cruncher(feature_4)

#FIFTH FEATURE
# if add_feature_toggle == True:
    features_slice = []
    features_slice_out = []
    feature_5_list = ip_cruncher(feature_5)


##PREPARE CITY INFO
### match city_list to city geographic data in order to get the lon/lat of desired cities.
temp_city_list = []
temp_position_list = []
if city_toggle == True:
    # # #Check for capital city or other feature code in city data:
    # #http://www.geonames.org/export/codes.html for codes
    # for col, row in city_df.iterrows():
    #     if row['feature code'] == 'PPLC':
    #         print(row)

    #Look to match city list against city data; asciiname helps reduce encoding incongruencies; i.e accents
    for col, row in city_df.iterrows():
        if row['name'] in [y[0] for y in city_list] or row['asciiname'] in [y[0] for y in city_list]:
#            print(row['name'])  #verify codes in loop
#            print(row['feature code'])
    #Check to make sure the city isn't already in the list
            if row['name'] in [y['name'] for y in temp_city_list] or row['asciiname'] in [z['asciiname'] for z in temp_city_list]: continue
    #Record city to list on the basis of importance (there are often multiple hits of different districts, etc)
            if row['feature code'] == 'PPLC':
                rowdict = row.to_dict()
                temp_city_list.append(row)
            elif row['feature code'] == 'PPLA':
                rowdict = row.to_dict()
                temp_city_list.append(row)
            elif row['feature code'] == 'PPLA2':
                    rowdict = row.to_dict()
                    temp_city_list.append(row)
            elif row['feature code'] == 'PPLA3':
                rowdict = row.to_dict()
                temp_city_list.append(row)
            elif row['feature code'] == 'PPLA4':
                rowdict = row.to_dict()
                temp_city_list.append(row)
            elif row['feature code'] == 'PPLA5':
                rowdict = row.to_dict()
                temp_city_list.append(row)
            else: pass
    city_slice = pd.DataFrame(temp_city_list) #create final df of cities to plot
    ###Now incorporate the label positioning stipulated in the original city_list
    for col, row in city_slice.iterrows():
        for y in city_list:
            if row['name'] in y[0] or row['asciiname'] in y[0]:
                temp_position_list.append(y[1])
    city_slice['position'] = temp_position_list #add a column for label position
else: pass


##OFFSET MARKER LABELS
marker_offset_toggle = True #Enable altered offsets for city and irregular plots
marker_offset_list = [['Islamabad', 'top-right', 5], ['Karachi', 'top-left', 5]]


##MAP OUT THE DATA
fig = go.Figure()

##DRAW INTERNAL BORDERS (fig.data[0])
if subnat_toggle == True:
    fig.add_scattermapbox(
        lat=internal_border_list[1],
        lon=internal_border_list[0],
        showlegend=False,
        mode="lines",
        fillcolor=background_color,
        fill=chlorocheck,
        opacity=subnat_border_opacity,
        line=dict(width=subnat_border_width, color=subnat_border_color))
else: pass

##DRAW ANY HIGHLIGHTED SUBNAT
if highlight_subnat_toggle == True:
    fig.add_scattermapbox(
        lat=internal_highlight_list[1],
        lon=internal_highlight_list[0],
        showlegend=False,
        mode="lines",
        fillcolor=highlighted_subnat_color,
        fill='toself',
        opacity=highlighted_subnat_border_opacity,
        line=dict(width=highlighted_subnat_border_width, color=subnat_border_color))
else: pass

#DRAW CHLOROPLETH LAYER (IF CSV DATA)
if px_chloro_toggle == True:
    choro_scale = px.colors.sequential.YlOrRd #assign color scale (allows for editing)
    choro_scale[0] = background_color #alter the base color to keep it more consistent with website template
    for i in province_list: #fill out the rest of the national data with 0s; done to control background color due to not being able to order traces properly in plotly
        if i not in [x for x in csv_data['Name']]:
            new_row = {'Name':i, 'Total':0}
            csv_data = csv_data.append(new_row, ignore_index=True)
    fig.add_choroplethmapbox(
        locations=csv_data['Name'],
        z=csv_data['Total'],
        colorscale=choro_scale,
        marker_opacity=1,
        marker_line_width=0,
        showscale=True,
        geojson=i_countries_slice_out,
        colorbar=dict(
            bordercolor='rgb(241,246,248)',
            borderwidth=2,
            thickness=70,
            outlinecolor='#282828',
            outlinewidth=2,
            len=0.5,
            bgcolor='#E8E8E8',
            ticklabelposition ='outside',
            tickcolor='#4c5b6b',
            showticklabels=True,
            title=dict(
            text='',
            side='right',
            font =dict(family= 'Courier New', size=23)),
            tickfont=dict(size=18, color='#282828', family='Courier New'))),

##DRAW EXTERNAL BORDERS (fig.data[0])
fig.add_scattermapbox(
    lat=external_border_list[1],
    lon=external_border_list[0],
    showlegend=False,
    mode="lines",
    fill=externalcheck,
    fillcolor=background_color,
    opacity=nat_border_opacity,
    line=dict(width=nat_border_width, color=nat_border_color))

##DRAW OPTIONAL FEATURES
if add_feature_toggle == True: #First feature: Turkey
    fig.add_scattermapbox(
        lat=feature_1_list[1],
        lon=feature_1_list[0],
        showlegend=False,
        mode="lines",
        fill='toself',
        fillcolor='rgba(0,147,146, 0.3)',
        opacity=0,
        line=dict(width=optional_feature_line_width, color='#282828'))

if add_feature_toggle == True: #Third feature: Kurds
    fig.add_scattermapbox(
        lat=feature_3_list[1],
        lon=feature_3_list[0],
        showlegend=False,
        mode="lines",
        fill='toself',
        fillcolor='rgba(233,226,156, 0.3)',
        opacity=0,
        line=dict(width=optional_feature_line_width, color=operational_feature_line_color))

if add_feature_toggle == True: #Fourth feature: Idlib
    fig.add_scattermapbox(
        lat=feature_4_list[1],
        lon=feature_4_list[0],
        showlegend=False,
        mode="lines",
        fill='toself',
        fillcolor='rgba(57,177,133, 0.3)',
        opacity=0,
        line=dict(width=optional_feature_line_width, color=operational_feature_line_color))

if add_feature_toggle == True: #Fifth feature: government zone
    fig.add_scattermapbox(
        lat=feature_5_list[1],
        lon=feature_5_list[0],
        showlegend=False,
        mode="lines",
        fill='toself',
        fillcolor='rgba(207,89,126, 0.3)',
        opacity=0,
        line=dict(width=optional_feature_line_width, color=operational_feature_line_color))


if add_feature_toggle == True: #Second feature: highway (ensure uppermost layer)
    fig.add_scattermapbox(
        lat=feature_2_list[1],
        lon=feature_2_list[0],
        showlegend=False,
        mode="lines",
        opacity=optional_feature_opacity,
        line=dict(width=2.5, color=operational_feature_line_color))

##ANOTHER BORDER FOR CLARITY
#DRAW EXTERNAL BORDERS (fig.data[0])
fig.add_scattermapbox(
    lat=external_border_list[1],
    lon=external_border_list[0],
    showlegend=False,
    mode="lines",
    opacity=nat_border_opacity,
    line=dict(width=2, color=nat_border_color))

##DRAW IRREGULARS
if irregular_toggle == True and marker_offset_toggle == False:
    for i in range(0, len(irregular_slice)):
        data = marker_plot(irregular_slice.iloc[[i]], irregular=True)
        fig.add_trace(data)
elif irregular_toggle == True and marker_offset_toggle == True:
    for i in range(0, len(irregular_slice)):
        if irregular_slice['name'].iloc[i] in [x[0] for x in marker_offset_list]: #THOSE NEEDING OFFSET
            data_m = marker_plot(irregular_slice.iloc[[i]], irregular=True)
            for z in marker_offset_list:
                if z[0] == irregular_slice['name'].iloc[i]:
                    offset_direction = z[1]
                    offset_distance = z[2]
            offset_text = label_offsetter(data_m, offset_direction, offset_distance) #process offset text
            data_m['mode'] = 'markers'
            offset_text['mode'] = 'text'
    #        fig.add_trace(data_m) #original marker
            fig.add_trace(offset_text) #offset label

    #        print('found: ', irregular_slice['name'].iloc[i])

        elif not irregular_slice['name'].iloc[i] in [x[0] for x in marker_offset_list]: #THOSE NOT NEEDING OFFSET
            data = marker_plot(irregular_slice.iloc[[i]], irregular=True)
            fig.add_trace(data)


##DRAW LABELS##
#SUBNAT LABELS
subnat_override = False #Engage an override of center-based lat/lon for labels
#Adjust position of labels - note: use original names if name converting
subnat_adjust_list = [['Jiangsu', 'top', 0.75], ['Inner Mongol', 'bottom-right', 2.5], ['Hebei', 'bottom-left', 2]]
#Adjust size of labels - Default size is 12 / USE ADJUSTED NAMES
subnat_size_adjust_list = [['Hainan', 0.5], ['Tianjin', 0.7], ['Jiangsu', 0.7]]
#Note: drop list uses pre-conversion dictionary names / names in adjust list won't be dropped
subnat_drop_list = ['Paracel Islands', 'Beijing', 'Shanghai', 'Chongqing', 'Hunan', 'Yunnan', 'Tianjin', 'Anhui', 'Xizang', 'Xinjiang', 'Inner Mongol', 'Qinghai', 'Ningxia', 'Gansu', 'Sichuan', 'Jilin', 'Heilongjiang', 'Jiangxi', 'Guangdong', 'Guangxi', 'Guizhou', 'Shaanxi']
if subnat_labels == True and subnat_override == False:
    for i in range(0, len(province_list)):
            text_size = subnat_label_size
            subnat_labels = get_centroid(countries, province_list[i], national=False)
            #Run check for dictionary conversion of subnats
            if province_list[i] in subnat_check_list:
                for key, value in subnat_conversions.items():
                    if province_list[i] == key:
                        text_output = value
            else: text_output = province_list[i]
            #Run check for text size adjustment
            if province[i] in [x[0] for x in subnat_size_adjust_list]:
                for x in subnat_size_adjust_list:
                    if text_output == x[0]:
                        text_size = subnat_label_size * x[1]
                    else: pass
            fig.add_scattermapbox(
                lat=subnat_labels[1],
                lon=subnat_labels[0],
                showlegend=False,
                text=text_output.upper(),
                mode="text",
                fillcolor='rgba(96,113,166,0.1)',
                opacity=subnat_label_opacity,
                textposition='middle center',
                textfont=dict(size=text_size, color=subnat_label_color, family='Courier New')),
elif subnat_labels == True and subnat_override == True:
    for i in range(0, len(province_list)):
        text_size = subnat_label_size
        if province_list[i] in [x[0] for x in subnat_adjust_list]:
            for x in subnat_adjust_list:
                if province_list[i] == x[0]:
                    original_subnat_label = get_centroid(countries, province_list[i], national=False)
                    adjusted_subnat_label = label_adjuster(original_subnat_label, x[1], x[2])
            #Run check for dictionary conversion of subnats
                if province_list[i] in subnat_check_list:
                    for key, value in subnat_conversions.items():
                        if province_list[i] == key:
                            text_output = value
                else: text_output = province_list[i]
            #Run text size adjustment
                if text_output in [x[0] for x in subnat_size_adjust_list]:
                    for x in subnat_size_adjust_list:
                        if text_output == x[0]:
                            text_size = subnat_label_size * x[1]
                        else: pass
            fig.add_scattermapbox(
                lat=adjusted_subnat_label[1],
                lon=adjusted_subnat_label[0],
                showlegend=False,
                text=text_output.upper(),
                mode="text",
                fillcolor='rgba(96,113,166,0.1)',
                opacity=subnat_label_opacity,
                textposition='middle center',
                textfont=dict(size=text_size, color=subnat_label_color, family='Courier New'))
            #REGULAR LABELS OUTSIDE OF LISTS - checks against drop list
        elif not province_list[i] in [x[0] for x in subnat_adjust_list] and not province_list[i] in subnat_drop_list:
            original_subnat_label = get_centroid(countries, province_list[i], national=False)
            #Run dictionary conversion check
            if province_list[i] in subnat_check_list:
                for key, value in subnat_conversions.items():
                    if province_list[i] == key:
                        text_output = value
            else: text_output = province_list[i]
            #Run text size adjustment
            if text_output in [x[0] for x in subnat_size_adjust_list]:
                for x in subnat_size_adjust_list:
                    if text_output == x[0]:
                        text_size = subnat_label_size * x[1]
                    else: pass
            fig.add_scattermapbox(
                lat=original_subnat_label[1],
                lon=original_subnat_label[0],
                showlegend=False,
                text=text_output.upper(),
                mode="text",
                fillcolor='rgba(96,113,166,0.1)',
                opacity=subnat_label_opacity,
                textposition='middle center',
                textfont=dict(size=text_size, color=subnat_label_color, family='Courier New'))

##HIGHLIGHTED SUBNAT LABEL
if h_subnat_label == True:
    for i in range(0, len(subnat_list)):
        highlighted_labels = get_centroid(countries, subnat_list[i], national=False)
        fig.add_scattermapbox(
            lat=highlighted_labels[1],
            lon=highlighted_labels[0],
            showlegend=False,
            text=subnat_list[i].upper(),
            mode="text",
            fillcolor='rgba(96,113,166,0.1)',
            opacity=highlighted_subnat_label_opacity,
            textposition='middle center',
            textfont=dict(size=subnat_label_size, color=subnat_label_color, family='Courier New')),

##NAT LABEL
override = True #Engage an override of center-based lat/lon for labels
nat_label_adjust_list = [['Turkey', 'bottom-right', 4], ['Syria', 'top-left', 0.4]] #input adjustments to be made to label positioning / [name, direction, distance]
nat_label_size_adjust = [['Eritrea', 0.39]]
if h_nat_label == True and override == False:
    for i in range(0, len(country_list)):
        highlighted_nat_labels = get_centroid(borders, country_list[i], national=True)
        fig.add_scattermapbox(
            lat=highlighted_nat_labels[1],
            lon=highlighted_nat_labels[0],
            showlegend=False,
            text=country_list[i].upper(),
            mode="text",
            fillcolor='rgba(96,113,166,0.1)',
            opacity=nat_label_opacity,
            textposition='middle center',
            textfont=dict(size=nat_label_size, color=nat_label_color, family='Courier New')),
elif h_nat_label == True and override == True:
    for i in range(0, len(country_list)):
        text_size = nat_label_size
        highlighted_nat_labels = get_centroid(borders, country_list[i], national=True) #get the original lat/lon to be altered
        #Run label position adjustment
        if country_list[i] in [z[0] for z in nat_label_adjust_list]:
            for x in nat_label_adjust_list:
                if x[0] == country_list[i]:
                    highlighted_nat_labels = label_adjuster(highlighted_nat_labels, x[1], x[2])
                else: pass
        #Run text size adjustment
        if country_list[i] in [z[0] for z in nat_label_size_adjust]:
            for x in nat_label_size_adjust:
                if country_list[i] == x[0]:
                    text_size = nat_label_size * x[1]
                else: pass
        fig.add_scattermapbox(
            lat=highlighted_nat_labels[1],
            lon=highlighted_nat_labels[0],
            showlegend=False,
            text=country_list[i].upper(),
            mode="text",
            fillcolor='rgba(96,113,166,0.1)',
            opacity=nat_label_opacity,
            textposition='middle center',
            textfont=dict(size=text_size, color=nat_label_color, family='Courier New')),
    else: pass

##DRAW CITIES / MANUALLY ADJUST FOR TEXT POSITIONING / use array based on list
##top left / top center / middle left / bottom left, etc / fig.data[2]
if city_toggle == True:
    if len(temp_city_list) >= 1:
        for i in range(0, len(city_list)):
            data = marker_plot(city_slice.iloc[[i]], irregular=False)
            fig.add_trace(data)
    else: pass

fig.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    coloraxis_showscale=True,
    showlegend=True,
    mapbox=go.layout.Mapbox(
        style="mapbox://styles/zbon/ckshpu8fb091a17p951bwv9hx",
    #    style='mapbox://styles/zbon/ckrtjfybq2gb717nbgtzxjv9q',
        zoom=5.12,
        accesstoken=mapboxt,
        center_lat = 33.121,
        center_lon = 42.334))


#SET CONFIG FOR DOWNLOAD PLOT RESOLUTION
config = {
  'toImageButtonOptions': {
    'format': 'png', # one of png, svg, jpeg, webp
    'filename': 'custom_image',
    'height': 1200,
    'width': 1400,
    'scale': 7 # Multiply title/legend/axis/canvas sizes by this factor
  }}

fig.show(config=config)

if not os.path.exists("images"):
    os.mkdir("images")
fig.write_html("images/output.html")
pio.write_image(fig, 'images/output.png', width=1400, height=1200)

