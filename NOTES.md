
## Optimal Powerflow Original

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

## Primary Questions

Inconsistencies between code implementation and the

|Variable | Objective/ Constraint |  Code Implementation |
|----------|----------------------------|------------|
| $c$ capacitor injection| $ 0 \le c \le C $ |    $ \|c\| \le C $|
| $g,h$ generator    | $ \sqrt{g^2 + h^2}   $ | $ \|g+ h \|$  |
| $d, e$  demand    |  $ \sqrt{d^2 + e^2}   $       | $ \|d+ e \|$      |
| Objective  |  $ P (\sqrt{g^2+h^2}+c+r) + 100 \hat{P} \sqrt{d^2+e^2} $ | $ P (\|g+ h \|+c) + 100 \hat{P} \|d+ e \|$ |


1. Why is there no $r$ in OPF problem code?  
    > Is it because we were trying to figure out the OPF with just capacitors?

2. Why is the capacitor constraint ```cp.abs(c) <= C``` instead of ``` 0<=c<= C```?
    > I thought capcitors could only inject reactive power and not absorb it like condensers

3. Why are capacitors included in real power constraint? 
    > Are we modeling the capacitors as being able to both absorb and dispatch reactive power as condensers, otherwise they should only be in the 2nd constraint -  $\Im(G) y - h - c + \Im(D) - e = 0$


## Updated Model 

$
\begin{aligned}
\min_{x,\,y,\,g,\,h,\,c,\,r,\,d,\,e}\quad
& \sum_{i=1}^{N} P_i\,\bigl|\,g_i +  h_i\,\bigr|
\;+\;
\Bigl(100\,\hat P\Bigr)\sum_{i=1}^{N} \bigl|\,d_i + e_i\,\bigr|
\\[0.75em]
\text{s.t.}\quad
& \Re(G)\,x \;-\; g \;+\; c \;+\; \Re(D) \;-\; d \;-\; r \;=\; 0,
&&\text{(real power balance)}\\
& \Im(G)\,y \;-\; h \;-\; c \;+\; \Im(D) \;-\; e \;+\; r \;=\; 0,
&&\text{(reactive power balance)}\\
& x_{\mathrm{ref}} = 0,\qquad y_{\mathrm{ref}} = 1,
&&\text{(reference bus)}\\
& |\,y - \mathbf{1}\,| \;\le\; \text{voltage\_limit},
&&\text{(voltage magnitude bounds)}\\
& |\,I\,x\,| \;\le\; F,
&&\text{(line flow proxy bounds)}\\
& g \;\ge\; 0,
&&\text{(real generation nonneg.)}\\
& |\,h\,| \;\le\; \Im(S),
&&\text{(reactive gen. limits)}\\
& \bigl|\,g +  h\,\bigr| \;\le\; \Re(S),
&&\text{(apparent gen. limits)}\\
& 0 \;\le\; c \;\le\; C,
&&\text{(capacitor setting bounds)}\\
& |r| \;\le\; R,
&&\text{(condenser bounds)}\\
& d \;\ge\; 0,\qquad \bigl|\,d +  e\,\bigr| \;\le\; |D|.
&&\text{(load curtailment bounds)}
\end{aligned}
$

### DATE: 08/22 

* A little unsure about the real and reactive power constraints that are being used

#### ISSUES: 
1. The P or the price vector is all 0s, shouldn't be the case in my opinion 
2. Both C and R are 0s which is also something that shouldn't be happening
3. The max voltage on the display has the units deg also the mean voltage magnitude is greater than the max voltage magnitude



#### Fix Plan
There might be value having some debug scripts 
1. Follow the code for P to the root and figure out what it is outputting 
2. Follow the code for C and R to the root and figure what it is outputting or copying from. 
3. Follow the code on how voltage is being displayed specifically at ```gld_pypower_corrected.py lines 1292 - 1305```


### Long-term but not immediate Fixes 
1. Update the notebook so it automatically opens the pypower example by default

#### Findings

#### 2. 

So the primary reason that the condenser and the capacitor is set to 0 is because the code is looking for a "shunts" key in ``` lines 795 - 810```, it relies on a ```self.find("shunt")``` which is not a valid "key" in the "objects" dictionary - the correct key is "capacity". However, "shunt" only gets defined when we setup the optimal sizing problem and then run the initial powerflow problem without refresh. In the first run of the model with initial powerflow, the condenser and the capacitor settings are 0. 


#### 1. 

