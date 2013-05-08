import os
os.chdir("d:\HeadFirstPython\chapter3")

try:
    data=open('sketch.txt')

    for each_line in data:
        try:
            (role,spoken)=each_line.split(':',1)
            print(role,end='')
            print(" said:  ",end='')
            print(spoken,end='')
        except ValueError:
            pass
        
    data.close()
except IOError:
    print("The data file is missing!")
    
