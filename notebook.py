import marimo

__generated_with = "0.16.5"
app = marimo.App(width="full", app_title="Optimal Powerflow/Sizing/Placement")


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(
    capacity_costs,
    diagram,
    file,
    get_main,
    help_view,
    input_data,
    mo,
    results_view,
    set_main,
    settings_view,
):
    1#Main UI


    main_tab = mo.ui.tabs(
        {
            "Model": mo.vstack([file, input_data]),
            "Costs": capacity_costs,
            "Results": results_view,
            "Network": diagram,
            "Settings": settings_view,
            "Help": help_view,
        },
        value=get_main(),
        on_change=set_main,
    )
    main_tab
    return


@app.cell(hide_code=True)
def _(mo):
    # Main tab state
    get_main, set_main = mo.state("Model")
    return get_main, set_main


@app.cell
def _(mo):
    # Model load
    file = mo.ui.file(label="Open JSON model", kind="area", filetypes=[".json"])
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
                        mo.md(
                            f"<B>Model name</B>: {os.path.split(model.name)[1]}"
                        ),
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
    concost_ui,
    curtailment_ui,
    file,
    gencost_ui,
    hint,
    mo,
    model,
    np,
    pd,
    substation_construction_cost_ui,
    substation_upgrade_cost_ui,
):
    # Optimal sizing result
    if file.value:
        _costdata = model.find("capacity", dict)
        if _costdata:
            gen_cost = np.zeros(N, dtype=complex)
            cap_cost = np.zeros(N)
            con_cost = np.zeros(N)

            bus_name = []
            for x, y in _costdata.items():
                bus_name.append(y["parent"])
                _bus = model.get_property(y["parent"], "bus_i") - 1
                gen_cost[_bus] = model.get_property(x, "generator")
                cap_cost[_bus] = model.get_property(x, "capacitor")
                con_cost[_bus] = model.get_property(x, "condenser")

            _showcost = pd.DataFrame(
                {
                    "Generator ($/MVA)": gen_cost, 
                    "Capacitor ($/MVAr)": cap_cost,
                    "Condenser ($/MVAr)": con_cost,
                },
                bus_name,
            )

        else:
            gen_cost = gencost_ui.value
            cap_cost = capcost_ui.value
            con_cost = concost_ui.value

            _showcost = mo.vstack(
                [
                    mo.md(
                        "No bus-level cost data found. Using the following settings instead:"
                    ),
                    gencost_ui,
                    capcost_ui,
                    concost_ui,
                    curtailment_ui,
                    substation_upgrade_cost_ui,
                    substation_construction_cost_ui
                ]
            )

        capacity_costs = mo.vstack([mo.md("# Capacity costs"), _showcost])

        try: 
            substation_upgrade_cost = float(substation_upgrade_cost_ui.value)
        except Exception as e: 
            print(f"Invalid value entered in textbox for {substation_upgrade_cost_ui.value=}  setting substation upgrade cost at 0 ")
            #print(e)
            substation_upgrade_cost = 0


        try: 
            substation_construction_cost= float(substation_construction_cost_ui.value)

        except Exception as e: 
            print(f"Invalid value entered in textbox for {substation_construction_cost_ui.value=} setting substation construction cost to infinity")
            #print(e)

            substation_construction_cost = np.inf  #infinite costs to construct a substation at a location without substations 

    else:
        capacity_costs = mo.vstack([file, hint("open your JSON model")])
    return (
        cap_cost,
        capacity_costs,
        con_cost,
        gen_cost,
        substation_construction_cost,
        substation_upgrade_cost,
    )


@app.cell
def _(mo):
    # Result state
    get_result, set_result = mo.state("Initial optimal powerflow")
    return get_result, set_result


@app.cell
def _(mo):
    mo.md(r"""### Diagnostic View (New Code)""")
    return


@app.cell
def _(
    get_optimal,
    get_result,
    mo,
    original,
    per_component_duals_view,
    per_component_view,
    set_result,
    sizing,
    summary_view,
):
    # Results UI
    # results_tab = mo.ui.tabs(
    #     {
    #         "Initial optimal powerflow": original,
    #         "Optimal sizing/placement solution": sizing,
    #         "Final optimal powerflow": get_optimal(),
    #     },
    #     value=get_result(),
    #     on_change=set_result,



    # # Rebuild results_tab to add a Diagnostics tab (keeps your variable name)
    # results_tab = mo.ui.tabs(
    #     {
    #         "Initial optimal powerflow": original,
    #         "Optimal sizing/placement solution": sizing,
    #         "Final optimal powerflow": get_optimal(),
    #         "Diagnostics (constraints)": diagnostics_view,
    #     },
    #     value=get_result(),
    #     on_change=set_result,
    # )



    # diagnostics_view = mo.tabs(
    #     {
    #         "Summary (max by constraint)": summary_view,          # from Cell 2
    #         "Details (per component)": per_component_view,        # from Cell 3
    #         "Duals (per component)": per_component_duals_view,    # from Cell 4
    #     },
    #     value="Summary (max by constraint)",
    # )

    # # Rebuild results_tab to include Diagnostics (keeps your variable name)
    # results_tab = mo.ui.tabs(
    #     {
    #         "Initial optimal powerflow": original,
    #         "Optimal sizing/placement solution": sizing,
    #         "Final optimal powerflow": get_optimal(),
    #         "Diagnostics (constraints)": diagnostics_view,
    #     },
    #     value=get_result(),
    #     on_change=set_result,
    # )


    # --- Diagnostics tab + results tab (marimo 0.16.x) ---

    # Build the diagnostics tabset
    diagnostics_view = mo.ui.tabs(
        {
            "Summary (max by constraint)": summary_view,          # from Summary view cell
            "Details (per component)": per_component_view,        # from Violations 3B cell
            "Duals (per component)": per_component_duals_view,    # from Duals 4B cell
        },
        value="Summary (max by constraint)",   # initial tab

    )

    # Rebuild results_tab to include Diagnostics
    results_tab = mo.ui.tabs(
        {
            "Initial optimal powerflow": original,
            "Optimal sizing/placement solution": sizing,
            "Final optimal powerflow": get_optimal(),
            "Diagnostics (constraints)": diagnostics_view,
        },
        value=get_result(),        # keep your existing state variable
        on_change=set_result,      # keep state in sync
    )

    # Render it
    #results_tab
    return (results_tab,)


