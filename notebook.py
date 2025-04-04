import marimo

__generated_with = "0.11.31"
app = marimo.App(width="full")


@app.cell
def _(
    capacity_costs,
    diagram,
    file,
    get_main,
    input_data,
    mo,
    results_view,
    set_main,
    settings_view,
):
    # Main UI
    main_tab = mo.ui.tabs(
        {
            "Model": mo.vstack([file, input_data]),
            "Costs": capacity_costs,
            "Results": results_view,
            "Network": diagram,
            "Settings": settings_view,
            "Help": mo.md(open("README.md", "r").read()),
        },
        value=get_main(),
        on_change=set_main,
    )
    main_tab
    return (main_tab,)


@app.cell
def _(mo):
    get_main,set_main = mo.state("Model")
    return get_main, set_main


@app.cell
def _(mo):
    # Model load
    file = mo.ui.file(label="Open JSON model", kind='area',filetypes=[".json"])
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
def _(
    N,
    capcost_ui,
    curtailment_ui,
    file,
    gencost_ui,
    hint,
    mo,
    model,
    np,
    pd,
):
    # Optimal sizing result
    if file.value:
        _costdata = model.find("capacity", dict)
        if _costdata:
            gen_cost = np.zeros(N, dtype=complex)
            cap_cost = np.zeros(N)
            bus_name = []
            for x, y in _costdata.items():
                bus_name.append(y["parent"])
                _bus = model.property(y["parent"], "bus_i") - 1
                gen_cost[_bus] = model.property(x, "generator")
                cap_cost[_bus] = model.property(x, "capacitor")
            _showcost = pd.DataFrame(
                {"Generator ($/MVA)": gen_cost, "Capacitor ($/MVAr)": cap_cost},
                bus_name,
            )
        else:
            gen_cost = gencost_ui.value
            cap_cost = capcost_ui.value
            _showcost = mo.vstack([mo.md("No bus-level cost data found. Using the following settings instead:"), gencost_ui, capcost_ui,curtailment_ui])
        capacity_costs = mo.vstack([mo.md("# Capacity costs"), _showcost])
    else:
        capacity_costs = mo.vstack([file, hint("open your JSON model")])
    return bus_name, cap_cost, capacity_costs, gen_cost, x, y


@app.cell
def _(mo):
    get_result,set_result = mo.state("Initial optimal powerflow")
    return get_result, set_result


@app.cell
def _(get_optimal, get_result, mo, original, set_result, sizing):
    # Results UI
    results_tab = mo.ui.tabs(
        {
            "Initial optimal powerflow": original,
            "Optimal sizing/placement solution": sizing,
            "Final optimal powerflow": get_optimal(),
        },
        value=get_result(),
        on_change=set_result,
    )
    return (results_tab,)


