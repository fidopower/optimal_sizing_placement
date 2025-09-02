
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
