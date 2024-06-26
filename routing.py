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

points = [[10, 10], [20, 10], [10, 20], [20, 20]]

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
with open("route", "w") as file:
    for i in range(len(points)):
        file.write("{},{}\n".format(points[i][0], points[i][1]))