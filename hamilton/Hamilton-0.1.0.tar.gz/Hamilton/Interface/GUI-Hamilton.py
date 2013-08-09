# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 00:38:24 2013

@author: Senne Van Baelen
         Koen Weverbergh
"""


"""
This interface consist of a main interface where the system can be defined and 
calculated. Through the main interface (after calculation) it is possible to go to two
subinterfaces; the 'simulate and visualize' and the 'control' interface.


Definitions:
    - makeform: create a frame with entry widgets for defining the system (inputs)
    - makeform_plotXY: create frame with entry widgets (drop-down box), for plotting 
      Y as a function of X (drop down for X and Y value)
    - time_ode: create a frame where an end time (for solving the ode) can be
      filled in

Classes:
    - Quitter: Is a class to create a Quit-button and when this button is pushed 
            a warning message will show up to ask the user to varify if he really
            wants to close the window concerned.
    - Windows: In this class three different methods are defined that each will 
            produce an an interface window. 
            There is the main window that will show up when the program is started 
            where the system must be defined, when the differential equations are 
            calculated you can eather open the 'simulate and visualise' interface or 
            the control interface. 
            In the simulate and visualise interface the user will be given different
            possibilities to make charts of the earlier defined system. This part also
            provides the numerical solutions of the system (in a new window).
            In the control interface the user will be able to control the system. 
            This part provides entry widgets for the necessary inputs of the
            LQR-method. Thought this interface, the user can control the 
            defined system. 

"""


# Starting the interface

from Tkinter import Tk, Text, Entry,END, Listbox, BOTH, StringVar, BOTTOM, TOP, X,Y, \
Frame, LEFT, RIGHT, YES,INSERT, END, Checkbutton,IntVar,N,E,S,W,NE,NW,SE,OptionMenu 
#tk is used to create a root window, frame is for widgets
from ttk import Button, Label, Scrollbar
from tkMessageBox import askokcancel
import Hamilton
from Hamilton import Solve_Hamilton,SimulateAndVisualize_Hamilton,Control_Hamilton

"""
First defined are the different fields used when constructing an interface
There are two kinds of fields: 
    - One is to label different areas where a certain value must be given by the user
    - And the second ones are the empty spaces for these values to be later filled 
    in by the user
"""
# These are the used labels so that the user knows what the system needs to be defined

field_labels_calculate = 'Degrees of freedom (DOF)', 'Kinetic Energy',\
 'Potential Energy' , 'Dissipation Energy','Parameters (also the ones for dissipation)',\
 'Value Of Parameters','Initial Values(dof1,Pdof1,dof2,Pdof2,...)',\
 'External Forces (values Fdof0,Fdof1,etc.)'
Default_val_calculate= '','','','','','','',''

field_labels_control1 = 'Initial Values (dof0,Pdof0,Fdof0,dof1,..)',\
'Workpoint for linearization (dof0,Pdof0,dof1,Pdof1,...)'
field_labels_control2='Q-Martrix (e.g. [rxow0],[row1],[row2],..)','R-Matrix',\
'Time Steps (T0,Tend,number of elements between T0 & Tend)',\
'Reference Functions (REFdof0,REFdof1,etc..)'

Default_val_control1= '',''
Default_val_control2= '','','',''
    
"""
The next function is to create a standard input field (label - input field)
This window will be made in the main window ('root') of the program
The organisation of the different labels and fields will be defined here by the
use of 'pack' which will position certain features to the left or the right
 
