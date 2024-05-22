#import glpk
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
    nindices = pow(npoints, 2)
    D = distance_matrix(points)
    model = glpk.LPX()
    model.name = 'routing'
    model.obj.maximize = False
    model.rows.add(3 * npoints)
    model.cols.add(nindices)
    matrix = []
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
    model.matrix = matrix
    for col in model.cols:
        i = floor(col.index / npoints)
        j = col.index - (i * npoints)
        col.name = "x(%d, %d)" % (i, j)
        col.kind = bool
        model.obj[i * npoints + j] = D[i][j]
    return model

points = [[2, 2],
          [2, 6],
          [4, 6],
          [6, 1],
          [7, 4]]

#model = routing_model(points)
#print(model.matrix)

matrix = np.empty((0, 100))
matrix = insert_loop_constraint(matrix, 0)
matrix = insert_loop_constraint(matrix, 3)
#matrix = insert_row_constraint(matrix, 10, 0)
#matrix = insert_row_constraint(matrix, 10, 1)
print(matrix)