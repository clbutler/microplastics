#!/usr/bin/env python
# coding: utf-8

# In[131]:


#import relevant packages

import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as ctx
import seaborn as sns
import numpy as np
import scipy.stats as stats
import pytest
import os

# In[87]:
    
#pytest - integration tests    
    
def test_files():
    assert os.path.exists('data/Marine Microplastic Concentrations.geojson'), 'could not find geojson file'
    assert os.path.exists('data/c20230705_OffshoreMPAs_WGS84.shp'), 'could not find shape file'


microplastic = gpd.read_file('data/Marine Microplastic Concentrations.geojson') #import geojson file containing microplastic survey data
MPAs = gpd.read_file('data/c20230705_OffshoreMPAs_WGS84.shp') #import shape file of marine protected area (MPAs)


# In[88]:


microplastic.head()

#pytest - integration tests

def test_geodataframe():
    assert isinstance(microplastic, gpd.geodataframe.GeoDataFrame), 'microplastic file is not able to load as a GeoDataFrame' 

def test_shapefile():
    assert isinstance(MPAs, gpd.GeoDataFrame), 'MPAs file is not able to load as a GeoDataFrame'
    
def test_geometrycolumn():
    assert 'geometry' in MPAs.columns, 'MPAs is missing a geometry column'  
    
def test_shape():
    assert microplastic.shape[1] > 0, 'Microplastic file is empty'

    
     





# In[89]:


MPAs.head()






# In[90]:


microplastic = microplastic.to_crs(epsg=3857) #convert to same coordinate reference system - epsg is one common used by contextily's base map


# In[91]:


MPAs = MPAs.to_crs(epsg = 3857) #convert to same coordinate reference system - epsg is one common used by contextily's base map


# In[92]:
    
#feature testing

def test_crs():
    assert microplastic.crs == 'EPSG:3857', 'microplastic data could not convert to the EPSG crs (co-ordinate reference system)'
    assert MPAs.crs == 'EPSG:3857', 'MPA data could not convert to the EPSG crs (co-ordinate reference system)'
    


microplastic.columns


# In[93]:


MPAs.columns


# In[94]:


microplastic['MEASUREMEN'] = pd.to_numeric(microplastic['MEASUREMEN'], errors='coerce') #ensure microplastic measurements are numeric


# In[95]:


plt.hist(microplastic['MEASUREMEN']) #display histogram of microplastic concentrations


# In[96]:


microplastic['MEASUREMEN'].describe() #mean concentration is 8.23, but heavy positive skew


# In[163]:


# Plot your data
fig, ax = plt.subplots(figsize=(10, 10))
MPAs.plot(ax = ax, color = 'DarkGreen', alpha = .2, edgecolor = 'Grey')
microplastic.plot(figsize=(10, 10), markersize = 40, column = 'MEASUREMEN', cmap = 'Blues', scheme="Quantiles", k =5, ax = ax) #splits range of microplastic concentration into 5 bins of equal ns.

# Add base map
ax.set_axis_off()

# Adjust the layout to make room for the legend
plt.tight_layout()
ctx.add_basemap(ax)


# In[98]:


MPAs['area'] = MPAs.geometry.area

# Group by 'SITE_NAME' and sum the areas
MPAs.groupby('SITE_NAME')['area'].sum().sort_values() #these are in square meters


# In[99]:


in_MPAs = gpd.sjoin(microplastic, MPAs , how='inner', predicate='within')


# In[100]:


in_MPAs['MPA_inout'] = 'Inside MPA'


# In[101]:


in_MPAs.describe()['MEASUREMEN'] #178 measurements in MPAs


# In[ ]:





# In[102]:


plt.hist(in_MPAs['MEASUREMEN']) 


# In[145]:


fig, ax = plt.subplots(figsize = (10,10))
MPAs.plot(ax = ax, color = '#1a1d26', alpha = .2)
in_MPAs.plot(figsize=(10, 10), markersize = 20, column = 'MEASUREMEN', cmap = 'coolwarm', scheme="Quantiles", k =5, legend = True, ax = ax)
ctx.add_basemap(ax = ax)

#vast majority of these are in one location (the firth of forth)


# In[104]:


#Get the indices of microplastics that are within MPAs
in_MPAs_index = in_MPAs.index

# Filter microplastics to exclude those that are within MPAs
outside_MPAs = microplastic.loc[~microplastic.index.isin(in_MPAs_index)]


# In[105]:


outside_MPAs.head()


# In[106]:


outside_MPAs['MPA_inout'] = 'Outside MPA'


# In[107]:


outside_MPAs.describe()['MEASUREMEN'] #558 measurements in MPAs


# In[108]:


plt.hist(outside_MPAs['MEASUREMEN']) 


# In[143]:


fig, ax = plt.subplots(figsize = (10,10))
MPAs.plot(ax = ax, color = 'green')
outside_MPAs.plot(figsize=(10, 10), markersize = 20, column = 'MEASUREMEN', cmap = 'coolwarm', scheme="Quantiles", k =5, legend = True, ax = ax)
ctx.add_basemap(ax = ax)


# In[110]:


#plotting


# In[111]:


plot = pd.concat([in_MPAs, outside_MPAs])


# In[127]:


barplot = plot.groupby('MPA_inout')['MEASUREMEN'].agg(['median', 'std', 'count', 'mean']).reset_index()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[128]:


barplot['se'] = barplot['std'] / np.sqrt(barplot['count'])


# In[ ]:





# In[173]:


fig, ax = plt.subplots(figsize = (10,10))
sns.barplot(x = 'MPA_inout', y = 'mean', yerr = barplot['se'], data = barplot, color = '#0da6ab', edgecolor = '#1a1d26')
ax.set_xlabel('\nSurvey Location', fontsize = 20)
ax.set_ylabel('Average Microplastic Concentration\n Pieces per M3 \n', fontsize = 20)
ax.set_ylim(0,45)
ax.tick_params(axis='both', which='major', labelsize=20)



# In[167]:


barplot


# In[139]:


stats.mannwhitneyu(in_MPAs['MEASUREMEN'], outside_MPAs['MEASUREMEN'].dropna()) #P is less than 0.05

