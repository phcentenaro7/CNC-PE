struct Piece
    width::Real
    height::Real
    holes::Vector{Tuple}
    hole_radius::Real

    function Piece(width::Real, height::Real, holes::Vector, hole_radius::Real)
        new(width, height, holes, hole_radius)
    end
end

struct Board
    piece_type::Piece
    ncols::Int
    nrows::Int
    xmargin::Real
    ymargin::Real

    function Board(piece_type::Piece, ncols::Int, nrows::Int, xmargin, ymargin)
        new(piece_type, ncols, nrows, xmargin, ymargin)
    end
end

function get_piece_coordinates(board::Board, row::Int, col::Int)
    if row > board.nrows || col > board.ncols
        error("specified number of rows and/or columns exceeds the capacity of the board")
    end
    x = (col - 1) * (board.piece_type.width + board.xmargin)
    y = (row - 1) * (board.piece_type.height + board.ymargin)
    return (x, y)
end

function get_board_dimensions(board::Board)
    width = board.ncols * board.piece_type.width + (board.ncols - 1) * board.xmargin
    height = board.nrows * board.piece_type.height + (board.nrows - 1) * board.ymargin
    return (width, height)
end

function get_piece_dimensions(board::Board)
    return (board.piece_type.width, board.piece_type.height)
end

function get_piece_hole_coordinates(board::Board)
    return board.piece_type.holes
end

function get_piece_hole_radius(board::Board)
    return board.piece_type.hole_radius
end

function get_all_hole_centroids(board::Board)
    centroids = []
    radius = get_piece_hole_radius(board)
    coords = get_piece_hole_coordinates(board)
    for row in 1:board.nrows, col in 1:board.ncols
        x, y  = get_piece_coordinates(board, row, col)
        for coord in coords
            push!(centroids, (x, y) .+ coord .+ (radius, radius))
        end
    end
    return centroids
end