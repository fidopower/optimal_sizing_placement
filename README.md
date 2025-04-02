# User's Guide

This Marimo notebook computes the optimal powerflow solution for a GridLAB-D
network modeled using **pypower**. The notebook is organized using 3 tabs
(not including the **Settings** and **Help** tabs), the **Model** tab, the **Costs** tab, and the **Results** tab. 

## Model 

The **Model** tab is used load the initial model. Only GridLAB-D JSON model are accepted. If you have a GLM file, you must run the command `gridlabd -C MYFILE.glm -o MYFILE.json` to compile the JSON file from the GLM file. 

To upload a JSON file, click on **Open JSON model** button and select the file you wish to work with.  If you have already opened a model, the new one you select will be opened in its place, or you can click on **Click to clear files** to close the existing model.

Once your model is opened, the model data will be displayed in Pandas DataFrames, one per class found in the model. Select a tab to view each class in the model. Data frames are organized by object name in rows, and object property in columns.

## Costs

If the model contains `capacity` objects with `generator` and `capacitor` data included, then a data frame is shown with the capacity addition costs for each bus in the model.  If no capacity data is found, then a single value for generators and capacitors is given using slider inputs.

The class definition for `capacity` object is 

~~~
class capacity 
{
    complex generator[$/MVA];
    double capacitor[$/MVAr];
}
~~~

with the parent referring to the bus at which the capacity addition costs apply. Note the generator costs are presented a complex value, with the real part corresponding to the cost of adding real power capacity and the imaginary part corresponding to the cost of added reactive power capacity.

## Results

Three optimization results are presented. 

The **Initial optimal powerflow** (OPF) tab shows the result of the fast-decoupled OPF solution prior to optimal sizing and placement, if feasible. The cost of the result is given in $/MWh. If load curtailment is necessary, it will be costed at 100x the maximum generation cost found in the model.

The **Optimal sizing/placement** (OSP) tab shows the fast-decoupled sizing and placement solution given the capacity costs.

The **Final optimal powerflow** (OPF) tab shows the fast-decoupled OPF solution after optimal sizing and placement is solved.

All results are presented in two parts, the **Summary Data** and the **Network Data**. The summary data include totals, means, minima, and maxima values found in the model.  The network data shows the breakdown on the results by bus and branch.

Each result model can be downloaded and run in GridLAB-D using the command

~~~
gridlabd MYFILE_RESULT.json
~~~

where `RESULT` is `opf_initial`, `osp`, or `opf_final` according to which optimization is selected.

## Example

You can try this notebook using the file `example.json`. If you are running an online notebook, you can download the example file from the **View Files** sidebar and open it in the **Model** tab.

----

# Technical Guide


## Optimal Powerflow

The OPF is the solution to the following convex optimization problem for a network having $N$ busses and $M$ branches.

$\begin{array}{rll}
    \underset{x,y,g,h,c,d}{\min} & P \sqrt{g^2+h^2} + 100 \hat{P} d
\\
    \textrm{subject to} 
    & \Re(G) x - g + c + \Re(D) - d = 0 & \textrm{real power flow balance} \\
    & \Im(G) y - h - c + \Im(D) - d \frac{\Im(D)}{\Re(D)} = 0 & \textrm{reactive power flow balance} \\
    & x_{ref} = 0 & \textrm{reference bus voltage angle is always 0} \\
    & y_{ref} = 1 & \textrm{reference bus voltage magnitude is always 1} \\
    & |y-1| \le 0.05 & \textrm{bus voltages within 5\% of nominal} \\
    & |Ix| \le F & \textrm{line flow constraints} \\
    & g \ge 0 & \textrm{real generation power constraints} \\
    & |h| \le \Im(S) & \textrm{reactive generation power constraints} \\
    & |g+hj| \le \Re(S) & \textrm{apparent generation power constraints} \\
    & 0 \le c \le C & \textrm{capacity setting constraints} \\
    & 0 \le d \le D & \textrm{load shedding constraints} \\
