#!/usr/bin/python


#-----Statement of Authorship----------------------------------------#
#
#  By submitting this task the signatories below agree that it
#  represents our own work and that we both contributed to it.  We
#  are aware of the University rule that a student must not
#  act in a manner which constitutes academic dishonesty as stated
#  and explained in QUT's Manual of Policies and Procedures,
#  Section C/5.3 "Academic Integrity" and Section E/2.1 "Student
#  Code of Conduct".
#
#  First student's no: PUT 1ST STUDENT'S NUMBER HERE
#  First student's name: PUT 1ST STUDENT'S NAME HERE
#  Portfolio contribution: PUT 1ST STUDENT'S PERCENTAGE CONTRIBUTION HERE
#
#  Second student's no: PUT 2ND STUDENT'S NUMBER HERE
#  Second student's name: PUT 2ND STUDENT'S NAME HERE
#  Portfolio contribution: PUT 2ND STUDENT'S PERCENTAGE CONTRIBUTION HERE
#
#  Contribution percentages refer to the whole portfolio, not just this
#  task.  Percentage contributions should sum to 100%.  A 50/50 split is
#  NOT necessarily expected.  The percentages will not affect your marks
#  except in EXTREME cases.
#
#--------------------------------------------------------------------#



#-----Task Description-----------------------------------------------#
#
#  FANTALES
#
#  Movie fans have strong opinions about their favourite actors.  In
#  this task you and your programming partner will develop a program
#  that helps visualise some of the opinions of movie fans derived
#  from a survey of Microsoft employees.  To do so you will make use
#  of three different computer languages, Python, SQL and HTML.  You
#  will develop a Python function, show popularity, which accesses
#  data in an SQL database and uses this to generate HTML documents
#  which visually display an actor's popularity according to the
#  survey results.  See the instructions accompanying this file for
#  full details.
#
#--------------------------------------------------------------------#



#-----Acceptance Tests-----------------------------------------------#
#
#  This section contains unit tests that run your program.  You
#  may not change anything in this section.  NB: 'Passing' these
#  tests does NOT mean you have completed the assignment because
#  they do not check the HTML files produced by your program.
#
"""
------------------- Normal Cases with valid input --------------------

>>> show_popularity(['Female', 'Male', '30-40'], 20, 'Test01') # Test 1

>>> show_popularity(['20-30', '30-40', '40-50'], 50, 'Test02') # Test 2

>>> show_popularity(['20-40', '40-80', 'All'], 30, 'Test03') # Test 3

>>> show_popularity(['Female', 'Male', '30-40', '40-60', '60-100', 'All'], 30, 'Test04') # Test 4

>>> show_popularity(['All'], 20, 'Test05') # Test 5

>>> show_popularity(['30-40'], 50, 'Test06') # Test 6

>>> show_popularity(['30-50'], 0, 'Test07') # Test 7

------------------- Cases with invalid input ------------------------

>>> show_popularity(['20-30', '30-40', '3a-34' ], 30, 'Test08') # Test 8
Invalid customer group: 3a-34

>>> show_popularity(['teens', '20-20','30-40','40-50', '50-50', '60-d0'], 30, 'Test09') # Test 9
Invalid customer group: teens
Invalid customer group: 60-d0

>>> show_popularity(['old people', '30', '40-60', '-70', '70-100'], 30, 'Test10') # Test 10
Invalid customer group: old people
Invalid customer group: 30
Invalid customer group: -70

>>> show_popularity(['-', '30-50', '40-60', '50-20', '40 60'], 50, 'Test11') # Test 11
Invalid customer group: -
Invalid customer group: 40 60

""" 
#
#--------------------------------------------------------------------#



#-----Students' Solution---------------------------------------------#
#
#  Complete the task by filling in the template below.

#import MySQLdb
from  mysql.connector import *
import random
import os
from pyh import *

db = connect(unix_socket = "/opt/lampp/var/mysql/mysql.sock" , host ="localhost", user = "root", passwd = "", db = "movie_survey")
cursor = db.cursor(buffered=True)

def fetch_total_count():
	cursor.execute("SELECT count(*) FROM customers ")
	return cursor.fetchall()[0][0]


