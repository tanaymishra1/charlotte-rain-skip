import matplotlib.pyplot as plt

from rain_skip import RAIN_LIMIT, load_data, rule_days, timer_days

data = load_data()
timer = timer_days(data)
timer["after_rain"] = timer["rain_recent"] >= RAIN_LIMIT
rule = rule_days(data)

years = sorted(timer["date"].dt.year.unique())
timer_count = timer.groupby(timer["date"].dt.year).size()
rule_count = rule.groupby(rule["date"].dt.year).size()
percent = timer.groupby(timer["date"].dt.year)["after_rain"].mean() * 100

# chart 1
plt.figure(figsize=(8, 4))
plt.bar(years, percent, color="#4a7fb5")
plt.title("Timer waterings that came right after real rain (Charlotte, Apr-Oct)")
plt.ylabel("% of timer waterings")
plt.xticks(years)
plt.tight_layout()
plt.savefig("figures/after_rain_by_year.png", dpi=150)

# chart 2
saved = timer_count - rule_count
plt.figure(figsize=(8, 4))
plt.bar(years, saved, color="#4a9b5f")
plt.title("Waterings saved by the rain-aware rule each season (out of 72)")
plt.ylabel("Waterings saved")
plt.xticks(years)
plt.tight_layout()
plt.savefig("figures/waterings_saved.png", dpi=150)

print("Saved charts to figures/")
