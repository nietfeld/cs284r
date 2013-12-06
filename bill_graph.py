#configs
# set some nicer defaults for matplotlib
from matplotlib import rcParams
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import json
import operator
import os.path
import vote_graph

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


def closeness_centrality(votes): 
    # Centrality stuff just moved here
    #calculate centrality 
    closeness_dict = nx.closeness_centrality(votes, distance="difference")
    """
    sorted_closenesses = sorted(closeness_dict.iteritems(), key=operator.itemgetter(1))
    sorted_keys = [x[0] for x in sorted_closenesses]
    sorted_values = [x[1] for x in sorted_closenesses]
    """
    """color = [votes.node[senator]['color'] for senator in votes.nodes()]

    centrality_party = zip(closeness_dict.values(), color)
    centrality_dems = [x[0] for x in centrality_party if x[1] == "b" ]
    centrality_gops = [x[0] for x in centrality_party if x[1] == "r" ]
    majority_size = max(len(centrality_dems), len(centrality_gops))"""
    return {"mean:" : np.mean(closeness_dict.values())}

def centralities_chart(): 
    centralities = [] 
    folder = 'senate_bills'
    f = open("senate_bills/senate_bills_113.txt", "r")
    f.close()
    for file_name in os.listdir(folder)[1:]:
        path = "senate_bills/%s" % file_name
        f = open(path, "r")
        vote_data = json.load(f)
        votes = bill_graph(vote_data)
        centralities.append(closeness_centrality(votes))
    print centralities

