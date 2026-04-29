# Meteo 473 Threat Index — Group 9

## Project Description
We developed a harshness index for NFL games using GFS model data. We incorporated precipiation, apparent temperature, and wind velocity. Precipitation was derived using rain/snow locations and precipitation rate at those locations. Apparent temperature was derived using temperature and incorporating heat index or wind chill where it was necessary using relative humidity and wind speed. Wind has an impact no matter the temperature, so it was incorporated seperately, as well. 

## Group Members
- Tyler Ferrara
- Ryan Fossella
- Benjamin Shank

## How to Run
1. Run `IndexGeneration.py`. This will download the necessary data, generate the index plots, and delete the leftover data.

## License
MIT