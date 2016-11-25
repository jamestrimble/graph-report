set terminal png

set style fill solid border -1

set key off

set xlabel "Degree"
set ylabel "Weight"
#set title "Degree and weight of each vertex"
set output degwtpngname
plot degwttxtname using 1:2

set xlabel "Degree"
set ylabel "Count"
#set title "Distribution of degrees"
set output degdistpngname
plot degdisttxtname using 1:2 with boxes

