# # CS284r
# 
# *Kendall and Emi Nietfeld*
# 

import numpy as np
import networkx as nx
import requests
from pattern import web
import matplotlib.pyplot as plt
import operator
import itertools
import json
from mpl_toolkits.basemap import Basemap
import csv
import random
import scipy
import math
from IPython.display import Image



#configs
# set some nicer defaults for matplotlib
from matplotlib import rcParams

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



# FIX THIS TO DOWNLOAD FROM THE RIGHT FILE
json_data=open('house_data.txt')
house_vote_data = json.load(json_data)
json_data.close()

json_data=open('senate_data.txt')
vote_data = json.load(json_data)
json_data.close()

senator_colors = {}








# <markdowncell>

# ### Problem 6
# 
# Centrality isn't a perfect proxy for bipartisanship, since it gauges how centralized a node is to the network as a whole, and not how similar a Democrat node is to the Republican sub-network (and vice versa).
# 
# Can you come up with another measure that better captures bipartisanship than closeness centrality? Develop your own metric -- how does it differ from the closeness centrality? Use visualizations to support your points.

# <codecell>

def add_bipartisan_edges(g, senators): 
    
    for senator in senators: 
        if senator["party"] == "D": 
            color = "b"
        elif senator["party"] == "R" : 
            color = "r"
        else : 
            color = "k"
        g.add_node(senator["display_name"], color=color)
        
    # create a list of all the pairs of senators
    senator_pairs = list(itertools.combinations([(x["display_name"], x['party']) for x in senators], r=2))
    for (sen1, sen1party), (sen2, sen2party) in senator_pairs: 
        # check if the senators are in different parties
        if (sen1party != sen2party): # and (sen1party == ("D" or "R")) and (sen2party == ("D" or "R")): 
            #increment or add an edge
            if g.has_edge(sen1, sen2): 
                g[sen1][sen2]['weight'] = (g[sen1][sen2]['weight'] + 1)
                g.edge[sen1][sen2]['difference'] = (1./g.edge[sen1][sen2]['weight'])
            else:
                g.add_edge(sen1, sen2, weight=1)
    return g
        
def bipartisan_graph(data): 
    graph = nx.Graph()
    
    for vote in data: 
        graph = add_bipartisan_edges(graph, vote["votes"]["Yea"])
        graph = add_bipartisan_edges(graph, vote["votes"]["Nay"])
    
    return graph

all_bipartisan_votes = bipartisan_graph(vote_data) 
bipartisan_votes = nx.minimum_spanning_tree(all_bipartisan_votes, weight='distance')




#this makes sure draw_spring results are the same at each call
np.random.seed(1)  

color = [mst.node[senator]['color'] for senator in bipartisan_votes.nodes()]

#determine position of each node using a spring layout
pos = nx.spring_layout(bipartisan_votes, iterations=500, k=.45)

#plot the edges
nx.draw_networkx_edges(bipartisan_votes, pos, alpha = .05)

#plot the nodes
nx.draw_networkx_nodes(bipartisan_votes, pos, node_color=color)

#draw the labels
lbls = nx.draw_networkx_labels(bipartisan_votes, pos, alpha=5, font_size=8)

#coordinate information is meaningless here, so let's remove it
plt.xticks([])
plt.yticks([])
remove_border(left=False, bottom=False)


# LATITUDE AND LONGITUDE
# This scans in the correct latitude and longitude for each state
location_csv = 'state_locations.csv'
states = {}

# Create a map of the United States
m = Basemap(llcrnrlon=-119, llcrnrlat=22, urcrnrlon=-64,
                               urcrnrlat=49, projection='lcc', lat_1=33, lat_2=45,
                               lon_0=-95, resolution='i', area_thresh=10000)

with open(location_csv, 'rb') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    # go through the csv file line by line
    for row in reader:
        states
        [row['name']] = m(row['long'],row['lat'])
# Save the state coordinates and correct color for each representative
rep_locations = {}
rep_colors = {}

