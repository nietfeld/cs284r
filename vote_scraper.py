import requests
from pattern import web
import json


# sample vote_url: https://www.govtrack.us/data/congress/113/votes/2013/
def vote_url(session, year): 
    return "https://www.govtrack.us/data/congress/%s/votes/%s/" % (session, year)

#gets a specific vote
def get_vote(url, number): 
    vote_page = url+str(number)+"data.json"
    return requests.get(vote_page).json()

#gets all the votes from a specific year
def get_year_votes(year_url):
    senate_votes = []
    house_votes = []
    vote_page = requests.get(year_url).text
    element = web.Element(vote_page)
    link_list = element.by_tag("a") 
    
    #MAKE SURE TO CHANGE THIS TO DO THE WHOLE LIST!!! 
    for link in link_list: 
        label=link[0]
        if str(label)[0] == "s": 
            senate_votes.append(get_vote(year_url, label))
        #if str(label)[0] == "h": 
            #house_votes.append(get_vote(year_url, label))
    return senate_votes, house_votes

def get_all_votes(session, year) : 
    all_votes_dict = {}
    #for session in range(100, 110): 
    senate_votes, house_votes = get_year_votes(vote_url(session, year))
    all_votes_dict["senate"] = senate_votes
    return all_votes_dict

#broke on 2009, so did the rest manually
"""
all_votes = get_all_votes()
all_votes[2009] = get_all_year_votes("https://www.govtrack.us/data/congress/111/votes/2009")
all_votes[2010] = get_all_year_votes("https://www.govtrack.us/data/congress/111/votes/2010")
all_votes[2011] = get_all_year_votes("https://www.govtrack.us/data/congress/112/votes/2011")
all_votes[2012] = get_all_year_votes("https://www.govtrack.us/data/congress/112/votes/2012")
all_votes[2013] = get_all_year_votes("https://www.govtrack.us/data/congress/113/votes/2013")


# download bills and dump into file
with open('votes_1990_2013.txt', 'w') as outfile:
  json.dump(all_votes, outfile)
"""

all_votes = get_all_votes(113, 2013)
with open('senate_votes_2013.txt', 'w') as outfile:
  json.dump(all_votes, outfile)


