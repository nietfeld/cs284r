import requests
from pattern import web
import json


# sample vote_url: https://www.govtrack.us/data/congress/113/votes/2013/
def senate_bill_url(session): 
    return "https://www.govtrack.us/data/congress/%s/bills/s/" % session

def house_bill_url(session): 
    return "https://www.govtrack.us/data/congress/%s/bills/hr/" % session

#gets a specific vote
def get_bill(url, number): 
    bill_page = url+str(number)+"data.json"
    print bill_page
    page_text = requests.get(bill_page).text
    json_dict = json.loads(page_text)
    return json_dict

#gets all the votes from a specific year
def get_senate_bills(session):
    senate_bills = []
    url = senate_bill_url(session)
    html = requests.get(url).text
    element = web.Element(html)
    senate_bill_list = element.by_tag("a")

    #MAKE SURE TO CHANGE THIS TO DO THE WHOLE LIST!!! 
    for link in senate_bill_list[1:3]:
        number=link[0]
        bill = get_bill(url,number)
        senate_bills.append(bill)

    return senate_bills

def get_house_bills(session):
    return []

def get_all_bills() : 
    all_bills_dict = {}
    #CHANGE THIS FOR aLL THE BILLS
    for session in range(101, 114): 
        all_bills_dict[session] = get_senate_bills(session)
    return all_bills_dict

all_bills = get_all_bills()
with open('senate_bills_1990_2013.txt', 'w') as outfile:
  json.dump(all_bills, outfile)
