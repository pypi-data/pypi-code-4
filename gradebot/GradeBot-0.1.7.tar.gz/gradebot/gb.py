# Json is a module that can be used to save and load Python dictionaries from a txt file. Decimal is used to specify rounding and decimal places for GPA.
import json
from decimal import Decimal

# Initialize handles the first operations when opening up the program. It prints a greeting and prompts for a new or loaded profile and goes to the corresponding class.
class Initialize(object):
	print "Welcome to Grade Bot"

	def new_or_existing(self):
		init_action = raw_input("If you are a new user, type \"new\". Otherwise, press ENTER: ")
		if init_action.lower() == "new":
			User().create_new()
		elif init_action.lower() == "":
			name = raw_input("Please enter your name: ")
			User().load_user(name)
		else:
			print "Sorry, I did not catch that"
			Initialize().new_or_existing()
			
class MainMenu(object):
	def __init__(self, username):
		self.username = username
		
	def menu(self, username):
		print "\nWelcome back %s!" % self.username
		print "What would you like to do?"
		print """
		1. Add new course
		2. Delete course
		3. Rename course
		
		4. Update specific grade entry
		5. Update all grades
		
		6. Edit unit count
		
		7. What do I need on the Final to get a __?
		
		8. Display grade report
		
		9. Calculate GPA
		
		10. Exit
		"""
		MainMenu(username).menu_selection()
		
	def menu_selection(self):
		menu_option = raw_input("Type the number of your selection: ")
		
		if "10" in menu_option:
			exit()
		elif "1" in menu_option:
			EditCourses().add_course()
			print "...Navigating to Main Menu..."
			MainMenu(username).menu(username)
		elif "2" in menu_option:
			EditCourses().del_course()
		elif "3" in menu_option:
			EditCourses().rename_course()
		elif "4" in menu_option:
			UpdateGrades().update_grade()
		elif "5" in menu_option:
			UpdateGrades().update_all_grades()
		elif "6" in menu_option:
			EditCourses().edit_units()
		elif "7" in menu_option:
			Required().required()
		# The prompt to return to the Main Menu is put here because Display().display_grades() is used for other functions where returning to the Main Menu 			is not needed.
		elif "8" in menu_option:
			Display().display_grades()
			raw_input("\nPress ENTER to return to the Main Menu: ")
			MainMenu(username).menu(username)
		elif "9" in menu_option:
			GPA().gpa()
		else:
			print "Sorry, I did not catch that"
			MainMenu(username).menu_selection()

class EditCourses(object):	
	def save(self):
		with open(username + ".txt", "a") as save_file:
			save_file.truncate()
			# user_data is the dictionary storing all student info which is written to the save_file using the json module.
			json.dump(user_data, save_file)
				
	def add_course(self):
		course = raw_input("Type the name of your course: ")
		
		while True:
			try:
				units = int(raw_input("How many units is this course? "))
				user_data[course + "_units"] = units
				break

			except ValueError:
				print "Please enter a valid number of units."
				
		while True:
			try:
				grade = int(raw_input("What is your percentage grade in this course? (Omit the '%'): "))
				user_data[course + "_grade"] = grade
				break

			except ValueError:
				print "Please enter a valid percentage."
			

	def del_course(self):
		Display().display_grades()
		course = raw_input("Type the name of the course you would like to remove: ")
		
		del user_data[course + "_units"]
		del user_data[course + "_grade"]
		
		EditCourses().save()
		
		print "...Navigating to Main Menu..."
		MainMenu(username).menu(username)
			
	def rename_course(self):
		Display().display_grades()
		course = raw_input("Type the name of the course you would like to rename: ")
		course_edit = raw_input("What would you like to change the course name to? ")
		
		user_data[course_edit + "_units"] = user_data.pop(course + "_units")
		user_data[course_edit + "_grade"] = user_data.pop(course + "_grade")
		
		EditCourses().save()
		
		print "...Navigating to Main Menu..."
		MainMenu(username).menu(username)

	def edit_units(self):
		Display().display_grades()
		course = raw_input("Type the name of the course you would like to edit the units on: ")
		units = raw_input("How many units is this course? ")
		
		user_data[course + "_units"] = units
		
		print "...Navigating to Main Menu..."
		MainMenu(username).menu(username)
		
class User(EditCourses):
	# user_data and username are made global variables because the savefile is the username and the user_data is constantly updated.
	def create_new(self):
		global user_data
		user_data = {}
		
		global username
		username = raw_input("Please enter your name: ")
		user_data["name"] = username

		while True:
			try:
				number_of_courses = int(raw_input("Please enter the number of courses you are currently taking: "))
				break

			except ValueError:
				print "Please enter a valid number of courses."
		
		for course_num in range(number_of_courses):
			User().add_course()
				
		EditCourses().save()
		
		print "...Navigating Title Screen..."
		Initialize().new_or_existing()
		
	def load_user(self, name):
		while True:
			try:
				with open(name + ".txt") as file_name:
					global user_data
					user_data = json.load(file_name)
				break

			except IOError:
				print "User \"%s\" does not exist." % name

				print "...Navigating Title Screen..."
				Initialize().new_or_existing()
			
			
		# This part could be made more efficient. The "name" in user_data and the name entered when loading will always be the exact same. A "name" 				key is unecessary.
		global username
		username = user_data["name"]
			
		MainMenu(username).menu(username)
			
