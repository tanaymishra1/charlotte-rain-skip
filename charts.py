import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from rain_skip import load_data, recent_rain, rule_days, timer_days


def main():
    data = load_data()
    timer = timer_days(data)
    timer["after_rain"] = timer.apply(recent_rain, axis=1)

    years = sorted(timer["date"].dt.year.unique())
    timer_count = timer.groupby(timer["date"].dt.year).size()
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
    width = 0.4
    plt.figure(figsize=(8, 4))
    for shift, sensor, color, label in [
        (-width / 2, False, "#4a9b5f", "Past rain only"),
        (width / 2, True, "#2f6b8f", "Knows today's rain"),
    ]:
        rule = rule_days(data, sensor)
        saved = timer_count - rule.groupby(rule["date"].dt.year).size()
        plt.bar([y + shift for y in years], saved, width, color=color, label=label)
    plt.title(f"Waterings saved each season (out of {timer_count.iloc[0]} timer waterings)")
    plt.ylabel("Waterings saved")
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xticks(years)
    plt.legend()
    plt.tight_layout()
    plt.savefig("figures/waterings_saved.png", dpi=150)

    print("Saved charts to figures/")


if __name__ == "__main__":
    main()
