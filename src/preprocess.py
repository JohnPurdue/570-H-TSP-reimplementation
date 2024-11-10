import os
import tsplib95 as tsp
import networkx as nx
import signal

'''
Not run by solver 
Should go through files in data and
    check if they are in the correct format
    normalize coords
    normalize weights
'''


def normalize_tsp_file(filename):
    
    problem = tsp.load(filename)
    G = problem.get_graph()
    
    # normalize coords
    min_x = float('inf')
    max_x = float('-inf')
    min_y = float('inf')
    max_y = float('-inf')
    # find mins and maxes
    for node, data in G.nodes(data=True):
        x, y = data['coord']
        if x < min_x:
            min_x = x
        if x > max_x:
            max_x = x
        if y < min_y:
            min_y = y
        if y > max_y:
            max_y = y
    
    for node, data in G.nodes(data=True):
        x, y = data['coord']
        normalized_x = (x - min_x) / (max_x - min_x)
        normalized_y = (y - min_y) / (max_y - min_y)
        data['coord'] = (normalized_x, normalized_y)
    
    # edges
    min_weight = float('inf')
    max_weight = float('-inf')
    
    for u, v, data in G.edges(data=True):
        weight = data.get('weight', 1)
        if weight < min_weight:
            min_weight = weight
        if weight > max_weight:
            max_weight = weight
    
    for u, v, data in G.edges(data=True):
        weight = data.get('weight', 1)
        normalized_weight = (weight - min_weight) / (max_weight - min_weight)
        data['weight'] = normalized_weight
    
    return G


if __name__ == '__main__':
    path = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(path, 'data')
    
    # G = normalize_tsp_file(os.path.join(data_dir, 'bayg29.tsp'))
    
    # nx.write_gpickle(G, os.path.join(data_dir, 'gpickle' ,'bayg29.tsp'[:-4]+'.gpickle'))
    
    # G = nx.read_gpickle(os.path.join(data_dir, 'gpickle' ,'bayg29.gpickle'))
    # assert all(0 <= data['weight'] <= 1 for u, v, data in G.edges(data=True))
    files_to_process = []
    already_processed = os.listdir(os.path.join(data_dir, 'gpickle'))
    already_processed = [filename[:-8] for filename in already_processed]
    # to refuce loading times only process files with less than 100 nodes
    for filename in os.listdir(data_dir):
        if filename.endswith('.tsp') and filename[:-4] not in already_processed and not filename[-8].isdigit():
            files_to_process.append(filename)
    total = len(files_to_process)
    
    print('Preprocessing data...')
    for i, file in enumerate(files_to_process):
        print('\rProcessing file', i+1, 'of', total, '...', end='')

        def handler(signum, frame):
            raise TimeoutError

        signal.signal(signal.SIGALRM, handler)
        signal.alarm(120)  # Set the timeout to 2 minutes
        try:
            G = normalize_tsp_file(os.path.join(data_dir, file))
            nx.write_gpickle(G, os.path.join(data_dir, 'gpickle', file[:-4]+'.gpickle'))
        except TimeoutError:
            print('Timeout processing file', file)
        except Exception as e:
            print('Error processing file', file, e)
        finally:
            signal.alarm(0)  # Disable the alarm
    print('Data preprocessing complete.')
