"""
vote_graph.py 

Handles creating an undirected graph based on votes

need to say vote_data = (open file)
votes = vote_graph(vote_data)

"""
import networkx as nx
import itertools
import json
import numpy as np

senator_colors = {}

def add_edges(g, senators): 
    
    for senator in senators: 

        if senator == "VP":
            pass
        elif senator["party"] == "D": 
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

def visualize_votes(votes):
    #this makes sure draw_spring results are the same at each call
    np.random.seed(1)  

    color = [votes.node[senator]['color'] for senator in votes.nodes()]

    pos = nx.spring_layout(votes, iterations=200) #determine position of each node using a spring layout
    nx.draw_networkx_edges(votes, pos, alpha = .05) #plot the edges
    nx.draw_networkx_nodes(votes, pos, node_color=color) #plot the nodes
    lbls = nx.draw_networkx_labels(votes, pos, alpha=5, font_size=8) #draw the labels

    #coordinate information is meaningless here, so let's remove it
    plt.xticks([])
    plt.yticks([])
    remove_border(left=False, bottom=False)


def visualize_mst(votes):
    min_spanning_tree = nx.minimum_spanning_tree(votes, weight = 'difference')

    #this makes sure draw_spring results are the same at each call
    np.random.seed(1)  

    color = [min_spanning_tree.node[senator]['color'] for senator in min_spanning_tree.nodes()]

    #determine position of each node using a spring layout
    pos = nx.spring_layout(min_spanning_tree, iterations=200)
    plt.figure(figsize=(25,25))


    #plot the edges
    nx.draw_networkx_edges(min_spanning_tree, pos, alpha = .5)

    #plot the nodes
    nx.draw_networkx_nodes(min_spanning_tree, pos, node_color=color)

    #draw the labels
    lbls = nx.draw_networkx_labels(min_spanning_tree, pos, alpha=5, font_size=8)

    #coordinate information is meaningless here, so let's remove it
    plt.xticks([])
    plt.yticks([])
    remove_border(left=False, bottom=False)

def closeness_centrality(votes): 
    # Centrality stuff just moved here
    #calculate centrality 
    closeness_dict = nx.closeness_centrality(votes, distance="difference")
    """
    sorted_closenesses = sorted(closeness_dict.iteritems(), key=operator.itemgetter(1))
    sorted_keys = [x[0] for x in sorted_closenesses]
    sorted_values = [x[1] for x in sorted_closenesses]
    """
    color = [votes.node[senator]['color'] for senator in votes.nodes()]

    centrality_party = zip(closeness_dict.values(), color)
    centrality_dems = [x[0] for x in centrality_party if x[1] == "b" ]
    centrality_gops = [x[0] for x in centrality_party if x[1] == "r" ]
    majority_size = max(len(centrality_dems), len(centrality_gops))
    return {"mean:" : np.mean(closeness_dict.values()), "dems" : np.mean(centrality_dems), "gop" : np.mean(centrality_gops), "majority_size": majority_size} 
    """
    #visualize centrality
    fig = plt.figure(num=None, figsize=(18, 6), dpi=80, facecolor='w', edgecolor='k')
    ax2 = fig.add_subplot(111)

    plt.bar(range(len(sorted_keys)), sorted_values, align='center', color=color)
    plt.xticks(range(len(sorted_keys)), sorted_keys, rotation=80, fontsize='small')
    plt.show()
    """
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
 

centralities = [] 
file_list = ["senate_votes_1990.txt", "senate_votes_1995.txt", "senate_votes_2000.txt", "senate_votes_2005.txt", "senate_votes_2010.txt", "senate_votes_2013.txt"] 
#file_list = ["senate_votes_2005.txt", "senate_votes_2010.txt", "senate_votes_2013.txt"]

for file_name in file_list:
    f = open(file_name, "r")
    vote_data = json.load(f)
    f.close()
    votes=vote_graph(vote_data)
    centralities.append(closeness_centrality(votes))

print centralities

"""
file_list = ["senate_votes_1990.txt", "senate_votes_1995.txt", "senate_votes_2000.txt", "senate_votes_2005.txt", "senate_votes_2010.txt", "senate_votes_2013.txt"] 

for file_name in file_list:
    f = open(file_name, "r")
    vote_data = json.load(f)
    f.close()
    votes=vote_graph(vote_data)
    print "average clustering %s: %f" % (file_name, nx.average_clustering(votes))
"""
