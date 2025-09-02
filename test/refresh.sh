#!/bin/bash
for JSON in case*.json; do
    PY=${JSON/.json/.py}
    GLM=${JSON/.json/.glm}
    curl -sLf https://raw.githubusercontent.com/rwl/PYPOWER/refs/heads/master/pypower/$PY > tmp.py && mv tmp.py $PY
    echo "#input \"$PY\" -t pypower" >py_$GLM
    gridlabd -C py_$GLM -o $JSON
    # rm -f $PY
done
