import mdptoolbox as mdpt
import mdptoolbox.example
import numpy as np


def naiveClusterSolving(G, tau):
    for node in G.nodes():
        if G.nodes[node]['visited'] is False:
            break
    target_cluster = G.nodes[node]['cluster']
    target_nodes = [n for n in G.nodes() if G.nodes[n]['visited'] is False and G.nodes[n]['cluster'] == target_cluster]
    
    # Ensure target_nodes has at least 3 nodes
    if len(target_nodes) < 3:
        for node in G.nodes():
            if G.nodes[node]['visited'] is False and node not in target_nodes:
                target_nodes.append(node)
                if len(target_nodes) >= 3:
                    break
    
    return target_nodes, target_nodes[0], target_nodes[-1]


def update_MDP(MDP, tau, sobSol, G, discount=0.7):
    # TODO currently generates new MDP for each subproblem
    # consider updating the MDP instead
    S = G.number_of_nodes() - len(tau)
    # Generate P and R
    P, R = mdptoolbox.example.forest(S=S, r1=4, r2=2, p=0.1)
            
    try:
        mdpt.util.check(P, R)
    except Exception as e:
        print('P:', P.shape)
        print('sum of P[0]:', np.sum(P[0]))
        print('sum of P[1]:', np.sum(P[1]))
        print("P1:", P[1])
        
        raise e
    MDP = mdpt.mdp.PolicyIteration(P, R, discount)
    return MDP

def generateSubProb(G, tau, MDP):
    # subProblem = []
    # # use mdp to solve subproblem
    # MDP.run()
    # # print('optimal_policy:', MDP.policy)
    # # print('optimal_value:', MDP.V)
    
    # for node, policy in enumerate(MDP.policy):
    #     if policy == 1:
    #         subProblem.append(node+1)
    
    # for node in G.nodes():
    #     if G.nodes[node]['visited'] is False and node not in subProblem:
    #         subProblem.append(node)
    #         break
    
    subProblem, start, end = naiveClusterSolving(G, tau)
    return subProblem, subProblem[0], subProblem[-1]
