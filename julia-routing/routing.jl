using JuMP
include("structs.jl")

function euclidean_distance(a, b)
    return sqrt((a[1] - b[1])^2 + (a[2] - b[2])^2)
end

function get_distance_matrix(centroids)
    n = length(centroids)
    C = zeros(n, n)
    for i in 1:n, j in (i+1):n
        C[i, j] = C[j, i] = euclidean_distance(centroids[i], centroids[j])
    end
    return C
end

function get_routing_model(distance_matrix, optimizer)
    model = Model(optimizer)
    n = size(distance_matrix, 1)
    @variable(model, X[1:n, 1:n], Bin)
    @objective(model, Min, sum(distance_matrix .* X))
    @constraint(model, [j = 1:n], sum(X[i, j] for i in 1:n) == 1)
    @constraint(model, [i = 1:n], sum(X[i, j] for j in 1:n) == 1)

    function lazy_constraint_callback(cb_data)
        status = callback_node_status(cb_data, model)
        if status != MOI.CALLBACK_NODE_STATUS_INTEGER
            return
        end
        Xrounded = callback_value.(cb_data, model[:X])
        cycles = get_cycles(Xrounded)
        if length(cycles) == 1
            return
        end
        for cycle in cycles
            constraint = @build_constraint(sum(model[:X][i, j] for i in cycle, j in cycle) <= length(cycle) - 1)
            MOI.submit(model, MOI.LazyConstraint(cb_data), constraint)
        end
    end
    set_attribute(model, MOI.LazyConstraintCallback(), lazy_constraint_callback)
    return model
end

function get_next_centroid(adjacency_matrix, row)
    X = round.(adjacency_matrix)
    return findfirst(==(1), X[row,:])
end

function get_cycle(adjacency_matrix, row)
    cycle = [row]
    while true
        next_row = get_next_centroid(adjacency_matrix, row)
        if next_row == first(cycle)
            return cycle
        elseif isnothing(next_row)
            error("adjacency matrix contains null rows")
        end
        push!(cycle, next_row)
        row = next_row
    end
end

function get_cycles(adjacency_matrix)
    unvisited_rows = collect(1:size(adjacency_matrix, 1))
    cycles = []
    while !isempty(unvisited_rows)
        cycle = get_cycle(adjacency_matrix, first(unvisited_rows))
        push!(cycles, cycle)
        filter!(!in(cycle), unvisited_rows)
    end
    return cycles
end

function get_optimal_route(board::Board, optimizer)
    centroids = get_all_hole_centroids(board)
    distance_matrix = get_distance_matrix(centroids)
    model = get_routing_model(distance_matrix, optimizer)
    optimize!(model)
    print("Found best route with objective value $(objective_value(model))")
    return value.(model[:X])
end

function show_optimal_route(board::Board, adjacency_matrix)
    plot = show_board(board)
    centroids = get_all_hole_centroids(board)
    for row in eachindex(adjacency_matrix[:, 1])
        col = findfirst(==(1), adjacency_matrix[row,:])
        add_shape!(plot, line(
            x0 = centroids[row][1], y0 = centroids[row][2], x1 = centroids[col][1], y1 = centroids[col][2],
            line = attr(
                color = "Red",
                width = 2
            )
        ))
    end
    return plot
end