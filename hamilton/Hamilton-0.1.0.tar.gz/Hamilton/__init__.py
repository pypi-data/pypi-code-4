# -*- coding: utf-8 -*-
"""

@authors:Koen Weverbergh
         Senne Van Baelen
         
This module is to apply the Hamilton equations to a system 
(Functions of this module are called in the Graphical User Interface (GUI) files)) 

__init__.py: initialization code of the Hamilton Package (__init__.py turns a folder into 
a package, therefore you create a hierarchy in the module, you can import the functions 
of this package in the GUI-file)

This module contains 3 important definitions: 
--> Solve Hamilton: solving the differential equations and saving these results
--> SimulateAndVisualize_Hamilton: simulation and visualization of the system using the
    saved calculation files
--> Control_Hamilton: controlling the system, using the LQR-control method (P(I)D control)

"""

import sympy
from sympy import diff, Symbol, Function, cos, sin, sqrt,atan, solve,Matrix, \
    solve_linear_system,lambdify, DeferredVector, powsimp,floor,simplify,zeros
import numpy as np
from numpy import linspace,array,pi,transpose,dot
import scipy
from scipy.integrate import ode
from scipy import array
import matplotlib
from matplotlib import pylab
from pylab import show, figure, plot,xlabel,ylabel,subplot,title,text,legend
import Tkinter
from Tkinter import Frame, Text, LEFT, RIGHT,TOP,Y
from ttk import Scrollbar
import math
import control
from control import lqr
import tkMessageBox

# Create a partial derivative function:
def partafgeleide(eq,param):
    param_sub= Symbol('param_sub')
    eq1=eq.subs(param,param_sub)
    deq_param_sub = diff(eq1,param_sub)
    deq_param = deq_param_sub.subs(param_sub,param)
    return deq_param
    
# SOLVE DIFFERENTIAL EQUATIONS:
    
