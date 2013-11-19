#configurations
api_key = 'YOUR KEY HERE'
movie_id = '770672122'
consumer_key = 'ylLqSZWgZ6CJlrJA4YmWkg'
consumer_secret = 'jhdsOlMCXO4pgJdmO3ioGECPcdMDhb68WVxo5hkufA'


#url = 'http://api.rottentomatoes.com/api/public/v1.0/movies/%s/reviews.json' % movie_id

#these are "get parameters"
options = {'review_type': 'top_critic', 'page_limit': 20, 'page': 1, 'apikey': api_key}
data = requests.get(url, params=options).text
data = json.loads(data)  # load a json string into a collection of lists and dicts

print json.dumps(data['reviews'][0], indent=2)  # dump an object into a json string
"""