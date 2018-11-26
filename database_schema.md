# Route table

start_pont | end_point | instruction
integer[]  | integer[] | json


# Landmarks table

point     | name
integer[] | varchar

# Thoughts

Database module is going to have route interpreter.
Start and end points of each instruction from the specific route will be calculated from the route start point.

In case of a large number of instructions in a route and users that are requesting routes, process of building route will be slow. Optimized database read should help, but not match.
