#!/usr/bin/python3
#    pyNSaudit
#    Copyright (C) 2015  RunasSudo (Yingtong Li)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import csv
import gzip
import xml.etree.ElementTree as ET
import urllib.request

#      CONFIGURATION     
REGION = 'Democratic Socialist Assembly' # The region in which to audit nations
WADELEGATE = 'Communicar' # The rightful WA delegate

RES_MIN_CR = 'Average' # The minimum Civil Rights score for Residents
RES_MIN_PF = 'Average' # The minimum Political Freedom score for Residents
MOC_MIN_CR = 'Good' # The minimum Political Freedom score for Members of Congress (Charter Members)
MOC_MIN_PF = 'Good' # The minimum Political Freedom score for Members of Congress (Charter Members)

PROHIBITED_CATEGORIES = ['Authoritarian Democracy',
                         'Benevolent Dictatorship',
                         'Compulsory Consumerist State',
                         'Conservative Democracy',
                         'Corporate Police State',
                         'Corrupt Dictatorship',
                         'Father Knows Best State',
                         'Free Market Paradise',
                         'Iron Fist Consumerists',
                         'Iron Fist Socialists',
                         'Libertarian Police State',
                         'Moralistic Democracy',
                         'Mother Knows Best State',
                         'Psychotic Dictatorship',
                         'Right-Wing Utopia',
                         'Tyranny By Majority']
#       END CONFIG       

freedomsBase = {'Outlawed': 1,
            'Unheard Of': 2,
            'Rare': 3,
            'Few': 4,
            'Some': 5,
            'Below Average': 6,
            'Average': 7,
            'Good': 8,
            'Very Good': 9,
            'Excellent': 10,
            'Superb': 11,
            'World Benchmark': 12,
            'Excessive': 13}
crScores = freedomsBase.copy()
crScores['Frightening'] = 14
crScores['Widely Abused'] = 15
pfScores = freedomsBase.copy()
pfScores['Widely Abused'] = 14
pfScores['Corrupted'] = 15

# Read list of Charter Members
charterMembers = []
with open('members.csv', newline='') as csvfile:
	csvreader = csv.reader(csvfile)
	for row in csvreader:
		if row[0][0] != '#':
			charterMembers.append(row[0])

# Get endorsements for WA delegate
waRoot = ET.parse(urllib.request.urlopen('https://www.nationstates.net/cgi-bin/api.cgi?nation={}&q=endorsements'.format(WADELEGATE))).getroot()
endorsements = waRoot.findtext('ENDORSEMENTS').split(',')

# Parse nations.xml.gz
gzfile = gzip.open('nations.xml.gz')
xmlreader = ET.iterparse(gzfile)
for event, elem in xmlreader:
	if elem.tag == 'NATION':
		if elem.findtext('REGION') != REGION:
			continue
		
		name = str.replace(str.lower(elem.findtext('NAME')), ' ', '_')
		
		category = elem.findtext('CATEGORY')
		if category in PROHIBITED_CATEGORIES:
			print('{} is in a prohibited category: {}'.format(name, category))
		
		freedoms = elem.find('FREEDOM')
		cr = freedoms.findtext('CIVILRIGHTS')
		pf = freedoms.findtext('POLITICALFREEDOM')
		
		if crScores[cr] < crScores[RES_MIN_CR]:
			print('{} has too few civil rights for a Resident: {}'.format(name, cr))
		elif name in charterMembers and crScores[cr] < crScores[MOC_MIN_CR]:
			print('{} has too few civil rights for a Charter Member: {}'.format(name, cr))
			
		if pfScores[pf] < pfScores[RES_MIN_CR]:
			print('{} has too few political freedoms for a Resident: {}'.format(name, pf))
		elif name in charterMembers and pfScores[pf] < pfScores[MOC_MIN_CR]:
			print('{} has too few political freedoms for a Charter Member: {}'.format(name, pf))
		
		if 'WA' in elem.findtext('UNSTATUS'):
			if name not in endorsements:
				print('{} has not endorsed the rightful WA delegate.'.format(name))
		
		elem.clear()

del xmlreader
