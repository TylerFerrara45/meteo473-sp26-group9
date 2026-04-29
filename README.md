# Meteo 473 Threat Index — Group 9

## Project Description
We developed a harshness index for NFL games using GFS model data. We incorporated precipiation, apparent temperature, and wind velocity. Precipitation was derived using rain/snow locations and precipitation rate at those locations. Apparent temperature was derived using temperature and incorporating heat index or wind chill where it was necessary using relative humidity and wind speed. Wind has an impact no matter the temperature, so it was incorporated seperately, as well. 

Weather has a huge effect on outdoor NFL games. Apparent temperature can increase the throwing, kicking, and catching difficulty, which can instantly flip the style and play of the game. Precipitation, especially snow, can make it harder to throw, catch, and kick the ball, but it also has an effect on running. Usually in games with heavy precipitation, and especailly snow, often times teams hardly pass the ball, and the overall amount of scoring is decreased. Wind speed also has an effect on games, as higher wind speeds and fast changing wind directions can heavily increase the kicking difficulty, which increases the difficulty of making extra points and feild goals, which changes a game.

## Group Members
- Tyler Ferrara
- Ryan Fossella
- Benjamin Shank

## How to Run
1. Run `IndexGeneration.py`. This will download the necessary data, generate the index plots, and delete the leftover data.

## License
MIT