"""
Create a function to solve the differential equations:
Parameters of the function (vars_cal,text,root,time_ode_end)
  --> vars_cal= variables for calculation (list of StringVar), length=9
      =[StrigVar0,StringVar1,StringVar2,...,StringVar8]
      StringVar0= Degrees of Freedom
      StringVar1= Kinetic Energy     
      StringVar2= Potential Energy
      StringVar3= Dissipation Energy
      StringVar4= Parameters (Symbols)
      StringVar5= Parameters (Values)
      StringVar6= Initial Values (dof0,momentum0,dof1,momentum1)
      StringVar7= External Forces (values)
      StringVar8= End time for solving ODE's
  --> text = e.g. text widget of an interface
  --> root = master window in the GUI (here main window)
  --> time_ode_end = end time for solving the differential equations
  
  Widgets (e.g. entry widgets, buttons, etc.) are implemented in the GUI-interface.

"""
def Solve_Hamilton(vars_cal,text,root,time_ode_end):
    
    q=vars_cal[0].get().split(',') # Get the degrees of freedom (dofs) of the system
    q_list=[]
    
    for var in zip(q,q):
        exec "%s=Symbol(%s)" % (var[0], 'var[1]') in globals(), locals()
        q_list.append(var[0])
    # Evaluate strings with the exec statement:
    # This statement supports dynamic execution of Python code. It evaluates a string,
    # an open file object, a code object or a tuple.
    # locals(): update and return a dictionary representing the current local symbol table. 
    # Free variables are returned by locals() when it is called in function blocks, 
    # (not in class blocks).
    # globals(): Return a dictionary representing the current global symbol table. 
    # This is always the dictionary of the current module (inside a function or method, 
    # this is the module where it is defined, not the module from which it is called).

    dofs= Matrix(len(q_list),1,q_list) 
    # Creation of Matrix (symbolic), because the types of the elements of the sympy.Matrix 
    # are 'Symbols' (so not strings), therefore they support the 'subs' function 
    # (=substitution).
    
    vq_list=[] # List for appending symbolic velocities
    for var in zip(q,q):
        exec "%s=Symbol(%s)" % (str("v")+var[0], 'str("v")+var[1]') in globals(), locals()
        vq_list.append(str('v')+var[0])   
    # Create velocities of the system
    velocity=Matrix(len(q_list),1,vq_list)
    
    
    params = vars_cal[4].get().split(',') # Split the values of the 4th list element
    # Get the parameters of the system
    p_list=[]
        
    for param in zip(params,params):
        exec "%s=Symbol(%s)" % (param[0], 'param[1]') in globals(), locals()
        p_list.append(param[0])   # List values are strings
    P= Matrix(len(params),1,p_list) 
    

    L_list=[] # List for appending the Lagrangian
    exec "L1=%s-(%s)" % (vars_cal[1].get(),vars_cal[2].get()) in globals(),locals()
    # vars_cal[1]=kinetic energy, vars_cal[2]=Potential energy
    # Create the Lagrangian (=kinetic energy - potential energy)
    L_list.append(L1)
    L=Matrix(1,1,L_list)    
    
    imp=[] # List with momenta of the system (imp comes from impuls)
    impformula=[] # List for later velocity calculation (from momenta)
    # Momentum = partafgeleide(L1,adot) -> momentum - partafgeleide(L1,adot)=0
    impdot=[] # List with derivatives of the impulses (=System forces)
    ex_force=[] # List with external forces of the system
    for i in range(len(dofs)): # len(arg) = length of the argument
        Pa=Symbol('P'+str(dofs[i]))
        impformula.append(Pa-partafgeleide(L1,velocity[i])) 
        # Adding the different formula of the different velocity calculations
        imp.append(Pa) # Adding the different momenta
        Padot=Symbol('P'+str(dofs[i])+'dot')
        impdot.append(Padot)
        F= Symbol('F'+str(dofs[i]))
        ex_force.append(F)
    
    # Get velocities from momenta through solving a system of equations (impformula's)
    s=solve(impformula,vq_list,dict=True) # Using dict=True to return a list   
    speed=s[0]

    
    for i in range(len(dofs)):
        s=speed[velocity[i]]
        L=L.subs(velocity[i],s) 
        # Substitute the velocities with the generated velocities from the impulses
    
    # Calculating Hamiltonian (H=sum(momenta*velocities)-Lagrangian)
    H=0
    for i in range(len(dofs)):
        calc=imp[i]*speed[velocity[i]]
        H=H+calc
        
    H=H-L[0]
        
    Diss=vars_cal[3].get().split(',') # Get the dissipation energy of the system

    Diss_list=[]
    for var in zip(Diss):
        exec "%s" % (var[0]) in globals(), locals()
        Diss_list.append(var[0])
    DISS=Matrix(len(q_list),1,Diss_list)
    
    LHS=[] # Left hand side (list) of the system of differential equations
    RHS=[] # Right hand side (list) of the system of differential equations
    for i in range(len(dofs)):
        if Diss[i]==0:
            Fdiss=0
        else:
            d=velocity[i]
            Fdiss=partafgeleide(DISS[i],d)
        LHS.append(velocity[i])
        LHS.append(impdot[i])
        RHS.append(partafgeleide(H,imp[i]))
        RHS.append(ex_force[i]-Fdiss-partafgeleide(H,dofs[i]))
             
    RHS_symbols=list(RHS) # Copy of the symbolic RHS for potential printing
    RHS_control=list(RHS) # Copy of the symbolic RHS for further use in the control part

    t=Symbol('t')

    init=vars_cal[6].get().split(',') # Get initial values (these are still strings here)
    init=[float(p) for p in init] # Create floating points of the values
 
    F=vars_cal[7].get().split(',') # Get values of external forces 
    F=[float(p) for p in F]

    P_val=vars_cal[5].get().split(',') # Get values of the parameters
    P_val=[float(p) for p in P_val]

    # Checking if the dimensions of the inputs are good:    
    while len(P_val)!=len(P):
        tkMessageBox.showerror(title="Error message",message="The dimension of the \
'values of the parameters' (%s) is not equal to the dimension of the\
'Parameters' (%s)"% (len(P_val),P.rows),type="ok")
        break # Breaks the loop
    while len(F)!=len(dofs):
        tkMessageBox.showerror(title="Error message",message="The dimension of the \
'Forces' (%s) is not equal to the dimension of the 'Degrees Of Freedom' \
(%s)"% (len(F),dofs.rows),type="ok")
        break
    while len(init)!=2*len(dofs):
        tkMessageBox.showerror(title="Error message",message="The dimension of the \
'Initial Values' (%s) is not equal to 2 times the dimension of the \
'Degrees Of Freedom' (%s)"% (len(init),2*dofs.rows),type="ok")
        break
    
    
    Q=sympy.DeferredVector('Q') # A vector whose components are deferred 
    # This allows 'lambdify' to take vectors 
    PQ=sympy.DeferredVector('PQ')

    for i in range(len(dofs)):
        for j in range(2*len(dofs)):
            # Substitute the velocities (from the dissipation energy) in the RHS 
            # with the RHS velocity expressions
            RHS[j]=RHS[j].subs(velocity[i],RHS[2*i]) 
            RHS[j]=RHS[j].subs(imp[i],PQ[i]) # Substute momenta with DefferedVector
            RHS[j]=RHS[j].subs(dofs[i],Q[i]) # Substute dofs with DefferedVector
     
    # Substitute the symbolic parameters with the values of the parameters
    for i in range(len(P)):
        for j in range(2*len(dofs)):
            RHS[j]=RHS[j].subs(P[i],P_val[i])
    # Substitute the symbolic parameters with the values of the parameters                         
    for i in range(len(ex_force)):
        for j in range(2*len(dofs)):
            RHS[j]=RHS[j].subs(ex_force[i],F[i])
  
    test=lambdify((Q,PQ,t),RHS) # lambdify(arguments,expression)
    # This module transforms sympy expressions to lambda functions,
    # which can be used to calculate numerical values very fast.
    
    """SOLVE THE DIFFERETIAL EQUATIONS (THROUGH INTEGRATION)"""
       
    # (use 'ode' from scipy.integrate class)

    # Create function for solving the differential equations
    def f(t,y):
        p1=[y[2*p] for p in range(len(q_list))]
        p2=[y[1+2*p] for p in range(len(q_list))]
        W=test(p1,p2,t)           
        out=W
        return out
    dt=0.01 # Infinitisimal change of t
    t0=0 # Initial time

    t_end=time_ode_end.get() # End time

    ODE = ode(f).set_integrator('vode',method='bdf')
    # 'vode'= real-valued variable-coefficient Ordinary Differential Equation solver

    ODE.set_initial_value(init,t0)

    Res=array(init) # Results (array) of the differential equations [dofs0,imp0,dofs1,..]
    # This Res array appends [dofs0,imp0,dofs1,..] for each time step
    T=[0] # List that appends time step after every integration
    fail=0 # Initialy there is no fail, but when the integration fails, this value
    # becomes 1
    while ODE.successful() and ODE.t<t_end:
        try:
            ODE.integrate(ODE.t+dt)
            Res=np.append([Res],[ODE.y.real])
            T=np.append([T],[ODE.t])

        except ZeroDivisionError: # When a ZeroDivisionError occures, do:
            tkMessageBox.showerror(title="ZeroDevisionError",message="Error while \
dividing by zero! \nYou can check the differential equations in the upper\
textbox and adjust initial value(s) and calculate again.")
            text.insert(Tkinter.END,"\n ----------------------------------------------\
            -------------------------")
            text.insert(Tkinter.END,"\n The differential equations in symbols are:")
            for eq in zip(LHS,RHS_symbols):
                text.insert(Tkinter.END,'                     ')      
                text.insert(Tkinter.END,"\n %s= %s"%(eq[0],eq[1]))
            fail=1
            break
        
    # Get rid of the deffered vectors 
    for i in range(len(dofs)):   
        for j in range(2*len(dofs)):
            RHS[j]=RHS[j].subs(PQ[i],imp[i])
            RHS[j]=RHS[j].subs(Q[i],dofs[i])
    
    # All constant values in this RHS are numeric, only the dofs & momenta are symbols 
    
    # Create symbolic array: [dof1,impuls1,dof2,impuls2]:     
    dof_imp=[]        
    for i in range(len(dofs)):
            dof_imp.append(dofs[i])
            dof_imp.append(imp[i])
        
    # The length of a matrix = number of elements in the matrix (rows*columns)
    # The length of Res=(number of dofs)*(number of timesteps)
    #    --> for each timestep Res appends '2*(number of dofs)' values
    
    M_RHS=zeros([len(Res)/(2*len(dofs)),2*len(dofs)]) # Create a zero matrix 
    M_Res=zeros([len(Res)/(2*len(dofs)),2*len(dofs)]) 
    
    for j in range(2*len(dofs)):
        for i in range(len(Res)/(2*len(dofs))):
            M_RHS[i,j]=RHS[j] 
            M_Res[i,j]=Res[j::2*len(dofs)][i] 
    # M_RHS=SYMBOLIC matrix (here) with len(Res)/2*len(dofs) rows,
    # --> in this Symbolic M_RHS matrix, every row = [vq1,Pdot1,vq2,Pdot2,..]
    # M_Res=NUMERICAL Matrix with len(Res)/4 rows: [dof1,Pdof1,dof2,Pdof2] 
 
    # Create NUMERICAL M_RHS matrix, through substitution of the dofs and momenta
    # with the results (M_Res) from the solved differential equations. 
            
    for j in range(2*len(dofs)):
        for i in range(len(Res)/(2*len(dofs))):
            for a in range(2*len(dofs)):
                M_RHS[i,j]=M_RHS[i,j].subs(dof_imp[a],M_Res[i,a])

    """SAVE DATA AND RESULTS IN TXT-FILES FOR POST-PROCESSING (for lower functions):"""
    
    """     SYMBOLIC DATA:    """
    import pickle
    with open("Degrees Of Freedom.txt", "w+") as outf:
        pickle.dump(dofs, outf)
    with open("Momenta.txt", "w+") as outf:
        pickle.dump(imp, outf)
    with open("Velocities.txt", "w+") as outf:
        pickle.dump(velocity, outf)
    with open("System Forces.txt", "w+") as outf:
        pickle.dump(impdot, outf)        
    with open("Hamiltonian.txt", "w+") as outf:
        pickle.dump(H, outf)            
    with open("External Forces.txt", "w+") as outf:
        pickle.dump(ex_force, outf)
    with open("Dissipation.txt", "w+") as outf:
        pickle.dump(DISS, outf)
    with open("RHS ode.txt", "w+") as outf:
        pickle.dump(RHS_symbols, outf)
    with open("LHS ode.txt", "w+") as outf:
        pickle.dump(LHS, outf)     
    with open("RHS_control.txt", "w+") as outf:
        pickle.dump(RHS_control, outf)   
    with open("Parameter Symbols.txt", "w+") as outf:
        pickle.dump(P, outf)  
    # Save strings of the dofs and parameters for later (XY-plot) evaluation (exec):
    with open("dofs_string.txt", "w+") as outf:
        pickle.dump(q, outf)
    with open("parameters_string.txt", "w+") as outf:
        pickle.dump(params, outf)  
        
    """     NUMERIC DATA:     """
    np.savetxt('Parameter Values.txt',P_val)
    np.savetxt('External Forces Values.txt',F)
    np.savetxt('results dofs & momenta matrix.txt',M_Res)
    np.savetxt('results velocities and system forces matrix.txt',M_RHS)
    np.savetxt('time steps.txt',T)

    if fail!=1: # When no errors occur in the function, fail = 0 
        tkMessageBox.showerror(title="Calculation Status",message="Calculation \
Successful! \nYou can now 'simulate and visualize' or 'control' the system.")




