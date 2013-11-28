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

"""
get_senate_vote

Scrapes a single JSON page for a particular Senate vote, given by the vote number

"""
vote_url = "https://www.govtrack.us/data/congress/113/votes/2013"

#gets a specific votes
def get_vote(number): 
    vote_page = vote_url+"/"+str(number)+"data.json"
    vote_dict = requests.get(vote_page).json()
    return vote_dict

#gets all the votes from a specific year
def get_all_year_votes(year_url):
    senate_votes = []
    house_votes = [] 
    vote_page = requests.get(year_url).text
    element = web.Element(vote_page)
    link_list = element.by_tag("a") 
    for link in link_list[0:5]: 
        label=link[0]
        if str(label)[0] == "s": 
            senate_votes.append(get_vote(str(label)))
        if str(label)[0] == "h": 
            house_votes.append(get_vote(str(label)))
    return (senate_votes, house_votes)

def get_all_votes() : 
    vote_dict = {}
    # for each session of congress with votes, get the pages
    for session in range(100, 110): 
    #for session in range(100, 114): 
        index_page = requests.get("https://www.govtrack.us/data/congress/%s/votes/" % session).text
        element = web.Element(index_page)
        link_list = element.by_tag("a") 
        # throw away the "back" links and get votes for each year
        for link in link_list[1:]: 
            year = link[0]
            url = "https://www.govtrack.us/data/congress/%s/votes/%s" % (session, year)
            (senate, house) = get_all_year_votes(url)
            vote_dict[str(year)] = {"senate": senate, "house": house}
    return vote_dict

#broke on 2009, so did the rest manually
all_votes = get_all_votes()
all_votes[2009] = get_all_year_votes("https://www.govtrack.us/data/congress/111/votes/2009")
all_votes[2010] = get_all_year_votes("https://www.govtrack.us/data/congress/111/votes/2010")
all_votes[2011] = get_all_year_votes("https://www.govtrack.us/data/congress/112/votes/2011")
all_votes[2012] = get_all_year_votes("https://www.govtrack.us/data/congress/112/votes/2012")
all_votes[2013] = get_all_year_votes("https://www.govtrack.us/data/congress/113/votes/2013")


# download bills and dump into file
with open('votes_1990_2013.txt', 'w') as outfile:
  json.dump(all_votes, outfile)

# Loading info from files 

"""
# FIX THIS TO DOWNLOAD FROM THE RIGHT FILE
json_data=open('house_data.txt')
house_vote_data = json.load(json_data)
json_data.close()

json_data=open('senate_data.txt')
vote_data = json.load(json_data)
json_data.close()
"""

# put into network

# make an empty "senator_colors array to save all colors"
senator_colors = {}

def add_edges(g, senators): 
    
    for senator in senators: 
        
        if senator["party"] == "D": 
            color = "b"
        elif senator["party"] == "R" : 
            color = "r"
        else : 
            color = "k"
        senator_colors[senator["last_name"] + ", " + senator["first_name"]] = color
        g.add_node(senator["display_name"], color=color)
        
    # create a list of all the pairs of senators
    senator_pairs = list(itertools.combinations([x["display_name"] for x in senators], r=2))
    for sen1, sen2 in senator_pairs: 
        #increment or add an edge
        if g.has_edge(sen1, sen2): 
            g[sen1][sen2]['weight'] = (g[sen1][sen2]['weight'] + 1)
            g.edge[sen1][sen2]['difference'] = (1./g.edge[sen1][sen2]['weight'])
        else:
            g.add_edge(sen1, sen2, weight=1)
    return g
    
        
def vote_graph(data): 
    graph = nx.Graph()
    
    for vote in data: 
        graph = add_edges(graph, vote["votes"]["Yea"])
        graph = add_edges(graph, vote["votes"]["Nay"])
    
    return graph

        

# <codecell>

votes = vote_graph(vote_data)    

#VISUALIZING

#this makes sure draw_spring results are the same at each call
np.random.seed(1)  

color = [votes.node[senator]['color'] for senator in votes.nodes()]

#determine position of each node using a spring layout
pos = nx.spring_layout(votes, iterations=200)

#plot the edges
nx.draw_networkx_edges(votes, pos, alpha = .05)

#plot the nodes
nx.draw_networkx_nodes(votes, pos, node_color=color)

#draw the labels
lbls = nx.draw_networkx_labels(votes, pos, alpha=5, font_size=8)

#coordinate information is meaningless here, so let's remove it
plt.xticks([])
plt.yticks([])
remove_border(left=False, bottom=False)

"""
Minimum-Spanning Tree Analysis
"""

mst = nx.minimum_spanning_tree(votes, weight='distance')


#this makes sure draw_spring results are the same at each call
np.random.seed(1)  

color = [mst.node[senator]['color'] for senator in mst.nodes()]

#determine position of each node using a spring layout
pos = nx.spring_layout(mst, iterations=2000, k=.50)

#plot the edges
nx.draw_networkx_edges(mst, pos, alpha = .05)

#plot the nodes
nx.draw_networkx_nodes(mst, pos, node_color=color)

#draw the labels
lbls = nx.draw_networkx_labels(mst, pos, alpha=5, font_size=8)

#coordinate information is meaningless here, so let's remove it
plt.xticks([])
plt.yticks([])
remove_border(left=False, bottom=False)



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


# Centrality stuff just moved here
#calculate centrality 
closeness_dict = nx.closeness_centrality(votes, distance="difference")
sorted_closenesses = sorted(closeness_dict.iteritems(), key=operator.itemgetter(1))
sorted_keys = [x[0] for x in sorted_closenesses]
sorted_values = [x[1] for x in sorted_closenesses]
color = [mst.node[senator]['color'] for senator in bipartisan_votes.nodes()]


#visualize centrality
fig = plt.figure(num=None, figsize=(18, 6), dpi=80, facecolor='w', edgecolor='k')
ax2 = fig.add_subplot(111)

plt.bar(range(len(sorted_keys)), sorted_values, align='center', color=color)
plt.xticks(range(len(sorted_keys)), sorted_keys, rotation=80, fontsize='small')
plt.show()
"""
print "Lowest closeness_centrality scores:" 
for senator in sorted_closenesses[0:5]: 
    print "%s : %s" % (senator[0], senator[1]) 

print
    
#TO DO REVERSE 
print "Highest closeness_centrality scores:"
for senator in sorted_closenesses[-5:]: 
    print "%s : %s" % (senator[0], senator[1])
"""
 

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
        states[row['name']] = m(row['long'],row['lat'])


"""
Turn the bill graph data into a NetworkX Digraph

"""
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
            

"""
PageRank
"""

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

nx.write_gexf(votes, 'votes.gexf')




path = 'gephishot.png'
Image(path)