Solved the issue, the code was looking at the cost of reactive power output instead of the real power output, which is $100. 


#### 3. Flows 

##### Graph Incidence Matrix
Fixed, the admittance was the same as the impedence in the previous version, corrected now.


### Questions 
1. Since were are working with pypower test cases and if I remember correctly dealing with the transmission network we should be working with the AC network correct? 



### DATE: 09/06/2025 


#### ISSUES
1. OSP was not taking into account condensor_costs (Resolved)
2. There is a way to save the settings for the capacitors which is good, however, the 
condenser bank configurations are not being saved, so I am going to be making those updates to save 
those to the model. (resolved)
3. Update Model is not reading the correct capacitor settings and updating itself accordingly (resolved)


Below is the OSP problem original as mentioned in the READM.md

$\begin{array}{rll}
    \underset{x,y,g,h,c}{\min} & P \sqrt{g^2+h^2} + Q |h| + \frac12 (R+S) |c| + \frac12(R-S) c
\\
    \textrm{subject to} 
    & \Re(G) x - g + c + (\Re (D))(1+E) = 0 & \textrm{real power flow balance} \\
    & \Im(G) y - h - c + (\Im (D))(1+E) = 0 & \textrm{reactive power flow balance} \\
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


#### Code version

In the code the following optimization is implemented- 

$$
\min_{x, y, g, h, c} \;
|P||g| + |\Im(P)||h| + \frac12 (R+S) |c| + \frac12(R-S) c
$$

**subject to:**

Real power balance:
$$
g - \Re(G) x + c -\Re(D) (1 + E) = 0
$$

Reactive power balance:
$$
h - \Im(G) y - c -\Im(D)(1 + E) = 0
$$

Reference bus constraints:
$$
x_{\text{ref}} = 0 \quad \text{and} \quad y_{\text{ref}} = 1
$$

Voltage magnitude limits:
$$
|y - 1| \leq \varepsilon_V
$$

Line flow constraints:
$$
|I x| \leq F
$$

Real generation constraint:
$$
g \geq 0
$$

Reactive generation constraint:
$$
|h| \leq \varphi g
$$

**Optional generator siting constraint:**
$$
|g + h|\leq \gamma \cdot |S|
$$

---

**Variables:**

- \( x \in \mathbb{R}^N \) — voltage angles  
- \( y \in \mathbb{R}^N \) — voltage magnitudes  
- \( g \in \mathbb{R}^N \) — real power generation  
- \( h \in \mathbb{R}^N \) — reactive power generation  
- \( c \in \mathbb{R}^N \) — capacitor/condenser setting  

**Parameters:**

- \( P \in \mathbb{R}^N \) — real power cost 
- \( Q \in \mathbb{R}^N \) — reactive power cost
- \( R \in \mathbb{R}^N \) — capacitor installation cost  
- \( S \in \mathbb{R}^N \) — condenser installation cost  
- \( G \in \mathbb{C}^{N \times N} \) — Laplacian admittance matrix  
- \( D \in \mathbb{R}^N \) —  demand  
- \( I \in \mathbb{R}^{M \times N} \) — incidence matrix  
- \( F \in \mathbb{R}^M \) — line flow limits  
- \( E\varepsilon_V \in \mathbb{R} \) — voltage deviation tolerance  
- \( \varphi \in \mathbb{R} \) — max reactive-to-real generation ratio  
- \( \gamma \in \mathbb{R} \) — generation expansion limit (optional)


I think the above implementation is okay, for each capacitor when are technically adding 
a condenser at some node that only absorbs reactive power. The positive values of c are 
reactive power injections and are associated with capacitors and the negative values are 
associated with condensors which absorb that reactive power. 


#### Code Issues

1. There is a way to save the settings for the capacitors which is good, however, the 
condenser bank configurations are not being saved, so I am going to be making those updates

### Date Sep 7 2025 

#### Issues in OSP 
1. The new generation that is being added is being stored with the wrong "parent" key in update_model. (resolved) 
> Parent key was fine, the gencost object associated with the gen object in the objects dictionary had the wrong price information, should be corrected now. 
2. The new generation currently is polynomial in nature, which leads to two possible suggested fixes 
i. Either have a more general objective function definition because that doesn't currently allow for polynomial model, and then implement the polynomial cost function, we might be stuck with this because there are some generation costs specified in the example.json, and I need to check whether those apply to new generation or are shared between the different generation units at the same bus.
3. We need to update the objective if reactive power is going to have different production costs, since the objective cannot deal with complex numbers, for now the simple fix would work but it is not a longterm solution. 


