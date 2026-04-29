from herbie import Herbie, FastHerbie
import pandas as pd, numpy as np
import xarray as xr
import dask
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import cartopy.crs as ccrs, cartopy.feature as cfeature
import requests
import pandas as pd
import io
import os
import matplotlib.colors as mcolors
from datetime import datetime, timedelta
import glob
import shutil

def latestrun():
    now = datetime.utcnow()
    now = now - timedelta(hours=5)
    if now.hour >=12:
        runhr=12
    else:
        runhr=0
    run = now.replace(hour=runhr, minute=0, second=0, microsecond=0)
    return pd.Timestamp(run)
run=latestrun()

# This function creates the index based on apparent temperature, wind, and precipitation
def points(fl, windmph, rain, snow):

# APPARENT TEMPERATURE
# I used AI to help write the temperature contributions in xarray code since that is what we used in our original index back in milestone 1
    temp_contribution = xr.zeros_like(fl)
    mask = ((fl >= 75) & (fl < 85))
    temp_contribution = xr.where(mask, (fl - 75) / 10, temp_contribution)
    mask = ((fl >= 85) & (fl < 105))
    temp_contribution = xr.where(mask, 1 + ((fl - 85) / 5), temp_contribution)
    mask = fl >= 105
    temp_contribution = xr.where(mask, 5, temp_contribution)
    mask = ((fl < 50) & (fl > 0))
    temp_contribution = xr.where(mask, (50 - fl) / 10, temp_contribution)
    mask = fl <= 0
    temp_contribution = xr.where(mask, 5, temp_contribution)

#WIND SPEED
    wind_contribution = xr.zeros_like(windmph)
    mask = ((windmph >= 5) & (windmph < 20))
    wind_contribution = xr.where(mask, ((windmph - 5) / 2.5), wind_contribution)
    mask = ((windmph >= 20) & (windmph < 30))
    wind_contribution = xr.where(mask, 4 + ((windmph - 20) / 10), wind_contribution)
    mask = windmph >= 30
    wind_contribution = xr.where(mask, 5, wind_contribution)               

#PRECIPITATION 
    # RAIN
    rain_contribution = xr.zeros_like(rain)
    mask = ((rain > 0) & (rain <= 0.4))
    rain_contribution = xr.where(mask, ((rain / 0.4) * 8), rain_contribution)
    mask = ((rain > 0.4) & (rain < 0.5))
    rain_contribution = xr.where(mask, 8 + (((rain - 0.4) / 0.1) * 2), rain_contribution)
    mask = rain >= 0.5
    rain_contribution = xr.where(mask, 10, rain_contribution)

    # SNOW
    snow_contribution = xr.zeros_like(snow)
    mask = ((snow > 0) & (snow <= 0.1))
    snow_contribution = xr.where(mask, ((snow / 0.1) * 2), snow_contribution)
    mask = ((snow > 0.1) & (snow <= 0.6))
    snow_contribution = xr.where(mask, 2 + (((snow - 0.1) / 0.5) * 5), snow_contribution)
    mask = ((snow > 0.6) & (snow < 1))
    snow_contribution = xr.where(mask, 7 + (((snow - 0.6) / 0.4) * 3), snow_contribution)
    mask = snow >= 1
    snow_contribution = xr.where(mask, 10, snow_contribution)

    # Combines the rain and snow contributions, but limits the index to only 10
    # Had to convert from xr.maximum() to np.maximum() since xr.maximum() did not work
    # Confirmed with AI that np.maximum() worked with my code
    precip_contribution = np.maximum(rain_contribution, snow_contribution)
    
    index = (temp_contribution + wind_contribution + precip_contribution)*(5)
    return index