"""

def makeform(root, field_labels,Default_val):
    # Creating the main window where the next features are placed in (root is the parent)
    # Creating internal windows that will be packed on the left and right side
    form = Frame(root)                                   
    left = Frame(form)                     
    rite = Frame(form)             # Basis to place a feature at the right side
    form.pack(fill=X)                       
    left.pack(side=LEFT) # Packing (placing) the frame to the LEFT-side of the frame
    rite.pack(expand=YES, fill=X)
    
    variables = []
    
    # Linking the predefined labels to the predefined values as field[0] and field [1]
    # Defining the dimensions of the label-areas
    # Positioning and defining the height space between lbl and another feature (pady)
    # TOP= placing the feature below the previous one at the top
    
    for field in zip(field_labels,Default_val):     
        lbl = Label(left, width=50, text=field[0])  
        area = Entry(rite)                          # Defining the area as an entry 
        lbl.pack(side=TOP, pady=4)                  
        area.pack(side=TOP, fill=X)                 
        var = StringVar()                  # Creating a variable of the type Stringvar
        area.config(textvariable=var)      # Link field to var
        var.set('%s'% field[1])            # Setting the vars in area to Default_val
        variables.append(var)                       
    return variables


"""
This next definition is a function called upon when creating the interface for the 
output of the XY-graphic. It uses the same basics as before with some extra features 
added, for example the drop-down box (for the X and Y value.)

"""
def makeform_plotXY(root):
    #read and write data from txt files, used as options for drop down
    import pickle
    with open("Degrees Of Freedom.txt") as inf:
        dofs = pickle.load(inf)
    with open("Velocities.txt") as inf:
        velocity = pickle.load(inf)    
    with open("Momenta.txt") as inf:
        imp = pickle.load(inf)   
    with open("System Forces.txt") as inf:
        impdot = pickle.load(inf)    
    with open("Parameter Symbols.txt") as inf:
        P = pickle.load(inf)    
    with open("External Forces.txt") as inf:
        ex_force = pickle.load(inf)
        
    optionlist=[]
    optionlist.append('time')
    for i in range(len(dofs)):
        optionlist.append(str(dofs[i]))
    for i in range(len(dofs)):
        optionlist.append(str(velocity[i]))
    for i in range(len(dofs)):
        optionlist.append(str(imp[i]))
    for i in range(len(dofs)):
        optionlist.append(str(impdot[i]))
    for i in range(len(dofs)):
        optionlist.append(str(ex_force[i]))
    for i in range(len(P)):
        optionlist.append(str(P[i]))
            
    #Option for the drop-down box (X & Y):
    OPTIONS = optionlist

    checkXY=IntVar()
    form = Frame(root)                        
    left = Frame(form)
    XX =Frame(form)
    rite = Frame(form)
    YY= Frame(form)
    form.pack(fill=X) 
    # Creating a checkbutton  and placing it to the left, the input here is an IntVar()
    Checkbutton(form,variable=checkXY).pack(side=LEFT,padx=4)
    # 'Anchor=W' : Positioning text at the WEST side (making this as an anchor point)
    left.pack(side=LEFT,anchor=W)
    XX.pack(side=LEFT)
    rite.pack(side=LEFT)
    YY.pack(side=LEFT)

    # Now with these predefined features the window will be visualed with the following
    # The result will be a checkbutton followed with: PLOT 'area' AS A FUNCTION OF 'area'
    # The X and Y values can be chosen from the drop-down box (same for X & Y)
    
    dropdownvar1 = StringVar(XX) 
    dropdownvar1.set(OPTIONS[1])
    dropdownvar2 = StringVar(YY) 
    dropdownvar2.set(OPTIONS[0])
    variables = []
    lbl = Label(left, width=5, text="PLOT")
    Xarea = apply(OptionMenu, (XX, dropdownvar1) + tuple(OPTIONS))
    lbl2 =Label(rite,width=16,text="AS A FUNCTION OF")
    Yarea= apply(OptionMenu, (YY, dropdownvar2) + tuple(OPTIONS))
    lbl.pack(pady=4)
    Xarea.pack()
    lbl2.pack(pady=4)
    Yarea.pack()

    variables.append(dropdownvar1)
    variables.append(dropdownvar2)
    return variables,checkXY
    # This definition will return the 2 filled in variables 
    # and the value of the checkbutton
    
"""
This next definition is almost the same as the definition before. In stead of the 
drop down for the X & Y value, the user can now input expressions (e.g. 'r+h*cos(th)')

