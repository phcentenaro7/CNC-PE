using GLPK
include("structs.jl")
include("show.jl")
include("routing.jl")

piece = Piece(35, 94, [(7, 7.5), (28, 7.5), (7, 16.5), (28, 16.5)], 2.5)
board = Board(piece, 6, 2, 8.9, 15)
show_board(board)
X = get_optimal_route(board, Gurobi.Optimizer)
show_optimal_route(board, X)