#### Questions 
The current code is not setup to allow for polynomial cost data and information. The polynomial costs are something like this "0.1, 100, 0" where the first might be the quadratic, the second term is the linear and the last is the constant. If that is the case then in the initial implementation of the "



### Date Sep 8 2025 

### DISCUSS 
1. The OPF objective function expects that there is one generation unit per bus and is indexed based on buses, however, there could be multiple generation units at a given bus.  Maybe need to introduce another P_n for the newly added generation units on top of the existing generation. 
2. The OPF objective also doesn't know how to deal with reactive power costs, which could be added as a different multiplication as well (Resolved) .
3. Also, need to double check but the 0.1 unit in the objective and the constraints is equivalant to 10 MW so the base is 100 MWs, and the prices are technically per MW, 
> There needs to be a 100 in front of both P and $\hat{P}$ (Resolved)


### Date Sep 12th 2025
1. Updated the Polynomial UI in the Settings, should reflect the correct units (Monday)
2. In the process of translating TODOs from the meeting recording. 


#### TODOs
1. Update the reactive and real power constraints in the OSP problem (resolved)
    i. There is a further issue caused by this, the current system is now leading ot curtialment, this might be likely because generation capacity is being replaced rather than being added to current generation.(resolved)
2.Update the reactive and real power constraint with existing capacitors and condensors to o (resolved)
3. Figure out the production functions for - 
    i. Combustion Turbines 
    ii. Combined Cycle
    iii. Wind 
    iv. Solar 
    v. Hydro 
4. Set Capacity Costs and Production Costs accordingly 


#### Questions 
1. In ```generation``` method what is the difference between keys 'capacity' and 'actual'
2. "On the existing generator side the cost isn't part of the objective function" when referring to the OPF problem. 


New OPF problem with binary costs to adding generation to non generating nodes

For N

$\begin{array}{rll}
    \underset{x,y,g_{1,1},...,g_{N,k},h_{1,1},...,h_{N,k},c,d,e}{\min}
    &   \sum_{n=1}^{N}\sum_{k=1}^{K} P_{n,k}(|g_{n,k} + ih_{n,k}|)+ \hat{P}*|d_{n,k}+ ie_{n,k}| \\
    \textrm{subject to} 
    & g =
      \begin{bmatrix}
        \sum_{k=1}^{K} g_{1,k} \\
        \sum_{k=1}^{K} g_{2,k} \\
        \vdots \\
        \sum_{k=1}^{K} g_{N,k}
      \end{bmatrix} \\
    &\\
    & h =
      \begin{bmatrix}
        \sum_{k=1}^{K} h_{1,k} \\
        \sum_{k=1}^{K} h_{2,k} \\
        \vdots \\
        \sum_{k=1}^{K} h_{N,k}
      \end{bmatrix} \\
    &\\ 
    & \Re(G) x - g + c + \Re(D) - d - r = 0 & \textrm{real power flow balance} \\
    & \Im(G) y - h - c + \Im(D) - e + r = 0 & \textrm{reactive power flow balance} \\
    & x_{ref} = 0 & \textrm{reference bus voltage angle is always 0} \\
    & y_{ref} = 1 & \textrm{reference bus voltage magnitude is always 1} \\
    & |y-1| \le 0.05 & \textrm{bus voltages within 5\% of nominal, default 5\%, can be set based on user preference} \\
    & |\Re{(I)}x + \Im{(I)}y | \le F & \textrm{line flow constraints} \\
    & g \ge 0 & \textrm{real generation power constraints} \\
    & |h| \le \Im(S) & \textrm{reactive generation power constraints} \\
    & |g + h| \le \Re(S) & \textrm{apparent generation power constraints} \\
    & 0 \le c \le C & \textrm{capacitor setting constraints} \\
    & |r| \le R & \textrm{synchronous condenser setting constraints} \\
    & d \ge 0 & \textrm{real power load shedding cannot be negative} \\
    & |d + e | \le |D| & \textrm{load shedding magnitude constraint}
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

* $P_{n,k}(.): \mathbb{C} \mapsto \mathbb{R} $ , production function for generator $k$ at bus $n$,
* $\hat P\in \mathbb{R}$ is the curtailment cost,
* $G \in \mathbb{C}^{N \times N}$ is the graph Laplacian,
* $D \in \mathbb{C}^N$ is the total demand,
* $I \in \mathbb{R}^{M \times N}$ is the graph incidence matrix,
* $S \in \mathbb{C}^N$ is the generation capacity,
* $C \in \mathbb{R}^N$ is the capacitor capacity, and
* $R \in \mathbb{R}^N$ is the synchronous condenser capacity.



