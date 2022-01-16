import json
import sys
import csv
from haralyzer import HarParser, HarPage

with open(sys.argv[1], 'r') as f_in:
	har_parser = HarParser(json.loads(f_in.read()))


PROPERTY_TYPES = {
	6: 'SINGLE_FAMILY_HOME',
	13: 'TOWNHOUSE',
	3: 'CONDO',
	2: 'CONDO',
	5: 'MULTI_FAMILY_5',
	4: 'MULTI_FAMILY_2_4',
	8: 'RESIDENTIAL_LOT',
	10: 'MOBILE_HOME',
	1: 'SINGLE_FAMILY_HOME',
	11: 'PARKING_LOT'
}

def get_from_map(home, key, m):
	if key in m:
		return m[key]
	else:
		raise KeyError("{} not present in {}, url: {}".format(key, m, home['url']))

data = har_parser.har_data

rows = {}
dups = 0
for e in data['entries']:
	request_url = e['request']['url']
	if 'https://www.redfin.com/stingray/' in request_url:
		response_text = e['response']['content'].get('text', None)
		if response_text:
			first_quote_idx = response_text.find('\"')
			response_json = json.loads(response_text[first_quote_idx-1:])
			for home in response_json.get('payload', {}).get('homes', []):
				property_id = home['propertyId']
				if property_id in rows:
					dups+=1

				rows[home['propertyId']] = {
					'PRICE': home.get('price', {}).get('value', None),
					'HOA': home.get('hoa', {}).get('value', None),
					'SQUARE_FEET': home.get('sqFt', {}).get('value', None),
					'BEDS': home.get('beds', None),
					'BATHS': home.get('baths', None),
					'PROPERTY_TYPE': get_from_map(home, home['propertyType'], PROPERTY_TYPES),
					'CITY': home.get('city', '').upper().strip(),
					'URL': home.get('url', None)
					}

with open(sys.argv[2], 'w+') as f_out:
	writer = csv.DictWriter(f_out, fieldnames=['PRICE', 'HOA', 'SQUARE_FEET', 'BEDS', 'BATHS', 'PROPERTY_TYPE', 'CITY', 'URL'])
	writer.writeheader()
	writer.writerows(rows.values())
	print("Collected {} rows".format(len(rows.values())))
	print("Detected {} duplicates".format(dups))