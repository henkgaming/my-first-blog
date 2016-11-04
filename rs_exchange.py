import sys, os
sys.path.append('/path/to/your/django/app')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.conf import settings

from urllib2 import urlopen
import ast
import simplejson
import math


#######################################################################
######################### TO DO LIST  ####$############################
#maak 1 api call, sla dit op in een list, en haal vervolgens de data uit 
# niet bekend of dat kan voor fluctuations, aangezien je elk item moet ophalen
# C heeft wel optimalisatie nodig -> duurt nu een paar minuten

#######################################################################
######################### DEFINING PRESETS ############################
# A takes about 30 seconds
# B takes about 5 seconds
choice = raw_input("Welcome, A = Bulk, B = high margin, C = fluctuations Bulk, D = fluctuations expensive  ")
if choice == "A":
	minimum_price_margin = 30
	wanted_quantity = 2000
	wanted_margin = 50
	wanted_perc = 0.03
if choice == "B":
	minimum_price_margin = 200000
	wanted_margin = 80000
	wanted_quantity = 4
	wanted_perc = 0.03
if choice == "C":    # fluctuations bulk
	wanted_perc = 0.07 #this will be 10% under usual price
	wanted_quantity = 2000
	wanted_minimum_price = 500
	wanted_maximum_price = 50000
if choice == "D":     #expensive
	wanted_perc = 0.05 #This will be 3% under usual price
	wanted_quantity = 5
	wanted_minimum_price = 1000000
	wanted_maximum_price = 2148000000
#######################################################################
######################### TO GRAB INFO ################################
summaryurl = "https://rsbuddy.com/exchange/summary.json"
data = json.load(urlopen(summaryurl))
######################### FOR BULK A & B  #################################
if choice == "A" or choice == "B":
	for items in data:
		id = data[items]['id']
		buy = data[items]['buy_average']
		sell = data[items]['sell_average']
		if buy > 0 and sell > 0:
			margin = abs(buy - sell)
			avg = (buy+sell)/2
			perc = float(margin)/float(avg)
			if margin > wanted_margin or (perc>wanted_perc and margin > minimum_price_margin):
				url = "https://api.rsbuddy.com/grandExchange?a=guidePrice&i=%s" % id
				response = json.load(urlopen(url))
				quantity_buy = response["buyingQuantity"]
				quantity_sell = response["sellingQuantity"]
				if quantity_buy > wanted_quantity and quantity_sell > wanted_quantity: 
					formatted = float("{0:.2f}".format(100*perc))   
					print data[items]["name"] + ' has margin ' + "{:,}".format(margin) + "(%s percent)" % formatted
					print "     - With a buying price of: " + "{:,}".format(buy)
					print "     - and a selling price of: " + "{:,}".format(sell)
					print "     - and hourly quantity Buy & Sell " +str(quantity_buy) + " & " +str(quantity_sell)

######################### FOR FLUCTUATIONS BULK(C) #################################
# can be optimized as follows: first from summary get the price -> filter out all low prices
# with remainder list -> do specific API calls to get avg quantity
# if we take a minimum price of 750 from data, it takes 2:35 
# if we take a minimum price of 300 from data, it takes: 3:00
# if we dont take a minimum price in data first, it takes: 9:30 -> then timeout

# for choice C, price 500-50.000 -> it takes 1:45
# for choice D, price > 500.000 -> it takes 20 seconds
if choice == "C" or choice == "D":
	for items in data:
		id = data[items]['id']
		price_total = 0
		completed_total = 0
		buy = data[items]['buy_average'] 
		if buy > wanted_minimum_price and buy < wanted_maximum_price:
			fluctuations_url = "https://api.rsbuddy.com/grandExchange?a=graph&g=30&i=%s" % id
			fluctuations = json.load(urlopen(fluctuations_url))
			for stamps in fluctuations:
				price_total += stamps['overallPrice']
				completed_total += stamps['overallCompleted']	
			if len(fluctuations) > 0:
				average = price_total/(len(fluctuations))	
				average_completed = completed_total/len(fluctuations)
				current_price = fluctuations[len(fluctuations)-1]['overallPrice']
				margin_perc = float(current_price)/float(average)
				difference_price = current_price - average
				if margin_perc < (1-wanted_perc) and average_completed > wanted_quantity and average > wanted_minimum_price and average < wanted_maximum_price:
					print "for item id: " + str(data[items]['name'])
					print "     - The average price from this week is: " + str(average)
					print "     - The current price is: " + str(current_price)
					print "     - Which is " + str(abs(difference_price)) + "GP (" +str(round(100*(1-margin_perc))) + "%) under the normal price" 
					print "     - With a quantity of " +str(average_completed) + " per 30 minutes"
