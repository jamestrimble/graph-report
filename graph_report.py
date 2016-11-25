from collections import deque
from PIL import Image
import random
import os
import shutil
import subprocess
import sys
import time

class Graph(object):
    def __init__(self, adjmat, weights):
        self.n = len(adjmat)
        self.adjmat = adjmat
        self.degree = [sum(row) for row in self.adjmat]
        self.weight = weights

    def adjmat_sorted_by_degree(self):
        v_and_deg = zip(range(self.n), self.degree)
        v_and_deg.sort(key=lambda x: x[1], reverse=True)
        vv = [x[0] for x in v_and_deg]
        return [[self.adjmat[v][w] for v in vv] for w in vv]

    def show(self, filename, sort_by_degree):
        img = Image.new('RGB', (self.n*3, self.n*3), "white")
        pixels = img.load()
        
        adjmat = self.adjmat_sorted_by_degree() if sort_by_degree else self.adjmat

        for i in range(self.n):
            for j in range(self.n):
                if adjmat[i][j]:
                    for k in range(3):
                        for l in range(3):
                            colour = (0,0,0)
                            if k==2 or l==2:
                                colour = (80,80,80)
                            if (k==2 and i%10==9) or (l==2 and j%10==9):
                                colour = (150,150,150)
                            pixels[i*3+k, j*3+l] = colour

        img.save(filename)

    def output_deg_distribution(self, filename):
        min_deg = min(self.degree)
        max_deg = max(self.degree)
        with open(filename, 'w') as f:
            for i in range(min_deg, max_deg+1):
                f.write("{} {}\n".format(i, sum(d==i for d in self.degree)))


def read_instance(lines):
    lines = [line.strip().split() for line in lines]
    p_line = [line for line in lines if line[0]=="p"][0]
    n_lines = [line for line in lines if line[0]=="n"]
    e_lines = [line for line in lines if line[0]=="e"]
    n = int(p_line[2])
    adjmat = [[False] * n for _ in range(n)]
    weights = [1] * n
    for line in n_lines:
        v, wt = int(line[1])-1, int(line[2])
        weights[v] = wt
    for e in e_lines:
        v, w = int(e[1])-1, int(e[2])-1
        if v==w:
            print "Loop detected", v
        if adjmat[v][w]:
            print "Duplicate edge", v, w
        adjmat[v][w] = adjmat[w][v] = True
    return Graph(adjmat, weights)


if __name__ == "__main__":
    if os.path.exists('output'):
        print "output directory already exists. Aborting."
        sys.exit(1)

    os.makedirs('output')
    os.makedirs('output/txt')
    os.makedirs('output/img')

    sections = []

    with open('templates/section.tex', 'r') as f:
        section_template = "\n".join(line for line in f.readlines()) + "\n"

    for filename in sys.argv[1:]:
        basename = os.path.basename(filename)
        dot_pos = basename.find('.')
        if dot_pos != -1:
            basename = basename[:dot_pos]

        with open(filename, "r") as f:
            g = read_instance([line for line in f.readlines()])

        num_edges = sum(sum(row) for row in g.adjmat)/2
        density = float(num_edges) / (g.n*(g.n-1)/2)

        degwttxtname = 'output/txt/deg-wt{}.txt'.format(basename)
        degdisttxtname = 'output/txt/deg-dist{}.txt'.format(basename)
        degwtpngname = 'output/img/deg-wt{}.png'.format(basename)
        degdistpngname = 'output/img/deg-dist{}.png'.format(basename)

        with open(degwttxtname, 'w') as f:
            for i in range(g.n):
                f.write("{} {}\n".format(g.degree[i], g.weight[i]))

        g.output_deg_distribution(degdisttxtname)

        g.show('output/img/adjmat{}.png'.format(basename), False)
        g.show('output/img/adjmat-sorted{}.png'.format(basename), True)

        subprocess.call(['gnuplot',
                         '-e',
                         "degwttxtname='{}'".format(degwttxtname), 
                         '-e',
                         "degdisttxtname='{}'".format(degdisttxtname), 
                         '-e',
                         "degwtpngname='{}'".format(degwtpngname), 
                         '-e',
                         "degdistpngname='{}'".format(degdistpngname), 
                         'scripts/plot_results.gnuplot'])

        sections.append((section_template
                .replace("*GRAPHNAME*", basename)
                .replace("*N*", str(g.n))
                .replace("*M*", str(num_edges))
                .replace("*DENSITY*", "{0:.2f}".format(density))))

    with open('templates/report.tex', 'r') as f:
        report = "\n".join(line for line in f.readlines()) + "\n"

    report = report.replace("*SECTIONS*", "\n".join(sections))

    with open('output/report.tex', 'w') as f:
        f.write(report)

