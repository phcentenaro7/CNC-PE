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

def routing_model(points):
    npoints = len(points)
    nindices = int(pow(npoints, 2))
    D = distance_matrix(points)
    model = glpk.LPX()
    model.name = 'routing'
    model.obj.maximize = False
    model.rows.add(3 * npoints)
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
        else:
            var_index = row.index - 2 * npoints
            matrix = insert_loop_constraint(matrix, var_index)
            row.bounds = 0
            row.name = "subcycle%d" % (var_index)
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

def get_cycles(model):
    cycles = []
    current_cycle = []
    unvisited_points = list(range(0, int(sqrt(len(model.cols)))))
    while len(unvisited_points) > 0:
        current_point = unvisited_points[0]
        current_cycle.append(current_point)
        for col in model.cols:
            start_point, end_point = list(map(int, re.findall("\d+", col.name)))
            print('%g - (%g, %g)' % (current_point, start_point, end_point))
            if start_point != current_point:
                continue
            if col.primal == 1:
                if end_point == current_cycle[0]:
                    cycles.append(current_cycle)
                    current_cycle = []
                print(col.name)
                unvisited_points.remove(end_point)
                current_cycle.append(end_point)
                current_point = end_point
    return cycles

class Callback:
    def select(self, tree):
        pass
    def prepro(self, tree):
        pass
    def rowgen(self, tree):
        tree.lp.obj.value_m
        return
    def heur(self, tree):
        pass
    def cutgen(self, tree):
        pass
    def branch(self, tree):
        pass
    def bingo(self, tree):
        pass

points = [[2, 2],
          [2, 6],
          [4, 6],
          [6, 1],
          [7, 4]]

model = routing_model(points)
model.simplex()
for col in model.cols:
    print(col.name)
    print(col.primal)
print(get_adjacency_matrix(model))