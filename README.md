# README
## Project
*reimplementing [this H-TSP paper](https://github.com/Learning4Optimization-HUST/H-TSP )*

*html flowchart in repo as well*

*final paper, code, and video demo in an anonomous repo, this is just for version control*

### Delivery Metrics

*Compare my results with their version running locally*
compare all these to [the og paper](https://github.com/Learning4Optimization-HUST/H-TSP ) and format like their tables
- runtime
- accuracy as Gap %
- memory footprint(?)

## Model
*Dataset from TSPLIB*
*[GitHub here](https://github.com/Learning4Optimization-HUST/H-TSP )*
### Inputs
Undirected Graph
$$
G=(V,E)
$$
N num nodes
V set of nodes
$$
V = \{v_i |1\leq i \leq N\}
$$
E set of edges
$$
E=\{e_{ij}| 1 \leq i,j \leq N)\}
$$
all  $e \in E$ range [0, 1]
$$cost(i, j)=e_{ij} \forall i, j \in E$$
1 Depot Node where salesman starts and ends
$$
v_d \in V
$$
### Outputs
returns $\tau$, list of nodes visited
Minimizes cost in traversing $\tau$
$$
L(\tau)=cost(\tau_N, \tau_1) + \sum_{i=1}^{N-1}{cost(\tau_i+\tau_{i+1})}
$$
### Process
#### H-TSP
*Hierarchical-TSP*
upper level splits and merges solutions
lower level generates open loop TSP with fixed endpoints
- $v_s$ start, $v_t$ target, both $\in V$
- can merge two open loop TSPs together to form a closed loop

##### Pseudo Code
```
Input V = {v_1, v_2, ..., v_N}

Output Tau = {tau_1, tau_2, ... tau_N} # in order list of nodes visited

Preprocess V with scalable Encoder
V = pseudo image
V = CNN(V)

tau_1 = v_D # first node travelled from is depot
tau_2 = nearest node to v_D

while len(Tau) < N
	SubProb = GenerateSubProb(V, Tau)
	SubSol = SolveSubProb(SubProb)
	Tau = MergeSubSol(SubSol, Tau)
end
return Tau
```

#### Upper Model
##### Scalable Encoder
split nodes into clusters based on where they fall on $H \cdot W$ grid 
augment each node with a vector
- node coordinates
- relative coordinates to grid center 
- relative coordinates to node cluster
- coordinates of previous node in $\tau$ (if applicable, 0 otherwise)
- coordinates of next node in $\tau$ (if applicable, 0 otherwise)
- Boolean whether node has been visited


Creates Tensor of (N, 11) (11 is num features above, coordinate = 2 numbers)
This processed by linear layer to create (N, C) tensor
- Max pooling and zero padding over C dimension to get grid features
Recombine to for pseudo image (H, W, C)
image processed by CNN
##### Sub Problem Generation
```
Inputs: k-NN graph G, partial solution Tau Tau_t, subLength, maxNumUnvisitedNodes

Outputs: subProblem P (v_s1, v_s2, ..., s_subLength), starting node v_s, target node v_t (both contained in P)

Initialize: P to 0s, Q is empty double ended Queue (Dequeue)
v_c = node closest to Coord_pred
v_b = node closest to v_c
push v_b to end of Q
S_v = Tau_t

while len(P) <= maxNumUnvisitedNodes and Q not empty
	v_i = pop front of Q
	for v_j in neighbors in G
		if v_j not in S_v
			push v_j to end of Q
			add v_j to S_v and P
oldLength = subLength - len(P)
P_t = SelectFragment(Tau_t, v_b, oldLength)
P = P union P_t
v_s, v_t = SetEndpoints(P_t)
return P, v_s, v_t
```



#### Lower Model
Transformer Network
- Multi head attention layer
- MLP layer
- mask mechanism
encoder-decoder
- encoder input
	- $q_{context}=q_{graph}+q_{first}+q_{last}+q_{source}+q_{target}$
		- graph feature vectors, first and last nodes of current partial solution
		- start and endpoints of open-loop TSP
Markov Decision Process (MDP)
- Kool, Van Hoof, and Welling 2019; Kwon et al. 2020
- mask removes nodes that have been visited
- reward is negative cost for each feasible solution

### Training
*used training sets with 1,000, 2,000, 5,000, and 10,000 nodes*

#### Upper Model
trained on Proximal Policy Optimization (Schulman et al. 2017)
- minimizes this objective function $L(\theta)=\hat{\mathbb{E}_t}[min(r_t(\theta)\hat{A_t},clip(r_t(\theta),1-\epsilon,1+\epsilon)\hat{A_t})]$
	- where $r_t$ denotes the probability ratio of 2 policies$$r_t(\theta)=\frac{\pi_{\theta}(a_t|s_t)}{\pi_{\theta old}(a_t|s_t)}$$
	- $\hat{A_t}$ is the advantage function, how much better the new policy is to the old one, Generalized Advantage Estimator (GAE) $$\hat{A_t}=\sum_{l=1}^{\infty}{(\gamma \lambda)^l(r_t+\gamma\hat{V}(s_t+l+1)-\hat{V}(s_t+l))}$$
		- where $r_t$ is the reward at t, $\hat{V}$ is the state value function, $\gamma$ is the discount factor, and $\lambda$ is a hyperparameter
#### Lower Model
*model for solving open loop TSPs, specifically with somewhat small amount of nodes*
trained by REINFORCE (Williams 1992) algorithm
- uses Monte Carlo sampling

policy gradient computation

_not sure why this eqn. doesn't render_

$$\nabla_{\theta}J(\theta)=\mathbb{E}_{\pi \theta}[\nabla_{\theta}log\pi_{\theta}(\tau|s)A^{\pi \theta}(\tau)]$$

- $$\approx \frac{1}{N} \sum_{i=1}^{N}{(R(\tau^i)-b(s))\nabla_{\theta}log\pi_{\theta}(\tau^i|s)}$$
- where $\tau$ is a a feasible tsp solution
- $R(\tau^i)$ is the reward, inverse of the length, ie $=-L(\tau^i)$  
- shared baseline: $b(s)=\frac{1}{N} \sum_{i=1}^N{R(\tau^i)}$   

#### Joint Training
need to *warm up* lower model because it significantly affects upper model effectiveness

use solutions from the low model to train upper, meanwhile the subsets generated by the upper are sent to the low model for more training
