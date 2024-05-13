using GLPK
include("structs.jl")
include("show.jl")
include("routing.jl")

piece = Piece(35, 94, [(7, 7.5), (28, 7.5), (7, 16.5), (28, 16.5)], 2.5)
board = Board(piece, 6, 2, 8.9, 15)
board_plot = show_board(board)
savefig(board_plot, "routing1.png")
X = get_optimal_route(board, GLPK.Optimizer)
routing_plot = show_optimal_route(board, X)
savefig(routing_plot, "routing2.png")