# SIMULATE AND VISUALIZE:

"""
Create a function to simulate and visualize a systems (use results from Solve_Hamilton):
Parameters of the function (text,root,vars_sim,check,checkXY,calculatecheck)

  --> text = e.g. text widget from an interface
  --> root = e.g. master window of the GUI (here the simulate&visualize window = 
      toplevel window)
  --> vars_simXY (and vars_simXY_func) = variables for XY plot (list of StringVar), 
      length=2
  --> check = check variables (0 or 1), to check if checkbutton is checked
  --> checkXY (and checkXY_func) =check variable (0 or 1), to check if checkbutton 
      for XY-graph is checked  
  --> calculatecheck = check variable, to check if the 'calculate button' is pressed
  
  Widgets (e.g. entry widgets, buttons, etc.) are implementen GUI-interface.
"""
    
def SimulateAndVisualize_Hamilton(text,root,vars_simXY,vars_simXY_func,check,checkXY,\
checkXY_func, calculatecheck):
    
    """"  READ DATA AND RESULTS FROM TXT-FILES:  """
    
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
    with open("RHS ode.txt") as inf:
        RHS = pickle.load(inf)  
    with open("LHS ode.txt") as inf:
        LHS = pickle.load(inf)  
    # We need to evaluate (exec) the dofs and parameter strings again for the XY-plot
    with open("dofs_string.txt") as inf: #
        q_str = pickle.load(inf)  
    with open("parameters_string.txt") as inf:
        par_str = pickle.load(inf) 

    M_Res=np.loadtxt('results dofs & momenta matrix.txt')
    M_RHS=np.loadtxt('results velocities and system forces matrix.txt')
    P_val=np.loadtxt('Parameter Values.txt')
    F=np.loadtxt('External Forces Values.txt')
    T=np.loadtxt('time steps.txt')
    
    # The lenght of the np.loadtxt matrices = number of rows (so not multiplied by 
    # columns).
    
    import Tkinter as tk
    # If checkbutton = checked: print the differential equations in symbols (in the 
    # simulate and visualize window):
    if check[3].get()==1:
        text.insert(Tkinter.END,"\n -------------------------------------------------\
----------------------")
        text.insert(Tkinter.END,"\n The differential equations in symbols are:")
        for eq in zip(LHS,RHS):
            text.insert(Tkinter.END,'                     ')      
            text.insert(Tkinter.END,"\n %s= %s"%(eq[0],eq[1]))
            
    # If checkbutton = checked: print numeric results of the degrees of freedom and 
    # momenta for every timestep  (in a new (Toplevel) window):
    if check[4].get()==1:
        top1 = tk.Toplevel(root)
        top1.geometry("1000x700+50+50")
        text_dofimp = Text(top1,height=20000,width=200)
        text_dofimp.insert(Tkinter.END,"\n DEGREES OF FREEDOM & MOMENTA FOR EVERY \
TIMESTEP")
        text_dofimp.insert(Tkinter.END,"\n ----------------------------------------\
---------------------------------")
        text_dofimp.insert(Tkinter.END,"\n Time [s]: [dof(1), Pdof(1), dofs(2), \
Pdof(2),...,dof(n),Pdof(n)]")      
        for i in range(len(M_Res)):
            text_dofimp.insert(Tkinter.END,"\n %s: %s"%(T[i],[M_Res[i,j] for j in 
            range(2*len(dofs))])) 
        text_dofimp.pack()

    
    # If checkbutton = checked: print numeric results of the velocities and 
    # system forces for every timestep  (in a new (Toplevel) window):
    if check[5].get()==1:
        top2 = tk.Toplevel(root)
        top2.geometry("1000x700+0+0")
        text_velforce = Text(top2,height=20000,width=200)  
        text_velforce.insert(Tkinter.END,"\n VELOCITIES AND SYSTEM FORCES FOR EVERY \
TIMESTEP")
        text_velforce.insert(Tkinter.END,"\n ---------------------------------------\
----------------------------------")
        text_velforce.insert(Tkinter.END,"\n Time [s]: [velocity(1), Pdofdof(1), \
velocity(2), Pdofdot(2),...,velocity(n),Pdofdot(n)]")
        for i in range(len(M_Res)):
            text_velforce.insert(Tkinter.END,"\n %s: %s"%(T[i],[M_RHS[i,j] \
            for j in range(2*len(dofs))]))
        text_velforce.pack()
    
    # If checkbutton = checked; plot dofs and momenta as a function of time:
    if check[0].get()==1:
        fig=figure() # Create new figure
        for i in range(2*len(dofs)):
            subplot(len(dofs),2,i+1)
            plot(T,M_Res[:,i])
            if i%2==0: # Plot dofs
                ylabel("%s"% dofs[floor(i/2)]) 
                # floor(x) returns the largest integer not greater than x
                xlabel("time[s]")
            else: # Plot momenta
                ylabel("P%s[Ns]"%dofs[floor(i/2)])
                xlabel("time[s]")
                    
        fig.text(.05,.95,'DOF-coordinates & impulses as a function of time')
        
    # If checkbutton = checked; plot velocity as a function of the time;
    if check[1].get()==1:
        fig=figure()
        for i in range(len(dofs)):
            subplot(len(dofs),1,i+1)
            plot(T,M_RHS[:,2*i])
            ylabel("%s [m/s]"% velocity[i])
            xlabel("time[s]")
            fig.text(.05,.95,'velocities as a function of time')
                
   # If checkbutton = checked; plot forces as a function of the time(derivative of 
   # the momenta);
    if check[2].get()==1:
        fig=figure()
        for i in range(len(dofs)):
            subplot(len(dofs),1,i+1)
            plot(T,M_RHS[:,1+2*i])
            ylabel("%s[N]"% ex_force[i]) 
            xlabel("time[s]")
        fig.text(.05,.95,'forces as a function of time')
    
    
    # If checkbutton = checked; plot Y as a function of X (interface has drop-down for
    # defining the X- and Y value):
    if checkXY.get()==1:
        for param in zip(q_str,q_str):
            exec "%s=Symbol(%s)" % (param[0], 'param[1]') in globals(), locals()
            exec "%s=Symbol(%s)" % (str("v")+param[0], 'str("v")+param[1]') \
            in globals(), locals()
            exec "%s=Symbol(%s)" % (str("P")+param[0], 'str("P")+param[1]') \
            in globals(), locals()
            exec "%s=Symbol(%s)" % (str("P")+param[0]+str("dot"), \
            'str("P")+param[1]+str("dot")') in globals(), locals() 
            exec "%s=Symbol(%s)" % (str("F")+param[0], 'str("F")+param[1]') \
            in globals(), locals()
        for param in zip(par_str,par_str):
            exec "%s=Symbol(%s)" % (param[0], 'param[1]') in globals(), locals()
                   
        time=Symbol('time')
        xfunc=[]
        yfunc=[]        
        exec "x1=%s" % (vars_simXY[1].get()) in globals(),locals()
        exec "y1=%s" % (vars_simXY[0].get()) in globals(),locals()
        xfunc.append(x1)
        yfunc.append(y1)
        # Create a list for appending copies of the entry 'x' & 'y' value, with length=
        # row length of the result matrices (= number of timesteps)
        Xfunction=[] 
        Yfunction=[]
        
        
        for i in range(len(M_Res)):
            Xfunction.append(xfunc[0]) #add xfunc to Xfunction LIST
            Yfunction.append(yfunc[0])  
            
        # Substitute every symbol of the X and Y functions with a value (defined before)
        for i in range(len(M_Res)):        
            for j in range(len(dofs)):
                # No substitution if type of the entry = integer or if entry = time
                if type(Xfunction[i])!= int and xfunc[0]!=time: 
                   Xfunction[i]=Xfunction[i].subs(dofs[j],M_Res[i,2*j])
                   Xfunction[i]=Xfunction[i].subs(imp[j],M_Res[i,2*j+1])
                   Xfunction[i]=Xfunction[i].subs(velocity[j],M_RHS[i,2*j])
                   Xfunction[i]=Xfunction[i].subs(impdot[j],M_RHS[i,2*j+1])
                   Xfunction[i]=Xfunction[i].subs(ex_force[j],F[j])

                if type(Yfunction[i])!= int and yfunc[0]!=time:   
                   Yfunction[i]=Yfunction[i].subs(dofs[j],M_Res[i,2*j])
                   Yfunction[i]=Yfunction[i].subs(imp[j],M_Res[i,2*j+1])
                   Yfunction[i]=Yfunction[i].subs(velocity[j],M_RHS[i,2*j])
                   Yfunction[i]=Yfunction[i].subs(impdot[j],M_RHS[i,2*j+1])
                   Yfunction[i]=Yfunction[i].subs(ex_force[j],F[j])

        for i in range(len(M_Res)):        
            for j in range(len(P)):
            # Length of the parameters is not equal to length dofs
                if type(Xfunction[i])!= int and xfunc[0]!=time:
                    Xfunction[i]=Xfunction[i].subs(P[j],P_val[j])
                if type(Yfunction[i])!= int and yfunc[0]!=time:
                    Yfunction[i]=Yfunction[i].subs(P[j],P_val[j]) 
        # When 't' is entered in the entry widget, substitute X and/or Y with timesteps:
        if xfunc[0]==time: 
            Xfunction=T
        if yfunc[0]==time: 
            Yfunction=T
        figure()    
        plot(Xfunction,Yfunction)
        xlabel(str(xfunc[0]))
        ylabel(str(yfunc[0]))
        title('"'+str(yfunc[0])+'" as a function of "'+str(xfunc[0])+'"')
    
    # Same as XY plot, but here an entry widget is created in the interface for the
    # X and Y input, therefore it is possible to input expressions
    if checkXY_func.get()==1:
        for param in zip(q_str,q_str):
            exec "%s=Symbol(%s)" % (param[0], 'param[1]') in globals(), locals()
            exec "%s=Symbol(%s)" % (str("v")+param[0], 'str("v")+param[1]') \
            in globals(), locals()
            exec "%s=Symbol(%s)" % (str("P")+param[0], 'str("P")+param[1]') \
            in globals(), locals()
            exec "%s=Symbol(%s)" % (str("P")+param[0]+str("dot"), \
            'str("P")+param[1]+str("dot")') in globals(), locals() 
            exec "%s=Symbol(%s)" % (str("F")+param[0], 'str("F")+param[1]') \
            in globals(), locals()
        for param in zip(par_str,par_str):
            exec "%s=Symbol(%s)" % (param[0], 'param[1]') in globals(), locals()
                   
        time=Symbol('time')
        xfunc=[]
        yfunc=[]        
        exec "x1=%s" % (vars_simXY_func[1].get()) in globals(),locals()
        exec "y1=%s" % (vars_simXY_func[0].get()) in globals(),locals()
        xfunc.append(x1)
        yfunc.append(y1)
        # Create a list for appending copies of the entry 'x' & 'y' value, with length=
        # row length of the result matrices (= number of timesteps)
        Xfunction=[] 
        Yfunction=[]
        
        
        for i in range(len(M_Res)):
            Xfunction.append(xfunc[0]) # Add xfunc to Xfunction LIST
            Yfunction.append(yfunc[0])  
            
        # Substitute every symbol of the X and Y functions with a value (defined before)
        for i in range(len(M_Res)):        
            for j in range(len(dofs)):
                # No substitution if type of the entry = integer or if entry = time
                if type(Xfunction[i])!= int and xfunc[0]!=time: 
                   Xfunction[i]=Xfunction[i].subs(dofs[j],M_Res[i,2*j])
                   Xfunction[i]=Xfunction[i].subs(imp[j],M_Res[i,2*j+1])
                   Xfunction[i]=Xfunction[i].subs(velocity[j],M_RHS[i,2*j])
                   Xfunction[i]=Xfunction[i].subs(impdot[j],M_RHS[i,2*j+1])
                   Xfunction[i]=Xfunction[i].subs(ex_force[j],F[j])

                if type(Yfunction[i])!= int and yfunc[0]!=time:   
                   Yfunction[i]=Yfunction[i].subs(dofs[j],M_Res[i,2*j])
                   Yfunction[i]=Yfunction[i].subs(imp[j],M_Res[i,2*j+1])
                   Yfunction[i]=Yfunction[i].subs(velocity[j],M_RHS[i,2*j])
                   Yfunction[i]=Yfunction[i].subs(impdot[j],M_RHS[i,2*j+1])
                   Yfunction[i]=Yfunction[i].subs(ex_force[j],F[j])

        for i in range(len(M_Res)):        
            for j in range(len(P)):
            # Length of the parameters is not equal to length dofs
                if type(Xfunction[i])!= int and xfunc[0]!=time:
                    Xfunction[i]=Xfunction[i].subs(P[j],P_val[j])
                    Yfunction[i]=Yfunction[i].subs(P[j],P_val[j]) 
        # When 't' is entered in the entry widget, substitute X and/or Y with timesteps:
        if xfunc[0]==time: 
            Xfunction=T
        if yfunc[0]==time: 
            Yfunction=T
        figure()    
        plot(Xfunction,Yfunction)
        xlabel(str(xfunc[0]))
        ylabel(str(yfunc[0]))
        title('"'+str(yfunc[0])+'" as a function of "'+str(xfunc[0])+'"')
    show()
    
    root.update()  # Update simulate&visualize window in interface   
 
 
    
