a = []
b = []
from frula_nester import print_lol
try:
        data = open("sketch2.txt") #type your .txt file
        for each_line in data:
                try:
                        (role,line_spoken) = each_line.split(":", 1)
                        line_spoken = line_spoken.strip()
                        if role == "A": #change role in your charachter, such as "Susane" 
                                a.append(line_spoken)

                        elif role == "B":
                                b.append(line_spoken)
                except ValueError:
                        pass
        data.close()
except IOError:
        print("The datafile is missing!")

try:
        with open("a_data.txt", "w") as a_file: #change output txt file in your format, such as Susane_data.txt
                print_lol(man, fh=a_file)
        with open("b_data.txt", "w") as b_file: #same here, but other participant
                print_lol(other, fh=b_file)
        
except IOError as err:
        print("File error: " + str(err))

                


        
