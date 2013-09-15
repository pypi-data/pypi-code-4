"""This is test for the exercise of release the file to the pyPI.
   This small function is used to check the element of list
   whether is a pure item or not."""
def ChecktheList(the_list):
    for each_item in the_list:
        if isinstance(each_item, list):
            print("This list is a nested list")
            exit();
    print("This list is a one-level list")
            
           