def influence_charts_2013(): 
    #open bills, make bill graph
    f = open("senate_bills/senate_bills_113.txt", "r")
    bill_list = json.load(f)
    bills = bill_graph(bill_list)
    f.close()

    #influence model metrics


    in_degree_dict = bills.in_degree() 
    sorted_in_degree = sorted(in_degree_dict.iteritems(), key=operator.itemgetter(1))
    # this is the order we'll base all of the graphs on
    sorted_senators = [x[0] for x in sorted_in_degree]
    senator_count = len(sorted_senators)

    in_degree_values = [in_degree_dict[x] for x in sorted_senators]


    pagerank_dict = nx.pagerank_numpy(bills)
    pagerank_values = [pagerank_dict[x] for x in sorted_senators]

    hubs, authorities = nx.hits_numpy(bills)
    hubs_values = [hubs[x] for x in sorted_senators]
    authorities_values = [authorities[x] for x in sorted_senators]

    #get the colors we'll need for coloring 
    f = open("party_dict.txt", "r")
    party_dict = json.load(f)
    color = [party_dict[x] for x in sorted_senators]

    #visualize in and out degree

    fig = plt.figure(num=None, figsize=(18, 6), dpi=80, facecolor='w', edgecolor='k')
    ax2 = fig.add_subplot(111)

    plt.bar(range(senator_count), in_degree_values, align='center', color=color)
    plt.xticks(range(senator_count), sorted_senators, rotation=90, fontsize=9)
    plt.xlabel("Senators by In-degree")
    plt.ylabel('In-degree')
    plt.show()

    #visualize centrality
    fig = plt.figure(num=None, figsize=(18, 6), dpi=80, facecolor='w', edgecolor='k')
    ax1 = fig.add_subplot(111)

    plt.bar(range(senator_count), pagerank_values, align='center', color=color)
    plt.xticks(range(senator_count), sorted_senators, rotation=90, fontsize=9)
    plt.xlabel("Senators by Pagerank Score")
    plt.ylabel('Pagerank Score')
    plt.show()


    fig = plt.figure(num=None, figsize=(18, 6), dpi=80, facecolor='w', edgecolor='k')
    ax3 = fig.add_subplot(111)

    plt.bar(range(senator_count), hubs_values, align='center', color=color)
    plt.xticks(range(senator_count), sorted_senators, rotation=90, fontsize=9)
    plt.xlabel("Senators by HITS Hub Score")
    plt.ylabel('Hub Score')
    plt.show()

    fig = plt.figure(num=None, figsize=(18, 6), dpi=80, facecolor='w', edgecolor='k')
    ax4 = fig.add_subplot(111)

    plt.bar(range(senator_count), authorities_values, align='center', color=color)
    plt.xticks(range(senator_count), sorted_senators, rotation=90, fontsize=9)
    plt.xlabel("Senators by HITS Authorities Score")
    plt.ylabel('Authorities Score')
    plt.show()


    voter_model_scores = {u'Burr, Richard': 60, u'Johnson, Tim': 50, u'Johanns, Mike': 60, u'Begich, Mark': 71, u'Inhofe, James M.': 38, u'McCain, John': 25, u'Portman, Rob': 89, u'Rockefeller, John D., IV': 71, u'Landrieu, Mary L.': 101, u'Heinrich, Martin': 20, u'Pryor, Mark L.': 61, u'Brown, Sherrod': 81, u'Toomey, Pat': 50, u'Cardin, Benjamin L.': 101, u'Tester, Jon': 91, u'Wyden, Ron': 81, u'Klobuchar, Amy': 50, u'Lee, Mike': 65, u'Fischer, Deb': 0, u'Bennet, Michael F.': 20, u'Blunt, Roy': 71, u'Collins, Susan M.': 81, u'Schumer, Charles E.': 61, u'Harkin, Tom': 91, u'McCaskill, Claire': 91, u'Lautenberg, Frank R.': 91, u'Cruz, Ted': 57, u'Schatz, Brian': 19, u'Feinstein, Dianne': 90, u'Coats, Daniel': 48, u'Hagan, Kay': 49, u'King, Angus S. Jr.': 10, u'Murray, Patty': 50, u'Enzi, Michael B.': 49, u'Whitehouse, Sheldon': 40, u'Reed, Jack': 51, u'Ayotte, Kelly': 50, u'Levin, Carl': 61, u'Kaine, Tim': 19, u'Cowan, William M.': 0, u'Grassley, Chuck': 61, u'Baldwin, Tammy': 30, u'Chambliss, Saxby': 9, u'Gillibrand, Kirsten E.': 79, u'Sanders, Bernard': 60, u'Hoeven, John': 48, u'Leahy, Patrick J.': 71, u'Coons, Christopher A.': 38, u'Sessions, Jeff': 0, u'Thune, John': 61, u'Donnelly, Joe': 19, u'Moran, Jerry': 71, u'Hirono, Mazie K.': 40, u'Manchin, Joe, III': 40, u'Shelby, Richard C.': 90, u'Menendez, Robert': 71, u'Mikulski, Barbara A.': 81, u'Alexander, Lamar': 69, u'Scott, Tim': 0, u'Hatch, Orrin G.': 88, u'Cornyn, John': 60, u'Booker, Cory A.': 0, u'Blumenthal, Richard': 81, u'Markey, Edward J.': 0, u'Rubio, Marco': 68, u'Risch, James E.': 9, u'Cochran, Thad': 20, u'Franken, Al': 69, u'Coburn, Tom': 86, u'Kirk, Mark Steven': 69, u'Durbin, Richard': 69, u'Boozman, John': 48, u'Corker, Bob': 9, u'Barrasso, John': 59, u'Flake, Jeff': 25, u'Murphy, Christopher S.': 20, u'Stabenow, Debbie': 80, u'Johnson, Ron': 49, u'Carper, Thomas R.': 61, u'Udall, Tom': 40, u'Roberts, Pat': 67, u'Shaheen, Jeanne': 81, u'Vitter, David': 71, u'Paul, Rand': 49, u'Reid, Harry': 30, u'Heller, Dean': 40, u'Warren, Elizabeth': 10, u'McConnell, Mitch': 0, u'Isakson, Johnny': 30, u'Baucus, Max': 81, u'Casey, Robert P., Jr.': 90, u'Graham, Lindsey': 70, u'Heitkamp, Heidi': 36, u'Udall, Mark': 48, u'Murkowski, Lisa': 40, u'Cantwell, Maria': 61, u'Crapo, Mike': 0, u'Warner, Mark R.': 61, u'Boxer, Barbara': 70, u'Merkley, Jeff': 91, u'Nelson, Bill': 100, u'Wicker, Roger F.': 20, u'Chiesa, Jeff': 0}
    voter_model_values = [voter_model_scores[x] for x in sorted_senators]

    fig = plt.figure(num=None, figsize=(18, 6), dpi=80, facecolor='w', edgecolor='k')
    ax5 = fig.add_subplot(111)

    plt.bar(range(senator_count), voter_model_values, align='center', color=color)
    plt.xticks(range(senator_count), sorted_senators, rotation=90, fontsize=9)
    plt.xlabel("Senators by Voter-Model Score")
    plt.ylabel('Voter-Model Score')
    plt.show()
    

# pretty prints a list of senators
def senator_list():
    f = open("senate_bills/senate_bills_113.txt", "r")
    bill_list = json.load(f)
    bills = bill_graph(bill_list)
    party_dict = {}
    for senator in sorted(bills.nodes()):
        party_dict[senator] = "b"
    print party_dict
    with open("party_dict.txt", "w") as outfile:
        json.dump(party_dict, outfile,sort_keys=True, indent=4, separators=(',', ': '))

influence_charts_2013()
