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


# The website [govtrack.us](http://www.govetrack.us) collects data on activities in the Senate and House of Representatives. It's a great source of information for making data-driven assessments about Congress.

# ### Problem 1.
# 
# The directories at http://www.govtrack.us/data/congress/113/votes/2013 contain JSON information about every vote cast for the current (113th)  Congress. Subdirectories beginning with "S" correspond to Senate votes, while subdirectories beginning with "H" correspond to House votes.
# 
# Write two functions: one that downloads and parses a single Senate vote page given the vote number, and another that repeatedly calls this function to build a full collection of Senate votes from the 113th Congress.

# <codecell>

"""
Function
--------
get_senate_vote

Scrapes a single JSON page for a particular Senate vote, given by the vote number

Parameters
----------
vote : int
   The vote number to fetch
   
Returns
-------
vote : dict
   The JSON-decoded dictionary for that vote
   
Examples
--------
>>> get_senate_vote(11)['bill']
{u'congress': 113,
 u'number': 325,
 u'title': u'A bill to ensure the complete and timely payment of the obligations of the United States Government until May 19, 2013, and for other purposes.',
 u'type': u'hr'}
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

# FIX THIS TO DOWNLOAD FROM THE RIGHT FILE
json_data=open('house_data.txt')
house_vote_data = json.load(json_data)
json_data.close()

json_data=open('senate_data.txt')
vote_data = json.load(json_data)
json_data.close()

# ### Problem 2
# 
# Now, turn these data into a NetworkX graph, according to the spec below. For details on using NetworkX, consult the lab materials for November 1, as well as the [NetworkX documentation](http://networkx.github.io/).

# put into network

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

# <markdowncell>

# The spring layout tries to group nodes with large edge-weights near to each other. In this context, that means it tries to organize the Senate into similarly-voting cliques. However, there's simply too much going on in this plot -- we should simplify the representation.

# <markdowncell>

# ### Problem 3
# 
# Compute the `Minimum Spanning Tree` of this graph, using the `difference` edge attribute as the weight to minimize. A [Minimum Spanning Tree](http://en.wikipedia.org/wiki/Minimum_spanning_tree) is the subset of edges which trace at least one path through all nodes ("spanning"), with minimum total edge weight. You can think of it as a simplification of a network.
# 
# Plot this new network, making modifications as necessary to prevent the graph from becoming too busy.

# <codecell>

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

# <markdowncell>

# ### Problem 4
# 
# While this graph has less information, the remaining information is easier to digest. What does the Minimum Spanning Tree mean in this context? How does this graph relate to partisanship in the Senate? Which nodes in this graph are the most and least bi-partisan?

# <markdowncell>

# The minimum spanning tree is the closest connections between all senators. We built up the tree by selecting the edge with the most votes in common and a senator not yet in the graph until every senator was included.
# 
# The nodes with the most connections are the most bipartison while the nodes at the bottom of the tree (only one connection). In the center, we have Alexander who is "The most bipartisan" according to this measure. On the outskirts we have the beleagured senators of NJ and MA who didn't stick around for very long. This graph really isn't fair to them, just because they weren't around long. Sucks to be them. 
# 
# Since the tree is not very deep, we don't really have too much information about the most and the least bipartisan. It looks like democrats have smaller difference scores than republicans (which you expect from the majority party). There are no really obvious partisans. 

# <markdowncell>

# ### Problem 5
# 
# (For this problem, use the full graph for centrality computation, and not the Minimum Spanning Tree)
# 
# Networkx can easily compute [centrality](https://en.wikipedia.org/wiki/Centrality) measurements. 
# 
# Briefly discuss what ``closeness_centrality`` means, both mathematically and in the context of the present graph -- how does the centrality relate to partisanship? Choose a way to visualize the `closeness_centrality` score for each member of the Senate, using edge `difference` as the distance measurement. Determine the 5 Senators with the highest and lowest centralities. 
# 
# Comment on your results. In particular, note the outliers John Kerry (who recently resigned his Senate seat when he became Secretary of State), Mo Cowan (Kerry's interim replacement) and Ed Markey (Kerry's permanent replacement) have low centrality scores -- why?

# <markdowncell>

# Mathematically, closeless centrality is the inverse of the sum of the distances to other nodes. The more central a node is the lower its total distance to all other nodes. If we were going to measure how long it would take to spread information from one node to all the others sequentially, closeness centrality would measure that. 
# 
# With regards to this graph, closeness centrality relates to partisanship, since a high score means a candidate is close to every other politician in the graph, in both parties. 
# 
# We notice that the people with the lowest closeness score only served part of their term in the senate. With fewer votes cast, they had many fewer oportunities to vote "Yea" or "Nay" with others on bills. Since this in not accounted for, it looks as though these politicians are incredibly partisan, when in fact they are just new. 

# <codecell>



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

# <markdowncell>

# Instead of just seeing how close one node is to all other nodes, we can look at how often a senator votes the same way on a bill as did someone from a different party. We calculate the relationship between senators from different parties in much the same way as we did problem 2 and then calculate the MST (which represents pairs of people from  different parties who vote the most similarly.) 
# 
# We see them clustered around a few key politians: Alexander (not surprising), the independents (democrats in disguise) and Amy Klobuchar (from my fine home state). We should have filtered out the independents, since they seem to always vote with democrats. But the relation to Amy Klobuchar is interesting and the criteria of voting on other parties' bills seems promising. 

# <markdowncell>

# ## Leadership in the Senate
# 
# There are many metrics to quantify the leadership in the Senate.
# 
#   1. Senate leaders sponsor and co-sponsor lots of bills
#   2. Leaders sit on many committees, as well as more important committees
#   3. Leaders usually have been in office for a long time
#   
# Another approach uses the philosophy behind how Google ranks search results. The core idea behind Google's PageRank algorithm is:
# 
# 1. A "good" website (i.e. one to rank highly in search results) is linked to by many other websites
# 2. A link found on a "good" website is more important than a link found on a "bad" website
# 
# The PageRank algorithm thus assigns scores to nodes in a graph based on how many neighbors a node has, as well as the score of those neighbors.
# 
# This technique can be adapted to rank Senate leadership. Here, nodes correspond to Senators, and edges correspond to a senator co-sponsoring a bill sponsored by another Senator. The weight of each edge from node A to B is the number of times Senator A has co-sponsored a bill whose primary sponsor is Senator B. If you interpret the PageRank scores of such a network to indicate Senate leadership, you are then assuming:
# 
# 1. Leaders sponsor more bills
# 1. Leaders attract co-sponsorship from other leaders
# 
# ### Problem 7
# 
# Govtrack stores information about each Senate bill in the current congress at http://www.govtrack.us/data/congress/113/bills/s/. As in problem 1, write two functions to scrape these data -- the first function downloads a single bill, and the second function calls the first to loop over all bills.

# <codecell>

"""
Function
--------
get_senate_bill

