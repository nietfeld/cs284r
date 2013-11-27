import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
import powerlaw
import requests
import random


def download_graphs(url):
    # create the url
    data = requests.get(url).text
    # send a request using the given url
    return data.splitlines()

#got this from Nate- I am VERY VERY BAD with making pretty graphs 
def remove_border(axes=None, top=False, right=False, left=True, bottom=True):
    """
    Minimize chartjunk by stripping out unnecesasry plot borders and axis ticks
    
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
 
def plot_degree(degree,ave_degree, title, loglog=False):
	fig = plt.figure()
	ax = fig.add_subplot(111)

	# the histogram of the data
	num_bins = len(set(degree))
	n, bins, patches = ax.hist(degree, num_bins,normed=True, facecolor='blue', alpha=0.5)

	# add in labels 
	if loglog:
	    plt.xlabel('Log(Degree)')
	    plt.ylabel('Log(Percent)')
	    plt.title('LogLog Degree: Average Degree: '+ str(ave_degree))
	    ax.loglog()
	    saveas = 'out/'+title+'_loglog_degree.png'
	else:
		plt.xlabel('Degree')
		plt.ylabel('Percent')
		plt.title('Degree: Average Degree: '+ str(ave_degree))
		saveas = 'out/'+title+'_degree.png'
	    
	remove_border()
	plt.show()
	fig.savefig(saveas)

def plot_clustering(clustering,ave_clustering,title):
	fig = plt.figure()
	ax = fig.add_subplot(111)

	# the histogram of the data
	num_bins = 10
	n, bins, patches = ax.hist(clustering, num_bins, normed=True, facecolor='blue', alpha=0.5)

	# add in labels 
	plt.xlabel('Clustering')
	plt.ylabel('Percent')
	plt.title(title+'Clustering: Average Clustering: '+ str(ave_clustering))

	ax.set_ybound(upper=800)
	remove_border()
	plt.show()
	fig.savefig('out/'+title+'_clustering.png')

def plot_shortest_paths(shortest_paths, avg_shortest_path, title):
	fig = plt.figure()
	ax = fig.add_subplot(111)

	# the histogram of the data
	num_bins = 6
	n, bins, patches = ax.hist(shortest_paths, num_bins, normed=True, facecolor='blue', alpha=0.5)

	# add in labels 
	plt.xlabel('shortest_paths')
	plt.ylabel('Length')
	plt.title(title+'Shortest Paths: Average Shortest Paths: '+ str(avg_shortest_path))

	#ax.set_ybound(upper=100)
	remove_border()
	plt.show()
	fig.savefig('out/'+title+'_shortestpath.png')

def get_shortest_paths(graph) : 
	shortest_path_dict = nx.shortest_path_length(graph, source=None, target=None, weight=None)
	dictlist = []
	for key, value in shortest_path_dict.iteritems(): 
		for inner_key, inner_value in value.iteritems(): 
			dictlist.append(inner_value)
	average_shortest_path = nx.average_shortest_path_length(graph, weight=None)
	plot_shortest_paths(dictlist, average_shortest_path, title)

def make_graphs(graph, title):
	degrees = nx.degree(graph).values()
	plot_degree(degrees,np.average(degrees),title)
	plot_degree(degrees,np.average(degrees),title,loglog=True)

	results = powerlaw.Fit(degrees)
	"""
	print "powerlaw alpha: "
	print results.power_law.alpha
	print "powerlaw xmin: "
	print results.power_law.xmin
	"""


	clustering=nx.clustering(graph).values() # degree sequence
	plot_clustering(clustering,nx.average_clustering(graph),title)

def voter_model(graph, steps):
	#make a list of all the nodes
	node_list = list(graph.nodes()) 
	node_num = len(node_list)

	for iteration in range(1000): 
		#make a list of 0's 
		state_list = [0 for i in range(node_num)]
		time_list = [-1 for i in range(node_num)]
		state_dict = dict(zip(node_list, zip(state_list, time_list)))
		
		#randomly infect 1000 nodes
		for i in range(1000): 
			rand_index = random.randint(0, node_num)
			state_dict[rand_index] = (1, 0)

		for step in range(1, 1000): 
			new_infected = [] 

			#for each edge, infect with weight w_ij
			for node in graph:
				if state_dict.get(node)[0] == 0: 
					#count the incoming edges and find the length 
					infected_neighbors = 0 
					in_edges = graph.neighbors(node)
					d = len(in_edges)

					#check each incoming edge
					for neighbor in in_edges: 
						infected_neighbors += state_dict.get(neighbor)[0]
					p_infect = float(infected_neighbors)/d

					if random.random() < (p_infect): 
						new_infected.append((node, 1, step))

			for (node, status, time_step) in new_infected: 
				state_dict[node] = (status, time_step)

			if len(new_infected) == 0:
				break
		
		for key, (a,b) in state_dict.iteritems(): 
			if a == 1: 
				print "%s %s %s" % (iteration, key, b)

	



urls = ["http://people.seas.harvard.edu/~yaron/cs284rFall2013/data/epinions.txt"] # ["http://people.seas.harvard.edu/~yaron/cs284rFall2013/data/enron.txt"] "http://people.seas.harvard.edu/~yaron/cs284rFall2013/data/livejournal.txt"]
for url in urls : 
	line_array = download_graphs(url)
	graph = nx.parse_adjlist(line_array,nodetype=int)
	voter_model(graph, 1000)
	title = url
	

	#make_graphs(graph, title)