class UpdateGrades(object):
	def update_grade(self):
		Display().display_grades()
		course = raw_input("What course would you like to update? ")
		course_grade = raw_input("What is your current grade percentage for this course? (Omit the '%'): ")
		
		user_data[course + "_grade"] = int(course_grade)
		
		EditCourses().save()
		
		print "...Navigating to Main Menu..."
		MainMenu(username).menu(username)
		
	def update_all_grades(self):
		for course in user_data:
			if "_grade" in course:
				course_grade = raw_input("Please enter your current grade percentage in " + course[:course.find("_")] + " (Omit the '%'): ")
				user_data[course] = int(course_grade)
				
				EditCourses().save()
				
		print "...Navigating to Main Menu..."
		MainMenu(username).menu(username)

# Need to find a way to combine letter_grade and course_gpa since the percentage parameters are the same.		
class Calculate(object):
	def __init__(self, percentage):
		self.percentage = percentage
	
	def letter_grade(self, percentage):
		if percentage >= 97:
			return "A+"
		elif percentage >= 93 and percentage < 97:
			return "A"
		elif percentage >= 90 and percentage < 93:
			return "A-"
		elif percentage >= 87 and percentage < 90:
			return "B+"
		elif percentage >= 83 and percentage < 87:
			return "B"
		elif percentage >= 80 and percentage < 83:
			return "B-"
		elif percentage >= 77 and percentage < 80:
			return "C+"
		elif percentage >= 73 and percentage < 77:
			return "C"
		elif percentage >= 70 and percentage < 73:
			return "C-"
		elif percentage >= 67 and percentage < 70:
			return "D+"
		elif percentage >= 65 and percentage < 66:
			return "D"
		elif percentage < 66:
			return "F"
		
	def course_gpa(self, percentage):
		if percentage >= 97:
			return 4.00
		elif percentage >= 93 and percentage < 97:
			return 4.00
		elif percentage >= 90 and percentage < 93:
			return 3.70
		elif percentage >= 87 and percentage < 90:
			return 3.30
		elif percentage >= 83 and percentage < 87:
			return 3.00
		elif percentage >= 80 and percentage < 83:
			return 2.70
		elif percentage >= 77 and percentage < 80:
			return 2.30
		elif percentage >= 73 and percentage < 77:
			return 2.00
		elif percentage >= 70 and percentage < 73:
			return 1.70
		elif percentage >= 67 and percentage < 70:
			return 1.30
		elif percentage >= 65 and percentage < 66:
			return 1.00
		elif percentage < 66:
			return 0.00

class GPA(object):
	def gpa(self):
		total = 0
		total_units = 0
		for course in user_data:
			if "_grade" in course:
				total += int(Calculate(user_data[course]).course_gpa(user_data[course])) * int(user_data[course[:course.find('_')] + "_units"])
				
				total_units += int(user_data[course[:course.find('_')] + "_units"])
		
		# Decimal utilizes the numbers as decimals rather than integers.
		gpa = (Decimal(total) / Decimal(total_units * 4)) * 4

		# %.2f specifies 2 floating points.
		print "\nYour GPA is %.2f" % gpa
		
		raw_input("\nPress ENTER to return to the Main Menu: ")
		MainMenu(username).menu(username)
		
class Display(object):
	def display_grades(self):
		grade_report = [["Name", "Grade", "Letter Grade", "Units"], ["---", "-----", "------------", "-----"]]
		
		print "\n" + username + "\n"
		
		# Looks for any key with "_grade" in it to find all classes (only once) and then it utilizes the name before the "_" to retrieve the other info.
		for course in user_data:
			course_report = []
			if "_grade" in course:
				course_report.append(str(course[:course.find('_')]))
				course_report.append(str(user_data[course]) + "%")
				course_report.append(Calculate(user_data[course]).letter_grade(user_data[course]))
				course_report.append(str(user_data[course[:course.find('_')] + "_units"]))
				
				grade_report.append(course_report)
				
		# Used for formatting purposes.
		for row in grade_report:
			print " / ".join(row)
			
class Required(object):
	def required(self):
		grade = raw_input("What is your current grade percentage? (Omit the '%'): ")
		final_percent = raw_input("What percent of your grade is the final? (Omit the '%'): ")
		goal_grade = raw_input("What letter grade are you aiming for? ")
		
		if goal_grade == "A+":
			goal_percent = 97
		if goal_grade == "A":
			goal_percent = 93
		if goal_grade == "A-":
			goal_percent = 90
		if goal_grade == "B+":
			goal_percent = 87
		if goal_grade == "B":
			goal_percent = 83
		if goal_grade == "B-":
			goal_percent = 80
		if goal_grade == "C+":
			goal_percent = 77
		if goal_grade == "C":
			goal_percent = 73
		if goal_grade == "C-":
			goal_percent = 70
		if goal_grade == "D+":
			goal_percent = 67
		if goal_grade == "D":
			goal_percent = 65
		if goal_grade == "F":
			goal_percent = 0
			
		required_percent = (Decimal(goal_percent) - (Decimal(grade) * ((100 - Decimal(final_percent)) / 100))) / (Decimal(final_percent) / 100)
		
		print "You need a %.2f percent on the final to get a(n) %s" % (required_percent, goal_grade)
		
		raw_input("\nPress ENTER to return to the Main Menu: ")
		MainMenu(username).menu(username)
