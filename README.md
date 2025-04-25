# User's Guide

This Marimo notebook computes the optimal powerflow solution for a GridLAB-D
network modeled using **pypower**. The notebook is organized using 3 tabs
(not including the **Settings** and **Help** tabs), the **Model** tab,
the **Costs** tab, and the **Results** tab. 

## Model 

The **Model** tab is used load the initial model. Only GridLAB-D JSON models
are accepted. If you have a GLM file, you must run the command `gridlabd -C
MYFILE.glm -o MYFILE.json` to compile the JSON file from the GLM file. If you
have a model from another tool or simulator you can try converting it using
the command `gridlabd -C MYFILE.EXT -o MYFILE.json`.

To upload a JSON file, click on **Open JSON model** button and select the file
you wish to work with.  If you have already opened a model, the new one you
select will be opened in its place, or you can click on **Click to clear
files** to close the existing model.

Once your model is opened, the model data will be displayed in a Pandas data
frame, one tab per class found in the model. Select a tab to view a class in
the model. Class data frames are organized by object name in rows, and object
property in columns.

## Costs

If the model contains `capacity` objects with `generator`, `capacitor`, and
`condenser` data included, then a data frame is shown with the capacity
addition costs for each bus in the model.  If no capacity data is found, then
a single value for generators, capacitors, synchronous condensers is given
using slider inputs. These values can also be set using the **Settings**
tab.

The class definition for `capacity` objects is 

~~~
class capacity 
{
    complex generator[$/MVA];
    double capacitor[$/MVAr];
    double condenser[$/MVAr];
}
~~~

with the parent referring to the bus at which the capacity addition costs
apply. Note the `generator` costs are presented a complex value, with the
real part corresponding to the cost of adding real power capacity in units of
`$/MW` and the imaginary part corresponding to the cost of added reactive
power capacity in units of `$/MVAr` in excess of the real power costs. The
cost of `capacitor` and `condenser` objects are only for the reactive power,
i.e., in `$/MVAr`.

## Results

Three optimization results are presented. 

The **Initial optimal powerflow** (OPF) tab shows the result of the
fast-decoupled OPF solution prior to optimal sizing and placement, if
feasible. The cost of the result is given in $/MWh. If load curtailment is
necessary, it will be costed at 100x the maximum generation cost found in the
model.

The **Optimal sizing/placement** (OSP) tab shows the fast-decoupled sizing and
placement solution given the capacity costs.

The **Final optimal powerflow** (OPF) tab shows the fast-decoupled OPF
solution after optimal sizing and placement is solved.

All results are presented in two parts, the **Summary Data** and the **Network
Data**. The summary data include totals, means, minima, and maxima values
found in the model.  The network data shows the breakdown on the results by
bus and branch.

Each result model can be downloaded and run in GridLAB-D using the command

~~~
gridlabd MYFILE_RESULT.json
~~~

where `RESULT` is `opf_initial`, `osp`, or `opf_final` according to which
optimization is selected.

When an optimization fails, checkboxes to enable verbose and problem output
are presented. These options can also be set using the **Settings** tab.

## Network

The **Network** tab displays a visual represention of the network.  Nodes are
presented as circles, loads as triangles, and generation as upside down
trianbles.  Normally the bus is labeled with its name. Options are presented
to display the bus id, bus voltage per unit kV, or bus net load per unit MVA.
The current flowing on lines is presented in units of `kA`.

## Settings

The **Settings** tab shows all the available options, organized by category.

## Example

You can try this notebook using the file `example.json`. If you are running an
online notebook, you can download the example file from the **View Files**
sidebar and open it in the **Model** tab.

----

# Technical Guide


## Optimal Powerflow

The OPF is the solution to the following convex optimization problem for a
network having $N$ busses and $M$ branches.

$\begin{array}{rll}
    \underset{x,y,g,h,c,d,e}{\min} & P (\sqrt{g^2+h^2}+c+r) + 100 \hat{P} \sqrt{d^2+e^2}
