import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    trips_per_day = 30
    return (trips_per_day,)


@app.cell
def _(trips_per_day):
    doubled = trips_per_day * 2
    return (doubled,)


@app.cell
def _(doubled):
    print(doubled)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
