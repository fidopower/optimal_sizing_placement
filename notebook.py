import marimo

__generated_with = "0.11.31"
app = marimo.App(width="medium")


@app.cell
def _(capacity_costs, file, input_data, mo, results_view):
    # Main UI
    mo.ui.tabs({
        "Model":mo.vstack([file,input_data]),
        "Costs":capacity_costs,
        "Results":results_view,
        "Help":mo.md(open("README.md","r").read())
    })
    return


@app.cell
def _(mo):
    # Model load
    file = mo.ui.file(label="Open JSON model", filetypes=[".json"])
    return (file,)


@app.cell
def _(file, header_ui, hint, mo, model, os, pd):
    # File upload
    def _noheader(x):
        return {y: z for y, z in x.items() if y not in model.data["header"]}

    if file.value:
        input_data = mo.vstack(
            [
                mo.md("# Input Data"),
                mo.hstack(
                    [
                        mo.md(f"<B>Model name</B>: {os.path.split(model.name)[1]}"),
                        header_ui,
                    ],
                ),
                mo.ui.tabs(
                    {
                        x: pd.DataFrame(
                            {
                                y: z if header_ui.value else _noheader(z)
                                for y, z in model.find(x, dict).items()
                            }
                        ).transpose()
                        for x in list(model.data["classes"])
                    }
                ),
            ],
        ) 
    else:
        input_data = hint("open your JSON model")
    return (input_data,)


@app.cell
def _(mo):
    # Header checkbox
    header_ui = mo.ui.checkbox(label="Show header data")
    return (header_ui,)


@app.cell
def _(N, capcost_ui, file, gencost_ui, hint, mo, model, np, pd):
    # Optimal sizing result
    if file.value:
        _costdata = model.find("capacity",dict)
        if _costdata:
            gen_cost = np.zeros(N,dtype=complex)
            cap_cost = np.zeros(N)
            bus_name = []
            for x,y in _costdata.items():
                bus_name.append(y["parent"])
                _bus = model.property(y["parent"],"bus_i")-1
                gen_cost[_bus] = model.property(x,"generator")
                cap_cost[_bus] = model.property(x,"capacitor")
            _showcost = pd.DataFrame({"Generator ($/MW)":gen_cost,"Capacitor ($/MVAr)":cap_cost},bus_name)
        else:
            gen_cost = gencost_ui.value
            cap_cost = capcost_ui.value
            _showcost = mo.hstack([gencost_ui,capcost_ui],justify='start')
        capacity_costs = mo.vstack([mo.md("# Capacity costs"),_showcost]) 
    else:
        capacity_costs = mo.vstack([file,hint("open your JSON model")])
    return bus_name, cap_cost, capacity_costs, gen_cost, x, y


@app.cell
def _(file, hint, mo, optimal, original, sizing):
    # Results UI
    if file.value:
        results_view = mo.ui.tabs({
            "Initial optimal powerflow":original,
            "Optimal sizing/placement solution":sizing,
            "Final optimal powerflow":optimal,
        })
    else:
        results_view = mo.vstack([file,hint("open your JSON model")])
    return (results_view,)


@app.cell
def _(error, exception, file, gld, mo):
    # Model check
    if file.value:
        try:
            model = gld.Model(file.contents(0).decode("utf-8"))
        except Exception as err:
            mo.stop(True, exception(err))
        _check = model.validate()
        mo.stop(_check, error(_check))
        N = len(model.find("bus", list))
        K = len(model.find("branch", list))
    return K, N, model


@app.cell
def _(K, N, mo, np, pd):
    # Result formatting
    def format(x,prefix="",suffix=""):
        if isinstance(x, list):
            return f"{prefix} {x[0]:.1f}<{x[1]:.1f} {suffix}"
        if isinstance(x, complex):
            return f"{prefix} {x.real:.1f}{x.imag:+.1f}j {suffix}"
        return f"{prefix} {x:.1f} {suffix}"


    def results(model, result):
        if "curtailment" not in result:
            result["curtailment"] = np.zeros(N)
        return mo.vstack(
            [
                mo.md("# Summary Data"),
                mo.md(f"**Cost of solution**: ${result['cost']:.2f}"),
                pd.DataFrame(
                    data={
                        "Total/Mean": [
                            format(abs(result["curtailment"].sum()),suffix="MW"),
                            format(sum([abs(x) for x in result["generation"]]),suffix="MW"),
                            format(abs(result["capacitors"].sum()),suffix="MVAr"),
                            format(abs(sum([x for x, y in result["voltage"]]) / N),suffix="V"),
                            format(sum([y for x, y in result["voltage"]]) / N,suffix="deg"),
                            format(abs(result["flows"].mean()),suffix="MW"),
                        ],
                        "Minimum": [
                            format(abs(result["curtailment"].min()),suffix="MW"),
                            format(min([abs(x) for x in result["generation"]]),suffix="MW"),
                            format(abs(result["capacitors"].min()),suffix="MVAr"),
                            format(abs(min([x for x, y in result["voltage"]])),suffix="V"),
                            format(min([y for x, y in result["voltage"]]),suffix="deg"),
                            format(abs(result["flows"].min()),suffix="MW"),
                        ],
                        "Maximum": [
                            format(abs(result["curtailment"].max()),suffix="MW"),
                            format(max([abs(x) for x in result["generation"]]),suffix="MW"),
                            format(abs(result["capacitors"].max()),suffix="MVAr"),
                            format(abs(max([x for x, y in result["voltage"]])),suffix="V"),
                            format(max([y for x, y in result["voltage"]]),suffix="deg"),
                            format(abs(result["flows"].max()),suffix="MW"),
                        ],
                    },
                    index=[
                        "Curtailment",
                        "Generation",
                        "Capacitors",
                        "Voltage magnitude",
                        "Voltage angle",
                        "Line flow",
                    ],
                ),
                mo.md("# Network Data"),
                mo.hstack(
                    [
                        pd.DataFrame(
                            data={
                                x: [format(z) for z in y.tolist()]
                                for x, y in result.items()
                                if isinstance(y, np.ndarray) and len(y) == N
                            },
                            index=model.get_name("bus"),
                        ),
                        pd.DataFrame(
                            data={
                                x: [format(z) for z in y.tolist()]
                                for x, y in result.items()
                                if isinstance(y, np.ndarray) and len(y) == K
                            },
                            index=model.get_name("branch"),
                        ),
                    ]
                ),
            ],
        )
    return format, results