\\
    \textrm{subject to} 
    & \Re(G) x - g + c + \Re(D) - d = 0 & \textrm{real power flow balance} \\
    & \Im(G) y - h - c + \Im(D) - e = 0 & \textrm{reactive power flow balance} \\
    & x_{ref} = 0 & \textrm{reference bus voltage angle is always 0} \\
    & y_{ref} = 1 & \textrm{reference bus voltage magnitude is always 1} \\
    & |y-1| \le 0.05 & \textrm{bus voltages within 5\% of nominal} \\
    & |Ix| \le F & \textrm{line flow constraints} \\
    & g \ge 0 & \textrm{real generation power constraints} \\
    & |h| \le \Im(S) & \textrm{reactive generation power constraints} \\
    & \sqrt{g^2+h^2} \le \Re(S) & \textrm{apparent generation power constraints} \\
    & 0 \le c \le C & \textrm{capacitor setting constraints} \\
    & |r| \le R & \textrm{synchronous condenser setting constraints} \\
    & d \ge 0 & \textrm{real power load shedding cannot be negative} \\
    & \sqrt{d^2+e^2} \le |D| & \textrm{load shedding magnitude constraint}
\end{array}$

with variables

* $x \in \mathbb{R}^N$ is the voltage angle,
* $y \in \mathbb{R}^N$ is the voltage magnitude,
* $g \in \mathbb{R}^N$ is the generator real power dispatch,
* $h \in \mathbb{R}^N$ is the generator reactive power dispatch,
* $d \in \mathbb{R}^N$ is the real power demand curtailment,
* $e \in \mathbb{R}^N$ is the reactive power demand curtailment, and
* $c \in \mathbb{R}^N$ is the capacitor settings
* $r \in \mathbb{R}^N$ is the synchronous condenser settings

and parameters

* $P \in \mathbb{R}^N$ is the generation price,
* $\hat P\in \mathbb{R}$ is the maximum generation price,
* $G \in \mathbb{C}^{N \times N}$ is the graph Laplacian,
* $D \in \mathbb{C}^N$ is the total demand,
* $I \in \mathbb{R}^{M \times N}$ is the graph incidence matrix,
* $S \in \mathbb{C}^N$ is the generation capacity,
* $C \in \mathbb{R}^N$ is the capacitor capacity, and
* $R \in \mathbb{R}^N$ is the synchronous condenser capacity.

## Optimal Sizing and Placement

Optimal sizing and placement (OSP) seeks to identify the lowest cost
configuration of generators, capacitors, and condensers that guarantees
demand can be met. The OSP is the solution to the following convex
optimization problem for a network having $N$ busses and $M$ branches.

$\begin{array}{rll}
    \underset{x,y,g,h,c}{\min} & P \sqrt{g^2+h^2} + Q |h| + \frac12 (R+S) |c| + \frac12(R-S) c
\\
    \textrm{subject to} 
    & \Re(G) x - g + c + (\Re D)(1+E) = 0 & \textrm{real power flow balance} \\
    & \Im(G) y - h - c + (\Im D)(1+E) = 0 & \textrm{reactive power flow balance} \\
    & x_{ref} = 0 & \textrm{reference bus voltage angle is always 0} \\
    & y_{ref} = 1 & \textrm{reference bus voltage magnitude is always 1} \\
    & |y-1| \le 0.05 & \textrm{bus voltages within 5\% of nominal} \\
    & |Ix| \le F & \textrm{line flow constraints} \\
    & |h| < 0.2 g & \textrm{constrain reactive power generation to 20\% of real power}
\end{array}$

with variables

* $x \in \mathbb{R}^N$ is the voltage angle,
* $y \in \mathbb{R}^N$ is the voltage magnitude,
* $g \in \mathbb{R}^N$ is the generator real power capacity,
* $h \in \mathbb{R}^N$ is the generator reactive power capacity, and
* $c \in \mathbb{R}^N$ is the capacitor/condenser size

and parameters

* $P \in \mathbb{R}^N$ is the generation energy price,
* $Q \in \mathbb{R}^N$ is the price of reactive power control (not including energy),
* $R \in \mathbb{R}^N$ is the price of installing capacitors,
* $S \in \mathbb{R}^N$ is the price of installing synchronous condensers, and
* $G \in \mathbb{C}^{N \times N}$ is the graph Laplacian,
* $E \in \mathbb{R}$ is the demand safety margin,
* $D \in \mathbb{C}^N$ is the total demand,
* $I \in \mathbb{R}^{M \times N}$ is the graph incidence matrix.