"""
def makeform_plotXY_func(root):
    checkXY=IntVar()    
    form = Frame(root)                        
    left = Frame(form)
    XX =Frame(form)
    rite = Frame(form)
    YY= Frame(form)
    form.pack(fill=X) 
    Checkbutton(form,variable=checkXY).pack(side=LEFT,padx=4)    
    left.pack(side=LEFT,anchor=W)
    XX.pack(side=LEFT)
    rite.pack(side=LEFT)
    YY.pack(side=LEFT)
        
    # Now with these predefined features the window will be visualed with the following
    # The result will be a checkbutton followed with: PLOT 'area' AS A FUNCTION OF 'area'
    # Where the two areas can be filled in by the user but will standard be defined 
    # as X-value and Y-value (expressions)
        
    variables = []
    lbl = Label(left, width=5, text="PLOT")
    area = Entry(XX)
    lbl2 =Label(rite,width=16,text="AS A FUNCTION OF")
    area2= Entry(YY)
    lbl.pack(pady=4)
    area.pack()
    lbl2.pack(pady=4)
    area2.pack()
    var = StringVar()
    var2= StringVar()
    area.config(textvariable=var,width=20)    
    var.set("Y-VALUE")
    area2.config(textvariable=var2,width=20)
    var2.set("X-VALUE")
    variables.append(var)
    variables.append(var2)
    return variables,checkXY   
    # This definition will return the 2 filled in variables 
    # and the value of the checkbutton


"""
Create time_ode function: field for end time input for solving the ode
"""

def time_ode(root):
    form=Frame(root)
    left = Frame(form)
    timeframe=Frame(form)
    form.pack(fill=X)
    left.pack(side=LEFT)
    # Placing the timeframe to the left of the frame and make it stuck on the West side
    timeframe.pack(side=LEFT,anchor=W,padx=4)               
    lbl = Label(left, width=10, text="end time [s]:")
    lbl.pack(padx=8)                        # Packing is the way to organise everything
    
    # The different windows are created, now the possibility to insert 
    # a time_end value is created
    
    time_end=IntVar()
    T=Entry(timeframe)
    T.pack(anchor=W)
    T.config(textvariable=time_end,width=5)
    time_end.set("10")
    return time_end


"""
From here on the different classes are defined
    - Quitter: a class to create a Quit-button and when this button is pushed 
               a warning message will show up to ask the user to varify if he really
               wants to close the window concerned.
    
    - Windows: In this class are three different definitions defined that will
            each produce an interface where other possibilities will be given.
            - simulation_window: This is an interface that will make it possible 
                    to get the numerical results and different plots of the system. 
                    This can only be done when the differential equations are already
                    calculated,which is done in the main window (last function in the 
                    window class).
            - control_window: In this window it will be possible to add some control
                    systems to the system you created.
            - main_window: In this last function the system needs to be defined,
                    the user will have to fill in the necesarry fields that define the 
                    system so that the differential equations can then be calculated
                    and so that it is possible to make a simulation and visualisation
                    and add a conrol unit to the system.
