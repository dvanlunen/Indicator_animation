import sqlite3
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.animation as animation
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
from math import log
from math import exp
from matplotlib import colors

# Grab :
# % of electricity from renewable sources EG.ELC.RNWX.ZS
# 1960 - 2013

# path = 'H:/USER/DVanLunen/indicator_data/world-development-indicators/'
# os.chdir(path)
con = sqlite3.connect('database.sqlite')

Indicator_df = pd.read_sql('SELECT * '
                           'FROM Indicators '
                           'WHERE IndicatorCode in('
                                                   '"EG.ELC.RNWX.ZS"'
                                                   ')'
                           , con)

# Test Data that shows it in action:
# Indicator_df = pd.DataFrame({'CountryName':['United States']*4+['Argentina']*4 ,
#                              'Year':[1960, 1961, 1962, 1963]*2,
#                              'Value':[5, 20, 40, 60]*2})

# setup colorbar stuff and shape files
highestpval = 60
logbase = exp(1)
norm = mpl.colors.Normalize(vmin=0, vmax=highestpval)
colors_in_map = []
for i in range(highestpval):
    val = log(i + 1, logbase) / log(highestpval + 1, logbase)
    colors_in_map.append((1 - val, val, 0))
cmap = colors.ListedColormap(colors_in_map)

shpfilename = shpreader.natural_earth(resolution='110m',
                                      category='cultural',
                                      name='admin_0_countries')
reader = shpreader.Reader(shpfilename)
countries_map = reader.records()

facecolor = 'gray'
edgecolor = 'black'

fig, ax = plt.subplots(figsize=(12, 6),
                       subplot_kw={'projection': ccrs.PlateCarree()})

# Draw all the gray countries just once in an init function
# I also make a dictionary for easy lookup of the geometries by country name
geom_dict = {}


def init_run():
    for n, country in enumerate(countries_map):
        ax.add_geometries(country.geometry, ccrs.PlateCarree(),
                          facecolor=facecolor, edgecolor=edgecolor)
        geom_dict[country.attributes['name_long']] = country.geometry


def run(data):
    """Update the Dist"""
    year = 1960 + data

    # get a subset of the df for the current year
    year_df = Indicator_df[Indicator_df['Year'] == year]
    for i, row in year_df.iterrows():
        # This loops over countries, gets the value and geometry and adds
        # the new-colored shape
        key = row['CountryName']
        if key in geom_dict:
            geom = geom_dict[row['CountryName']]
            value = row['Value']
            greenamount = (log(float(value) + 1, logbase) /
                           log(highestpval + 1, logbase))
            facecolor = 1 - greenamount, greenamount, 0
            ax.add_geometries(geom, ccrs.PlateCarree(),
                              facecolor=facecolor, edgecolor=edgecolor)
    ax.set_title('Percent of Electricity from Renewable Sources ' +
                 str(year))

cax = fig.add_axes([0.92, 0.2, 0.02, 0.6])
cb = mpl.colorbar.ColorbarBase(cax, cmap=cmap, norm=norm,
                               spacing='proportional')
cb.set_label('%')

ani = animation.FuncAnimation(fig, run, init_func=init_run, frames=54,
                              interval=500, blit=False)

plt.show()
