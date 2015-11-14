#!/usr/bin/env python
#=======================================================================================#
# title           :Fixture Finder							#
# description     :Scrapes the web to find top v bottom fixtures for a set date range	#
# author          :Shane Brennan							#
# date            :20111114								#
# version         :0.1									#
# usage           :python FixtureFinder --help						#
# notes           :Scrapes the web, could be volatile if the URL's change.		#
# python_version  :2.7.3								#
#=======================================================================================#

import sys
import os
import json
import re
import BeautifulSoup as bts
import urllib2
from collections import OrderedDict
from optparse import OptionParser

class FixtureFinder:

	def __init__(self, listLeagueCodes, leagueCode):
		leagueCodes = {}
		leagueCodes['E0']  = 'competition-118996114'
		leagueCodes['E1']  = 'competition-118996115'
		leagueCodes['E2']  = 'competition-118996116'
		leagueCodes['E3']  = 'competition-118996117'
		leagueCodes['E4']  = 'competition-118996118'
		leagueCodes['E5']  = 'competition-118996307'
		leagueCodes['E6']  = 'competition-118996308'
		leagueCodes['SC0'] = 'competition-118996176'
		leagueCodes['SC1'] = 'competition-118996177'
		leagueCodes['SC2'] = 'competition-118996178'
		leagueCodes['SC3'] = 'competition-118996179'
		leagueCodes['SC4'] = 'competition-118999031'
		leagueCodes['SC5'] = 'competition-119003997'
		leagueCodes['W1']  = 'competition-118996207'
		leagueCodes['NI1'] = 'competition-118996238'
		leagueCodes['IE1'] = 'competition-118996240'
		leagueCodes['AR1'] = 'competition-999999994'
		leagueCodes['AU1'] = 'competition-999999995'
		leagueCodes['AT1'] = 'competition-119000919'
		leagueCodes['B1']  = 'competition-119000924'
		leagueCodes['BR1'] = 'competition-999999996'
		leagueCodes['DK1'] = 'competition-119000950'
		leagueCodes['N1']  = 'competition-119001012'
		leagueCodes['FI1'] = 'competition-119000955'
		leagueCodes['F1']  = 'competition-119000981'
		leagueCodes['D1']  = 'competition-119000986'
		leagueCodes['G1']  = 'competition-119001136'
		leagueCodes['I1']  = 'competition-119001017'
		leagueCodes['NO1'] = 'competition-119001043'
		leagueCodes['PT1'] = 'competition-119001048'
		leagueCodes['RU1'] = 'competition-999999990'
		leagueCodes['SP1'] = 'competition-119001074'
		leagueCodes['SE1'] = 'competition-119001079'
		leagueCodes['CH1'] = 'competition-119001105'
		leagueCodes['T1']  = 'competition-119001110'
		leagueCodes['US1'] = 'competition-999999988'

		# Just list the league codes and exit
		if listLeagueCodes:
			leagueCodesList = sorted(leagueCodes.keys())
			outputString = ''
			print "LeagueCodes:\n================"
			for x in xrange(0,len(leagueCodesList)):
				outputString += str(leagueCodesList[x])+",\t"
				if ((x+1)%10) == 0 and x != 0:
					print outputString
					outputString = ''
			print outputString[:-1]
			exit(1)

		try:
			fixturesURL = 'http://www.bbc.com/sport/football/fixtures?filter='
			url = fixturesURL+leagueCodes[leagueCode]+".html"
			html = self.getRawHTML(url)
			self.scrapeBBCSport(html)
		except KeyError as error:
			print "\nError - Invalid league code (",leagueCode,")..."
			exit(1)

	def getRawHTML(self, url):
		try:
			response = urllib2.urlopen(url)
			html = response.read()
			return html
		except urllib2.HTTPError as e:
			print e.code
			print e.read() 
			exit(1)
			
	def scrapeBBCSport(self, html):
		soup = bts.BeautifulSoup(html)
		tableList = soup.findAll("table", "table-stats")

		for table in tableList:
			date = table.findAll("caption")
			matchList = table.findAll("td","match-details")
			
			dateString="UNKNOWN"
			
			if len(date) == 1:
				rawDateString = date[0].getText()
				if 'This table charts the fixtures during' in rawDateString:
					dateString = self.convertDateToYYYYMMDD(rawDateString)
			
			for match in matchList:
				jsonFixture = {}
				homeTeamList = match.findAll("span","team-home teams")
				awayTeamList = match.findAll("span","team-away teams")
				jsonFixture['date'] = dateString
				jsonFixture['homeTeam'] = homeTeamList[0].getText()
				jsonFixture['awayTeam'] = awayTeamList[0].getText()
				print json.dumps(jsonFixture)
					

	def convertDateToYYYYMMDD(self, dateString):
		dateTokens = dateString.split(' ')[7:]		
		day = dateTokens[0]
		day = day[:-2]
		if int(day) < 10:
			day = "0"+day
		
		monthTextList = ['January','February','March','April','May','June','July','August','September','October','November','December']
		monthDateList = ['01','02','03','04','05','06','07','08','09','10','11','12']
		month = monthDateList[monthTextList.index(dateTokens[1])]
		
		year = dateTokens[2]
		if len(year) == 2:
			year = "20"+year
			
		return int(year+month+day)
		
def main(argv):
	parser = OptionParser(usage="Usage: FixtureScraper [leagueCode]")
	parser.add_option("-l", "--list",
		action="store_true",
		dest="listLeagueCodes",
		default=False,
		help="lists the league codes")
		
	parser.add_option("-t", "--target",
	    	action='store',
		dest='leagueCode',
		default=None,
		help='the league code to be scraped')

	(options, filename) = parser.parse_args()

	if options.leagueCode is None and not options.listLeagueCodes:
		parser.print_help()
		sys.exit(1)
	
	scraper = FixtureFinder(options.listLeagueCodes, options.leagueCode)
		
if __name__ == "__main__":
    sys.exit(main(sys.argv))