"""    

class Quitter(Frame):                          
    def __init__(self, parent=None):           
        Frame.__init__(self, parent)                             # Creating a frame
        self.pack()                                              
        # Creating a widget: button quit that will quit the program
        widget = Button(self, text='Quit', command=self.quit)    
        widget.pack(expand=YES, fill=BOTH, side=LEFT)            
    # Defining an extra definition for the quit button to verify if you want to quit
    def quit(self):                                              
        ans = askokcancel('Verify exit', "Really quit?")
        if ans: Frame.quit(self)


import Tkinter as tk

class Windows():
    
    # First will be checked if the differential equations are already calculated 
    # This is done in the main window
    # If not, the Calculation will be unsuccesfull and it won't be possible 
    # to simulate (given as an error message)
    # If it is succesfull, the window to give the different simulation 
    # posibilities will be displayed    
    
    def simulation_window(self):
        if self.calculatecheck.get()==0:
            tkMessageBox.showerror(title="Calculation Status",message="Calculation\
Unsuccesful!                                      Press 'calculate' first.")
        # Creating the simulation window, this is a toplevel window ("child" window
        # of the main (parent) window)
        else:                                                                                    
            root = tk.Toplevel()                                                                 
            root.title("Dynamic Model (Hamilton's Principle) - Simulation And \
Visualization")
            root.geometry("1100x600+0+45")
            # Creating an information box window:
            text = Text(root,height=16,width=200,bg='LightGreen')          
      
        
            def textnewline(s):  # Defenition to insert a new text 's' on a new line
                text.insert(INSERT, '\n' + s)
            
            # In the next few lines there will be different lines created to insert
            # in the textarea that is already defined
            
            textnewline("*IN ORDER TO CREATE THE X-Y PLOT (X-& Y EXPRESSIONS), \
YOU NEED TO APPLY THE FOLLOWING RULES: ")
            text.tag_add("regel2", "2.0","2.100")
            text.tag_config("regel2",underline=True)
            textnewline("--> use the right strings (check the drop-down to \
see which symbols you can use in your expressions):")
            textnewline("    DOF='dof', MOMEMNTUM='Pdof', VELOCITY='vdof', \
SYSTEM FORCE(derivative of momentum)='Pdofdot' (e.g.'Pthetadot)', \
EXTERNAL FORCES='Fdof',TIME='time'")
            textnewline("--> you can also implement a function for X and for Y\
(e.g. 'r*cos(th)')")        
            textnewline("--> for trigonometric functions (e.g. sin, cos, etc.), \
use the sympy module names \
(http://docs.sympy.org/0.7.1/modules/mpmath/functions/trigonometric.html)")        
            textnewline("")
            textnewline("*notice that you can't input values or changes when there \
are still windows running from your previous simulation and plot")        
            text.pack()
            
            # After the information-textbox of the simulation interface is constucted,
            # the checkbuttons are created
            # Each checkbutton will give a certain possibility 
            # (the ability of each checkbutton is given in green)
            
            check=[]
            for i in range(6):
                check.append(IntVar())             
            Checkbutton(root, text='Give the differential equations in symbols',\
variable=check[3]).pack(anchor=W,padx=4)
            Checkbutton(root,text='Give the numeric values of the dofs & momenta \
at every timestep (NEW WINDOW)',variable=check[4]).pack(anchor=W,padx=4)
            Checkbutton(root,text='Give the numeric values of the velocities and \
resulting system forces(Pdofdot) at every timestep (NEW WINDOW)',\
variable=check[5]).pack(anchor=W,padx=4)      
            # Inserting an information box:           
            text2=Text(root,height=1,width=200,borderwidth=10,background='grey70')
            text2.insert(INSERT,"PLOT FUNCTIONS:")
            text2.pack()
            # Adding some more checkbuttons:
            Checkbutton(root, text='Plot dofs & momenta as function of the time',\
variable=check[0]).pack(anchor=W,padx=4)
            Checkbutton(root, text='Plot velocities as function of the time',\
variable=check[1]).pack(anchor=W,padx=4)
            Checkbutton(root, text='Plot resulting forces in the system as \
function of the time',variable=check[2]).pack(anchor=W,padx=4)
            # Creating a Quit Button by the use of the Quitter class (right side)            
            Quitter(root).pack(side=RIGHT)
            # Creating a frame widget with the use of the makeform definition where 
            # different variables can be given to different labels
            makeform_plotXY_returnvalue=makeform_plotXY(root) 
            makeform_plotXY_func_returnvalue=makeform_plotXY_func(root)
            checkXY=makeform_plotXY_returnvalue[1]
            checkXY_func=makeform_plotXY_func_returnvalue[1]
            vars_simXY=makeform_plotXY_returnvalue[0]
            vars_simXY_func=makeform_plotXY_func_returnvalue[0]
            calculatecheck=self.calculatecheck
            # Finally creating a button to make it possible to simmulate the things 
            # where you checked the button of
            # This button makes an action that refers to the __init__ definition 
            # of SimulateAndVisualise with the needed inputs
            Button(root,text='Simulate & Plot',
                       command=(lambda : SimulateAndVisualize_Hamilton(text,\
                       root,vars_simXY,vars_simXY_func,check,checkXY,checkXY_func, \
                       calculatecheck))).pack(side=LEFT)
                

    
    def control_window(self):
        
        # First will be checked if the differential equations are already calculated
        # If not, the Calculation will be unsuccesfull and it won't be possible to simulate
        # If it is succesfull, the window to give the different control 
        # posibilities will be displayed    
        
        if self.calculatecheck.get()==0:
            tkMessageBox.showerror(title="Calculation Status",message="Calculation\
Unsuccesful! \nPress 'calculate' first.")
        else:
            # Creating the simulation window, this is a toplevel window ("child" window
            # of the main (parent) window)
            root = tk.Toplevel()  
            root.title("Dynamic Model (Hamilton's Principle) - Control")
            root.geometry("1150x650+0+45")
            
            def textnewline(s): # Defenition to insert a new text 's' on a new line
                text.insert(INSERT, '\n' + s)
                         
            # In the next few lines there will be different lines created to insert
            # in the textarea that is already defined
   
            text = Text(root,height=20,width=200,bg='LightGreen')
            text.insert(INSERT,"CONTROL PART")
            textnewline("")
            textnewline("*initial values in ODE: WATCH OUT FOR ERRORS WHEN \
DIVIDING BY ZERO")
            # Creating a tag on a part of the text to make different actions on
            text.tag_add("regel2", "3.23","3.100")
            text.tag_add("2regel3", "3.00","3.100")
            # Applying actions to the predefined tags
            text.tag_config("2regel3",underline=True) 
            text.tag_config("regel2",background="LightSkyBlue")    
            textnewline("--> program cannot solve the differential equation")
            textnewline("")
            textnewline("*when you add the I-action:")
            textnewline("--> don't change the workpoints for linearization \
(don't add extra values), because the I-part is already linear")
            textnewline("--> adjust number of initial values, Q-matrix and R-matrix \
(extend these dimensions with 'number of dofs')")

            text.tag_add("regel6", "6.00","6.200")
            text.tag_config("regel6",underline=True)
            text.pack()
            
            
            check=[]
            for i in range(2):
                check.append(IntVar())
            
            # Creating a frame widget with the use of the makeform definition where 
            # different variables can be given to different labels
            
            vars_control1= makeform(root, field_labels_control1, Default_val_control1)
            # makeform_linearization_returnvalue=makeform_linearization(root)
            
            # Creating a second information box
            
            text2=Text(root,height=1,width=200,borderwidth=5,background='grey70')
            text2.insert(INSERT,"LQR-CONTROL:")
            text2.pack()
            
            # Checkbutton to show K&E matrix from LQR
            
            ch=Checkbutton(root, text='Show K & E matrix from LQR',variable=check[1],\
            bg='grey92')
            ch.select() # Sets the value of the button to an on-value
            ch.pack(anchor=W,padx=4)
            
            # Creating a second window with predefined values
            
            vars_control2= makeform(root, field_labels_control2,Default_val_control2)
            # vars_workpoint=makeform_linearization_returnvalue[0]
            # check_linearization=makeform_linearization_returnvalue[1]
            time_ode_end=IntVar()
            time_ode_end.set("1") 
            
            # Creating button to add the I-control
            
            Checkbutton(root, text='add I-CONTROL to the system (CHANGE Q-& R-MATRIX \
& ADD INITIAL VALUES)',bg='grey92',variable=check[0]).pack(anchor=W,padx=4)
            # Checkbutton(root, text='plot velocity as function of the time',variable=\
            # check[1]).pack()
            # Checkbutton(root, text='plot force as function of the time',\
            # variable=check[2]).pack()
            # Checkbutton(root, text='plot X as a function of Y',variable=check[3]).pack()
            Quitter(root).pack(side=RIGHT)   
            
            Button(root, text='CONTROL', 
                   command=(lambda : Control_Hamilton(text,root,vars_control1,\
                   vars_control2,check))).pack(side=LEFT)
                   
    def buttoncalculateClick(self, event):
            self.calculatecheck.set("1") # Confirms that the calculations are done.
            
    def main(self):
        root=Tk()   
        root.geometry("1500x900+0+0")
        
        # Creating an information box
        
        text = Text(root,height=20,width=200,bg='LightSkyBlue')
        
        def textnewline(s): # Defenition to insert a new text 's' on a new line
            text.insert(INSERT, '\n' + s)
            
        # Creating the information box for the main window
            
        text.insert(INSERT,"*for velocities in the energy & dissipation input: \
use 'vDOF'(e.g. 'vtheta' or 'vr')")   
        textnewline("")
        text.tag_add("regel1", "1.0","1.96")
        text.tag_config("regel1",underline=True)
        textnewline("*initial values in ODE: WATCH OUT FOR ERRORS WHEN DIVIDING BY ZERO")
        text.tag_add("regel3", "3.23","3.100")
        text.tag_add("2regel3", "3.00","3.100")
        text.tag_config("2regel3",underline=True)
        text.tag_config("regel3",background="LightGreen")    
        textnewline("--> program cannot solve the differential equation")
        textnewline("")
        textnewline("*MAKE SURE TO 'CALCULATE' YOUR SYSTEM FIRST")
        textnewline("--> wait until message 'Calculation Successful' is shown")

        text.tag_add("regel6", "6.00","6.50")
        text.tag_config("regel6",background="LightGreen",underline=True)
        text.pack()
        
        root.title("Dynamic model (Hamilton's Principle) - Define System")
        # Creating a window with the use of makeform
        vars_cal=makeform(root, field_labels_calculate,Default_val_calculate)   
        # Getting the end time by the use of the time_ode definition
        time_ode_end=time_ode(root)                                             

        frame1=Frame(root)
        # ipady= adding internal vertical padding
        frame1.pack(side=TOP,anchor=W,pady=15,ipady=15)
        
        # Creating a Calculate button to calculate the differntial equations of the system
        
        self.button1=Button(frame1, text='Calculate', 
                 command=(lambda : Solve_Hamilton(vars_cal,text,root,time_ode_end)))
        self.button1.pack(side=LEFT)        
        # Binding the button to also another action (= predefined definition)
        self.button1.bind("<Button-1>", self.buttoncalculateClick)              
    
        self.calculatecheck=IntVar()
        
        # Creating a second frame inside the main root 
        
        frame2=Frame(root)
        frame2.pack(side=TOP,anchor=W)
        
        # Buttons to make it possible to call upon the simulate and control interfaces
        
        b1=tk.Button(frame2, text="Simulate & Visualize", 
                             command=self.simulation_window)
        b1.pack(side="left") 
        b2=tk.Button(frame2, text="CONTROL", 
                                command=self.control_window)
        b2.pack(side="left") 
        
        Quitter(root).pack(side=TOP,anchor=E)
        
        # Keep on looping the root so that every aspect of the interface is checked 
        # on changes and so that the program can act upon these changes
        
        root.mainloop()
         

if __name__ == '__main__':
    win=Windows()  
    win.main()