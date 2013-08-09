# -*- coding: utf-8 -*-
"""
Created on Thu May  9 16:05:25 2013

Crosslides Exercise
PD-controller

This is the graphical user interface (GUI) for the crosslides exercise, with PID controller (LQR-method)

"""

# starting to interface

from Tkinter import Tk, Text, Entry,END, Listbox, BOTH, StringVar, BOTTOM, TOP, X,Y, Frame, LEFT, RIGHT, YES,INSERT, END, Checkbutton,IntVar,N,E,S,W,NE,NW,SE,OptionMenu #tk is used to create a root window, frame is for widgets
from ttk import Button, Label, Scrollbar
from tkMessageBox import askokcancel
import Hamilton
from Hamilton import Solve_Hamilton,SimulateAndVisualize_Hamilton,Control_Hamilton
import os
import tkMessageBox


field_labels_calculate = 'Degrees of freedom (DOF)', 'Kinetic Energy', 'Potential Energy' , 'Dissipation Energy','Parameters (also the ones for dissipation)','Value Of Parameters','Initial Values(dof1,Pdof1,dof2,Pdof2,...)','External Forces (values Fdof0,Fdof1,etc.)'
Default_val_calculate= 'x,y', '0.5*(m+M)*vy**2+0.5*m*vx**2', '0' , '0,0','m,M','25,80','0,0,0,0','0,0'

field_labels_control1 = 'Initial Values (dof0,Pdof0,Fdof0,dof1,..)','Workpoint for linearization (dof0,Pdof0,dof1,Pdof1,...)'
field_labels_control2='Q-Martrix (e.g. [rxow0],[row1],[row2],..)','R-Matrix','Time Steps (T0,Tend,number of elements between T0 & Tend)','Reference Functions (REFdof0,REFdof1,etc..)'

Default_val_control1= '0,0,0,0,0,0','0'
Default_val_control2='[1e8,0,0,0],[0,1e1,0,0],[0,0,1e8,0],[0,0,0,1e1]','[1e-6,0,0,0],[0,1e-6,0,0],[0,0,1e-6,0], [0,0,0,1e-6]','0,1,2000','0.1+0.5*(sign(t-0.5)+1)*t,0.5*(sign(t-0.2)+1)*t'
# WITH I ACTION:
#Default_val_control1='0,0,0,0,0,0,0,0','0'
#Default_val_control2='[1e8,0,0,0,0,0],[0,1e1,0,0,0,0],[0,0,1e8,0,0,0], [0,0,0,1e1,0,0],[0,0,0,0,1e13,0], [0,0,0,0,0,1e13]','[1e-6,0,0,0,0,0],[0,1e-6,0,0,0,0],[0,0,1e-6,0,0,0], [0,0,0,1e-6,0,0],[0,0,0,0,1e-6,0], [0,0,0,0,0,1e-6]','0,1,2000','0.1+0.5*(sign(t-0.5)+1)*t,0.5*(sign(t-0.2)+1)*t'  

    

def makeform(root, field_labels,Default_val):
    form = Frame(root)                        
    left = Frame(form)
    rite = Frame(form)
    form.pack(fill=X) 
    left.pack(side=LEFT)
    rite.pack(expand=YES, fill=X)
    
    variables = []
    for field in zip(field_labels,Default_val):
        lbl = Label(left, width=50, text=field[0])
        area = Entry(rite)
        lbl.pack(side=TOP, pady=4)
        area.pack(side=TOP, fill=X)
        var = StringVar()
        area.config(textvariable=var)    # link field to var
        var.set('%s'% field[1])
        variables.append(var)
    return variables
    
def makeform_plotXY(root):
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
            
    OPTIONS = optionlist

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

def time_ode(root):
    form=Frame(root)
    left = Frame(form)
    timeframe=Frame(form)
    form.pack(fill=X)
    left.pack(side=LEFT)
    timeframe.pack(side=LEFT,anchor=W,padx=4)
    lbl = Label(left, width=10, text="end time [s]:")
    lbl.pack(padx=8)
    time_end=IntVar()
    T=Entry(timeframe)
    T.pack(anchor=W)
    T.config(textvariable=time_end,width=5)
    time_end.set("10")
    return time_end
    
