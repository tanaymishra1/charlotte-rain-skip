# charlotte-rain-skip

How often does a sprinkler timer in Charlotte, NC water right after it already rained? And how much would a simple rain-aware schedule actually save? I used 10 years of NOAA weather data (2016 to 2025) to find out.

I made this as a starting point for a bigger project I have in mind: an irrigation controller that decides when to water using weather and soil data. I wanted some experience with this kind of weather data first.

## Results

A timer that waters every 3 days from April to October would water 720 times over the 10 seasons. 111 of those waterings (15.4%) came right after a day with at least half an inch of rain.

![Percent of timer waterings that came right after rain, by year](figures/after_rain_by_year.png)

A rule that only waters when it's been 3 days since the garden last got water, from the sprinkler or from real rain, would water 651 times. That saves 69 waterings, or 9.6%.

![Waterings saved by the rain-aware rule each year](figures/waterings_saved.png)

The part that surprised me most is that gap. About 15% of timer waterings happen right after rain, but skipping them only saves about 10%. A skipped watering doesn't always disappear. Often it just gets pushed back a day or two.

## How it works

prepare_data.py takes NOAA's daily file for Charlotte Douglas Airport, keeps 2016 to 2025 and converts the units. The data folder has its own README with the source and columns.

rain_skip.py simulates both schedules. The timer waters every third day from April 1 to October 31. A watering counts as "right after rain" if either of the 2 days before it had 0.5 inches or more. The rain-aware rule keeps a count of days since the garden last got water and resets it after a watering or a day with 0.5 inches of rain. The settings are at the top of the file if you want to try different numbers.

charts.py makes the two charts above.

rain_model.py trains the rain model described below, cross-validates it, tests it and draws its ROC curve.

## Running it

```
pip install pandas matplotlib scikit-learn
python rain_skip.py
python charts.py
python rain_model.py
```

## Can a model look ahead?

I also trained a model to guess whether tomorrow will get at least half an inch of rain, using today's weather: rain, temperature, humidity, pressure, wind, dew point and the month. It's a gradient-boosted decision tree model from scikit-learn. I checked it two ways: 5-fold cross-validation on 2016 to 2022, with folds in time order so the model never trains on the future, and a final test on 2023 to 2025.

It didn't work well. Its AUC was 0.63 in cross-validation and 0.61 on the test years, where 0.5 is random guessing and 1.0 is perfect.

![ROC curve for the rain model](figures/rain_model_roc.png)

Accuracy makes it look better than it is. Big rain followed only 7.9% of days, so guessing "no big rain" every day is right 92.1% of the time. A random 50/50 guess is right 50% of the time, and a random guess at the real rate is right 85.4%. The model was right 92.1% of the time at a 50% cutoff, which only ties with always guessing no.

Using it to delay watering didn't help either. With a 20% cutoff, the model told the schedule to wait 11 times, and big rain came only 3 of those times. With a 10% cutoff it waited 66 times and was right 9 times.

I also tried more features, smaller trees, balancing the classes and a logistic regression. None of them got past an AUC of about 0.63 in cross-validation. So predicting tomorrow's rain well isn't really possible with one station's daily numbers. For the irrigation controller, a real weather forecast will probably work better than a model trained only on this data.

## Limits

The weather data comes from one station at the airport, so it won't match every yard in Charlotte. The simulation only looks at rain. It ignores soil type, heat, sun and what's planted, and it assumes half an inch of rain is enough to skip a watering.

## What I learned

This was my first time building a simulation. I also learned how to use shift() and groupby() in pandas, and that a model has to beat a simple guess before it's worth using.

## Next steps

- Running the same check for nearby cities
- Testing a real weather forecast instead of my own rain model
- Using this as a starting point for my irrigation controller

## License

MIT
