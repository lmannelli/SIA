import numpy as np
import node
import Utils.priorityQueue as priorityQueue
import Utils.priorityQueueGreedy as priorityQueueGreedy
import time
import math
import Utils.fillzoneUtils as fillzoneUtils
import Utils.heuristic as heuristics

TRIES = 2

movement_cost = 1

# M
colors = 6
# NxN
dim = [4, 6, 8]


# armo una cola y voy sacando el nodo que hace más tiempo se encuentra en la cola
def bfs_search_fill_zone(root, dimension):
    queue = [root]
    total_nodes = 1
    border_nodes = 1

    while queue:
        actual_node = queue.pop(0)
        border_nodes = border_nodes - 1

        if fillzoneUtils.is_goal(actual_node, dimension):
            return actual_node, border_nodes, total_nodes

        # por cada color veo como queda la matriz al escogerlo
        for color in range(colors):
            if color != actual_node.color:
                new_state = fillzoneUtils.change_color(np.copy(actual_node.state), actual_node.visited, color,
                                                       dimension)
                blank_matrix = np.zeros((dimension, dimension))
                main_island, island_size = fillzoneUtils.get_principal_block_recursive(new_state, blank_matrix, 0, 0, color, 0,
                                                                             dimension)
                if not fillzoneUtils.is_insignificant_move(actual_node.visited, main_island, dimension):
                    new_node = node.Node(new_state, main_island, actual_node.cost + movement_cost,
                                         actual_node, color, island_size)
                    queue.append(new_node)
                    total_nodes = total_nodes + 1
                    border_nodes = border_nodes + 1


def dfs_search_fill_zone(actual_node, dimension, border_nodes_dfs=1, total_nodes_dfs=1):
    border_nodes_dfs = border_nodes_dfs - 1
    # nodo Encontrado
    if fillzoneUtils.is_goal(actual_node, dimension):
        return actual_node, border_nodes_dfs, total_nodes_dfs

    # siguiente nodo
    for color in range(colors):
        if color != actual_node.color:
            new_state = fillzoneUtils.change_color(np.copy(actual_node.state), actual_node.visited, color, dimension)
            blank_matrix = np.zeros((dimension, dimension))
            main_island, island_size = fillzoneUtils.get_principal_block_recursive(new_state, blank_matrix, 0, 0, color, 0,
                                                                         dimension)
            if not fillzoneUtils.is_insignificant_move(actual_node.visited, main_island, dimension):
                new_node = node.Node(new_state, main_island, actual_node.cost + movement_cost,
                                     actual_node, color, island_size)
                next_node, border_nodes, total_nodes = dfs_search_fill_zone(new_node, dimension, border_nodes_dfs + 1,
                                                                  total_nodes_dfs + 1)
                if next_node is not None:
                    return next_node, border_nodes, total_nodes


def a_search_fill_zone(root, dimension, heuristic, blocks_count):
    queue = priorityQueue.PriorityQueue()
    queue.insert(root)

    if fillzoneUtils.is_goal(root, dimension):
        return root, 1, 1

    total_nodes = 1
    border_nodes = 1
    gained_blocks = 0
    while not queue.isEmpty():
        actual_node = queue.pop()
        border_nodes = border_nodes - 1
        if fillzoneUtils.is_goal(actual_node, dimension):
            #print('GOAL ACHIVED')
            return actual_node, border_nodes, total_nodes
        
        # por cada color veo como queda la matriz al escogerlo
        for color in range(colors):
            if color != actual_node.color:
                new_state = fillzoneUtils.change_color(np.copy(actual_node.state), actual_node.visited, color,
                                                       dimension)
                gained_blocks += 1
                blank_matrix = np.zeros((dimension, dimension))
                main_island, island_size = fillzoneUtils.get_principal_block_recursive(new_state, blank_matrix, 0, 0, color, 0,
                                                                             dimension)
                if actual_node.island_size < island_size:
                    new_node = node.Node(new_state, main_island, actual_node.cost + movement_cost,
                                         actual_node, color, island_size)
                    if heuristic == 1:
                        heuristic_val = heuristics.heuristic1(new_node, dimension, colors)
                    elif heuristic == 2:
                      heuristic_val = heuristics.heuristic2(new_state, new_node, dimension)
                    else:
                       heuristic_val = heuristics.heuristic3(new_node, dimension)

                    new_node.set_value(heuristic_val)
                    total_nodes = total_nodes + 1
                    border_nodes = border_nodes + 1

                    if heuristic_val == 0:
                        return new_node, border_nodes, total_nodes
                    queue.insert(new_node)


def greedy_fill_zone(root, dimension, heuristic, blocks_count):
    current = root
    total_nodes = 1
    border_nodes = 0
    gained_blocks = 0

    while not fillzoneUtils.is_goal(current, dimension):
        queue = priorityQueueGreedy.PriorityQueue()
        # por cada color veo como queda la matriz al escogerlo
        for color in range(colors):
            if color != current.color:
                aux = np.copy(current.state)
                new_state = fillzoneUtils.change_color(aux, current.visited, color, dimension)
                gained_blocks += 1                
                blank_matrix = np.zeros((dimension, dimension))
                main_island, island_size = fillzoneUtils.get_principal_block_recursive(new_state, blank_matrix, 0, 0, color, 0,
                                                                             dimension)
                if not fillzoneUtils.is_insignificant_move(current.visited, main_island, dimension):
                    new_node = node.Node(new_state, main_island, current.cost + movement_cost,
                                         current, color, island_size)

                    if heuristic == 1:
                        heuristic_val = heuristics.heuristic1(new_node, dimension, colors)
                    elif heuristic == 2:
                      heuristic_val = heuristics.heuristic2(new_state, new_node, dimension)
                    else:
                       heuristic_val = heuristics.heuristic3(new_node, dimension)

                    new_node.set_value(heuristic_val)
                    queue.insert(new_node)
                    total_nodes = total_nodes + 1
                    border_nodes = border_nodes + 1
        current = queue.pop()
        border_nodes = border_nodes - 1

    return current, border_nodes, total_nodes