class Quitter(Frame):                          
    def __init__(self, parent=None):           
        Frame.__init__(self, parent)     #creating a frame
        self.pack()                                 # pack is a way to organise everything
        widget = Button(self, text='Quit', command=self.quit)  #creating a widget: button quit that will quit the program
        widget.pack(expand=YES, fill=BOTH, side=LEFT)   # by the use of pack we will place it on the right spot
    def quit(self):             #defining the an extra definition for the quit button
        ans = askokcancel('Verify exit', "Really quit?")
        if ans: Frame.quit(self)

import Tkinter as tk

class Windows():
    def simulation_window(self):
        if self.calculatecheck.get()==0:
            tkMessageBox.showerror(title="Calculation Status",message="Calculation Unsuccesful!                                      Press 'calculate' first.")
        else:
            root = tk.Toplevel()
            root.title("Dynamic Model (Hamilton's Principle) - Simulation And Visualization")
            #t.wm_title("Window #%s" % self.counter)
            root.geometry("1100x600+0+45")
            text = Text(root,height=16,width=200,bg='LightGreen')

        
            def textnewline(s):         #start text s on a new line
                text.insert(INSERT, '\n' + s)
            textnewline("*IN ORDER TO CREATE THE X-Y PLOT (X-& Y EXPRESSIONS), YOU NEED TO APPLY THE FOLLOWING RULES: ")
            text.tag_add("regel2", "2.0","2.100")
            text.tag_config("regel2",underline=True)
            textnewline("--> use the right strings (check the drop-down to see which symbols you can use in your expression):")
            textnewline("    DOF='dof', MOMEMNTUM='Pdof', VELOCITY='vdof', SYSTEM FORCE(derivative of momentum)='Pdofdot' (e.g.'Pthetadot)', EXTERNAL FORCES='Fdof',TIME='time'")
            textnewline("--> you can also implement a function for X and for Y (e.g. 'r*cos(th)')")        
            textnewline("--> for trigonometric functions (e.g. sin, cos, etc.), use the sympy module names (http://docs.sympy.org/0.7.1/modules/mpmath/functions/trigonometric.html)")        
            textnewline("")
            textnewline("*notice that you can't input values or changes when there are still windows running from your previous simulation and plot")        
            text.pack()
            
            check=[]
            for i in range(6):
                check.append(IntVar())             
            Checkbutton(root, text='give the differential equations in symbols',variable=check[3]).pack(anchor=W,padx=4)
            Checkbutton(root,text='give the numeric values of the dofs & momenta at every timestep (NEW WINDOW)',variable=check[4]).pack(anchor=W,padx=4)
            Checkbutton(root,text='give the numeric values of the velocities and resulting system forces(Pdofdot) at every timestep (NEW WINDOW)',variable=check[5]).pack(anchor=W,padx=4)      
            text2=Text(root,height=1,width=200,borderwidth=10,background='grey70')
            text2.insert(INSERT,"PLOT FUNCTIONS:")
            text2.pack()
            Checkbutton(root, text='plot dofs & momenta as function of the time',variable=check[0]).pack(anchor=W,padx=4)
            Checkbutton(root, text='plot velocities as function of the time',variable=check[1]).pack(anchor=W,padx=4)
            Checkbutton(root, text='plot resulting forces in the system as function of the time',variable=check[2]).pack(anchor=W,padx=4)
            Quitter(root).pack(side=RIGHT)
            makeform_plotXY_returnvalue=makeform_plotXY(root)
            makeform_plotXY_func_returnvalue=makeform_plotXY_func(root)
            checkXY=makeform_plotXY_returnvalue[1]
            checkXY_func=makeform_plotXY_func_returnvalue[1]
            vars_simXY=makeform_plotXY_returnvalue[0]
            vars_simXY_func=makeform_plotXY_func_returnvalue[0]
            calculatecheck=self.calculatecheck
            Button(root,text='Simulate & Plot',
                       command=(lambda : SimulateAndVisualize_Hamilton(text,root,vars_simXY,vars_simXY_func,check,checkXY,checkXY_func, calculatecheck))).pack(side=LEFT)
    
    def control_window(self):
        if self.calculatecheck.get()==0:
            tkMessageBox.showerror(title="Calculation Status",message="Calculation Unsuccesful!                             Press 'calculate' first.")
        else:
            root = tk.Toplevel()
            root.title("Dynamic Model (Hamilton's Principle) - Control")
            #t.wm_title("Window #%s" % self.counter)
            root.geometry("1150x650+0+45")
            def textnewline(s):         #start text s on a new line
                text.insert(INSERT, '\n' + s)
            text = Text(root,height=20,width=200,bg='LightGreen')
            text.insert(INSERT,"CONTROL PART")
            textnewline("")
            textnewline("*initial values in ODE: WATCH OUT FOR ERRORS WHEN DIVIDING BY ZERO")
            text.tag_add("regel2", "3.23","3.100")
            text.tag_add("2regel3", "3.00","3.100")
            text.tag_config("2regel3",underline=True)
            text.tag_config("regel2",background="LightSkyBlue")    
            textnewline("--> program cannot solve the differential equation")
            textnewline("")
            textnewline("*when you add the I-action:")
            textnewline("--> don't change the workpoints for linearization (don't add extra values), because the I-part is already linear")
            textnewline("--> adjust number of initial values, Q-matrix and R-matrix (extend these dimensions with 'number of dofs')")

            text.tag_add("regel6", "6.00","6.200")
            text.tag_config("regel6",underline=True)
            text.pack()
            check=[]
            for i in range(2):
                check.append(IntVar())
            vars_control1= makeform(root, field_labels_control1, Default_val_control1)
            #makeform_linearization_returnvalue=makeform_linearization(root)
            text2=Text(root,height=1,width=200,borderwidth=5,background='grey70')
            text2.insert(INSERT,"LQR-CONTROL:")
            text2.pack()
            ch=Checkbutton(root, text='Show K & E matrix from LQR',variable=check[1],bg='grey92')
            ch.select()                
            ch.pack(anchor=W,padx=4)
            vars_control2= makeform(root, field_labels_control2,Default_val_control2)
            #vars_workpoint=makeform_linearization_returnvalue[0]
            #check_linearization=makeform_linearization_returnvalue[1]
            time_ode_end=IntVar()
            time_ode_end.set("1") 
            Checkbutton(root, text='add I-CONTROL to the system (CHANGE Q-& R-MATRIX & ADD INITIAL VALUES)',bg='grey92',variable=check[0]).pack(anchor=W,padx=4)
            #Checkbutton(root, text='plot velocity as function of the time',variable=check[1]).pack()
            #Checkbutton(root, text='plot force as function of the time',variable=check[2]).pack()
            #Checkbutton(root, text='plot X as a function of Y',variable=check[3]).pack()
            Quitter(root).pack(side=RIGHT)   
            
            Button(root, text='CONTROL', 
                   command=(lambda : Control_Hamilton(text,root,vars_control1,vars_control2,check))).pack(side=LEFT)

    def buttoncalculateClick(self, event):
            self.calculatecheck.set("1")
            
    def main(self):
        root=Tk()   
        root.geometry("1500x900+0+0")
        text = Text(root,height=20,width=200,bg='LightSkyBlue')
        def textnewline(s):         #start text s on a new line
            text.insert(INSERT, '\n' + s)
        text.insert(INSERT,"*for velocities in the energy & dissipation input: use 'vDOF'(e.g. 'vtheta' or 'vr')")   
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
        textnewline("--> wait until message 'Calculation Succesful' is shown")

        #text.tag_add("regel6", "6.15","6.26")
        text.tag_add("regel6", "6.00","6.50")
        text.tag_config("regel6",background="LightGreen",underline=True)
        text.pack()
        
        root.title("Dynamic model (Hamilton's Principle) - Define System")
        vars_cal=makeform(root, field_labels_calculate,Default_val_calculate)  
        
        time_ode_end=time_ode(root)

        frame1=Frame(root)
        frame1.pack(side=TOP,anchor=W,pady=15,ipady=15)
        
        self.button1=Button(frame1, text='Calculate', 
                 command=(lambda : Solve_Hamilton(vars_cal,text,root,time_ode_end)))
        self.button1.pack(side=LEFT)        
        self.button1.bind("<Button-1>", self.buttoncalculateClick)
    
        self.calculatecheck=IntVar()
  
        frame2=Frame(root)
        frame2.pack(side=TOP,anchor=W)
                
        b1=tk.Button(frame2, text="Simulate & Visualize", 
                             command=self.simulation_window)
        b1.pack(side="left") 
        b2=tk.Button(frame2, text="CONTROL", 
                                command=self.control_window)
        b2.pack(side="left") 
        
        Quitter(root).pack(side=TOP,anchor=E)
        root.mainloop()
         
    

if __name__ == '__main__':
    win=Windows()  
    win.main()
    
 