def add_sponsors(g, bill):
    sponsor = bill['sponsor']['name']
    # Save each representative's locations
    rep_locations[sponsor] = states[bill['sponsor']['state']]

    cosponsors = [x['name'] for x in bill['cosponsors']]
    
    # get each person's state
    for cosponsor in bill['cosponsors']:
        rep_locations[cosponsor['name']] = states[cosponsor['state']]
    
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


#plot the edges
nx.draw_networkx_edges(bills, rep_locations, alpha = .03)

#plot the nodes
nx.draw_networkx_nodes(bills, rep_locations, node_color=color, node_size=150)

#coordinate information is meaningless here, so let's remove it
plt.xticks([])
plt.yticks([])
remove_border(left=False, bottom=False)

# Plot the map
m.drawcoastlines()
m.drawcountries()
m.drawstates()
m.shadedrelief()

cmap = plt.cm.hot
ax = plt.gca()
plt.show()

# Got this from online to calculate distance between two coordinate points
def distance_calc(lat1, long1, lat2, long2):

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + math.cos(phi1)*math.cos(phi2))
    arc = math.acos(cos)

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc

# <codecell>

# This block of code searches the graph for weights and distances

G = bills
distance = []
weight = []
same_party = []

for u in G:
    for v in G:
        if u != v:
            i = G.get_edge_data(u,v,default=0)
            if i == 0:
                weight.append(0)
            else:
                weight.append(i['weight'])
            lon,lat = rep_locations[u]
            lon1,lat1 = m(lon,lat,inverse=True)
            lon,lat = rep_locations[v]
            lon2,lat2 = m(lon,lat,inverse=True)
            d = 0
            if lon1 != lon2 or lat1 != lat2:
                d = distance_calc(lat1,lon1,lat2,lon2)
            distance.append(d)
            if u in senator_colors and v in senator_colors:
                same_party.append(senator_colors[u] == senator_colors[v])
            else:
                same_party.append(random.random() > .5)

# We can then regress to figure out the relationship:
# Use StatsModel instead!
# at http://statsmodels.sourceforge.net/stable/example_formulas.html

"""
results = ols.ols(weight,[distance,same_party],"weight",["distance, same_party"])
print results.summary()
"""

slope, intercept, r_value, p_value, std_err = stats.linregress(weight,distance)
print "Slope: %s \nIntercept: %s \nR-Val: %s \nP-val %s\nStd Err: %s" % (slope, intercept, r_value, p_value, std_err)
            
# ### Problem 9
# 
# Using `nx.pagerank_numpy`, compute the PageRank score for each senator in this graph. Visualize the results. Determine the 5 Senators with the highest
# PageRank scores. How effective is this approach at identifying leaders? How does the PageRank rating compare to the degree of each node?
# 
# Note: you can read about individual Senators by searching for them on the [govtrack website](https://www.govtrack.us/).

# <codecell>

pagerank_scores = nx.pagerank_numpy(bills)
#print top and bottom 5
sorted_pagerank = sorted(pagerank_scores.iteritems(), key=operator.itemgetter(1))
"""
print "Lowest pagerank scores:" 
for senator in sorted_pagerank[0:5]: 
    print "%s: pagerank: %s, indegree: %s, outdegree: %s" % (senator[0], senator[1], (bills.in_degree([senator[0]])).values()[0], (bills.out_degree([senator[0]])).values()[0]) 

print
    
print "Highest pagerank scores:"
for senator in sorted_pagerank[-5:]: 
    print "%s: pagerank: %s, indegree: %s, outdegree: %s" % (senator[0], senator[1], (bills.in_degree([senator[0]])).values()[0], (bills.out_degree([senator[0]])).values()[0])
"""

# <codecell>

#bills.tounderected
#make mst 
# size == raise to the power and multiply by a big size

#calculate centrality 
sorted_page_keys = [x[0] for x in sorted_pagerank]
sorted_page_values = [x[1] for x in sorted_pagerank]

in_degree = [(bills.in_degree([x])).values()[0] for x in sorted_page_keys]
out_degree = [(bills.out_degree([x])).values()[0] for x in sorted_page_keys]

#visualize centrality
fig = plt.figure(num=None, figsize=(18, 6), dpi=80, facecolor='w', edgecolor='k')
ax1 = fig.add_subplot(111)

