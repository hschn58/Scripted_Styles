using CSV
using DataFrames
using Printf

# Parameters
iter = 1_000_000_000
x = collect(LinRange(0, iter, iter + 1))

daty = []

for dec in 1:1
    y = []
    ncur = 1.01

    for iteration in 1:(iter + 1)  # Ensure y has the same length as x
        push!(y, ncur)

        if parse(Int, string(ncur)[end]) % 2 == 0
            ncur /= 2
        else
            ncur = 3 * ncur
        end
    end
    push!(daty, y)
end

y = daty[1]

# Create DataFrame and save to CSV
data = DataFrame(x = x, y = y)
CSV.write("/Users/henryschnieders/downloads/ftdata.csv", data)
