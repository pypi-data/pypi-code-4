# pugnester is used to list all data in a more readable format if necessary.

import pugnest

# The sanitize function cleans data, returning it in a consistent format.

def sanitize(string):
    if ':' in string:
        splitter = ':'
    elif '-' in string:
        splitter = '-'
    else:
        return(string)
    
    (mins, secs) = string.split(splitter)
    return(mins + '.' + secs)

# The Athlete class contains all the data, and inherits list functionality.

class Athlete(list):
    def __init__(self, a_name = 'you', a_dob = None, a_times = []):
        self.name = a_name
        self.dob = a_dob
        self.extend(a_times)
    
    # The top3 method returns the fastest 3 times.
    def top3(self):
        return(str(sorted(set([sanitize(t) for t in self])) [0:3]))

# The get_data function opens a file and processes the data.
# The data is assigned to the Athlete class.

def get_data(filename):
    try:
        with open(filename) as file:
            data = file.readline()
        temploc = data.strip().split(',')
        return(Athlete(temploc.pop(0), temploc.pop(0),temploc))
    except IOError as err:
        print('File error: ' + str(err))
        return(None)
        
# The go_user function asks the user to input the name of the file.
# The functions are called and the file is processed.
# go_user displays the results.
# go_user is recursive, so the user can choose to display another result.

def go_user():
    # The again value repeats the function until the user ends the session.
    again = True
    while again == True:
        user = input('Please input the filename: ')
        user_dat = get_data(user)
        print()
        print('What would you like to display?')
        print()
        what = input("Type 'top' to display your top 3 times, and 'all' to show all. ")
        # Depending on what the user typed, the program will display differently.
        if what.lower() == 'top':
            print()
            print("The top three fastest times for " + user_dat.name + ":")
            print("------")
            print(user_dat.top3())
            print()
        elif what.lower() == 'all':
            print()
            print("The time strings for " + user_dat.name + " are: ")
            print("------")
            pugnest.print_lol(user_dat)
            print()
        else:
            print()
            print("I'm sorry, I didn't understand. Please try again.")
            print()
            go_user()
        # Now go_user asks if you want to try a different file.
        go_again = input("Would you like to try another file? Y/n: ")
        if go_again.lower() == 'y':
            pass
        elif go_again.lower() == 'n':
            print('The program will now close.')
            again = False
        else:
            print("I'm sorry, I didn't understand. The program will now close.")
            print("You can use the 'go_user()' command to try again.")
            again = False


# The program is explained and the function is called!
print()
print('------Pug Athlete------')
print()
print("This program is meant for athletes to organize their data.")
print("It will open a .txt file with the name, birthday and list of stopwatch times.")
print("The text file must be organized like this: Name, Birthday, 1.22, 2.44, 3.55...")
print("Time strings can be formatted using ':', '.', and '-', liks this: 1:22, 2.44, 3-55...")
print("However, commas (',') are used to determine each list item.")
print("Please only use commas to split each list item, not the minutes and seconds.")
print()
print("I haven't made a program that generates the .txt file yet.")
print("Therefore, this program obviously comes with limitations.")
print("For example, if the file cannot be found, the program continues on anyway.")
print("It is, however, my first 'real' program that I wrote myself.")
print("It's based on the Head First Python book, chapter 6.")
print("Enjoy!")
print()
go_user()