# Coordinates for every NFL Stadium
Stadiums = {
        'State Farm\nStadium': (33.5276, -112.2626),
        'Mercedes-Benz Stadium': (33.7550, -84.4008),
        'M&T Bank Stadium': (39.2779, -76.6227),
        'HighMark Stadium': (42.7738, -78.7868),
        'Bank of America Stadium': (35.2251, -80.8529),
        'Soldier Field': (41.8623, -87.6167),
        'Paycor Stadium': (39.0954, -84.5160),
        'Huntington Bank Field': (41.5061, -81.6995),
        'AT&T Stadium': (32.7473, -97.0945),
        'Empower Field\nat Mile High': (39.7439, -105.0201),
        'Ford Field': (42.3400, -83.0456),
        'Lambeau Field': (44.5013, -88.0622),
        'NRG Stadium': (29.6847, -95.4107),
        'Lucas Oil Stadium': (39.7601, -86.1639),
        'TIAA Bank Field': (30.3239, -81.6373),
        'GEHA Field at\nArrowhead Stadium': (39.0489, -94.4849),
        'Allegiant Stadium': (36.0908, -115.1830),
        'SoFi Stadium': (33.9535, -118.3392),
        'Hard Rock Stadium': (25.9580, -80.2389),
        'U.S. Bank Stadium': (44.9738, -93.2575),
        'Gillette Stadium': (42.0909, -71.2643),
        'Caesars\nSuperdome': (29.9511, -90.0812),
        'Metlife Stadium': (40.8135, -74.0745),
        'Lincoln Financial Field': (39.9008, -75.1675),
        'Acrisure Stadium': (40.4468, -80.0158),
        "Levi's Stadium": (37.4030, -121.9700),
        'Lumen Field': (47.5952, -122.3316),
        'Raymond James Stadium': (27.9759, -82.5033),
        'Nissan Stadium': (36.1665, -86.7713),
        'Northwest Field': (38.9078, -76.8644),
    }
# All custom colormaps used for future plots
tcolors = ['#FFFFFF', '#FFD1DC', '#FF69B4', '#C71585', '#8A2BE2', '#1E90FF', '#40E0D0', '#7CFC00', '#FFFF00', '#FF8500', '#FF0000', '#B22222', '#800000']   
tcmap = LinearSegmentedColormap.from_list('temperature', tcolors)
rcolors = ["#00FF00", "#66FF00", "#CCFF00", "#FFFF00", "#FFCC00", "#FF9900",  "#FF4D00", "#FF0000",  "#CC00CC", "#8000FF"]
rain_cmap = mcolors.LinearSegmentedColormap.from_list("rain_radar", rcolors)
idxcolors = ["#2ECC71", "#A3E635", "#FDE047", "#F59E0B", "#EF4444", "#7F1D1D"]
idxcmap = mcolors.LinearSegmentedColormap.from_list("index_map", idxcolors)

# Create the base map
def makebasemap():
    fig = plt.figure(figsize=(24,18))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([-128, -65, 24, 47])  # CONUS
    ax.add_feature(cfeature.COASTLINE, edgecolor='lightblue')
    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.STATES, edgecolor='gray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
    
# Plot stadiums
    for stadium, (lat, lon) in Stadiums.items():
        ax.plot(lon, lat, marker='o', color='black', markersize=8,
                markeredgecolor='white', transform=ccrs.PlateCarree())
        ax.text(lon + 0.5, lat + 0.2, stadium, fontsize=8,
                fontweight='bold', transform=ccrs.PlateCarree())
    return fig, ax
    
# The following is the function for constructing the multiplot
def makemultiplot(x, y):
    # Creating the figure as four subplots, as well as naming the plots and stroing the stadiums
    fig, axes = plt.subplots(2, 2, figsize=(20, 10), subplot_kw={'projection': ccrs.PlateCarree()}, constrained_layout=True)
    axes=axes.flatten()
    plottitles = ["Index", "Apparent Temperature", "Wind Direction", "Precipitation"]


