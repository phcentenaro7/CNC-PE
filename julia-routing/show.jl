using PlotlyJS
include("structs.jl")

function show_board(board::Board)
    board_width, board_height = get_board_dimensions(board)
    piece_width, piece_height = get_piece_dimensions(board)
    pieces, holes = [], []
    hole_index = 1
    nodes = []
    for row in 1:board.nrows, col in 1:board.ncols
        xrect, yrect = get_piece_coordinates(board, row, col)
        push!(pieces, rect(
            x0 = xrect, y0 = yrect,
            x1 = xrect + piece_width, y1 = yrect + piece_height,
            fillcolor = "Green"
        ))
        circles = get_all_hole_centroids(board)
        radius = get_piece_hole_radius(board)
        for circ in circles
            push!(holes, circle(
                x0 = xrect + circ[1] - radius, y0 = yrect + circ[2] - radius,
                x1 = xrect + circ[1] + radius, y1 = yrect + circ[2] + radius,
                fillcolor = "White"
            ))
            push!(nodes, attr(
                x = xrect + circ[1] + radius * 4,
                y = yrect + circ[2] + radius,
                text = "$hole_index",
                showarrow = false)
            )
            hole_index += 1
        end
    end
    layout = Layout(
        xaxis_range = [0, board_width],
        yaxis_range = [0, board_height],
        shapes = [pieces..., holes...],
        annotations = [nodes...]
    )
    p = plot(layout)
    return p
end