@app.cell
def _(file, hint, mo, results_tab):
    # Result view
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
def _(K, N, message, mo, np, pd, warning):
    # Result formatting
    def format(x, prefix="", suffix=""):
        if isinstance(x, list):
            return f"{prefix} {x[0]:.2f}<{x[1]:.2f} {suffix}"
        if isinstance(x, complex):
            return f"{prefix} {x.real:.2f}{x.imag:+.2f}j {suffix}"
        return f"{prefix} {x:.2f} {suffix}"


    def results(model, result):
        if "curtailment" not in result:
            result["curtailment"] = np.zeros(N)
        return mo.vstack(
            [
                mo.md("# Summary Data"),
                mo.md(f"**Cost of solution**: ${result['cost']:,.2f}"),
                (message if result["status"] == "optimal" else warning)(
                    f"**Solution status**: {result['status']}"
                ),
                pd.DataFrame(
                    data={
                        "Total": [
                            format(abs(result["demand"].sum()), suffix="MW"),
                            format(abs(result["curtailment"].sum()), suffix="MW"),
                            format(
                                sum([abs(x) for x in result["generation"]]),
                                suffix="MVA",
                            ),
                            format(abs(result["capacitors"].sum()), suffix="MVAr"),
                            format(abs(result["condensers"].sum()), suffix="MVAr"),
                            format(abs(result["flows"]).sum(), suffix="MVA"),
                            "-",
                            "-",
                            "-",
                        ],
                        "Mean": [
                            format(
                                abs(result["demand"].sum()) / N, suffix="MW"
                            ),
                            format(
                                abs(result["curtailment"].sum()) / N, suffix="MW"
                            ),
                            format(
                                sum([abs(x) for x in result["generation"]]) / N,
                                suffix="MVA",
                            ),
                            format(
                                abs(result["capacitors"].sum()) / N, suffix="MVAr"
                            ),
                            format(
                                abs(result["condensers"].sum()) / N, suffix="MVAr"
                            ),
                            format(abs(result["flows"]).mean(), suffix="MVA"),
                            format(
                                abs(sum([x for x, y in result["voltage"]]) / N),
                                suffix="kV",
                            ),
                            format(
                                sum(result["magnitude"]) / K,
                                suffix="pu.V",
                            ),
                            format(
                                sum(result["angle"]) / K,
                                suffix="deg",
                            ),
                        ],
                        "Minimum": [
                            format(abs(result["demand"].min()), suffix="MW"),
                            format(abs(result["curtailment"].min()), suffix="MW"),
                            format(
                                min([abs(x) for x in result["generation"]]),
                                suffix="MVA",
                            ),
                            format(abs(result["capacitors"].min()), suffix="MVAr"),
                            format(abs(result["condensers"].min()), suffix="MVAr"),
                            format(abs(result["flows"].min()), suffix="MVA"),
                            format(
                                abs(min([x for x, y in result["voltage"]])),
                                suffix="kV",
                            ),
                            format(
                                min(result["magnitude"]),
                                suffix="pu.V",
                            ),
                            format(
                                min(result["angle"]),
                                suffix="deg",
                            ),
                        ],
                        "Maximum": [
                            format(abs(result["demand"].max()), suffix="MW"),
                            format(abs(result["curtailment"].max()), suffix="MW"),
                            format(
                                max([abs(x) for x in result["generation"]]),
                                suffix="MVA",
                            ),
                            format(abs(result["capacitors"].max()), suffix="MVAr"),
                            format(abs(result["condensers"].max()), suffix="MVAr"),
                            format(abs(result["flows"].max()), suffix="MVA"),
                            format(
                                abs(max([x for x, y in result["voltage"]])),
                                suffix="kV",
                            ),
                            format(
                                max(result["magnitude"]),
                                suffix="deg",
                            ),
                            format(
                                max(result["angle"]),
                                suffix="deg",
                            ),
                        ],
                    },
                    index=[
                        "Demand",
                        "Curtailment",
                        "Generation",
                        "Capacitors",
                        "Condensers",
                        "Line flow",
                        "Voltage",
                        "  Magnitude",
                        "  Angle",
                    ],
                ),
                mo.md("# "),
                mo.hstack(
                    [
                        pd.DataFrame(
                            data={
                                x: [format(z) for z in y.tolist()]
                                for x, y in result.items()
                                if x in ["voltage","generation","capacitors","condensers","demand","curtailment","substation constr cost", "substation upgrade cost"] and isinstance(y, np.ndarray) and len(y) == N
                            },
                            index=model.get_name("bus"),
                        ),
                        pd.DataFrame(
                            data={
                                x: [format(z) for z in y.tolist()]
                                for x, y in result.items()
                                if x in ["flows"] and isinstance(y, np.ndarray) and len(y) == K
                            },
                            index=model.get_name("branch"),
                        ),
                    ]
                ),
            ],
        )
    return (results,)