### Improved OSP with Substation Fees


$$
\min_{x, y, g, h, c} \;
|P||g| + |\Im(P)||h| + \frac12 (R+S) |c| + \frac12(R-S) c + \mathbb{1}_{\{
    \text{no generators present at bus and }  g_i > 0  \}}*H
$$

**subject to:**

Real power balance:
$$
\Re(G) x - g + c + \Re(D) (1 + E) = 0
$$

Reactive power balance:
$$
\Im(G) y  - h - c + \Im(D)(1 + E) = 0
$$

Reference bus constraints:
$$
x_{\text{ref}} = 0 \quad \text{and} \quad y_{\text{ref}} = 1
$$

Voltage magnitude limits:
$$
|y - 1| \leq \varepsilon_V
$$

Line flow constraints:
$$
|\Re(I)x + \Im(I)y| \leq F
$$

Real generation constraint:
$$
g \geq 0
$$

Reactive generation constraint:
$$
|h| \leq \varphi g
$$

**Optional generator siting constraint:**
$$
|g + h|\leq \gamma \cdot |S|
$$



**Variables:**

- \( x \in \mathbb{R}^N \) — voltage angles  
- \( y \in \mathbb{R}^N \) — voltage magnitudes  
- \( g \in \mathbb{R}^N \) — real power generation  
- \( h \in \mathbb{R}^N \) — reactive power generation  
- \( c \in \mathbb{R}^N \) — capacitor/condenser setting  

**Parameters:**

- \( P \in \mathbb{R}^N \) — real power cost 
- \( Q \in \mathbb{R}^N \) — reactive power cost
- \( R \in \mathbb{R}^N \) — capacitor installation cost  
- \( S \in \mathbb{R}^N \) — condenser installation cost  
- \( G \in \mathbb{C}^{N \times N} \) — Laplacian admittance matrix  
- \( D \in \mathbb{R}^N \) —  demand  
- \( I \in \mathbb{R}^{M \times N} \) — incidence matrix  
- \( F \in \mathbb{R}^M \) — line flow limits  
- \( H \in \mathbb{R}^N \) —  constant interconnection/substation fees for adding new generation to buses with no previous generation
- \( E\varepsilon_V \in \mathbb{R} \) — voltage deviation tolerance  
- \( \varphi \in \mathbb{R} \) — max reactive-to-real generation ratio  
- \( \gamma \in \mathbb{R} \) — generation expansion limit (optional)
    
------
### Current OSP implementation 
       
\[
\begin{array}{rll}
    \underset{x,y,g,h,c,s,z}{\min} 
    & P^T|g+h| +  Q^T|h|
        + \tfrac{1}{2}(R + S)|c| 
        + \tfrac{1}{2}(R - S)c 
        + \tfrac{1}{2}L^T(|g+h| - |M|) 
        + \tfrac{1}{2}L^T\;|\;(|g+h| - |M|)\;| \\
    \textrm{s.t.}
    & \Re(G)x - g + c + \Re(D)(1+E)  = 0 
    & \textrm{real power balance} 
    \\
    & \Im(G)y - h - c + \Im(D)(1+E) = 0 
    & \textrm{reactive power balance} 
    \\
    & x_{\text{ref}} = 0,\;\; y_{\text{ref}} = 1 
    & \textrm{reference bus constraints} 
    \\
    & |y-1| \le \varepsilon_V 
    & \textrm{voltage magnitude limits} 
    \\
    & |\Re(I)x + \Im(I)y| \leq F
    & \textrm{line flow limits} 
    \\
    & g \ge 0, |h| \le \varphi g 
    & \textrm{generator capability limits} 
    \\
\end{array}
\]

\( \mathcal{B}_0\) is the set of buses where there is no existing generation 

**Variables:**

- \( x \in \mathbb{R}^N \) — voltage angles  
- \( y \in \mathbb{R}^N \) — voltage magnitudes  
- \( g \in \mathbb{R}^N \) — real power generation  
- \( h \in \mathbb{R}^N \) — reactive power generation  
- \( c \in \mathbb{R}^N \) — capacitor/condenser setting  

**Parameters:**

