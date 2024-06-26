import glpk
import re
import numpy as np
from math import sqrt, pow, floor

def euclidean_distance(u, v):
    return sqrt(pow(u[0] - v[0], 2) + pow(u[1] - v[1], 2))

def distance_matrix(points):
    npoints = len(points)
    D = np.zeros((npoints, npoints))
    for (i, u) in enumerate(points):
        for (j, v) in enumerate(points):
            D[i][j] = euclidean_distance(u, v)
    return D

def insert_row_constraint(matrix, row_index):
    nvars = int(sqrt(matrix.shape[1]))
    row = []
    for i in range(0, nvars):
        if i != row_index:
            row = np.concatenate((row, np.zeros(nvars)))
        else:
            row = np.concatenate((row, np.ones(nvars)))
    return np.append(matrix, [row], axis=0)

def insert_column_constraint(matrix, col_index):
    nvars = int(sqrt(matrix.shape[1]))
    row = []
    for j in range(0, nvars):
        row = np.concatenate((row, np.zeros(col_index)))
        row = np.concatenate((row, np.ones(1)))
        row = np.concatenate((row, np.zeros(nvars - col_index - 1)))
    return np.append(matrix, [row], axis=0)

def insert_loop_constraint(matrix, index):
    nvars = int(sqrt(matrix.shape[1]))
    row = np.zeros(int(pow(nvars, 2)))
    true_index = index * (nvars + 1)
    row[true_index] = 1
    return np.append(matrix, [row], axis=0)

def routing_model(points, cycles):
    npoints = len(points)
    nindices = int(pow(npoints, 2))
    D = distance_matrix(points)
    model = glpk.LPX()
    model.name = 'routing'
    model.obj.maximize = False
    model.rows.add(3 * npoints + 2 * len(cycles))
    model.cols.add(nindices)
    matrix = np.empty((0, nindices))
    for row in model.rows:
        if row.index < npoints:
            matrix = insert_row_constraint(matrix, row.index)
            row.bounds = 1
            row.name = 'rowsum%d' % (row.index)
        elif row.index < 2 * npoints:
            col_index = row.index - npoints
            matrix = insert_column_constraint(matrix, col_index)
            row.bounds = 1
            row.name = 'colsum%d' % (col_index)
        elif row.index < 3 * npoints:
            var_index = row.index - 2 * npoints
            matrix = insert_loop_constraint(matrix, var_index)
            row.bounds = 0
            row.name = "loop%d" % (var_index)
    matrix = insert_cycle_constraints(matrix, cycles)
    j = -1
    for i in reversed(range(0,len(cycles))):
        model.rows[j].bounds = 0, len(cycles[i]) - 1
        model.rows[j-1].bounds = 0, len(cycles[i]) - 1
        j -= 2
    model.matrix = np.concatenate(matrix)
    for col in model.cols:
        i = floor(col.index / npoints)
        j = col.index - (i * npoints)
        col.name = "x(%d, %d)" % (i, j)
        col.kind = bool
        model.obj[i * npoints + j] = D[i][j]
    return model

def get_adjacency_matrix(model):
    length = int(sqrt(len(model.cols)))
    matrix = np.zeros((length, length))
    for col in model.cols:
        if col.primal == 1:
            i, j = list(map(int, re.findall("\d+", col.name)))
            matrix[i, j] = 1
    return matrix

def get_cycles(X):
    npoints = int(sqrt(len(model.cols)))
    nindices = int(pow(npoints, 2))
    unvisited_points = list(range(0, npoints))
    cycles = []
    while unvisited_points != []:
        i = unvisited_points[0]
        cycle = []
        while cycle == [] or i != cycle[0]:
            unvisited_points.remove(i)
            cycle.append(i)
            i = X[i].tolist().index(1)
        cycles.append(cycle)
    return cycles

def cycle_to_constraint(cycle, npoints):
    row = np.zeros(int(pow(npoints, 2)))
    i = 0
    while i < len(cycle) - 1:
        k = cycle[i] * npoints + cycle[i + 1]
        row[k] = 1
        i += 1
    k = cycle[-1] * npoints + cycle[0]
    row[k] = 1
    return row

def insert_cycle_constraints(matrix, cycles):
    npoints = int(sqrt(matrix.shape[1]))
    for cycle in cycles:
        row = cycle_to_constraint(cycle, npoints)
        matrix = np.append(matrix, [row], axis=0)
        row = cycle_to_constraint(np.flip(cycle), npoints)
        matrix = np.append(matrix, [row], axis=0)
    return matrix

# class Callback:
#     def select(self, tree):
#         pass
#     def prepro(self, tree):
#         pass
#     def rowgen(self, tree):
#         X = get_adjacency_matrix(tree.lp)
#         cycles = get_cycles(X)
#         npoints = int(X.shape[0])
#         i = len(tree.lp.rows)
#         if len(cycles) > 1:
#             tree.lp.rows.add(2 * len(cycles))
#         for cycle in cycles:
#             tree.lp.rows[i].bounds = 0, len(cycle) - 1
#             tree.lp.rows[i+1].bounds = 0, len(cycle) - 1
#             row = cycle_to_constraint(cycle, npoints)
#             tree.lp.matrix.extend(row.tolist())
#             row = cycle_to_constraint(np.flip(cycle), npoints)
#             tree.lp.matrix.extend(row.tolist())
#             i += 2
#         return
#     def heur(self, tree):
#         pass
#     def cutgen(self, tree):
#         pass
#     def branch(self, tree):
#         pass
#     def bingo(self, tree):
#         pass

points = [[7.0, 7.5],
          [28.0, 7.5],
          [7.0, 16.5],
          [28.0, 16.5],
          [50.9, 7.5],
          [71.9, 7.5],
          [50.9, 16.5],
          [71.9, 16.5],
          [94.8, 7.5],
          [115.8, 7.5],
          [94.8, 16.5],
          [115.8, 16.5],
          [138.7, 7.5],
          [159.7, 7.5],
          [138.7, 16.5],
          [159.7, 16.5],
          [182.6, 7.5],
          [203.6, 7.5],
          [182.6, 16.5],
          [203.6, 16.5],
          [226.5, 7.5],
          [247.5, 7.5],
          [226.5, 16.5],
          [247.5, 16.5],
          [7.0, 116.5],
          [28.0, 116.5],
          [7.0, 125.5],
          [28.0, 125.5],
          [50.9, 116.5],
          [71.9, 116.5],
          [50.9, 125.5],
          [71.9, 125.5],
          [94.8, 116.5],
          [115.8, 116.5],
          [94.8, 125.5],
          [115.8, 125.5],
          [138.7, 116.5],
          [159.7, 116.5],
          [138.7, 125.5],
          [159.7, 125.5],
          [182.6, 116.5],
          [203.6, 116.5],
          [182.6, 125.5],
          [203.6, 125.5],
          [226.5, 116.5],
          [247.5, 116.5],
          [226.5, 125.5],
          [247.5, 125.5]]

cycles = []
i = 1
model = None
while True:
    model = routing_model(points, cycles)
    model.simplex()
    model.integer()# (callback=Callback())
    X = get_adjacency_matrix(model)
    new_cycles = get_cycles(X)
    if len(new_cycles) == 1:
        break
    for cycle in new_cycles:
        cycles.append(cycle)
    print("%g" % (model.obj.value))

X = get_adjacency_matrix(model)
print("%g" % (model.obj.value))