Scrape the bill data from a single JSON page, given the bill number

Parameters
-----------
bill : int
   Bill number to fetch
   
Returns
-------
A dict, parsed from the JSON

Examples
--------
>>> bill = get_senate_bill(10)
>>> bill['sponsor']
{u'district': None,
 u'name': u'Reid, Harry',
 u'state': u'NV',
 u'thomas_id': u'00952',
 u'title': u'Sen',
 u'type': u'person'}
>>> bill['short_title']
u'Agriculture Reform, Food, and Jobs Act of 2013'
"""

bill_url = "http://www.govtrack.us/data/congress/113/bills/s/"
    
def get_senate_bill(number): 
    bill_page = bill_url+"/s"+str(number)+"/data.json"
    # print bill_page
    bill_dict = requests.get(bill_page).json()
    return bill_dict

# <codecell>

"""
Function
--------
get_all_bills

Scrape all Senate bills at http://www.govtrack.us/data/congress/113/bills/s

Parameters
----------
None

Returns
-------
A list of dicts, one for each bill
"""
def get_all_bills():
    dict_list = []
    bill_list = requests.get(bill_url).text
    element = web.Element(bill_list)
    link_list = element.by_tag("a") 
    for link in link_list: 
        label=link[0]
        if str(label)[0] == "s": 
            dict_list.append(get_senate_bill(str(label)[1:-1]))
    return dict_list

# <codecell>

bill_list = get_all_bills()
with open('bills_2013.txt', 'w') as outfile:
  json.dump(all_votes, outfile)

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

Parameters
----------
data : list of dicts
    The data returned from get_all_bills

Returns
-------
graph : A NetworkX DiGraph, with the following properties
    * Each node is a senator. For a label, use the 'name' field 
      from the 'sponsor' and 'cosponsors' dict items
    * Each edge from A to B is assigned a weight equal to how many 
      bills are sponsored by B and co-sponsored by A
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

# <codecell>

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

