#!/usr/bin/env python3

# Updated Wednesday 19 January 2022
# Sajid Nawaz Khan, @snkhan
# Queries a local Mihari database
# Requirements: `pip install maltego-trx`

from maltego_trx.entities import Phrase
from maltego_trx.transform import DiscoverableTransform
import sqlite3


# Configuration
# Absolute path to your Mihari database (sqlite3 only)
mihari_db = "./mihari.db"


class IPToC2(DiscoverableTransform):
	"""
	Returns the name of the C2 Framework associated with an IP
	Due to nuances in how Maltego treats labels, identical framework detections for a single host will return a single date label
	As a design principle, the SQL query will select the most recent sighting / observed date
	"""

	@classmethod
	def create_entities(cls, request, response):
		ip = request.Value
		
		try:
			C2s = cls.get_C2(ip)
			if C2s:
				for C2 in C2s:
					detection = C2[0]
					observed = C2[1][:10]

					entity = response.addEntity(Phrase, detection)
					entity.setLinkColor("#DE3163")
					entity.setLinkLabel("Observed " + observed)
			
			else:
				response.addUIMessage("IP not associated with any C2s.")
		
		except IOError:
			response.addUIMessage("Unable to connect to the Mihari database. Please check your paths.", messageType=UIM_PARTIAL)
		
	
	@staticmethod
	def get_C2(search_ip):
		ip = search_ip
		matching_C2 = []
		
		connect = sqlite3.connect(mihari_db)
		mihari = connect.cursor()
		
		results = mihari.execute(f'''
		SELECT
			alerts.title AS "Alert Type",
			artifacts.created_at AS "Date"
		FROM artifacts
		INNER JOIN alerts ON alerts.id = artifacts.alert_id
		WHERE data = "{ip}"
		ORDER BY "Date" DESC;
		''')
		
		matching_C2 = results.fetchall()
		
		# Close the database
		connect.close()
		
		return matching_C2
	
	
if __name__ == "__main__":
	print(IPToC2.get_C2("127.0.0.1"))