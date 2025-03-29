import marimo

__generated_with = "0.11.31"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    # Model load
    file = mo.ui.file(label="GridLAB-D model", filetypes=[".json"])
    file
    return (file,)


@app.cell
def _(error, exception, file, gld, hint, mo):
    # Model check
    mo.stop(not file.value, hint("upload a JSON file"))
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
def _(K, N, message):
    message(f"{N=}, {K=}")
    return


@app.cell
def _(mo):
    def message(msg,kind=None,color="black",background="white"):
        if not kind:
            return mo.md(f"<font color={color} style=\"background:{background}\">{msg}</font>")
        else:
            return mo.md(f"<font color={color} style=\"background:{background}\"><b>{kind}</b>: {msg}</font>")

    def hint(msg):
        return message(msg,"HINT","blue","white")

    def warning(msg):
        return message(msg,"WARNING","blue","yellow")

    def error(msg):
        return message(msg,"ERROR","red","white")

    def exception(msg):
        return message(msg,"EXCEPTION","red","yellow")
    return error, exception, hint, message, warning


@app.cell
def _():
    import marimo as mo
    import os
    import sys
    if os.environ["HOME"] == "/home/pyodide":
        # replace these...
        import numpy
        import cvxpy
        # ...with this after https://github.com/marimo-team/marimo/issues/4307 is resolved
        # import micropip
        # await micropip.install(
        #     [x.strip() for x in open("requirements.txt", "r").readlines()]
        # )
    else:
        import subprocess
        subprocess.run([sys.executable,"-m","pip","install","-r","requirements.txt"],capture_output=True)
    import gld_pypower as gld
    return cvxpy, gld, mo, numpy, os, subprocess, sys


if __name__ == "__main__":
    app.run()
