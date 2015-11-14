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
import operator
import BeautifulSoup as bts
import urllib2
from collections import OrderedDict
from optparse import OptionParser

class FixtureFinder:

	def __init__(self, listFlag, allFlag, leagueCode):

		# Get all the league codes for each league 
		self.leagueCodes = {}
		self.leagueCodes['E0']  = 'competition-118996114'
		self.leagueCodes['E1']  = 'competition-118996115'
		self.leagueCodes['E2']  = 'competition-118996116'
		self.leagueCodes['E3']  = 'competition-118996117'
		self.leagueCodes['E4']  = 'competition-118996118'
		self.leagueCodes['E5']  = 'competition-118996307'
		self.leagueCodes['E6']  = 'competition-118996308'
		self.leagueCodes['SC0'] = 'competition-118996176'
		self.leagueCodes['SC1'] = 'competition-118996177'
		self.leagueCodes['SC2'] = 'competition-118996178'
		self.leagueCodes['SC3'] = 'competition-118996179'
		self.leagueCodes['SC4'] = 'competition-118999031'
		self.leagueCodes['SC5'] = 'competition-119003997'
		self.leagueCodes['W1']  = 'competition-118996207'
		self.leagueCodes['NI1'] = 'competition-118996238'
		self.leagueCodes['IE1'] = 'competition-118996240'
		self.leagueCodes['AR1'] = 'competition-999999994'
		self.leagueCodes['AU1'] = 'competition-999999995'
		self.leagueCodes['AT1'] = 'competition-119000919'
		self.leagueCodes['B1']  = 'competition-119000924'
		self.leagueCodes['BR1'] = 'competition-999999996'
		self.leagueCodes['DK1'] = 'competition-119000950'
		self.leagueCodes['N1']  = 'competition-119001012'
		self.leagueCodes['FI1'] = 'competition-119000955'
		self.leagueCodes['F1']  = 'competition-119000981'
		self.leagueCodes['D1']  = 'competition-119000986'
		self.leagueCodes['G1']  = 'competition-119001136'
		self.leagueCodes['I1']  = 'competition-119001017'
		self.leagueCodes['NO1'] = 'competition-119001043'
		self.leagueCodes['PT1'] = 'competition-119001048'
		self.leagueCodes['RU1'] = 'competition-999999990'
		self.leagueCodes['SP1'] = 'competition-119001074'
		self.leagueCodes['SE1'] = 'competition-119001079'
		self.leagueCodes['CH1'] = 'competition-119001105'
		self.leagueCodes['T1']  = 'competition-119001110'
		self.leagueCodes['US1'] = 'competition-999999988'

		# Just list the league codes and exit
		if listFlag:
			leagueCodesList = sorted(self.leagueCodes.keys())
			outputString = ''
			print "LeagueCodes:\n================"
			for x in xrange(0,len(leagueCodesList)):
				outputString += str(leagueCodesList[x])+",\t"
				if ((x+1)%10) == 0 and x != 0:
					print outputString
					outputString = ''
			print outputString[:-1]
			exit(1)

		if allFlag:
			for key in self.leagueCodes.keys():
				self.getLeagueCode(key)				
		else:
			self.getLeagueCode(leagueCode)

	def getLeagueCode(self, leagueCode):
		try:
			tablesBaseURL = 'http://www.bbc.com/sport/football/tables?filter='
			fixturesBaseURL = 'http://www.bbc.com/sport/football/fixtures?filter='

			tablesUrl = fixturesBaseURL+self.leagueCodes[leagueCode]+".html"
			fixturesUrl = fixturesBaseURL+self.leagueCodes[leagueCode]+".html"

			tablesHtml = self.getRawHTML(tablesUrl)
			fixturesHtml = self.getRawHTML(fixturesUrl)

			if tablesHtml is not None and fixturesHtml is not None:
				leagueTable = self.scrapeTables(tablesHtml)
				self.scrapeFixtures(fixturesHtml, leagueCode, leagueTable)
	
		except KeyError as error:
			print "\nError - Invalid league code (",leagueCode,")..."
			exit(1)

	def getRawHTML(self, url):
		""" Returns the raw html from a specified URL or None
		    if there's a problem with the URL.
		"""

		try:
			response = urllib2.urlopen(url)
			html = response.read()
			return html
		except urllib2.HTTPError as e:
			print e.code
			print e.read() 
			return None
	
	def scrapeFixtures(self, html, leagueCode, leagueTable):
		goodTeams = self.getGoodTeams(leagueTable)
		badTeams  = self.getBadTeams(leagueTable)

		dateList = []
		homeList = []
		awayList = []

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
				dateList.append(dateString)
				homeList.append(homeTeamList[0].getText())
				awayList.append(awayTeamList[0].getText())

		for x in xrange(0, len(dateList)):
			date = dateList[x]
			home = homeList[x]
			away = awayList[x]

			if home in goodTeams and away in badTeams:
				print 'Home Win: {0}, {1}, {2} v {3}'.format(leagueCode, date, self.uescape(home), self.uescape(away))
			elif home in badTeams and away in goodTeams:			
				print 'Away Win: {0}, {1}, {2} v {3}'.format(leagueCode, date, self.uescape(home), self.uescape(away))

	def uescape(self, text):
		return text.encode('utf-8')

	def getGoodTeams(self, leagueTable):
		teams = []
		for row in leagueTable:
			position = row[0]
			played = float(row[1])
			teamName = row[2]
			points = row[3]

			if (points/played) >= 2.0:
				teams.append(teamName)

		if len(teams) == 0:
			teams.append(leagueTable[0][2])
			teams.append(leagueTable[1][2])

		return teams


	def getBadTeams(self, leagueTable):
		teams = []
		for row in leagueTable:
			position = row[0]
			played = float(row[1])
			teamName = row[2]
			points = row[3]

			if (points/played) <= 0.9:
				teams.append(teamName)

		if len(teams) == 0:
			teams.append(leagueTable[-2][2])
			teams.append(leagueTable[-1][2])

		return teams

	def convertDateToYYYYMMDD(self, dateString):
		""" Converts a date string of the form 10th May 2015 to 20150510
		"""
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
		
	def scrapeTables(self, html):
		table = []

		if len(html) < 10:
			print "Error - Problems with HTML input to generate league tables..."
			exit(1)

		soup = bts.BeautifulSoup(html)
		teamList = soup.findAll("tr", "team")

		for team in teamList:
			position = team.findAll("span", "position-number")[0].getText()		
			teamName = team.findAll("td", "team-name")[0].getText()
			played = team.findAll("td", "played")[0].getText()					
			points = team.findAll("td", "points")[0].getText()
			tablerow = [int(position), int(played), teamName, int(points)]
			table.append(tablerow)

		return table

def main(argv):
	parser = OptionParser(usage="Usage: FixtureFinder [OPTIONS] [leagueCode]")
	parser.add_option("-l", "--list",
		action="store_true",
		dest="listLeagueCodes",
		default=False,
		help="lists the league codes")

	parser.add_option("-a", "--all",
		action="store_true",
		dest="allCodes",
		default=False,
		help="get all fixtures")

	parser.add_option("-t", "--target",
	    	action='store',
		dest='leagueCode',
		default=None,
		help='get fixtures for specified league')

	(options, filename) = parser.parse_args()

	if options.leagueCode is None and not options.listLeagueCodes and not options.allCodes:
		parser.print_help()
		sys.exit(1)
	
	scraper = FixtureFinder(options.listLeagueCodes, options.allCodes, options.leagueCode)
		
if __name__ == "__main__":
    sys.exit(main(sys.argv))
