import glpk
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

def make_row(npoints, ones):
    row = np.zeros(npoints)
    

def routing_model(points):
    npoints = len(points)
    nindices = npoints * npoints
    D = distance_matrix(points)
    model = glpk.LPX()
    model.name = 'routing'
    model.obj.maximize = False
    model.rows.add(3 * npoints)
    matrix = []
    for row in model.rows:
        if row.index < npoints:
            pattern = npoints * np.array([row.index, 1, npoints - (row.index + 1)])
            matrix += np.repeat([0, 1, 0], pattern).tolist()
            row.bounds = 1
            row.name = 'rowsum%d' % row.index
        elif row.index < 2 * npoints:
            col_index = row.index - npoints
            pattern = np.repeat([0, 1, 0], [col_index, 1, npoints - 1 - col_index])
            matrix += np.tile(pattern, npoints).tolist()
            row.bounds = 1
            row.name = 'colsum%d' % (row.index - npoints)
            print(len(np.tile(pattern, npoints).tolist()))
            print(np.tile(pattern, npoints).tolist())
        else:
            row_index = row.index - 2 * npoints
            col_index = row_index * (npoints) + row_index
            pattern = np.zeros((npoints * npoints))
            pattern[col_index] = 1
            matrix += pattern.tolist()
            row.bounds = 0
            row.name = "subcycle%d" % (row.index - 2 * npoints)
    model.cols.add(nindices)
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

model = routing_model(points)
print(model.matrix)