import tsplib95 as tsp
import os
from time import time
from augment_data import augment_data
import networkx as nx
from lower import solveSubproblem
from upper import generateSubProb
from upper import update_MDP
from numpy.linalg import norm as linalg_norm
from numpy import array
import mdptoolbox as mdpt
import numpy as np


def calculateDistance(G, route):
    distance = 0.0
    try:
        for node in route:
            if node+1 <= G.number_of_nodes():
                distance += G.edges[node, node+1]['weight']
            else:
                distance += G.edges[node, 1]['weight']
    except Exception as e:
        print('Error in calculateDistance:', e)
        return 1
    return distance


def loadProblem(tsp_file, tour_file):
    problem = tsp.load(tsp_file)
    solution = tsp.load(tour_file)
    return problem, solution


def save_file_func(save_file, tsp_file, time_taken, calc_distance, best_distance, gap_percent):
    open_mode = 'a' if os.path.exists(save_file) else 'w'

    with open(save_file, open_mode) as file:
        file.write('{}\n'.format(tsp_file))
        file.write('    Time taken (s): '+str(time_taken)+'\n')
        file.write('    Calculated Tour Length:'+str(calc_distance)+'\n')
        file.write('    Actual Tour Length: '+str(best_distance)+'\n')
        file.write('    Gap %: '+str(round(gap_percent, 2))+'\n')
    print('Results saved to', save_file)


def get_closest_node(G, coord):
    closest_node = None
    closest_distance = None
    coord = array(coord)
    for node in G.nodes:
        if G.nodes[node]['visited']:
            continue
        distance = linalg_norm(array(G.nodes[node]['coord']) - coord)
        if closest_distance is None or distance < closest_distance:
            closest_distance = distance
            closest_node = node
    return closest_node


def update_graph(G, tau):
    for i, node in enumerate(tau):
        G.nodes[node]['visited'] = True
        if i == 0:
            continue
        G.nodes[tau[i]]['prev_coord'] = G.nodes[tau[i-1]]['coord']
        G.nodes[tau[i-1]]['next_coord'] = G.nodes[tau[i]]['coord']
    return G


def solveProblem(tsp_file, tour_file, save_file=None):
    path = os.path.dirname(os.path.dirname(__file__))
    
    print('Solving tsp for', tsp_file, '...')
    problem, solution = loadProblem(tsp_file, tour_file)
    # for attribute in dir(problem):
    #     if not attribute.startswith('_'):
    #         print('ATTR:', attribute, getattr(problem, attribute))
    start_time = time()
    # load graph
    if problem.name.endswith('.tsp'):
        problem.name = problem.name[:-4]
    try:
        G = nx.read_gpickle(os.path.join(path, 'data/gpickle', problem.name+'.gpickle'))
    except Exception as e:
        print('Error reading gpickle file:', e)
        return
    
    G = augment_data(G)
    
    # initial 2 datapoints
    tau = []
    tau.append(G.nodes[1]['number'])
    G.nodes[1]['visited'] = True
    
    closest_node = get_closest_node(G, G.nodes[1]['coord'])
    tau.append(G.nodes[closest_node]['number'])
    # print('tau:', tau)
    
    G = update_graph(G, tau)
    
    # print('G.nodes[1]:', G.nodes[8])
    
    # main loop
    while len(tau) < G.number_of_nodes():
        
        # print(len(tau), 'of', G.number_of_nodes())
        # print('optimal policy', MDP.policy)
        S = G.number_of_nodes() - len(tau)
        # print(S, 'states')
        if S == 1:
            subProb_nodes = [node for node in G.nodes() if G.nodes[node]['visited'] is False]
        else:
            MDP = update_MDP(None, tau, None, G)
            subProb_nodes, start, end = generateSubProb(G, tau, MDP)
        
        if len(subProb_nodes) < 3:
            sobSol = subProb_nodes
        else:
            sobSol = solveSubproblem(G, subProb_nodes, start, end)
        
        tau.extend(sobSol)
        G = update_graph(G, tau)

    end_time = time()
    tau = G.nodes
    print('tau:', tau)
    print('solution:', solution.tours[0])
    calc_distance = calculateDistance(G, tau)
    best_distance = calculateDistance(G, solution.tours[0])
    
    time_taken = end_time - start_time
    gap_percent = (calc_distance - best_distance)/calc_distance*100

    print('Time taken (s):', time_taken)
    print('bayg29 Calculated Tour Length:', calc_distance)
    print('bayg29 actual Tour Length:', best_distance)
    print('Gap %:', round(gap_percent, 2))

    if save_file:
        save_file_func(save_file, tsp_file, time_taken, calc_distance, best_distance, gap_percent)


if __name__ == '__main__':
    path = os.path.dirname(os.path.dirname(__file__))
    timestamp = time()

    # comment for testing
    # save_file = path+'/solutions/manual_solutions_'+str(timestamp)+'.txt'
    save_file = None
    
    # filename = 'att48.tsp'
    # tsp_file = path+'/data/'+filename
    # tour_file = path+'/data/'+filename[:-4]+'.opt.tour'
    # solveProblem(tsp_file, tour_file, save_file)
    
    # getting num files
    files_to_process = []
    for filename in os.listdir(path+'/data'):
        if filename.endswith('.tsp'):
            files_to_process.append(filename)
    total = len(files_to_process)   

    # processing files
    for i, filename in enumerate(files_to_process):
        tour_file = path+'/data/'+filename[:-4]+'.opt.tour'
        tsp_file = path+'/data/'+filename
        if not os.path.exists(tour_file):
            print('No tour file found for', filename)
            continue
        print('\rProcessing file', filename, i, 'of', total, end='')
        
        solveProblem(tsp_file, tour_file, save_file)
    print('All files processed')
