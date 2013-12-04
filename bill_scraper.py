import requests
from pattern import web
import simplejson as json


# sample vote_url: https://www.govtrack.us/data/congress/113/votes/2013/
def bill_url(chamber, session):
    if chamber == "senate":
        return "https://www.govtrack.us/data/congress/%s/bills/s/" % session
    elif chamber == "house":
        return "https://www.govtrack.us/data/congress/%s/bills/hr/" % session

#gets a specific vote
def get_bill(url, number): 
    bill_page = url+str(number)+"data.json"
    page_text = requests.get(bill_page).text
    json_dict = json.loads(page_text)
    return json_dict

#gets all the votes from a specific year
def get_year_bills(chamber, session):
    bills = []
    url = bill_url(chamber, session)
    html = requests.get(url).text
    element = web.Element(html)
    bill_list = element.by_tag("a")

    for link in bill_list[1:]:
        number=link[0]
        bill = get_bill(url,number)
        bills.append(bill)

    return bills


def get_all_bills(chamber) : 
    all_bills_dict = {}
    for session in range(105, 107): 
        print "session: %s" % session
        all_bills_dict[session] = get_year_bills(chamber, session)
    return all_bills_dict


all_bills = get_all_bills("senate")
with open('senate_bills_105_107.txt', 'w') as outfile:
    json.dump(all_bills, outfile)

