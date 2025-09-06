
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

#### Code Implementation - 

'''

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

However, this constraint can result in an infeasible problem, and should not be included if feasibility must be assured.'''

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

There is a way to save the settings for the capacitors which is good, however, the 
condenser bank configurations are not being saved, so I am going to be making those updates