# This function is for calculating all of the necessary values to input into our index function
def variablecalc(data, fh):
    fh6 = fh // 6
    gd = data.isel(valid_time=fh6)  
    
    # Set initial and valid times to variables
    initial_datetime = pd.to_datetime(data.valid_time.values[0])
    itime = initial_datetime.strftime("%Hz %a %b %d %Y")
    valid_datetime = pd.to_datetime(data.valid_time.values[fh6])
    vtime = valid_datetime.strftime("%Hz %a %b %d %Y")

    # Adjust coordinates to make 
    gd = gd.assign_coords( longitude = (((gd.longitude + 180) % 360) - 180))
    gd=gd.sortby('longitude')
    
    # Temp and wind conversions
    tempF = (gd['t2m']- 273.15) * 9/5 + 32
    windms = np.sqrt(gd['u10']**2+gd['v10']**2)
    windmph=windms*2.237
    
    # Calculating wind chill 
    wc = (35.7 + 0.6215 * tempF - 35.75 * (windmph ** 0.16) + 0.4275 * tempF * (windmph ** 0.16))
    # Only applying wind chill to areas with temperatures uner 50F and wind > 3 mph
    wctemp = xr.where((tempF <= 50) & (windmph >= 3), wc, tempF)
    
    # Pulling relative humidity data and calculating heat index from NWS formula
    rh = gd['r2']
    hi = (-42.379 + 2.04901523 * tempF + 10.14333127 * rh - 0.22475541 * tempF * rh - 0.00683783 * tempF**2 - 0.05481717 * rh**2 + 0.00122874 * tempF**2 * rh +  0.00085282* tempF * rh**2 - 0.00000199 * tempF**2 * rh**2)
    # NWS formula contains adjustments under certain conditions; these were applied accordingly
    # Adjustment for when T is between 80F and 112F and RH < 13%
    adj1 = ((13 - rh) / 4) * np.sqrt(np.maximum(0, (17 - np.abs(tempF - 95.)) / 17))
    hi = xr.where((rh < 13) & (tempF >= 80) & (tempF <= 112), hi - adj1, hi)
    # Adjustment for when T is between 80F and 87F, and RH > 85%
    adj2 = ((rh - 85) / 10) * ((87 - tempF) / 5)
    hi = xr.where((rh > 85) & (tempF >= 80) & (tempF <= 87), hi + adj2, hi)
    # Combining original heat index and both adjustments into one group
    hitemp = xr.where(tempF >= 80, hi, tempF)
    # Applying both wind chill and heat index to create a map of real feel
    fl = xr.where(tempF <= 50, wctemp, xr.where(tempF >= 80, hitemp, tempF))
    
    #Create variables for the u component and v component of the wind directions
    u10 = gd["u10"]*1.94384 # Converts m/s to kts
    v10 = gd["v10"]*1.94384
    # Convert wind from u and v component vectors into a magnitude 
    wind_spd = np.sqrt(u10**2 + v10**2)
    
    # Rain Rate 'RPRATE', snow 'SPRATE'
    #Assign variables to the right forecast hour (16)
    rain = gd['prate'] * 141.73
    snow = gd['prate'] * 141.73 * 10
    lat = gd['latitude']
    lon = gd['longitude']
    crain = gd['crain']
    csnow = gd['csnow']
    
    #Mask the zero values 
    rain_mask = rain.where(crain >0)
    snow_mask = snow.where(csnow >0)  
    
    # Returning all variables as a dictionary to make access to variables easier
    return {'lat': lat, 'lon': lon, 'tempF': tempF, 'fl': fl, 'wind_mph': windmph, 'wind_spd': wind_spd, 'u10' : u10, 'v10': v10, 'rain':rain, 'snow':snow,
            'rain_mask': rain_mask, 'snow_mask': snow_mask, 'itime': itime, 'vtime': vtime}


# This function plots the index by itseld
def indexplot(data, fh):
    
    idxdata = variablecalc(data, fh)
    index = points(idxdata["fl"], idxdata["wind_mph"], idxdata["rain"], idxdata["snow"])
    fig, ax = makebasemap()
    idxcolors = ["#2ECC71", "#A3E635", "#FDE047", "#F59E0B", "#EF4444", "#7F1D1D"]
    ax.set_title(f"$\\bf{{{'GFS'}}}$ • NFL Stadium Harshness Index • Initialized: {idxdata['itime']} • Valid: {idxdata['vtime']}",loc = 'left', fontsize=15)
    idxcmap = mcolors.LinearSegmentedColormap.from_list("index_map", idxcolors)
    idxplot = ax.contourf(idxdata['lon'], idxdata['lat'], index, cmap=idxcmap, levels=np.arange(0, 101, 1), transform=ccrs.PlateCarree())
    idxbar = plt.colorbar(idxplot, ax=ax, orientation='horizontal', pad=0.01, fraction = .1, aspect = 100)
    idxbar.set_ticks(range(0, 101, 10))
    return fig, ax