@app.cell
def _(file, hint, mo, results_tab):
    if file.value:
        results_view = mo.vstack([results_tab])
    else:
        results_view = mo.vstack([file, hint("open your JSON model")])
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
                mo.md(f"**Cost of solution**: ${result['cost']:,.2f}"),
                pd.DataFrame(
                    data={
                        "Total": [
                            format(abs(result["curtailment"].sum()),suffix="MW"),
                            format(sum([abs(x) for x in result["generation"]]),suffix="MVA"),
                            format(abs(result["capacitors"].sum()),suffix="MVAr"),
                            format(abs(result["flows"]).sum(),suffix="MVA"),
                            "-",
                            "-",
                        ],
                        "Mean": [
                            format(abs(result["curtailment"].sum())/N,suffix="MW"),
                            format(sum([abs(x) for x in result["generation"]])/N,suffix="MVA"),
                            format(abs(result["capacitors"].sum())/N,suffix="MVAr"),
                            format(abs(result["flows"]).mean(),suffix="MVA"),
                            format(abs(sum([x for x, y in result["voltage"]]) / N),suffix="V"),
                            format(sum([y for x, y in result["voltage"]]) / N,suffix="deg"),
                        ],
                        "Minimum": [
                            format(abs(result["curtailment"].min()),suffix="MW"),
                            format(min([abs(x) for x in result["generation"]]),suffix="MVA"),
                            format(abs(result["capacitors"].min()),suffix="MVAr"),
                            format(abs(result["flows"].min()),suffix="MVA"),
                            format(abs(min([x for x, y in result["voltage"]])),suffix="V"),
                            format(min([y for x, y in result["voltage"]]),suffix="deg"),
                        ],
                        "Maximum": [
                            format(abs(result["curtailment"].max()),suffix="MW"),
                            format(max([abs(x) for x in result["generation"]]),suffix="MVA"),
                            format(abs(result["capacitors"].max()),suffix="MVAr"),
                            format(abs(result["flows"].max()),suffix="MVA"),
                            format(abs(max([x for x, y in result["voltage"]])),suffix="V"),
                            format(max([y for x, y in result["voltage"]]),suffix="deg"),
                        ],
                    },
                    index=[
                        "Curtailment",
                        "Generation",
                        "Capacitors",
                        "Line flow",
                        "Voltage magnitude",
                        "Voltage angle",
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
def _(
    curtailment_ui,
    error,
    file,
    get_result,
    json,
    mo,
    model,
    os,
    problem_ui,
    results,
    solver_ui,
    verbose_ui,
):
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
            with mo.capture_stderr() as _stderr:
                with mo.capture_stdout() as _stdout:
                    _result = results(
                        model,
                        model.optimal_powerflow(
                            verbose=verbose_ui.value,
                            curtailment_price=curtailment_ui.value,
                            solver=solver_ui.value,
                        ),
                    )
            _output = _stdout.getvalue() + _stderr.getvalue()
            original = mo.vstack(
                [
                    _result,
                    initial_download_ui,
                    mo.md(f"""~~~\n{_output}\n~~~""" if verbose_ui.value else ""),
                ]
            )
        except Exception as err:
            _output = _stdout.getvalue() + _stderr.getvalue()
            original = mo.vstack(
                [
                    mo.hstack([error(err), verbose_ui, problem_ui], justify="start"),
                    mo.md(f"""~~~\n{_output}\n~~~""" if verbose_ui.value else ""),
                ]
            )
    else:
        original = mo.md("")
    if problem_ui.value and get_result() == "Initial optimal powerflow":
        mo.output.append(mo.md("---"))
        mo.output.append(f"{get_result()} problem data")
        mo.output.append(model.problem)
    return initial_download_ui, original


@app.cell
def _(
    cap_cost,
    copy,
    demand_margin_ui,
    error,
    file,
    gen_cost,
    get_result,
    json,
    mo,
    model,
    os,
    problem_ui,
    results,
    solver_ui,
    verbose_ui,
):
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
            with mo.capture_stderr() as _stderr:
                with mo.capture_stdout() as _stdout:
                    _result = results(
                        osp_model,
                        osp_model.optimal_sizing(
                            gen_cost=gen_cost,
                            cap_cost=cap_cost,
                            refresh=True,
                            update_model=True,
                            verbose=verbose_ui.value,
                            solver=solver_ui.value,
                            margin=demand_margin_ui.value/100,
                        ),
                    )
            _output = _stdout.getvalue() + _stderr.getvalue()
            sizing = mo.vstack(
                [
                    _result,
                    osp_download_ui,
                    mo.md(f"""~~~\n{_output}\n~~~""" if verbose_ui.value else ""),
                ]
            )
        except Exception as err:
            _output = _stdout.getvalue() + _stderr.getvalue()
            sizing = mo.vstack(
                [
                    mo.hstack([error(err),verbose_ui,problem_ui],justify='start'),
                    mo.md(f"""~~~\n{_output}\n~~~""" if verbose_ui.value else ""),
                ]
            )
    else:
        sizing = mo.md("")
    if problem_ui.value and get_result() == "Optimal sizing/placement solution":
        mo.output.append(mo.md("---"))
        mo.output.append(f"{get_result()} problem data")
        mo.output.append(osp_model.problem)
    return osp_download_ui, osp_model, sizing


@app.cell
def _(mo):
    get_optimal,set_optimal = mo.state(None)
    return get_optimal, set_optimal


@app.cell
def _(
    copy,
    curtailment_ui,
    error,
    file,
    get_result,
    json,
    mo,
    os,
    osp_model,
    problem_ui,
    results,
    set_optimal,
    solver_ui,
    verbose_ui,
):
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
            with mo.capture_stderr() as _stderr:
                with mo.capture_stdout() as _stdout:
                    _result = opf_model.optimal_powerflow(
                        refresh=True,
                        verbose=verbose_ui.value,
                        curtailment_price=curtailment_ui.value,
                        solver=solver_ui.value,
                    )
            _output = _stdout.getvalue() + _stderr.getvalue()
            set_optimal(mo.vstack(
                [
                    results(
                        opf_model,
                        _result,
                    ),
                    final_download_ui,
                    mo.md(f"""~~~\n{_output}\n~~~""" if verbose_ui.value else ""),
                ]
            ))
        except Exception as err:
            _output = _stdout.getvalue() + _stderr.getvalue()
            set_optimal(mo.vstack(
                [
                    mo.hstack([error(err), verbose_ui,problem_ui], justify="start"),
                    mo.md(f"""~~~\n{_output}\n~~~""" if verbose_ui.value else ""),
                ]
            ))
    else:
        set_optimal(mo.md(""))
    if problem_ui.value and get_result() == "Final optimal powerflow":
        mo.output.append(mo.md("---"))
        mo.output.append(f"{get_result()} problem data")
        mo.output.append(opf_model.problem)
    return final_download_ui, opf_model


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
def _(mo):
    # Solver settings
    verbose_ui = mo.ui.checkbox(label="**Enable verbose output**")
    solver_ui = mo.ui.dropdown(
        label="**Preferred solver**:",
        options=["CLARABEL", "OSQP"],
        value="CLARABEL",
        allow_select_none=False,
    )
    problem_ui = mo.ui.checkbox(label="**Show problem data**")
    osqp_max_iter = mo.ui.slider(
        label="**Maximum iterations**:",
        steps=[10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000],
        value=10000,
        debounce=True,
    )
    osqp_eps_abs = mo.ui.slider(
        label="**Absolute epsilon (10^)**:",
        steps=range(-10, 1),
        value=-5,
        debounce=True,
        show_value=True,
    )
    osqp_eps_rel = mo.ui.slider(
        label="**Relative epsilon (10^)**:",
        steps=range(-10, 1),
        value=-5,
        debounce=True,
        show_value=True,
    )
    clarabel_max_iter = mo.ui.slider(
        label="**Maximum iterations**:",
        steps=[10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000],
        value=10000,
        debounce=True,
        show_value=True,
    )
    clarabel_time_limit = mo.ui.slider(
        label="**Time limit (s)**:",
        start=0,
        stop=3600,
        step=10,
        value=0,
        debounce=True,
        show_value=True,
    )
    solver_options = {
        "OSQP": [osqp_max_iter, osqp_eps_abs, osqp_eps_rel],
        "CLARABEL": [clarabel_max_iter,clarabel_time_limit],
    }
    return (
        clarabel_max_iter,
        clarabel_time_limit,
        osqp_eps_abs,
        osqp_eps_rel,
        osqp_max_iter,
        problem_ui,
        solver_options,
        solver_ui,
        verbose_ui,
    )


@app.cell
def _(mo):
    # Capacity costs
    gencost_ui = mo.ui.slider(
        label="**Generation cost**: ($/MVA)",
        start=0,
        stop=10000,
        step=100,
        value=1000,
        show_value=True,
        debounce=True,
    )
    capcost_ui = mo.ui.slider(
        label="**Capacitor cost**: ($/MVAr)",
        start=0,
        stop=1000,
        step=10,
        value=100,
        show_value=True,
        debounce=True,
    )
    return capcost_ui, gencost_ui


@app.cell
def _(gencost_ui, mo, np):
    # Curtailment settings
    curtailment_ui = mo.ui.slider(
        label="**Curtailment cost**: ($/MW)",
        steps=np.array([0, 0.01,0.02,0.05,0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100],dtype=float)
        * gencost_ui.value,
        value = 10*gencost_ui.value,
        debounce=True,
        show_value=True,
    )
    demand_margin_ui = mo.ui.slider(
        label="**Load capacity margin**: (%)",
        start=0,
        stop=100,
        value=20,
        debounce=True,
        show_value=True,
    )
    return curtailment_ui, demand_margin_ui


@app.cell
def _(mo):
    # Graph settings
    voltage_ui = mo.ui.range_slider(label="**Voltage limits**: (pu.V)",start=0.5,stop=1.5,step=0.01,value=[0.95,1.05],debounce=True,show_value=True)
    current_ui = mo.ui.slider(label="**High flow**: (kA)",steps=[0,1,2,5,10,20,50,100,200,500,1000,2000,5000,10000],value=1000,debounce=True,show_value=True)
    showbusdata_ui = mo.ui.checkbox(label="**Show bus data**")
    return current_ui, showbusdata_ui, voltage_ui


@app.cell
def _(
    capcost_ui,
    current_ui,
    curtailment_ui,
    demand_margin_ui,
    gencost_ui,
    mo,
    problem_ui,
    showbusdata_ui,
    solver_options,
    solver_ui,
    verbose_ui,
    voltage_ui,
):
    # Setting tabs
    settings_view = mo.accordion(
        {"**Optimizer**":
            mo.vstack(
                [
                    solver_ui,
                    verbose_ui,
                    problem_ui]+solver_options[solver_ui.value]
                ),
         "**Capacity costs**":
                mo.vstack([
                    gencost_ui,
                    capcost_ui,
                    curtailment_ui,
                ]),
         "**Loads**":
             mo.vstack([
                 demand_margin_ui,
             ]),
         "**Network**":
             mo.vstack([voltage_ui,current_ui,showbusdata_ui]),
        },
        multiple=True,
        lazy=True,
    )
    return (settings_view,)


@app.cell
def _(file, mo, model, opf_model, osp_model):
    if file.value:
        graph_model_ui = mo.ui.radio(
            label="**Model**:",
            options={"Original": model, "Capacity": osp_model, "Optimal": opf_model},
            value="Original",
            inline=True,
        )
        graph_orientation_ui = mo.ui.radio(
            label="**Orientation**:",
            options={"Horizontal": "horizontal", "Vertical": "vertical"},
            value="Vertical",
            inline=True,
        )
        graph_label_ui = mo.ui.dropdown(
            label="**Bus labels**:",
            options={"Name":None,
                     "Id":"id",
                     "|V|":"Vm",
                     "<V":"Va",
                     "Type":"type",
                     "Area":"area",
                     "Zone":"zone"
                    },
            value="Name"
        )
    return graph_label_ui, graph_model_ui, graph_orientation_ui


@app.cell
def _(
    current_ui,
    file,
    graph_label_ui,
    graph_model_ui,
    graph_orientation_ui,
    hint,
    mo,
    showbusdata_ui,
    voltage_ui,
):
    # Network graph

    if file.value:
        _diagram = graph_model_ui.value.mermaid(
            orientation=graph_orientation_ui.value,
            label=graph_label_ui.value,
            undervolt=voltage_ui.value[0],
            overvolt=voltage_ui.value[1],
            highflow=current_ui.value,
            showbusdata=showbusdata_ui.value,
            )
        diagram = mo.vstack(
            [
                mo.hstack(
                    [graph_model_ui, graph_label_ui, graph_orientation_ui,showbusdata_ui],
                    align="stretch",
                ),
                mo.mermaid(_diagram),
            ]
        )
    else:
        diagram = mo.vstack([file, hint("open your JSON model")])
    return (diagram,)


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
        import pypower
    else:
        import subprocess
        subprocess.run([sys.executable,"-m","pip","install","-r","requirements.txt"],capture_output=True)
    import gld_pypower as gld
    return copy, cvxpy, gld, json, mo, np, os, pd, pypower, subprocess, sys


if __name__ == "__main__":
    app.run()
