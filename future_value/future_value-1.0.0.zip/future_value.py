

def future_value(value_1, rate_1, n_1):
    fut_value = value_1 * ((1 + rate_1) ** n_1)
    return(fut_value)

def future_value_s(value_2, rate_2, n_2):
    futu_value = (value_2 * (rate_2)) * n_2 + value_2
    return(futu_value)
    
#def init():
   # global value, rate, n
value = input("Type the value, the rate and the number of times. Value: ")
rate = input("Rate: The rate must be typed like '10% = 0.10': ")
n = input("Time: ")
type_j = input("What's the type of taxes? Simple or Compost: ")

if type_j == 'simple':
    print(future_value_s(float(value), float(rate), float(n)))
elif type_j == 'compost':
    print(future_value(float(value), float(rate), float(n)))
else:
    print("This is not a type of tax...")
