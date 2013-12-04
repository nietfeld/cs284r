#configs
# set some nicer defaults for matplotlib
from matplotlib import rcParams
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import json
import operator

#these colors come from colorbrewer2.org. Each is an RGB triplet
dark2_colors = [(0.10588235294117647, 0.6196078431372549, 0.4666666666666667),
                (0.8509803921568627, 0.37254901960784315, 0.00784313725490196),
                (0.4588235294117647, 0.4392156862745098, 0.7019607843137254),
                (0.9058823529411765, 0.1607843137254902, 0.5411764705882353),
                (0.4, 0.6509803921568628, 0.11764705882352941),
                (0.9019607843137255, 0.6705882352941176, 0.00784313725490196),
                (0.6509803921568628, 0.4627450980392157, 0.11372549019607843),
                (0.4, 0.4, 0.4)]

rcParams['figure.figsize'] = (10, 6)
rcParams['figure.dpi'] = 150
rcParams['axes.color_cycle'] = dark2_colors
rcParams['lines.linewidth'] = 2
rcParams['axes.grid'] = False
rcParams['axes.facecolor'] = 'white'
rcParams['font.size'] = 14
rcParams['patch.edgecolor'] = 'none'

def remove_border(axes=None, top=False, right=False, left=True, bottom=True):
    """
    Minimize chartjunk by stripping out unnecessary plot borders and axis ticks
    
    The top/right/left/bottom keywords toggle whether the corresponding plot border is drawn
    """
    ax = axes or plt.gca()
    ax.spines['top'].set_visible(top)
    ax.spines['right'].set_visible(right)
    ax.spines['left'].set_visible(left)
    ax.spines['bottom'].set_visible(bottom)
    
    #turn off all ticks
    ax.yaxis.set_ticks_position('none')
    ax.xaxis.set_ticks_position('none')
    
    #now re-enable visibles
    if top:
        ax.xaxis.tick_top()
    if bottom:
        ax.xaxis.tick_bottom()
    if left:
        ax.yaxis.tick_left()
    if right:
        ax.yaxis.tick_right()


# Save the state coordinates and correct color for each representative
rep_locations = {}
rep_colors = {}

def add_sponsors(g, bill):
    sponsor = bill['sponsor']['name']
    cosponsors = [x['name'] for x in bill['cosponsors']]
    
    for cosponsor in cosponsors:
        if g.has_edge(cosponsor, sponsor): 
            g[cosponsor][sponsor]['weight'] = (g[cosponsor][sponsor]['weight'] + 1)
        else:
            g.add_edge(cosponsor, sponsor, weight=1)
    return g
        
def bill_graph(data): 
    graph = nx.DiGraph()
    
    for bill in data: 
        graph = add_sponsors(graph, bill)
    
    return graph


f = open("senate_bills_113_113.txt", "r")
bill_list = json.load(f)
bills = bill_graph(bill_list)

pagerank_scores = nx.pagerank_numpy(bills)
sorted_pagerank = sorted(pagerank_scores.iteritems(), key=operator.itemgetter(1))

#calculate centrality 
sorted_page_keys = [x[0] for x in sorted_pagerank]
sorted_page_values = [x[1] for x in sorted_pagerank]

hubs, authorities = nx.hits_numpy(bills)
sorted_hubs = [hubs[x] for x in sorted_page_keys]
sorted_authorities = [authorities[x] for x in sorted_page_keys]

in_degree = [(bills.in_degree([x])).values()[0] for x in sorted_page_keys]
out_degree = [(bills.out_degree([x])).values()[0] for x in sorted_page_keys]

#visualize centrality
fig = plt.figure(num=None, figsize=(18, 6), dpi=80, facecolor='w', edgecolor='k')
ax1 = fig.add_subplot(111)

plt.bar(range(len(sorted_page_keys)), sorted_page_values, align='center')
plt.xticks(range(len(sorted_page_keys)), sorted_page_keys, rotation=80, fontsize=9)
plt.xlabel("Senators by Pagerank Score")
plt.ylabel('Pagerank Score')
plt.show()

#visualize in and out degree

fig = plt.figure(num=None, figsize=(18, 6), dpi=80, facecolor='w', edgecolor='k')
ax2 = fig.add_subplot(111)

plt.bar(range(len(sorted_page_keys)), in_degree, align='center')
plt.xticks(range(len(sorted_page_keys)), sorted_page_keys, rotation=90, fontsize=9)
plt.xlabel("Senators by In-degree")
plt.ylabel('In-degree')
plt.show()

fig = plt.figure(num=None, figsize=(18, 6), dpi=80, facecolor='w', edgecolor='k')
ax3 = fig.add_subplot(111)

plt.bar(range(len(sorted_page_keys)), sorted_hubs, align='center')
plt.xticks(range(len(sorted_page_keys)), sorted_page_keys, rotation=90, fontsize=9)
plt.xlabel("Senators by HITS Hub Score")
plt.ylabel('Hub Score')
plt.show()