#CONTROL:  
    
"""
Create a function to control the system:
We use the LQR-method to generate feedback control
Parameters of the function (text,root,vars_control1,vars_control2,check)

  --> text = e.g. text widget from an interface
  --> root = e.g. master window of the GUI (here the control window = Toplevel window)
  --> vars_control1 = variables for control (list of StringVar), length=2
      StringVar1=Initial Values (dofs,momenta & external forces (for control))
      StringVar2=Worpkoint Values for linearization      
  --> vars_control2 = variables for control (list of StringVar), length=4
      StringVar1=Q-Matrix (FOR LQR, e.g. [row0],[row1],[row3],..)
      StringVar2=R-Matrix (FOR LQR, e.g. [row0],[row1],[row3],..)
      StringVar3=Time Steps (T0,Tend,number of elements between T0 & Tend)
      StringVar4= Reference Functions (REFdof0,REFdof1,etc..)
  --> check = check variables (0 or 1), to check if checkbutton is checked
      check variable=0: PD-control
      check variable=1: add I-action for PID control
"""
  
def Control_Hamilton(text,root,vars_control1,vars_control2,check):
    
    """  READ DATA AND RESULTS FROM TXT-FILES:  """
    
    import pickle
    with open("Degrees Of Freedom.txt") as inf:
        dofs = pickle.load(inf)
    with open("Velocities.txt") as inf:
        velocity = pickle.load(inf)    
    with open("Momenta.txt") as inf:
        imp = pickle.load(inf)      
    with open("Parameter Symbols.txt") as inf:
        P = pickle.load(inf)       
    with open("External Forces.txt") as inf:
        ex_force = pickle.load(inf)
    with open("RHS_control.txt") as inf:
        RHS_control = pickle.load(inf)
    with open("LHS ode.txt") as inf:
        LHS = pickle.load(inf)
        
    P_val=np.loadtxt('Parameter Values.txt')


    """ 
    CONTINUOUS-TIME LINEAR SYSTEM:
    Xdot = A*X + B*U 
    
    (with Xdot=Left Hand Side (LHS),from Solve_Hamilton())
    
    """    
  
    X=[] # List for appending dofs & momenta [dof0,imp0,dof1...]
        
    for i in range(len(dofs)):
        X.append(dofs[i])
        X.append(imp[i])
    
    
    if check[0].get()==1: # ADD I ACTION TO THE SYSTEM
        I=[] 
        for i in range(len(dofs)):
            I.append(Symbol('I'+str(dofs[i]))) # Append extra DOFS 
        for i in range(len(dofs)):   
            X.append(I[i])
            # In LHS, append Idof0dot,Idof1dot, etc. :
            LHS.append(Symbol('I'+str(dofs[i])+'dot')) 
        
        A=zeros([3*len(dofs),3*len(dofs)])
        B=zeros([3*len(dofs),3*len(dofs)])
        for i in range(len(dofs)):
            A[2*len(dofs)+i,2*i]=1
        
    else: # No I-action, PD CONTROL: 
        A=zeros([2*len(dofs),2*len(dofs)])
        B=zeros([2*len(dofs),2*len(dofs)])
   
    # Create B-Matrix (same for PD- and PID-control)
    for i in range(len(dofs)):
        B[1+2*i,1+2*i]=1
        
    # Get values for linearization (when no linearization required; entry=0):        
    WPval=vars_control1[1].get().split(',') 
    WPval=[float(p) for p in WPval]
    
         
    if vars_control1[1].get()!=str('0'): # Linearization = required
        # LINEARIZE: use (part of) Taylor Expansion
        # Function ƒ(x) that is infinitely differentiable at a (=workpoint value): 
        # Use term: f(a) of the Taylor expansion to create Matrix A:
        for i in range(2*len(dofs)):
            for j in range(2*len(dofs)):
                # Derivative:
                A[i,j]=partafgeleide(RHS_control[i],X[j])
                # Substitute symbolic values with workpoint values:
                for a in range(2*len(dofs)): 
                    A[i,j]=A[i,j].subs(X[a],WPval[a])
                for val in range(len(P)):
                    A[i,j]=A[i,j].subs(P[val],P_val[val])
        
    else: # In this case no linearization is required 
        for i in range(2*len(dofs)):
            for j in range(2*len(dofs)):
                A[i,j]=partafgeleide(RHS_control[i],X[j])
                for val in range(len(P)):
                    A[i,j]=A[i,j].subs(P[val],P_val[val])
                               
    # Create copy of the symbolic list of the RHS of the differential equations
    RHS_control_sym=list(RHS_control)  
    
    import ast
    R=vars_control2[1].get() # Get rows of R-Matrix (R=[row0],[row1],[row2],etc.)    
    R=ast.literal_eval(R) # Evaluate the string entry    
    # For Q-matrix use 'Qval', because 'Q' is already used
    Qval=vars_control2[0].get() # Get rows of Q-Matrix (R=[row0],[row1],[row2],etc.)  
    Qval=ast.literal_eval(Qval) # Evaluate the string entry 
    
    # Create numpy.arrays (for LQR-method):
    A=np.array(A) 
    B=np.array(B) 
    R=np.array(R) 
    Qval=np.array(Qval) 
    
    fail=0 # Starting with no fail
    
    # Checking if the dimensions of the inputs are correct:    
    if check[0].get()==1: # WHEN I ACTION IS ADDED:
        while len(R)!=3*len(dofs):
            tkMessageBox.showerror(title="Error message",message="The row dimension \
of the 'R-Matrix' is incorrect, it should be %s"%(3*len(dofs)),type="ok")
            fail=1            
            break
        for i in range(3*len(dofs)):
            while len(R[i])!=3*len(dofs):
                tkMessageBox.showerror(title="Error message",message="One or \
more column dimension(s) of the 'R-Matrix' are incorrect, column dimension should \
be %s"%(3*len(dofs)),type="ok")
                fail=1            
                break
        while len(Qval)!=3*len(dofs):
            tkMessageBox.showerror(title="Error message",message="The row dimension\
of the 'Q-Matrix' is incorrect, row dimension should be %s"%(3*len(dofs)),type="ok")
            fail=1                        
            break
        for i in range(3*len(dofs)):
            while len(Qval[i])!=3*len(dofs):
                tkMessageBox.showerror(title="Error message",message="One or\
more column dimension(s) of the 'Q-Matrix' are incorrect, column dimension should be \
%s"%(3*len(dofs)),type="ok")
                fail=1            
                break

    else:
        while len(R)!=2*len(dofs):
            tkMessageBox.showerror(title="Error message",message="The row dimension\
of the 'R-Matrix' is incorrect, row dimension should be %s"%(2*len(dofs)),type="ok")
            fail=1            
            break
        for i in range(2*len(dofs)):
            while len(R[i])!=2*len(dofs):
                tkMessageBox.showerror(title="Error message",message="One or more \
column dimension(s) of the 'R-Matrix' are incorrect, column dimension should be\
 %s"%(2*len(dofs)),type="ok")
                fail=1            
                break
        while len(Qval)!=2*len(dofs):
            tkMessageBox.showerror(title="Error message",message="The row dimension \
of the 'Q-Matrix' is incorrect, row dimension should be %s"%(2*len(dofs)),type="ok")
            fail=1                        
            break
        for i in range(2*len(dofs)):
            while len(Qval[i])!=2*len(dofs):
                tkMessageBox.showerror(title="Error message",message="One or more\
column dimension(s) of the 'Q-Matrix' are incorrect,  column dimension should \
be %s"%(2*len(dofs)),type="ok")
                fail=1            
                break  
    
    if fail==0: # If the dimensions of the input values are correct..
        # Handling execption (errors) with try & except (therefore a message can be
        # raised when the LQR-method failed):
        try:
            K, S, E = lqr(A, B, Qval, R)         
        
        except ValueError:
            tkMessageBox.showerror(title="ValueError",message="LQR-method failed: \
adjust value(s) of the Q-matrix (e.g. some value(s) might be too high or too low)")
 
    np.savetxt("K-Matrix (LQR).txt",K)    
    np.savetxt("E-Matrix (LQR).txt",E)    

    KK=Matrix(K)
    EE=list(E)
    
    for i in range(len(K)):
        for j in range(len(K)):
            KK[i,j]=round(KK[i,j], 3) # Round decimals in K matrix for printing
           
    # Show K & E matrices in text widget:
    if check[1].get()==1:
        text.insert(Tkinter.END,"\n ------------------------------------------------\
-------------------------------------------------------------------")
        text.insert(Tkinter.END,"\n K & E matrix from LQR-control")
        text.insert(Tkinter.END,"\n ------------------------------------------------\
-------------------------------------------------------------------")
        text.insert(Tkinter.END,"\n K:")
        text.insert(Tkinter.END,"\n%s"%KK)
        text.insert(Tkinter.END,"\n")
        text.insert(Tkinter.END,"\n E:")
        text.insert(Tkinter.END,"\n%s"%EE)
        
    root.update() # Update control-window in interface
    
    """
    the principles for solving the system are the same as in Solve_Hamilton
    For comments; check Solve_Hamilton documentation
    For the control system; 
    --> the method for solving the differential equations is repeated in for loop,
        so feedback is applied
    --> for example: we solve the diiferential equations from t=0->1,
        with 2000 points between 0 & 1, so the 'solve-method' is applied 2000 times, 
        for a very small interval
        
    
    """
    Q=sympy.DeferredVector('Q')
    PQ=sympy.DeferredVector('PQ')
    FQ=sympy.DeferredVector('FQ')   
    IQ=sympy.DeferredVector('IQ') # For I-action
    
    
    for i in range(len(dofs)):
        for j in range(2*len(dofs)):
            RHS_control[j]=RHS_control[j].subs(velocity[i],RHS_control[2*i])
            RHS_control[j]=RHS_control[j].subs(imp[i],PQ[i])
            RHS_control[j]=RHS_control[j].subs(dofs[i],Q[i])
            RHS_control[j]=RHS_control[j].subs(ex_force[i],FQ[i])
    
    for i in range(len(P)):
        for j in range(2*dofs.rows):
            RHS_control[j]=RHS_control[j].subs(P[i],P_val[i])
    ex_Finit=[] # Initial values for the external forces
    for i in range(len(dofs)):
        ex_Finit.append(0)
        
    # Add external forces in the RHS in this sequence: 
    # [velocity0,system force0,external force0,velocity0,system force1,etc]
    RHS_CONTROL=[]
    for i in range(len(dofs)):
        RHS_CONTROL.append(RHS_control[2*i])
        RHS_CONTROL.append(RHS_control[1+2*i])
        RHS_CONTROL.append(ex_Finit[i])
    RHS_control=RHS_CONTROL

    t=Symbol('t')
    
    # I-action: Idot=dof-reference    
    # Add first part of symbolic I action: dof (we add reference later in for loop):
    if check[0].get()==1:
        for j in range(len(dofs)):
            RHS_control.append(Q[j])  
            
    # Get time functions: string= T0,Tend,number of elements between T0 & Tend:
    timesteps=vars_control2[2].get().split(',') 
    TS=[float(p) for p in timesteps]
    t1=linspace(TS[0],TS[1],TS[2])  # Create linear spaced vector for time function

    from sympy.functions import sign # Used in the reference functions
    ref=vars_control2[3].get().split(',') # Get reference functions
    # The reference functions are a function of t1
    ref_list=[]
    for refs in zip(ref):
        exec "%s" %(refs[0]) in globals(), locals()
        ref_list.append(refs[0])
    M_ref= Matrix(len(ref),1,ref_list) # Symbolic reference function (for subs)
    
    # Matrix with vectors of t1 and reference values: [t1,REFdof1,REFdof2,etc.]   
    # with length of rows = length of t1:    
    REF=np.zeros([(len(t1)),len(dofs)+1]) # In 'for loop' we substitute zeros
    
    # No reference signals for momenta (although this is possible) or I-function 
    # (if reference function for I is added, an undesirable static error is obtained)    
    
    # Matrix with vectors of degrees of freedom functions (after control), for plotting:
    DOF_control=np.zeros([len(t1),len(dofs)])   # In for loop we substitute zeros
    
    # U matrix = K*(error signal), with K from LQR
    # error signal= Xref - X:
    # = [(REFdof-dof0), (impdof0),(Refdof1-dof1),(impdof1-0), ...]
    # with length rows = length t1
    error_signal_PD=np.zeros([len(t1),2*len(dofs)])
    if check[0].get()==1: # FOR PID:
    # error signal= [(REFdof-dof0),(impdof0),(Refdof1-dof1),(impdof1-0),Idof0,Idof1,..]
        error_signal_PID=np.zeros([len(t1),3*len(dofs)])
        
    init=vars_control1[0].get().split(',') # Get initial values
    init_lqr=[float(p) for p in init]       
    
    # Check dimensions of vars_control1
    if check[0].get()==1: 
        while len(init_lqr)!=4*len(dofs):
            tkMessageBox.showerror(title="Error message",message="The dimension of \
the initial values (%s) is not correct, it should be %s" %(len(init_lqr),4*len(dofs)),\
type="ok")
            break
        if vars_control1[1].get()!=str('0'):
            while len(WPval)!=2*len(dofs): 
                tkMessageBox.showerror(title="Error message",message="The dimension \
of the 'workpoint values' (%s) is not correct, it should be %s" \
%(len(WPval),2*len(dofs)),type="ok")
                break
    
    else:
        while len(init_lqr)!=3*len(dofs):
            tkMessageBox.showerror(title="Error message",message="The dimension of \
the initial values (%s) is not correct, it should be %s" %(len(init_lqr),3*len(dofs))\
,type="ok")
            break
        if vars_control1[1].get()!=str('0'):
            while len(WPval)!=2*len(dofs):
                tkMessageBox.showerror(title="Error message",message="The dimension\
of the 'workpoint values' (%s) is not correct, it should be %s" \
%(len(WPval),2*len(dofs)),type="ok")
                break

    
    fail=0
    for i in range(len(t1)):
        if fail==1: # If there iss a fail in the dimensions, break the for loop
            break
        # Substitute REF values with numerical values for every i
        for j in range(len(dofs)):
            REF[i,0]=t1[i] 
            REF[i,j+1]=M_ref[j].subs(t,t1[i])   
            
        if check[0].get()==1: # FOR I ACTION
        # ADD SECOND PART (reference) in Idot (Idot=dof-reference)
            if i==0:
                for j in range(len(dofs)):
                    RHS_control[3*len(dofs)+j]=RHS_control[3*len(dofs)+j]-REF[i,j+1]                    
            else:
                 for j in range(len(dofs)):
                    RHS_control[3*len(dofs)+j]=RHS_control[3*len(dofs)+j]-\
                    REF[i,j+1]+REF[i-1,j+1] 
                    # +REF[i-1,j+1]: previous REF value so there no addition of
                    # the REF signal
                
        # Check Solve_Hamilton
        if check[0].get()==1: # With I-action
            lamd=lambdify((Q,PQ,FQ,IQ,t),RHS_control)
            def f_lqr(t,y):
                p1=[y[3*p] for p in range(len(dofs))]
                p2=[y[1+3*p] for p in range(len(dofs))]
                p3=[y[2+3*p] for p in range(len(dofs))]
                p4=[y[3*len(dofs)+p] for p in range(len(dofs))]
                W_LQR=lamd(p1,p2,p3,p4,t)        
                out=W_LQR
                return out
        else:            
            lamd=lambdify((Q,PQ,FQ,t),RHS_control)
            def f_lqr(t,y):
                p1=[y[3*p] for p in range(len(dofs))]
                p2=[y[1+3*p] for p in range(len(dofs))]
                p3=[y[2+3*p] for p in range(len(dofs))]
                W_LQR=lamd(p1,p2,p3,t)
                #print t,y[1]
                out=W_LQR
                return out

        dt=t1[1]  # If t1=(0,1,2000)--> t1[1]=0.000499
        t0=t1[i]  # Start time
        t_end=t1[i]+t1[1] # t1[1]= space between 2 points in t1

        ODE_lqr = ode(f_lqr).set_integrator('vode',method='bdf')
        ODE_lqr.set_initial_value(init_lqr,t0)
        
        
        # Substitute zeros of error signal with values:
        for j in range(len(dofs)):
            error_signal_PD[i,2*j]=REF[i,1+j]-ODE_lqr.y[3*j]
            error_signal_PD[i,1+2*j]=-ODE_lqr.y[1+3*j]
            
        if check[0].get()==1: # With I-action
            for j in range(len(dofs)):
                error_signal_PID[i,2*j]=REF[i,1+j]-ODE_lqr.y[3*j]
                error_signal_PID[i,1+2*j]=-ODE_lqr.y[1+3*j]
                error_signal_PID[i,2*len(dofs)+j]=-ODE_lqr.y[3*len(dofs)+j]
        
        # CONTROL: external F (=U) = K*(error_signal):
        
        """
        EXAMPLE: "external force = U = K*(error_signal)"

        error signal = Xref-X
        (Xref = 0 for momenta and I-function)        
        #for two dofs and without I action: (Matrix multiplication)
        
        #[0 0 0 0]  [Ref[dof0]-ODE_lqr.y[0]]
        #[K K K K]  [-ODE lqr.y[1]         ]
        #[0 0 0 0]  [Ref[dof1]-ODE_lqr.y[3]]
        #[K K K K]  [-ODE_lqr.y[4]         ]
        """
        
        for a in range(len(dofs)):
                    if check[0].get()==1:
                        ODE_lqr.y[2+3*a]=np.dot(K[1+2*a,:],error_signal_PID[i,:])
                    else:
                        ODE_lqr.y[2+3*a]=np.dot(K[1+2*a,:],error_signal_PD[i,:])
         
        # Integrate
        while ODE_lqr.successful() and ODE_lqr.t<t_end:
            try:            
                ODE_lqr.integrate(ODE_lqr.t+dt)
            # Wrong initial values can lead to a ZeroDevisionError while solving ode's
            except ZeroDivisionError: 
                tkMessageBox.showerror(title="ZeroDevisionError",message="Error while \
dividing by zero! \nYou can check the differential equations in the upper textbox and \
adjust initial value(s) and calculate again.")
                text.insert(Tkinter.END,"\n -----------------------------------------\
                --------------------------------")
                text.insert(Tkinter.END,"\n The differential equations in symbols are:")
                for eq in zip(LHS,RHS_control_sym):
                    text.insert(Tkinter.END,'                     ')      
                    text.insert(Tkinter.END,"\n %s= %s"%(eq[0],eq[1]))
                fail=1
                break
                
        # The initial values for the next timestep are the results of the previous step:
        init_lqr=ODE_lqr.y 
        
        # Vector of the degrees of freedom in matrix:
        for j in range(len(dofs)):
            DOF_control[i,j]=ODE_lqr.y[j*(len(dofs)+1)] # Substitute zeros
            
    np.savetxt("DOF_control.txt",DOF_control)
    np.savetxt("References (time,dof0,dof1,etc.).txt",REF)
    
    # Plot controlled degrees of freedom and reference functions:
    if fail!=1: # If there was nog failure in the integration
        for i in range(len(dofs)):
            figure()
            plot(t1,DOF_control[:,i],'blue',label='system')
            plot(t1,REF[:,i+1],'red',label='reference')
            legend(loc='upper left')
            title('controlled system for ['+str(dofs[i])+']')
            xlabel('time [s]')
            ylabel(str(dofs[i])+'-position') 
    show()
    
    return 