# Function for downloading all plots of the index in a given model run
def saveplots(data):
    # This function selects all forecast hours in a model run and creates a plot of our index for each
    n = len(data.valid_time)
    for i in range(n):
        fh = i*6
        fig, ax = indexplot(data, fh)
        filename = os.path.join(OUTDIR, f'NFL_Harshness_{fh:03d}.png')
        # AI was used to find the function that saves the function, as well as defining what the other constraints do
        fig.savefig(filename, dpi=100, bbox_inches='tight')
        plt.close(fig)
def cleanupfiles(filepaths):
    for f in filepaths:
        os.remove(f)
def deletenetcdf(nc_path):
    os.remove(nc_path)
def deleteidx(directory, run):
    rundate = run.strftime('%Y%m%d')
    rundir=os.path.join(directory, "gfs", rundate)
    patterns = ['*.idx', 'subset_*']
    for pattern in patterns:
        files = glob.glob(os.path.join(rundir, pattern))
        for f in files:
            os.remove(f)
def deletefolder(basedir, run):
    rundir = os.path.join(basedir, "gfs", run.strftime("%Y%m%d"))
    shutil.rmtree(rundir)

run=latestrun()
fxxRange = range(0, 241, 6) # Herbie run and inventory 
FH = FastHerbie([run], model="gfs", product="pgrb2.0p50", fxx=fxxRange, save_dir='/home/bds5658/meteo473/sp26_groupwork/473_sp26_group9/data', overwrite=True) 
FH.inventory() # Defining a search string for the desired variables and downloading the associated GRIB files 
variableSearch = ":(TMP:2 m.*|UGRD:10 m.*|VGRD:10 m.*|APCP:surface|CSNOW|CRAIN|PRATE|RH:2 m.*):" 
fp = FH.download(variableSearch) # Extracting the data from each of the GRIB files and merging them into one variable using xarray 
# The data was broken into three subsets. ds1 is set to a height above ground of 2, specifically for 2m temperature. 
ds1 = xr.open_mfdataset(fp, engine = 'cfgrib', backend_kwargs={'filter_by_keys': {'typeOfLevel': 'heightAboveGround', 'level':2}}, combine='nested', concat_dim='valid_time') 
# ds2 is set to a level of 10, which was used for gathering 10m wind in the u and v directions. 
ds2 = xr.open_mfdataset(fp, engine = 'cfgrib', backend_kwargs={'filter_by_keys': {'typeOfLevel': 'heightAboveGround', 'level':10}}, combine='nested', concat_dim='valid_time') 
#ds3 is set to surface level, which is used to monitor the current precipitation at the surface (rain or snow). 
ds3 = xr.open_mfdataset(fp, engine = 'cfgrib', backend_kwargs={'filter_by_keys': {'typeOfLevel': 'surface', 'stepType':'instant'}}, combine='nested', concat_dim='valid_time') 
ds = xr.merge([ds1, ds2, ds3], compat = 'override')
ds = ds.load()# Used AI to fix the longitude range to match with cartopy 
ds = ds.assign_coords(longitude = (((ds.longitude + 180) % 360) - 180)) # Sorting the data chronologically and removing data outside of the continental US. 
ds = ds.sortby('valid_time') 
ds = ds.sel(latitude=slice(60,24), longitude=slice(-130, -65)) 
# Setting the file name and creating the NetCDF file from the data assigned to ds 
fname = 'NewestRun' 
path = f"/home/bds5658/meteo473/sp26_groupwork/473_sp26_group9/data/{fname}.nc" 
OUTDIR = "/home/bds5658/meteo473/sp26_groupwork/473_sp26_group9/webfiles/IndexPNGs"
os.makedirs(OUTDIR, exist_ok=True)
ds.to_netcdf(path)
newestdata = xr.open_dataset(path).load()
saveplots(newestdata)
newestdata.close()
deletenetcdf(path)
cleanupfiles(fp)
basedir="/home/bds5658/meteo473/sp26_groupwork/473_sp26_group9/data"
deletefolder(basedir, run)