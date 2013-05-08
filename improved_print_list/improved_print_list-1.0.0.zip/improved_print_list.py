'''this is my first python program in pypi
   the program is designed to print the list
'''
def print_list(the_list, indent = False, level = 0, mark = '\t'):
        '''
        there are fore parameters, the_list is the list to print
        indent is to chech if you need print the indent before the nested list, False by default
        level represent the current level of the to-print list, 0 by default
        mark: you could set the mark before nest list, the tab mark by default
        '''
        for each_item in the_list:
                if isinstance(each_item, list):
                        print_list(each_item, indent, level+1, mark)
                else:
                        if indent:
                                for num in range(level):
                                        print mark,
                        print(each_item)