\end{array}$

where

* $P \in \mathbb{R}^N$ is the generation price,
* $g \in \mathbb{R}^N$ is the generator real power dispatch,
* $h \in \mathbb{R}^N$ is the generator reactive power dispatch,
* $\hat P\in \mathbb{R}$ is the maximum generation price,
* $d \in \mathbb{R}^N$ is the demand curtailment,
* $G \in \mathbb{C}^{N \times N}$ is the graph Laplacian,
* $x \in \mathbb{R}^N$ is the voltage angle,
* $c \in \mathbb{R}^N$ is the capacitor settings,
* $D \in \mathbb{C}^N$ is the total demand,
* $y \in \mathbb{R}^N$ is the voltage magnitude,
* $I \in \mathbb{R}^{M \times N}$ is the graph incidence matrix,
* $S \in \mathbb{C}^N$ is the generation capacity
* $y \in \mathbb{R}^N$ is the voltage magnitude, and
* $C \in \mathbb{R}^N$ is the capacitor capacity.

## Optimal Sizing and Placement

The OSP is the solution to the following convex optimization problem for a network having $N$ busses and $M$ branches.

$\begin{array}{rll}
    \underset{x,y,g,h,c}{\min} & P g + Q |h| + R |c|
\\
    \textrm{subject to} 
    & \Re(G) x - g + c + \Re(D)(1+d) = 0 & \textrm{real power flow balance} \\
    & \Im(G) y - h - c + \Im(D)(1+d) = 0 & \textrm{reactive power flow balance} \\
    & x_{ref} = 0 & \textrm{reference bus voltage angle is always 0} \\
    & y_{ref} = 1 & \textrm{reference bus voltage magnitude is always 1} \\
    & |y-1| \le 0.05 & \textrm{bus voltages within 5\% of nominal} \\
    & |Ix| \le F & \textrm{line flow constraints} \\
    & g \ge 0 & \textrm{real generation power constraint} \\
    & c \ge 0 & \textrm{capacity setting constraint} \\
\end{array}$

where

* $P \in \mathbb{R}^N$ is the generation price,
* $g \in \mathbb{R}^N$ is the generator real power dispatch,
* $h \in \mathbb{R}^N$ is the generator reactive power dispatch,
* $\hat P\in \mathbb{R}$ is the maximum generation price,
* $G \in \mathbb{C}^{N \times N}$ is the graph Laplacian,
* $d \in \mathbb{R}$ is the demand safety margin,
* $x \in \mathbb{R}^N$ is the voltage angle,
* $c \in \mathbb{R}^N$ is the capacitor settings,
* $D \in \mathbb{C}^N$ is the total demand,
* $y \in \mathbb{R}^N$ is the voltage magnitude,
* $I \in \mathbb{R}^{M \times N}$ is the graph incidence matrix,
* $y \in \mathbb{R}^N$ is the voltage magnitude, and

# References

* [Joshua Taylor, *Convex Optimization of Power Systems*, Cambridge University Press (2015)](https://books.google.com/books?hl=en&lr=&id=JBdoBgAAQBAJ&oi=fnd&pg=PR11&dq=info:4_zKJR2GVGAJ:scholar.google.com&ots=A23AB6jlr9&sig=D2uoDpJMlNfCT9an9WOMuBvfk_k#v=onepage&q&f=false)
* [FIDOpower Optimal Powerflow/Sizing/Placement on GitHub](https://github.com/fidopower/optimal_sizing_placement)
* [Arras Energy Home](https://www.arras.energy/)
* [Arras Energy Documentation](https://docs.arras.energy/)
* [Arras Energy Source](https://github.com/arras-energy/)
* [PyPOWER Documentation](https://rwl.github.io/PYPOWER/)
* [PyPOWER Source](https://github.com/rwl/PYPOWER/)