- \( P \in \mathbb{R}^N \) — real power cost 
- \( Q \in \mathbb{R}^N \) — reactive power cost
- \( R \in \mathbb{R}^N \) — capacitor installation cost  
- \( S \in \mathbb{R}^N \) — condenser installation cost  
- \( G \in \mathbb{C}^{N \times N} \) — Laplacian admittance matrix  
- \( D \in \mathbb{R}^N \) —  demand  
- \( I \in \mathbb{R}^{M \times N} \) — incidence matrix  
- \( F \in \mathbb{R}^M \) — line flow limits  
- \( L \in \mathbb{R}^M \) - substation capacity upgrade cost ($/MW)
- \( M \in \mathbb{C}^N \) — existing substation power capacity
- \( E\varepsilon_V \in \mathbb{R} \) — voltage deviation tolerance  
- \( \varphi \in \mathbb{R} \) — max reactive-to-real generation ratio  
- \( \gamma \in \mathbb{R} \) — generation expansion limit (optional)


### Questions 
So currently M is the same as S (existing capacity at each bus) and is complex, I am currently taking the absolute value of that capacity to calculate the apparent power capacity at each of those buses. There might be a different way to do it, if we think that the controls and substation upgrades for reactive power control are different.


### Fixed Cost Substation Installation OSP (incorrect)

       
\[
\begin{array}{rll}
    \underset{x,y,g,h,c,s,z,m}{\min} 
    & P^T|g+jh| +  Q^T|jh|
        + \tfrac{1}{2}(R + S)|c| 
        + \tfrac{1}{2}(R - S)c 
        + 4H(-(m-0.5)^2) + \tfrac{1}{2}L^T((|g+jh| - |M|)+ ||g+jh| - |M||) \\
    \textrm{s.t.}
    & \Re(G)x - g + c + \Re(D)(1+E)  = 0 
    & \textrm{real power balance} 
    \\
    & \Im(G)y - h - c + \Im(D)(1+E) = 0 
    & \textrm{reactive power balance} 
    \\
    & x_{\text{ref}} = 0,\;\;\  y_{\text{ref}} = 1 
    & \textrm{reference bus constraints} 
    \\
    & |y-1| \le \varepsilon_V 
    & \textrm{voltage magnitude limits} 
    \\
    & |\Re(I)x + \Im(I)y| \leq F
    & \textrm{line flow limits} 
    \\
    & g \ge 0, |jh| \le \varphi g 
    & \textrm{generator capability limits} 
    \\
    & |g + jh| \leq Um \\ 
    & 0 \leq m \leq 1 \\
\end{array}
\]


**Variables:**

- \( x \in \mathbb{R}^N \) — voltage angles  
- \( y \in \mathbb{R}^N \) — voltage magnitudes  
- \( g \in \mathbb{R}^N \) — real power generation  
- \( h \in \mathbb{R}^N \) — reactive power generation  
- \( c \in \mathbb{R}^N \) — capacitor/condenser setting  

**Parameters:**

- \( P \in \mathbb{R}^N \) — real power cost 
- \( Q \in \mathbb{R}^N \) — reactive power cost
- \( R \in \mathbb{R}^N \) — capacitor installation cost  
- \( S \in \mathbb{R}^N \) — condenser installation cost  
- \( H \in \mathbb{R}^N \) - fixed costs for installing a new substation, 0 if a bus has generation capacity already installed, (Assumed to be amortized already)
- \( G \in \mathbb{C}^{N \times N} \) — Laplacian admittance matrix  
- \( D \in \mathbb{R}^N \) —  demand  
- \( I \in \mathbb{R}^{M \times N} \) — incidence matrix  
- \( F \in \mathbb{R}^M \) — line flow limits  
- \( L \in \mathbb{R}^M \) - substation capacity upgrade cost ($/MW)
- \( M \in \mathbb{C}^N \) — existing substation power capacity (equal to existing generation)
- \( U \in \mathbb{C}^N \) — Max allowed generation at bus i 
- \( \varepsilon_V \in \mathbb{R} \) — voltage deviation tolerance  
- \( \varphi \in \mathbb{R} \) — max reactive-to-real generation ratio  
- \( \gamma \in \mathbb{R} \) — generation expansion limit (optional)


### Variable Cost Premium Substation Installation OSP

#### Define: 

\(s = |g + jh|\)
\(q = |jh|\)