@app.cell
def _(error, file, json, mo, model, os, results):
    # Initial powerflow result
    if file.value:
        try:
            _name = os.path.split(model.name)[1]
            _name = os.path.splitext(_name)
            _name = f"{_name[0]}_opf_initial.json"
            initial_download_ui = mo.download(
                json.dumps(model.data, indent=4),
                mimetype="application/json",
                filename=_name,
                label=f"Save optimal <U>{_name}</U>",
            )
            original = mo.vstack([results(model, model.optimal_powerflow()),initial_download_ui])
        except Exception as err:
            original = error(err)
    else:
        original = mo.md("")
    return initial_download_ui, original


@app.cell
def _(mo):
    # Capacity costs
    gencost_ui = mo.ui.slider(
        label="<B>Generation cost</B>: ($/MW)",
        start=0,
        stop=10000,
        step=100,
        value=1000,
        show_value=True,
        debounce=True,
    )
    capcost_ui = mo.ui.slider(
        label="<B>Capacitor cost</B>: ($/MW)",
        start=0,
        stop=1000,
        step=10,
        value=100,
        show_value=True,
        debounce=True,
    )
    return capcost_ui, gencost_ui


@app.cell
def _(cap_cost, copy, error, file, gen_cost, json, mo, model, os, results):
    # Optimal sizing and placement
    if file.value:
        osp_model = copy.deepcopy(model)
        try:
            _name = os.path.split(osp_model.name)[1]
            _name = os.path.splitext(_name)
            _name = f"{_name[0]}_osp.json"
            osp_download_ui = mo.download(
                json.dumps(osp_model.data, indent=4),
                mimetype="application/json",
                filename=_name,
                label=f"Save optimal <U>{_name}</U>",
            )
            sizing = mo.vstack(
                [
                    results(
                        osp_model,
                        osp_model.optimal_sizing(
                            gen_cost=gen_cost,
                            cap_cost=cap_cost,
                            refresh=True,
                            update_model=True,
                        ),
                    ),
                    osp_download_ui
                ]
            )
        except Exception as err:
            sizing = error(err)
    else:
        sizing = mo.md("")
    return osp_download_ui, osp_model, sizing


@app.cell
def _(copy, error, file, json, mo, os, osp_model, results):
    # Final powerflow result
    if file.value:
        opf_model = copy.deepcopy(osp_model)
        try:
            _name = os.path.split(opf_model.name)[1]
            _name = os.path.splitext(_name)
            _name = f"{_name[0]}_opf_final.json"
            final_download_ui = mo.download(
                json.dumps(opf_model.data, indent=4),
                mimetype="application/json",
                filename=_name,
                label=f"Save optimal <U>{_name}</U>",
            )
            optimal = mo.vstack(
                [
                    results(opf_model, opf_model.optimal_powerflow(refresh=True)),
                    final_download_ui,
                ]
            )
        except Exception as err:
            optimal = error(err)
    else:
        optimal = mo.md("")
    return final_download_ui, opf_model, optimal


@app.cell
def _(mo):
    # Message formatting
    def message(msg, kind=None, color="black", background="white"):
        if not kind:
            return mo.md(
                f'<font color={color} style="background:{background}">{msg}</font>'
            )
        else:
            return mo.md(
                f'<font color={color} style="background:{background}"><b>{kind}</b>: {msg}</font>'
            )


    def hint(msg):
        return message(msg, "HINT", "blue", "white")


    def warning(msg):
        return message(msg, "WARNING", "blue", "yellow")


    def error(msg):
        return message(msg, "ERROR", "red", "white")


    def exception(msg):
        return message(msg, "EXCEPTION", "red", "yellow")
    return error, exception, hint, message, warning


@app.cell
def _():
    # Notebook setup
    import marimo as mo
    import os
    import sys
    import json
    import pandas as pd
    import numpy as np
    import copy
    if os.environ["HOME"] == "/home/pyodide":
        # cannot import from requirements.txt in WASM
        import cvxpy
    else:
        import subprocess
        subprocess.run([sys.executable,"-m","pip","install","-r","requirements.txt"],capture_output=True)
    import gld_pypower as gld
    return copy, cvxpy, gld, json, mo, np, os, pd, subprocess, sys


if __name__ == "__main__":
    app.run()
