


""" declares the recrsive function..."""

def rec_func(each_data):       
    for i in each_data:
        if(isinstance(i,list)):
            rec_func(i)
        else:
            print(i)

""" end of the function.."""