An additional constraint can be imposed if we wish to limit where generators can be placed to only locations where generators exist, and limit how much generation is located there to some factor, say 2x existing existing capacity, e.g.,

$\qquad 0 \le \sqrt{g^2+h^2} \le 2 \Re H \qquad \textrm{generation total power constraint}$

where

* $H \in \mathbb{R}^N$ is the intalled generation capacity.

However, this constraint can result in an infeasible problem, and should not be included if feasibility must be assured.


---- 

# Troubleshooting Guide

The following optimizer results may be observed:

## Optimal

A complementary (primal and dual) solution has been found. The primal and dual
variables are replaced with their computed values, and the objective value of
the problem returned.

## Infeasible

The problem is infeasible as a result of an unbounded direction. The values of
the variables are filled with `NaN`, and the objective value is set to
$+\infty$ for minimizations and feasibility problems, and $-\infty$ for
maximizations.

## Unbounded

The solver has determined that the problem is unbounded. The objective value
is set to $-\infty$ for minimizations, and $+\infty$ for maximizations. The
values of any dual variables are replaced with `NaN`, as the dual problem is
in fact infeasible.

For unbounded problems, CVX stores an unbounded direction into the problem
variables. This is is a direction along which the feasible set is unbounded,
and the optimal value approaches $\pm\infty$. 

## Inaccurate

The solution may be inaccurate for the following reasons.

### Optimal/Unbounded/Infeasible

These three status values indicate that the solver was unable to make a
determination to within the default numerical tolerance. However, it
determined that the results obtained satisfied a relaxed tolerance level and
therefore may still be suitable for further use. If this occurs, you should
test the validity of the computed solution before using it in further
calculations. See Controlling precision for a more advanced discussion of
solver tolerances and how to make adjustments. 

### Approximation

This status value indicates that the voltage angle assumption required by
the **Settings** $\rightarrow$ **Voltage angle accuracy limit** has been
exceeded by one or more voltages in the solution. Exceeding this limit
implies that the solution is inaccurate because the error in the
approximation $\sin(x) \approx x$ used by the fast-decoupled powerflow
constraints is unacceptably large. Exceptionally large angles, e.g., in
excess of 45$^\circ$ will result in potentially wildly inaccurate results. In
general, the simplest solution is to add busses on branches over which large
angles are observed.

## Failed

The solver failed to make sufficient progress towards a solution, even to
within the relaxed tolerance setting. The objective values and primal and
dual variables are filled with `NaN`. This result usually arises from
numerical problems within the model itself.

## Overdetermined

The presolver has determined that the problem has more equality constraints
than variables, which means that the coefficient matrix of the equality
constraints is singular. In practice, such problems are often, but not
always, infeasible. Unfortunately, solvers typically cannot handle such
problems, so a precise conclusion cannot be reached. This result usually
arises from numerical problems within the model itself.

# References

* [Joshua Taylor, *Convex Optimization of Power Systems*, Cambridge University Press (2015)](https://books.google.com/books?hl=en&lr=&id=JBdoBgAAQBAJ&oi=fnd&pg=PR11&dq=info:4_zKJR2GVGAJ:scholar.google.com&ots=A23AB6jlr9&sig=D2uoDpJMlNfCT9an9WOMuBvfk_k#v=onepage&q&f=false)
* [FIDOpower](https://github.com/fidopower/)
    * [Optimal Powerflow/Sizing/Placement](https://github.com/fidopower/optimal_sizing_placement)
* [Arras Energy](https://www.arras.energy/)
    * [Documentation](https://docs.arras.energy/)
    * [Source](https://github.com/arras-energy/)
* [PyPOWER Documentation](https://rwl.github.io/PYPOWER/)
    * [Source](https://github.com/rwl/PYPOWER/)
* [CVXPY](https://www.cvxpy.org/index.html)