plt.bar(range(len(sorted_page_keys)), sorted_page_values, align='center')
plt.xticks(range(len(sorted_page_keys)), sorted_page_keys, rotation=80, fontsize='small')
plt.xlabel("Senators by Pagerank Score")
plt.ylabel('Pagerank Score')
plt.show()

#visualize in and out degree

fig = plt.figure(num=None, figsize=(18, 6), dpi=80, facecolor='w', edgecolor='k')
ax2 = fig.add_subplot(111)

plt.bar(range(len(sorted_page_keys)), in_degree, align='center')
plt.xticks(range(len(sorted_page_keys)), sorted_page_keys, rotation=80, fontsize='small')
plt.xlabel("Senators organized by Pagerank Score")
plt.ylabel('In-degree')
plt.show()

fig = plt.figure(num=None, figsize=(18, 6), dpi=80, facecolor='w', edgecolor='k')
ax2 = fig.add_subplot(111)

plt.bar(range(len(sorted_page_keys)), out_degree, align='center')
plt.xticks(range(len(sorted_page_keys)), sorted_page_keys, rotation=80, fontsize='small')
plt.xlabel("Senators organized by Pagerank Score")
plt.ylabel('Out-degree')
plt.show()

# <markdowncell>

# As we see comparing the pagerank graph to the identically ordered in and out degree graphs, the pagerank is a pretty good prediction of who is a good leader. We see in the second graph some senators that really deviate from the trend, but overall they both slope upwards.
# 
# We also see that the pagerank is pretty much unrelated to the outdegree, which is what we expect. Signing onto other people's bills doesn't really make you a leader. 

# <markdowncell>

# ### Interactive Visualization
# 
# Producing a good node link layout is not quite so simple. Nevertheless, we will give it a try. 
# 
# We will use [Gephi](https://gephi.org/) for interactive graph visualization. Gephi supports a wide variety of graph file formats, and NetworkX exports to several of them. We'll use the Graph Exchange XML Format (GEXF).

# <codecell>

nx.write_gexf(votes, 'votes.gexf')

# <markdowncell>

# ### Problem 10: Analysis with Gephi
# 
# Download and install [Gephi](https://gephi.org/). See the [lab](http://goo.gl/SzHioP) for a brief introduction. Load the exported votes file. Try to produce a layout that clearly separates Democrats from Republicans (hint: filter on edge weight and re-layout once you filtered). Run PageRank and some other statistics and try encoding them with node color and node size. Run the "Modularity" statistic and encode the results in color.
# 
# Include a screenshot of your "best" visualization and embed the image here with `IPython.display.Image`. Make sure to include this image in your submission.
# 
# Explain your observations. Is the network visualization very helpful? Try to visualize your LinkedIn network (see the lab) or the one provided in the lab. Which dataset is more suitable for visualization and why is there a difference?

# <codecell>



path = 'gephishot.png'
Image(path)


# <markdowncell>

# First of all, working with the Gephi GUI reminded me of why CS179 exists... I think if Photoshop were open source, magazines would still show models with body fat... 
# 
# Now onto the network! I think this analysis is helpful- essentially we want to see who is "closest to the center" and this makes this loud and clear. We see Collins in the center, right where we expect him! In a sense, this graph is useful since it mirrors the layout we imagine on a senate floor. No one is disconnected from everyone else, but is one tangled, disfunctional glob. 
# 
# I wish I'd been able to get the results of PageRank to show up on my nodes, but unfortunately it wasn't working for me (also Preview wasn't working, so the image is a bit rough.)

# <markdowncell>

# ### How to Submit
# 
# To submit your homework, create a folder named lastname_firstinitial_hw5 and place this notebook file in the folder. Double check that this file is still called HW5.ipynb, and that it contains your solutions. Also include any Gephi screenshots. Compress the folder (please use .zip compression) and submit to the CS109 dropbox in the appropriate folder. If we cannot access your work because these directions are not followed correctly, we will not grade your work.

# <markdowncell>

# ---
# *css tweaks in this cell*
# <style>
# div.text_cell_render {
#     line-height: 150%;
#     font-size: 110%;
#     width: 800px;
#     margin-left:50px;
#     margin-right:auto;
#     }
# </style>