@app.cell
def _(
    angle_limit_ui,
    complex_flows_ui,
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
    voltage_limit_ui,
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
                            angle_limit=angle_limit_ui.value,
                            voltage_limit=voltage_limit_ui.value/100,
                            complex_flows = complex_flows_ui.value
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
            raise
            _output = _stdout.getvalue() + _stderr.getvalue()
            original = mo.vstack(
                [
                    mo.hstack(
                        [error(err), verbose_ui, problem_ui], justify="start"
                    ),
                    mo.md(f"""~~~\n{_output}\n~~~""" if verbose_ui.value else ""),
                ]
            )
    else:
        original = mo.md("")
    
    if problem_ui.value and (get_result() == "Initial optimal powerflow") and file.value:
        print(f"{get_result()} problem data")
        mo.output.append(mo.md("---"))
        mo.output.append(f"{get_result()} problem data")
        mo.output.append(model.problem)
    return (original,)


@app.cell
def _(
    angle_limit_ui,
    cap_cost,
    con_cost,
    copy,
    demand_margin_ui,
    error,
    file,
    gen_cost,
    gen_prodcost_ui_c,
    gen_prodcost_ui_x,
    gen_prodcost_ui_x2,
    get_result,
    json,
    mo,
    model,
    os,
    problem_ui,
    results,
    solver_ui,
    substation_construction_cost,
    substation_upgrade_cost,
    verbose_ui,
    voltage_limit_ui,
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

            gen_prod_cost_dict = {"model": "POLYNOMIAL",
                                 "x2": gen_prodcost_ui_x2.value, 
                                 "x1": gen_prodcost_ui_x.value, 
                                 "c": gen_prodcost_ui_c.value}

            with mo.capture_stderr() as _stderr:
                with mo.capture_stdout() as _stdout:
                    _result = results(
                        osp_model,
                        osp_model.optimal_sizing(
                            refresh=True,
                            verbose=verbose_ui.value,
                            update_model=True,
                            gen_cost=gen_cost,
                            cap_cost=cap_cost,
                            con_cost = con_cost,
                            solver=solver_ui.value,
                            margin=demand_margin_ui.value / 100,
                            angle_limit=angle_limit_ui.value,
                            voltage_limit=voltage_limit_ui.value/100,
                            gen_prod_cost=gen_prod_cost_dict,
                            substation_upgrade_cost = substation_upgrade_cost,
                            substation_constr_cost = substation_construction_cost

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
            #raise
            _output = _stdout.getvalue() + _stderr.getvalue()
            sizing = mo.vstack(
                [
                    mo.hstack(
                        [error(err), verbose_ui, problem_ui], justify="start"
                    ),
                    mo.md(f"""~~~\n{_output}\n~~~""" if verbose_ui.value else ""),
                ]
            )
    else:
        sizing = mo.md("")
    
    if problem_ui.value and (get_result() == "Optimal sizing/placement solution") and file.value:
        mo.output.append(mo.md("---"))
        mo.output.append(f"{get_result()} problem data")
        mo.output.append(osp_model.problem)
    return osp_model, sizing


@app.cell
def _(mo):
    # Optimization state
    get_optimal,set_optimal = mo.state(None)
    return get_optimal, set_optimal


@app.cell
def _(mo):
    mo.md(r"""## Newly added Cells start""")
    return


@app.cell
def _(model, pd):

    try:
        N_ = len(model.find("bus", list))
    except Exception:
        N_ = 0

    try:
        K_ = len(model.find("branch", list))
    except Exception:
        K_ = 0

    try:
        BUS_INDEX_ = pd.Index(model.get_name("bus"), name="bus")
    except Exception:
        BUS_INDEX_ = pd.Index(range(N_), name="bus")

    try:
        BRANCH_INDEX_ = pd.Index(model.get_name("branch"), name="branch")
    except Exception:
        BRANCH_INDEX_ = pd.Index(range(K_), name="branch")
    return BRANCH_INDEX_, BUS_INDEX_, K_, N_


@app.cell
def _(mo, osp_model, pd):

    # Pull last OSP result safely
    try:
        _osp_res = osp_model.get_result("optimal_sizing")
    except Exception:
        _osp_res = {}

    # Build the diagnostics table (one row per constraint)
    viol_df = pd.DataFrame(_osp_res.get("constraint_report", []))

    # Friendly fallback so downstream cells always render
    if viol_df.empty:
        viol_df = pd.DataFrame([{
            "idx": -1,
            "constraint": "(no diagnostics)",
            "type": "",
            "max_violation": 0.0,
            "binding": True,
            "dual_abs_max": float("nan"),
            "status": _osp_res.get("status", "")
        }])

    diagnostics_status = mo.md(
        f"**OSP status:** `{_osp_res.get('status','')}` &nbsp;&nbsp; "
        f"**Solver:** `{_osp_res.get('solver','')}`"
    )
    return diagnostics_status, viol_df


@app.cell
def _(mo):


    sort_by = mo.ui.dropdown(
        label="Sort by",
        options=["max_violation", "idx", "constraint", "type", "dual_abs_max", "status"],
        value="max_violation",
        allow_select_none=False,
    )
    ascending = mo.ui.switch(value=False, label="Ascending")
    tol_ui = mo.ui.slider(
        label="Binding tolerance", start=0.0, stop=1e-2, step=1e-6,
        value=1e-6, show_value=True, debounce=True,
    )
    only_viol = mo.ui.switch(value=True, label="Only violated (>0)")
    show_duals = mo.ui.switch(value=False, label="Show duals")

    summary_controls = mo.hstack([sort_by, ascending, tol_ui, only_viol, show_duals], justify="start")
    summary_controls
    return ascending, only_viol, show_duals, sort_by, summary_controls, tol_ui


@app.cell
def _(
    ascending,
    diagnostics_status,
    mo,
    only_viol,
    show_duals,
    sort_by,
    summary_controls,
    tol_ui,
    viol_df,
):

    _df = viol_df.copy()

    if "max_violation" in _df.columns and only_viol.value:
        _df = _df[_df["max_violation"] > 0]
    if "max_violation" in _df.columns:
        _df["binding@tol"] = (_df["max_violation"] <= float(tol_ui.value))

    cols = ["idx", "constraint", "type", "max_violation", "binding@tol", "status"]
    if show_duals.value and "dual_abs_max" in _df.columns:
        cols.insert(4, "dual_abs_max")
    cols = [c for c in cols if c in _df.columns]

    _df = _df[cols].sort_values(by=sort_by.value, ascending=ascending.value)

    download_btn = mo.download(
        _df.to_csv(index=False),
        mimetype="text/csv",
        filename="constraint_report.csv",
        label="Download CSV",
    )

    summary_view = mo.vstack([diagnostics_status, summary_controls, mo.ui.table(_df, page_size=25), download_btn])
    summary_view
    return (summary_view,)


@app.cell
def _(mo, viol_df):
    def _viol_row_label(row):
        return f"{int(row['idx'])} — {row.get('type','')} — {row.get('constraint','')}"

    if "idx" in viol_df.columns and len(viol_df) > 0:
        _viol_labels = [_viol_row_label(r) for _, r in viol_df.sort_values("idx").iterrows()]
    else:
        _viol_labels = ["-1 —  — (no diagnostics)"]

    con_picker = mo.ui.dropdown(
        label="Select constraint (by idx/name)",
        options=_viol_labels,
        value=_viol_labels[0],
        allow_select_none=False,
    )
    only_pos = mo.ui.switch(value=True, label="Show only positive violations")

    viol_controls = mo.hstack([con_picker, only_pos], justify="start")
    viol_controls

    return con_picker, only_pos, viol_controls


@app.cell
def _(
    BRANCH_INDEX_,
    BUS_INDEX_,
    K_,
    N_,
    con_picker,
    mo,
    np,
    only_pos,
    osp_model,
    pd,
    viol_controls,
    viol_df,
):

    # Rebuild label -> idx mapping locally
    def _viol_row_label(row):
        return f"{int(row['idx'])} — {row.get('type','')} — {row.get('constraint','')}"
    _label_to_idx = (
        { _viol_row_label(r): int(r["idx"]) for _, r in viol_df.sort_values("idx").iterrows() }
        if "idx" in viol_df.columns and len(viol_df) > 0 else
        {"-1 —  — (no diagnostics)": -1}
    )

    _selected_idx = _label_to_idx.get(con_picker.value, -1)

    try:
        vals = np.array(osp_model.constraint_component_violations(int(_selected_idx)), dtype=float).ravel()
    except Exception:
        vals = np.array([], dtype=float)

    if vals.size == N_ and N_ > 0:
        idx_labels_v = BUS_INDEX_
    elif vals.size == K_ and K_ > 0:
        idx_labels_v = BRANCH_INDEX_
    else:
        idx_labels_v = pd.Index(range(vals.size), name="component")


    comp_df = pd.DataFrame({"violation": vals}, index=idx_labels_v)
    if only_pos.value:
        comp_df = comp_df[comp_df["violation"] > 0]
    comp_df = comp_df.sort_values("violation", ascending=False)

    components_csv = mo.download(
        comp_df.reset_index().to_csv(index=False),
        mimetype="text/csv",
        filename=f"constraint_{_selected_idx}_components.csv",
        label="Download components CSV",
    )

    per_component_view = mo.vstack([viol_controls, mo.ui.table(comp_df.reset_index(), page_size=25), components_csv])
    per_component_view
    return (per_component_view,)


@app.cell
def _(mo, viol_df):


    def _dual_row_label(row):
        return f"{int(row['idx'])} — {row.get('type','')} — {row.get('constraint','')}"

    if "idx" in viol_df.columns and len(viol_df) > 0:
        _dual_labels = [_dual_row_label(r) for _, r in viol_df.sort_values("idx").iterrows()]
    else:
        _dual_labels = ["-1 —  — (no diagnostics)"]

    dual_picker = mo.ui.dropdown(
        label="Select constraint (by idx/name)",
        options=_dual_labels,
        value=_dual_labels[0],
        allow_select_none=False,
    )
    dual_abs = mo.ui.switch(value=True, label="Show |dual| (absolute value)")
    only_nonzero_dual = mo.ui.switch(value=True, label="Hide zeros")

    dual_controls = mo.hstack([dual_picker, dual_abs, only_nonzero_dual], justify="start")
    dual_controls
    return dual_abs, dual_controls, dual_picker, only_nonzero_dual


@app.cell
def _(
    BRANCH_INDEX_,
    BUS_INDEX_,
    K_,
    N_,
    dual_abs,
    dual_controls,
    dual_picker,
    mo,
    np,
    only_nonzero_dual,
    osp_model,
    pd,
    viol_df,
):

    def _dual_row_label(row):
        return f"{int(row['idx'])} — {row.get('type','')} — {row.get('constraint','')}"

    # Build label -> idx mapping locally
    _label_to_idx_dual = (
        { _dual_row_label(r): int(r["idx"]) for _, r in viol_df.sort_values("idx").iterrows() }
        if "idx" in viol_df.columns and len(viol_df) > 0 else
        {"-1 —  — (no diagnostics)": -1}
    )

    _dual_idx = _label_to_idx_dual.get(dual_picker.value, -1)

    # Fetch duals (can be None/empty/scalar/vector)
    try:
        dual_vals = osp_model.constraint_component_duals(int(_dual_idx), absval=dual_abs.value)
    except Exception:
        dual_vals = None

    # Normalize to a 1D numpy array safely
    if dual_vals is None:
        dual_arr = np.array([], dtype=float)
    else:
        dual_arr = np.array(dual_vals, dtype=float).ravel()
        # Some solvers return a single scalar dual for scalar constraints
        if dual_arr.size == 1 and not np.isscalar(dual_vals):
            dual_arr = dual_arr.ravel()

    # Choose index labels by shape, but ONLY if sizes match
    if dual_arr.size == 0:
        # empty -> empty index and DF
        idx_labels_d = pd.Index([], name="component")
    elif dual_arr.size == N_:
        idx_labels_d = BUS_INDEX_
    elif dual_arr.size == K_:
        idx_labels_d = BRANCH_INDEX_
    else:
        idx_labels_d = pd.Index(range(dual_arr.size), name="component")

    duals_df = pd.DataFrame({"dual": dual_arr}, index=idx_labels_d)

    # Optional filtering
    if only_nonzero_dual.value and duals_df.shape[0] > 0:
        duals_df = duals_df[np.abs(duals_df["dual"]) > 0]

    duals_df = duals_df.sort_values("dual", ascending=False) if duals_df.shape[0] > 0 else duals_df

    duals_csv = mo.download(
        duals_df.reset_index().to_csv(index=False),
        mimetype="text/csv",
        filename=f"constraint_{_dual_idx}_duals.csv",
        label="Download duals CSV",
    )

    per_component_duals_view = mo.vstack([
        dual_controls,
        mo.ui.table(duals_df.reset_index(), page_size=25),
        duals_csv,
    ])
    per_component_duals_view
    return (per_component_duals_view,)


@app.cell
def _():


    # # --- Diagnostics filters + table (marimo 0.16.5-compatible) ---

    # # Controls (dropdown instead of select; number uses start/stop, not min/max)
    # sort_by = mo.ui.dropdown(
    #     label="Sort by",
    #     options=["max_violation", "idx", "constraint", "type", "dual_abs_max", "status"],
    #     value="max_violation",
    #     allow_select_none=False,
    # )
    # ascending = mo.ui.switch(value=False, label="Ascending")


    # # --- Binding tolerance as a slider (marimo 0.16.5) ---
    # tol_ui = mo.ui.slider(
    #     label="Binding tolerance",
    #     start=0.0,          # min allowed
    #     stop=1e-2,          # max allowed (adjust if you like)
    #     step=1e-6,          # slider increment
    #     value=1e-6,         # initial value
    #     show_value=True,
    #     debounce=True,
    # )


    return


@app.cell
def _():

    # only_viol = mo.ui.switch(value=True, label="Only violated (>0)")
    # show_duals = mo.ui.switch(value=False, label="Show duals")
    return


@app.cell
def _():


    # # Build filtered/sorted view from viol_df created in the previous cell
    # _df = viol_df.copy()

    # if "max_violation" in _df.columns:
    #     if only_viol.value:
    #         _df = _df[_df["max_violation"] > 0]
    #     _df["binding@tol"] = (_df["max_violation"] <= float(tol_ui.value))

    # cols = ["idx", "constraint", "type", "max_violation", "binding@tol", "status"]
    # if show_duals.value and "dual_abs_max" in _df.columns:
    #     cols.insert(4, "dual_abs_max")
    # cols = [c for c in cols if c in _df.columns]

    # _df = _df[cols].sort_values(by=sort_by.value, ascending=ascending.value)

    # download_btn = mo.download(
    #     _df.to_csv(index=False),
    #     mimetype="text/csv",
    #     filename="constraint_report.csv",
    #     label="Download CSV",
    # )

    # # diagnostics_view = mo.vstack([
    # #     diagnostics_status,  # from the previous cell
    # #     mo.hstack([sort_by, ascending, tol_ui, only_viol, show_duals], justify="start"),
    # #     mo.ui.table(_df, page_size=25),
    # #     download_btn,
    # # ])

    # diagnostics_view = mo.tabs(
    #     {
    #         "Summary (max by constraint)": mo.vstack([
    #             diagnostics_status,
    #             mo.hstack([sort_by, ascending, tol_ui, only_viol, show_duals], justify="start"),
    #             mo.ui.table(_df, page_size=25),
    #             download_btn,
    #         ]),
    #         "Details (per component)": per_component_view,        # violations (you already added)
    #         "Duals (per component)": per_component_duals_view,    # <— new tab
    #     },
    #     value="Summary (max by constraint)",
    # )
    return


@app.cell
def _(mo):
    mo.md(r"""### Violations dataframe""")
    return


@app.cell
def _():
    # def _row_label(row):
    #     # Looks like: 3 — <= — cp.abs(I.real@x + I.imag@y) <= F
    #     return f"{int(row['idx'])} — {row.get('type','')} — {row.get('constraint','')}"

    # # Build mapping: label -> idx (int)
    # if "idx" in viol_df.columns and len(viol_df) > 0:
    #     _label_to_idx = {
    #         _row_label(r): int(r["idx"])
    #         for _, r in viol_df.sort_values("idx").iterrows()
    #     }
    # else:
    #     _label_to_idx = {"-1 —  — (no diagnostics)": -1}

    # _labels = list(_label_to_idx.keys())
    # _initial_label = _labels[0]

    # con_picker = mo.ui.dropdown(
    #     label="Select constraint (by idx/name)",
    #     options=_labels,               # <-- pass a list of labels
    #     value=_initial_label,          # <-- initial selection is a label
    #     allow_select_none=False,
    # )

    # only_pos = mo.ui.switch(value=True, label="Show only positive violations")
    return


@app.cell
def _():

    # # Fetch per-component violations from the model (vector)
    # try:
    #     vals = np.array(osp_model.constraint_component_violations(con_picker.value), dtype=float).ravel()
    # except Exception:
    #     vals = np.array([], dtype=float)

    # # Choose row labels by shape
    # if vals.size == N:
    #     idx_labels = pd.Index(model.get_name("bus"), name="bus")
    # elif vals.size == K:
    #     idx_labels = pd.Index(model.get_name("branch"), name="branch")
    # else:
    #     idx_labels = pd.Index(range(vals.size), name="component")

    # comp_df = pd.DataFrame({"violation": vals}, index=idx_labels)

    # if only_pos.value:
    #     comp_df = comp_df[comp_df["violation"] > 0]

    # comp_df = comp_df.sort_values("violation", ascending=False)

    # download_components = mo.download(
    #     comp_df.reset_index().to_csv(index=False),
    #     mimetype="text/csv",
    #     filename=f"constraint_{con_picker.value}_components.csv",
    #     label="Download components CSV",
    # )

    # per_component_view = mo.vstack([
    #     mo.hstack([con_picker, only_pos], justify="start"),
    #     mo.ui.table(comp_df.reset_index(), page_size=25),
    #     download_components,
    # ])
    return


@app.cell
def _(mo):
    mo.md(r"""### Duals Dataframe""")
    return


@app.cell
def _():
    # def _row_label(row):
    #     # Looks like: 3 — <= — cp.abs(I.real@x + I.imag@y) <= F
    #     return f"{int(row['idx'])} — {row.get('type','')} — {row.get('constraint','')}"

    # if "idx" in viol_df.columns:
    #     _dual_opts = {_row_label(r): int(r["idx"]) for _, r in viol_df.sort_values("idx").iterrows()}
    # else:
    #     _dual_opts = {"(no constraints)": 0}

    # dual_picker = mo.ui.dropdown(
    #     label="Select constraint (by idx/name)",
    #     options=_dual_opts,
    #     value=list(_dual_opts.values())[0] if _dual_opts else 0,
    #     allow_select_none=False,
    # )

    # dual_abs = mo.ui.switch(value=True, label="Show |dual| (absolute value)")
    # only_nonzero_dual = mo.ui.switch(value=True, label="Hide zeros")

    # # Pull duals from the model (vector)
    # try:
    #     dual_vals = np.array(
    #         osp_model.constraint_component_duals(dual_picker.value, absval=dual_abs.value),
    #         dtype=float
    #     ).ravel()
    # except Exception:
    #     dual_vals = np.array([], dtype=float)

    # # Choose index labels by shape (N => buses, K => branches, else generic)
    # if dual_vals.size == N:
    #     dual_index = pd.Index(model.get_name("bus"), name="bus")
    # elif dual_vals.size == K:
    #     dual_index = pd.Index(model.get_name("branch"), name="branch")
    # else:
    #     dual_index = pd.Index(range(dual_vals.size), name="component")

    # duals_df = pd.DataFrame({"dual": dual_vals}, index=dual_index)

    # if only_nonzero_dual.value:
    #     # filter tiny numerical noise too
    #     duals_df = duals_df[np.abs(duals_df["dual"]) > 0]

    # duals_df = duals_df.sort_values("dual", ascending=False)

    # dual_download_btn = mo.download(
    #     duals_df.reset_index().to_csv(index=False),
    #     mimetype="text/csv",
    #     filename=f"constraint_{dual_picker.value}_duals.csv",
    #     label="Download duals CSV",
    # )

    # per_component_duals_view = mo.vstack([
    #     mo.hstack([dual_picker, dual_abs, only_nonzero_dual], justify="start"),
    #     mo.ui.table(duals_df.reset_index(), page_size=25),
    #     dual_download_btn,
    # ])
    return


@app.cell
def _(mo):
    mo.md(r"""## Newly Added Cells End""")
    return


@app.cell
def _(
    angle_limit_ui,
    complex_flows_ui,
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
    voltage_limit_ui,
):
    # Final powerflow result
    if file.value:
        opf_model = copy.deepcopy(osp_model) #NOTE: should this be a deep copy of model or osp_model 

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
                    #TODO: commenting below for testing, will 
                    # _result = opf_model.optimal_powerflow(
                    #     refresh=True,
                    #     verbose=verbose_ui.value,
                    #     curtailment_price=curtailment_ui.value,
                    #     solver=solver_ui.value,
                    #     angle_limit=angle_limit_ui.value,
                    #     voltage_limit=voltage_limit_ui.value/100,
                    # )

                    #TODO: Test below 
                    _result = results(
                        opf_model,
                        opf_model.optimal_powerflow(
                        refresh=True,
                        verbose=verbose_ui.value,
                        curtailment_price=curtailment_ui.value,
                        solver=solver_ui.value,
                        angle_limit=angle_limit_ui.value,
                        voltage_limit=voltage_limit_ui.value/100,
                        complex_flows = complex_flows_ui.value
                        ),
                        )
            _output = _stdout.getvalue() + _stderr.getvalue()
            set_optimal(
                mo.vstack(
                    [
                       _result,
                        final_download_ui,
                        mo.md(
                            f"""~~~\n{_output}\n~~~""" if verbose_ui.value else ""
                        ),
                    ]
                )
            )
        except Exception as err:
            _output = _stdout.getvalue() + _stderr.getvalue()
            set_optimal(
                mo.vstack(
                    [
                        mo.hstack(
                            [error(err), verbose_ui, problem_ui], justify="start"
                        ),
                        mo.md(
                            f"""~~~\n{_output}\n~~~""" if verbose_ui.value else ""
                        ),
                    ]
                )
            )
    else:
        set_optimal(mo.md(""))
    if problem_ui.value and (get_result() == "Final optimal powerflow") and file.value:
        mo.output.append(mo.md("---"))
        mo.output.append(f"{get_result()} problem data")
        mo.output.append(opf_model.problem)
    return (opf_model,)


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
    complex_flows_ui = mo.ui.checkbox(label="**Enable Complex Flows in Optimizer Solution**")

    osqp_max_iter = mo.ui.slider(
        label="**Maximum iterations**:",
        steps=[10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000],
        value=10000,
        debounce=True,
    )
    osqp_eps_abs = mo.ui.slider(
        label="**Absolute epsilon**: (10^)",
        steps=range(-10, 1),
        value=-5,
        debounce=True,
        show_value=True,
    )
    osqp_eps_rel = mo.ui.slider(
        label="**Relative epsilon**: (10^)",
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
    angle_limit_ui = mo.ui.slider(
        label="**Voltage angle accuracy limit**: (deg)",
        start=0,
        stop=45,
        step=1,
        value=10,
        debounce=True,
        show_value=True,
    )
    voltage_limit_ui = mo.ui.slider(
        label="**Voltage magnitude constraints**: (%)",
        steps=[1,2,3,4,5,6,7,8,9,10,15,20,25,30,35,40,45,50,60,70,80,90,100],
        value=5,
        debounce=True,
        show_value=True,
    )
    solver_options = {
        "OSQP": [osqp_max_iter, osqp_eps_abs, osqp_eps_rel, angle_limit_ui,voltage_limit_ui],
        "CLARABEL": [clarabel_max_iter, clarabel_time_limit, angle_limit_ui,voltage_limit_ui],
    }
    return (
        angle_limit_ui,
        complex_flows_ui,
        problem_ui,
        solver_options,
        solver_ui,
        verbose_ui,
        voltage_limit_ui,
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
    concost_ui = mo.ui.slider(
        label="**Condenser cost**: ($/MVAr)",
        start=0,
        stop=10000,
        step=100,
        value=1000,
        show_value=True,
        debounce=True,
    )

    substation_upgrade_cost_ui = mo.ui.text(label="**Substation capacity upgrade costs ($/MVA)**", 
                                            placeholder="default 0",
                                            debounce=True)

    substation_construction_cost_ui = mo.ui.text(label="**New Substation construction costs ($/MVA)**", 
                                            placeholder="default inf",
                                            debounce=True)
    return (
        capcost_ui,
        concost_ui,
        gencost_ui,
        substation_construction_cost_ui,
        substation_upgrade_cost_ui,
    )


@app.cell
def _(mo):
    #Operations Cost Slider
    gen_prodcost_ui_x2 = mo.ui.slider(
        label="$x^2$ quadratic coefficient: ($/MWH)^2/H",
        start=0,
        stop=1000,
        step=10,
        value=0,
        show_value=True,
        debounce=True,
    )
    gen_prodcost_ui_x = mo.ui.slider(
        label= "$x$ linear coefficient: ($/MWH)",
        start=0,
        stop=1000,
        step=10,
        value=100,
        show_value=True,
        debounce=True,
    )
    gen_prodcost_ui_c = mo.ui.slider(
        label="$c$ constant coefficient: ($/H)",
        start=0,
        stop=1000,
        step=10,
        value=0,
        show_value=True,
        debounce=True,
    )
    return gen_prodcost_ui_c, gen_prodcost_ui_x, gen_prodcost_ui_x2


@app.cell
def _(gen_prodcost_ui_c, gen_prodcost_ui_x, gen_prodcost_ui_x2):

    gen_prod_polytext_ui = f"{gen_prodcost_ui_x2.value}x^2 + {gen_prodcost_ui_x.value}x + {gen_prodcost_ui_c.value}"
    return (gen_prod_polytext_ui,)


@app.cell
def _(gencost_ui, mo, np):
    # Curtailment settings
    curtailment_ui = mo.ui.slider(
        label="**Curtailment cost**: ($/MW)",
        steps=np.array(
            [0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100],
            dtype=float,
        )
        * gencost_ui.value,
        value=10 * gencost_ui.value,
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
def _(file, mo, model, voltage_limit_ui):
    # Graph settings
    voltage_ui = mo.ui.range_slider(
        label="**Voltage limits**: (pu.V)",
        start=0.5,
        stop=1.5,
        step=0.01,
        value=[max(0.5,1-voltage_limit_ui.value/100),min(1+voltage_limit_ui.value/100,1.5)],
        debounce=True,
        show_value=True,
    )
    current_ui = mo.ui.slider(
        label="**High flow**: (kA)",
        steps=[0, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000],
        value=1000,
        debounce=True,
        show_value=True,
    )
    showbusdata_ui = mo.ui.multiselect(
        label="**Show bus data**:",
        options=["id", "type", "area", "Vm", "Va", "zone"],
        value=None,
    )
    showarea_ui = mo.ui.dropdown(
        label="**Show area**:",
        options=sorted(model.get_areas()) if file.value else [],
    )
    showloads_ui = mo.ui.checkbox(label="**Show loads**")
    showgens_ui = mo.ui.checkbox(label="**Show generators**")
    return (
        current_ui,
        showarea_ui,
        showbusdata_ui,
        showgens_ui,
        showloads_ui,
        voltage_ui,
    )


@app.cell
def _(
    capcost_ui,
    complex_flows_ui,
    concost_ui,
    current_ui,
    curtailment_ui,
    demand_margin_ui,
    gen_prod_polytext_ui,
    gen_prodcost_ui_c,
    gen_prodcost_ui_x,
    gen_prodcost_ui_x2,
    gencost_ui,
    mo,
    problem_ui,
    showbusdata_ui,
    showgens_ui,
    showloads_ui,
    solver_options,
    solver_ui,
    substation_construction_cost_ui,
    substation_upgrade_cost_ui,
    verbose_ui,
    voltage_ui,
):
    # Setting tabs
    settings_view = mo.accordion(
        {
            "**Optimizer**": mo.vstack(
                [solver_ui, verbose_ui, problem_ui, complex_flows_ui]
                + solver_options[solver_ui.value]
            ),
            "**Capacity costs**": mo.vstack(
                [
                    gencost_ui,
                    capcost_ui,
                    concost_ui,
                    curtailment_ui,
                    substation_upgrade_cost_ui,
                    substation_construction_cost_ui
                ]
            ),
            "**Added Generation Polynomial Production Cost Function**" : mo.vstack(
                [
                    gen_prodcost_ui_x2,
                    gen_prodcost_ui_x, 
                    gen_prodcost_ui_c,
                    "Polynomial Prdouction Function:",
                    gen_prod_polytext_ui
                ]
            ),
            "**Loads**": mo.vstack(
                [
                    demand_margin_ui,
                ]
            ),
            "**Network**": mo.vstack(
                [voltage_ui, current_ui, showbusdata_ui, showloads_ui, showgens_ui]
            ),
        },
        multiple=True,
        lazy=True,
    )
    return (settings_view,)


@app.cell
def _(file, mo, model, opf_model, osp_model):
    # Graph settings
    if file.value:
        graph_model_ui = mo.ui.radio(
            label="**Model**:",
            options={
                "Original": model,
                "Capacity": osp_model,
                "Optimal": opf_model,
            },
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
            label="**Bus label**:",
            options={
                "Name": None,
                "Id": "id",
                "|V|": "Vm",
                "<V": "Va",
                "Type": "type",
                "Area": "area",
                "Zone": "zone",
            },
            value="Name",
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
    showarea_ui,
    showbusdata_ui,
    showgens_ui,
    showloads_ui,
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
            showarea=showarea_ui.value,
            showloads=showloads_ui.value,
            showgens=showgens_ui.value,
        )
        diagram = mo.vstack(
            [
                mo.hstack(
                    [
                        graph_model_ui,
                        graph_orientation_ui,
                        voltage_ui,
                    ],
                    align="start",
                ),
                mo.hstack(
                    [
                        graph_label_ui,
                        showarea_ui,
                        showbusdata_ui,
                        showloads_ui,
                        showgens_ui,
                    ],
                    align="start",
                ),
                mo.mermaid(_diagram),
            ]
        )
    else:
        diagram = mo.vstack([file, hint("open your JSON model")])
    return (diagram,)


@app.cell
def _(gld, mo):
    gld
    help_view = mo.md(open("README.md", "r").read())
    return (help_view,)


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
    return copy, gld, json, mo, np, os, pd


if __name__ == "__main__":
    app.run()