def run_all():
    #[[costo,nodos,nodos frontera,tiempo],[costo,nodos,nodos frontera,tiempo],...]
    prints = ["A* HEURISTIC 1", "A* HEURISTIC 2", "A* HEURISTIC 3",
                "GREEDY HEURISTIC 1", "GREEDY HEURISTIC 2", "GREEDY HEURISTIC 3", "DFS", "BFS"]
    print_len = prints.__len__()

    info = [[0 for _ in range(4)] for _ in range(print_len)]

    for _ in range(TRIES):
        for dimension in dim:
            random_matrix = np.random.randint(0, colors, (dimension, dimension))

            print("--------------------------------------------------------------")
            print("NxN = " + str(dimension) + " x "+ str(dimension))
            print("M = " + str(colors))
            print()
            print()
            print(random_matrix)

            visited = np.zeros((dimension, dimension))

            main_island, island_size = fillzoneUtils.get_principal_block_recursive(random_matrix, visited, 0, 0,
                                                                        random_matrix[0][0], 0, dimension)

            root = node.Node(random_matrix, main_island, 0, None,
                            random_matrix[0][0], island_size)


        
            goals = [None] * print_len
            border_nodes = [0] * print_len
            total_nodes = [0] * print_len
            total_times = [0] * print_len



            blocks = 0
            for i in range(dim-1):
                for j in range(dim-1):
                    if i == 0 and j == 0: # estoy en el primer color
                        blocks += 1 
                        
            
            blocks_count = len(blocks)
            
            iteration = 0
            timer = time.time()
            goals[iteration], border_nodes[iteration], total_nodes[iteration] = a_search_fill_zone(root, dimension, 1, blocks_count)
            total_times[iteration] = time.time() - timer
            info[iteration][0] += goals[iteration]
            info[iteration][1] += border_nodes[iteration]
            info[iteration][2] += total_nodes[iteration]
            info[iteration][3] += total_times[iteration]
            iteration += 1

            timer = time.time()
            goals[iteration], border_nodes[iteration], total_nodes[iteration] = a_search_fill_zone(root, dimension, 2, blocks_count)
            total_times[iteration] = time.time() - timer
            info[iteration][0] += goals[iteration]
            info[iteration][1] += border_nodes[iteration]
            info[iteration][2] += total_nodes[iteration]
            info[iteration][3] += total_times[iteration]
            iteration += 1
            
            timer = time.time()
            goals[iteration], border_nodes[iteration], total_nodes[iteration] = a_search_fill_zone(root, dimension, 3, blocks_count)
            total_times[iteration] = time.time() - timer
            info[iteration][0] += goals[iteration]
            info[iteration][1] += border_nodes[iteration]
            info[iteration][2] += total_nodes[iteration]
            info[iteration][3] += total_times[iteration]
            iteration += 1

            timer = time.time()
            goals[iteration], border_nodes[iteration], total_nodes[iteration] = greedy_fill_zone(root, dimension, 1, blocks_count)
            total_times[iteration] = time.time() - timer
            info[iteration][0] += goals[iteration]
            info[iteration][1] += border_nodes[iteration]
            info[iteration][2] += total_nodes[iteration]
            info[iteration][3] += total_times[iteration]
            iteration += 1

            timer = time.time()
            goals[iteration], border_nodes[iteration], total_nodes[iteration] = greedy_fill_zone(root, dimension, 2, blocks_count)
            total_times[iteration] = time.time() - timer
            info[iteration][0] += goals[iteration]
            info[iteration][1] += border_nodes[iteration]
            info[iteration][2] += total_nodes[iteration]
            info[iteration][3] += total_times[iteration]
            iteration += 1

            timer = time.time()
            goals[iteration], border_nodes[iteration], total_nodes[iteration] = greedy_fill_zone(root, dimension, 3, blocks_count)
            total_times[iteration] = time.time() - timer
            info[iteration][0] += goals[iteration]
            info[iteration][1] += border_nodes[iteration]
            info[iteration][2] += total_nodes[iteration]
            info[iteration][3] += total_times[iteration]
            iteration += 1

            timer = time.time()
            goals[iteration], border_nodes[iteration], total_nodes[iteration] = dfs_search_fill_zone(root, dimension=dimension)
            total_times[iteration] = time.time() - timer
            info[iteration][0] += goals[iteration]
            info[iteration][1] += border_nodes[iteration]
            info[iteration][2] += total_nodes[iteration]
            info[iteration][3] += total_times[iteration]
            iteration += 1

            timer = time.time()
            # Comentado dado que tarda mucho
            # goals[iteration], border_nodes[iteration], total_nodes[iteration] = bfs_search_fill_zone(root, dimension=dimension)
            total_times[iteration] = time.time() - timer

            # for i in range(print_len):
            #     print(prints[i])
            #     print(total_times[i])

            #     print('Total cost: ' + str(goals[i].cost))
            #     print('Total nodes: ' + str(total_nodes[i]))
            #     print('Border nodes: ' + str(border_nodes[i]))
            #     print()
            #     print()

    for i in range(print_len):
        print(prints[i])

        print('Average Total Cost: ' + str(goals[i].cost/TRIES))
        print('Average Expanded Nodes: ' + str(total_nodes[i]/TRIES))
        print('Average Border Nodes: ' + str(border_nodes[i]/TRIES))
        print('Average Time: '+ total_times[i]/TRIES)
        print()
        print()

if __name__ == '__main__':
    run_all()