def fetch_data(category, display_count):

	# Prepare SQL query to Fetch records from the database.
	sql = ''

	if category.find("-") != -1:				
		age = category.split("-")
		if age[0].isdigit() and age[1].isdigit():
			sql = " SELECT favorite_actors.actor, COUNT( favorite_actors.actor ) AS num FROM customers, favorite_actors \
	 				WHERE customers.customerID = favorite_actors.customerID AND age BETWEEN %s AND %s  \
	 				GROUP BY favorite_actors.actor  \
	 				order by num DESC limit %d " %(age[0], age[1], display_count)
	 	else:
	 		print "Error: Invalid customer group: %s" %(category)
	elif category.lower() == "male" or category.lower() == "female":			
		sql = " SELECT favorite_actors.actor, COUNT( favorite_actors.actor ) AS num FROM customers, favorite_actors \
	 				WHERE customers.customerID = favorite_actors.customerID AND  gender = '%s' \
	 				GROUP BY favorite_actors.actor  \
	 				order by num DESC limit %d " %(category, display_count)
	elif category.lower() == "all":
		sql = " SELECT favorite_actors.actor, COUNT( favorite_actors.actor ) AS num FROM customers, favorite_actors \
	 				WHERE customers.customerID = favorite_actors.customerID  \
	 				GROUP BY favorite_actors.actor  \
	 				order by num DESC limit %d " %(display_count)
	else:
		print "Error: Invalid customer group: %s" %(category)


	try:
		# Execute the SQL command
		cursor.execute(sql)
		# Fetch all the rows in a list of lists.
		results = cursor.fetchall()		
	except:
		print "Error: unable to fecth data"
	
	return results

def calculate_size(popularity_count):
	if popularity_count < 10:
		return "font-size:14px;"
	elif popularity_count >= 10 and  popularity_count < 20:
		return "font-size:16px;"
	elif popularity_count >= 20 and popularity_count < 50:
		return "font-size:20px;"
	elif popularity_count >=50 and popularity_count < 100:
		return "font-size:26px;"
	elif popularity_count >= 100 and popularity_count < 200:
		return "font-size: 32px;"
	elif popularity_count >= 200 and popularity_count < 300:
		return "font-size: 38px;"
	elif popularity_count >= 300 and popularity_count < 400:
		return "font-size: 44px;"
	elif popularity_count >= 400 and popularity_count < 500:
		return "font-size: 50px;"
	else:
		return "font-size: 60px;"


def generate_html(category, display_count, page_name, prev, next):
	file_name = page_name + "_" + category + ".html"
	#create a file
	target = open (file_name, 'w+')

	# Generating HTML content 
	page = PyH('Popular Actors')
	
	# Header Content
	header = page << div(id='header', style='text-align:center;border-bottom: 2px solid;')
	header << h2( "Top %d Most Popular Actors" %(display_count))
	header << h3( "Customer Group: %s" %(category))
	header << h3( "Number of customers: %s" %(fetch_total_count()))

	# Main Content
	content = page << div(id='content', style="margin:20px;text-align:center")

	records = fetch_data(category, display_count)

	for row in records:
		sub_content = content << span(style="color:#%6x; margin: 5px;" % random.randint(0,0xFFFFFF))		 
		sub_content << span(row[0], style=calculate_size(row[1]))
		sub_content << span("(%s)" %(row[1]), style="font-size:7px;")
	
	# Footer Content 
	footer = page << div(id='footer', style='border-top: 2px solid; padding: 20px;')
	if prev != 'nil':
		footer << a("Previous page", href="%s/%s_%s.html" %(os.getcwd(), page_name, prev))
	if next != 'nil':
		footer << a("Next page", href="%s/%s_%s.html" %(os.getcwd(), page_name, next), style="float:right;")


	target.write(page.render())
	

def show_popularity(category_list, display_count, page_name):
	try:
		categories = [[category_list[i],category_list[i+1],category_list[i+2]] for i in range(len(category_list)-2)]
		categories.insert(0,['nil',category_list[0],category_list[1]])
		categories.append([category_list[-2],category_list[-1],'nil'])
	except:
		categories = [('nil', category_list[0], 'nil')]
	for category in categories:			
		generate_html(category[1], display_count, page_name, category[0], category[2])


#--------------------------------------------------------------------#



#-----Automatic Testing----------------------------------------------#
#
#  The following code will automatically run the unit tests
#  when this program is "run".  Do not change anything in this
#  section.  If you want to prevent the tests from running, comment
#  out the code below, but ensure that the code is uncommented when
#  you submit your program.
#
if __name__ == "__main__":
     from doctest import testmod
     testmod(verbose=True)   
#
#--------------------------------------------------------------------#



	
