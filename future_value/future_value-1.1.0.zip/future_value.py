#Get the future value of an compost tax
def future_value(value_1, rate_1, time_1):
    fut_value = value_1 * ((1 + rate_1) ** time_1)
    return(fut_value)
#Get the future value of an simple tax
def future_value_s(value_2, rate_2, time_2):
    futu_value = ((value_2 * (rate_2)) * time_2) + value_2
    return(futu_value)

#Get the present value taken the future one
def present_value(f_value, p_rate, p_time):
    pres_val = f_value / ((1 + p_rate) ** p_time)
    return(pres_val)

#def init():
   # global value, rate, n
value = input("Type the value, the rate and the number of times. Value: ")
rate = input("Rate: The rate must be typed like '10% = 0.10': ")
n_times = input("Time: ")
type_t = input("What's the type of taxes? Simple, Compost or Present Value: ")

if type_t == 'simple':
    print(future_value_s(float(value), float(rate), float(n_times)))
elif type_t == 'compost':
    print(future_value(float(value), float(rate), float(n_times)))
elif type_t == 'present value':
    print(present_value(float(value), float(rate), float(n_times)))
else:
    print("This is not a type of tax...")
