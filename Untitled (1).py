#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup


# In[2]:


import requests
import pandas as pd


# In[3]:


source= requests.get('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M').text
soup= BeautifulSoup(source, 'lxml')


# In[4]:


My_table = soup.find('table',{'class':'wikitable sortable'})
My_table


# In[5]:


print(My_table.tr.text)


# In[6]:


headers="Postcode,Borough,Neighbourhood"


# converting To a format easier to input for dataframe
# ===

# In[7]:


table1=""
for tr in My_table.find_all('tr'):
    row1=""
    for tds in tr.find_all('td'):
        row1=row1+","+tds.text
    table1=table1+row1[1:]
print(table1)


# In[8]:


file=open("toronto.csv","wb")
#file.write(bytes(headers,encoding="ascii",errors="ignore"))
file.write(bytes(table1,encoding="ascii",errors="ignore"))


# In[9]:


import pandas as pd
df = pd.read_csv('toronto.csv',header=None)
df.columns=["Postalcode","Borough","Neighbourhood"]


# In[10]:


df.head()


# In[11]:


# First Get names of indexes for which column Borough has value "Not assigned"
indexNames = df[ df['Borough'] =='Not assigned'].index

# Then you should delete these row indexes from dataFrame
df.drop(indexNames , inplace=True)


# In[12]:


df.head()


# In[13]:


df.loc[df['Neighbourhood'] =='Not assigned' , 'Neighbourhood'] = df['Borough']
df.head(10)


# In[14]:


result = df.groupby(['Postalcode','Borough'], sort=False).agg( ', '.join)


# In[15]:


df_new=result.reset_index()
df_new.head(15)


# In[16]:


df_new.shape


# In[27]:


df_lon_lat = pd.read_csv("http://cocl.us/Geospatial_data")
df_lon_lat.head()


# In[28]:


df_lon_lat.columns=['Postalcode','Latitude','Longitude']


# In[29]:


df_lon_lat.head()


# In[30]:


Toronto_df = pd.merge(df_new,
                 df_lon_lat[['Postalcode','Latitude', 'Longitude']],
                 on='Postalcode')
Toronto_df


# Explore and cluster neighborhoods in Toronto
# ===

# In[34]:



from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# import k-means from clustering stage
from sklearn.cluster import KMeans

#!conda install -c conda-forge folium=0.5.0 --yes # uncomment this line if you haven't completed the Foursquare API lab
import folium # map rendering library

print('Libraries imported.')


# In[35]:


address = 'Toronto, ON'

geolocator = Nominatim(user_agent="Toronto")
location = geolocator.geocode(address)
latitude_toronto = location.latitude
longitude_toronto = location.longitude
print('The geograpical coordinate of Toronto are {}, {}.'.format(latitude_toronto, longitude_toronto))


# In[36]:



map_toronto = folium.Map(location=[latitude_toronto, longitude_toronto], zoom_start=10)

# add markers to map
for lat, lng, borough, Neighbourhood in zip(Toronto_df['Latitude'], Toronto_df['Longitude'], Toronto_df['Borough'], Toronto_df['Neighbourhood']):
    label = '{}, {}'.format(Neighbourhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_toronto)  
    
map_toronto


# In[37]:



CLIENT_ID = 'QFFKK25PK2HRN2WMKXUKJCBPSOW0DSTDAGYAJXSHCT2FWQUB' # your Foursquare ID
CLIENT_SECRET = '3S2A0J2GPKKDYC2LZOW3IP3AN1BTNIRW15EPUE0UR2Q0D1B3' # your Foursquare Secret
VERSION = '20180604'
LIMIT = 30
print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# In[38]:



# defining radius and limit of venues to get
radius=500
LIMIT=100


# In[46]:



def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighbourhood', 
                  'Neighbourhood Latitude', 
                  'Neighbourhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)