#### Optimization
\[\begin{array}{rll}
    \underset{x,y,g,h,c,s,z,m}{\min} 
    & P^Ts +  Q^Tq
        + \tfrac{1}{2}(R + S)|c| 
        + \tfrac{1}{2}(R - S)c \\
        & +  \underbrace{KH^Tm}_{\text{Substation Installation costs}}
         + \underbrace{\tfrac{1}{2}L^T((s - |M|)+ |s - |M||)}_{\text{Substation upgrade cost}} \\
    \textrm{s.t.}
    & \Re(G)x - g + c + \Re(D)(1+E)  = 0 
    & \textrm{real power balance} 
    \\
    & \Im(G)y - h - c + \Im(D)(1+E) = 0 
    & \textrm{reactive power balance} 
    \\
    & x_{\text{ref}} = 0,\;\;\  y_{\text{ref}} = 1 
    & \textrm{reference bus constraints} 
    \\
    & |y-1| \le \varepsilon_V 
    & \textrm{voltage magnitude limits} 
    \\
    & |\Re(I)x + \Im(I)y| \leq F
    & \textrm{line flow limits} 
    \\
    & g \ge 0, q \le \varphi g 
    & \textrm{generator capability limits} 
    \\
    & s \leq Um \\ 
    & 0 \leq m \leq 1 \\
\end{array} \]

When the optimal value of m is solved for there should be no slack in the constraint $s \leq Um$
as the optimizer tries to solve for suit
\(H \in \{0, 1\}^N\)
\(K \in R\) ($/MW cost of constructing a substation)
\(U \in R\) This is an upper bound that is likely never achieved by apparent power out of a bus, we set it at \( 3\sum_{i}|d_i + je_i|\) where max output for a bus is 3 times the total apparent power demand accross all buses.
\(M \in C^N \) Existing apparent power substation capacity at a given bus 

Users can specify the amortized \$/MW cost for constructing a substation at a given bus location call it $A$

We can use the following equation to solve for K
$$A = \frac{K}{U}$$
$$K = AU$$

Where $U$ is a property of the network and $A$ is specified by the User

#### Note: 
The reason we have this problem formualated this way is when the optimizer minimizes the objective by lowering the value of m. Since it's m is linear in the objective, it will lower it tills there is no slack on the following constraint $$s \leq Um$$

At the optimal m we would have 

$$ m = \frac{s}{U}$$

Plugging into the objective, the cost per $/MW for constructing a substation at a location that doesn't have any generation becomes the following - 

$$ KH^Tm = KH^T  (\frac{s}{U}) = \frac{KH^T}{U}s = \frac{(AU)H^T}{U}s = AH^Ts $$

For bus index i with no generation capacity $H_i = 1$ so the cost of adding generation at that bus needs 
to account for the construction of the substation in \$/MW way where the substation construction costs are - 

$$As$$ 

(Since s is $/MWH and the apparent power generation at a given bus)

For buses i that have capacity and construction of new substation is not necessary ($H_i = 0$), the costs for upgrading the substation apparent power capacity if necessary are represented using the following ReLU function in the objective- 

$$ \tfrac{1}{2}L_i((s_i - |M_i|)+ |s_i- |M_i||) $$

For buses $i^-$ that **don't** have capacity present and the construction of a new substation **is** necessary ($H_i = 1$), adding generation capacity is slightly higher when compared to buses with prexisting generation. They incur a $/MW generation cost for the construction of new substation. When combined with the additional substation upgrade costs we see that if the optimization suggests that we need to add capacity at a given location which did not previously have capacity then the total substation costs for that location (as expressed in the objective) end up being to following - 

$$ =As_{i^-} +  \tfrac{1}{2}L_{i^-}((s_{i^-} - |M_{i^-}|)+ |s_{i^-}- |M_{i^-}||) $$

$$= As_{i^-} +  \tfrac{1}{2}L_{i^-}((s_{i^-})+ |s_{i^-}|) \quad \quad (\text{because }M_{i^-}= 0)$$ 

$$= As_{i^-} +  L_{i^-}s_{i^-}$$ 
$$= (A + L_{i^-})s_{i^-} $$ 

Notice that as long as $A >0$ and $M_i > 0$ for buses i with existing substation capacity , and $i^-$ refer to buses without substation or previously existent generation, the following would always hold - 

$$ (A + L_{i^-})s_{i^-} >  \tfrac{1}{2}L_i((s_i - |M_i|)+ |s_i- |M_i||)  $$ 

Implying the $/MW cost for adding generation at a location without previous generation and substation is higher than adding capacity to buses with existing generation. 


