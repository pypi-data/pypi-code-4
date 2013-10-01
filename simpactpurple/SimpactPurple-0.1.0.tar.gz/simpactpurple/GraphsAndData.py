"""
A module of functions for data and graphs of things from Simpact.
"""

import math
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


def age_mixing_graph(s):
    """
    Generates a scatter plot of male and female ages for each relationship
    formed.
    """
    males = []
    females = []
    for r in s.relationships:
        #eventually need an if statement to not include homosexual relations
        if r[0].gender:
            male = r[1]
            female = r[0]
        else:
            female = r[1]
            male = r[0]

        
        time_since_relationship = s.time - r[3]
        males.append(((s.age(male)*52.0) - time_since_relationship)/52.0)
        females.append(((s.age(female)*52.0) - time_since_relationship)/52.0)

    plt.figure()
    plt.scatter(males, females)
    plt.xlim(15, 65)
    plt.ylim(15, 65)
    plt.title("Age Mixing Scatter")
    plt.xlabel("Male Age")
    plt.ylabel("Female Age")
    plt.show()

def age_mixing_heat_graph(s, grid = 10):
    """
    Generates a heat map of male and female ages for each relationship
    formed.
    """
    boxes = np.zeros((grid, grid))
    maximum = s.MAX_AGE + 1
    minimum = s.MIN_AGE
    for r in s.relationships:
        #eventually need an if statement to not include homosexual relations
        if r[0].gender:
            male = r[1]
            female = r[0]
        else:
            female = r[1]
            male = r[0]

        time_since_relationship = s.time - r[3]

        male_age_at_formation = (((s.age(male) * 52.0) - time_since_relationship) / 52.0)
        male_index = math.floor(((male_age_at_formation - minimum)/(maximum - minimum)) * grid)
        female_age_at_formation = (((s.age(female) * 52.0) - time_since_relationship) / 52.0)
        female_index = math.floor(((female_age_at_formation-minimum) / (maximum - minimum)) * grid)
        boxes[female_index][male_index] += 1.0

    boxes_max = max([max(row) for row in boxes])
    boxes = np.array([[value / boxes_max for value in row] for row in boxes])

    plt.figure()
    plt.pcolormesh(boxes)
    #plt.matshow(boxes)
    plt.colorbar()
    #plt.xlim(15,65)
    #plt.ylim(15,65)
    plt.title("Age Mixing HeatMap")
    plt.xlabel("Male Age Bins")
    plt.ylabel("Female Age Bins")
    plt.show()

def formation_hazard():
    """
    Generates an age mixing scatter for many relationships with random
    ages for partners colored by the hazard of formation
    """
    #some graph parameters
    pop = 2000
    min_age = 15
    max_age = 65
    range_age = max_age - min_age

    #calculate some random age differences
    male_ages = (np.random.rand(pop)*range_age)+min_age
    female_ages = (np.random.rand(pop)*range_age)+min_age
    mean_age = ((male_ages+female_ages)/2) -15
    age_difference = female_ages-male_ages

    #hazard parameters (note: for factors lower -> narrower)
    #1)
#    baseline = 1
#    age_difference_factor = -0.2
#    mean_age_factor = -0.01
#    h = baseline*np.exp(age_difference_factor*age_difference + mean_age_factor*mean_age)

    #2) since age_difference = female_age - male_age, this is from male perspective
#    preferred_age_difference = -0.5
#    probability_multiplier = -0.1
#    preferred_age_difference_growth = 1
#
#    top = abs(age_difference - (preferred_age_difference*preferred_age_difference_growth*mean_age) )
#    h = np.exp(probability_multiplier * top)

    #3) (same as two)
    preferred_age_difference = -0.5
    probability_multiplier = -0.1
    preferred_age_difference_growth = 0.9
    age_difference_dispersion = -0.01
    top = abs(age_difference - (preferred_age_difference * preferred_age_difference_growth * mean_age) )
    bottom = preferred_age_difference * mean_age * age_difference_dispersion
    h = np.exp(probability_multiplier * (top/bottom)  )

    #make graph
    plt.scatter(male_ages,female_ages,c=h)
    plt.colorbar()
    plt.xlim(15,65)
    plt.ylim(15,65)
    plt.title("Age Mixing Scatter Tester")
    plt.xlabel("Male Age")
    plt.ylabel("Female Age")
    plt.show()


def formed_relations_data(s):
    """
    Returns a list of the number of relationships at every timestep
    """
    num_weeks = min(s.time, int(math.ceil(52 * s.NUMBER_OF_YEARS)))
    relations = [0] * num_weeks
    for r in s.relationships:
        start = r[2]
        end = min((r[3], num_weeks))
        #print start,ends
        for t in range(start, end):
            relations[t] += 1

    return relations

def formed_relations_graph(s):
    """
    Generates a plot of the number of relationships over time
    """
    num_weeks = min(s.time,int(math.ceil(52*s.NUMBER_OF_YEARS)))
    relations = formed_relations_data(s)

    plt.figure()
    plt.plot(np.arange(0,num_weeks)/52.0,relations)
    plt.xlabel('Time (Years)')
    plt.ylabel('Number of relationships')
    plt.title('Formed Relations')

def infection_data(s):
    """
    Returns a list with total number of infections at every timestep.
    """
    num_weeks = min(s.time,int(math.ceil(52*s.NUMBER_OF_YEARS)))
    counts = [0]*num_weeks
    agents = s.agents.values()
    for agent in agents:
        if agent.time_of_infection >= np.Inf: continue
        start = int(agent.time_of_infection)
        end = int(min(num_weeks, agent.attributes["TIME_REMOVED"]))
        for t in range(start, end):
            counts[t]+=1.0
    return counts

def population_data(s):
    """
    Returns a list with total number of individuals at every timestep.
    """
    num_weeks = min(s.time,int(math.ceil(52*s.NUMBER_OF_YEARS)))
    counts = [0]*num_weeks
    agents = s.agents.values()
    for agent in agents:
        start = agent.attributes["TIME_ADDED"]
        end = min(num_weeks,agent.attributes["TIME_REMOVED"])
        for t in range(start, end):
            counts[t]+=1.0
    return counts

def prevalence_data(s):
    """
    Returns a list with prevalence at every time step.
    """
    infections = np.array(infection_data(s))
    population = np.array(population_data(s))
    prevalence = infections / population
    return prevalence

def prevalence_graph(s):
    """
    Generates a graph of prevalence over time
    """
    num_weeks = min(s.time,int(math.ceil(52*s.NUMBER_OF_YEARS)))
    prev = prevalence_data(s)
    plt.figure()
    plt.plot(np.arange(0,num_weeks)/52.0,prev)
    plt.ylim(0,1)
    plt.xlabel('Time (Years)')
    plt.ylabel('Prevalence (%)')
    plt.title('Prevalence')

def demographics_data(s,time_granularity = 4,num_boxes = 7,box_size = 10):
    """
    Returns a list of lists, with the first dimension being time, the second
    dimension being age groups.
    """
    data = []
    now = min(s.time,int(math.ceil(52*s.NUMBER_OF_YEARS))) #determine if we are at the end of the simulation or in the middle
    for t in range(0,now,time_granularity):
        demographic = [0]*num_boxes; #create an list with the number of slots we want

        #go through agents...
        agents = s.agents.values()
        for agent in agents:
            age = s.age(agent)*52;  #convert age to weeks
            age_at_t = age - now + t;

            if (agent.attributes["TIME_ADDED"]>= t or agent.attributes["TIME_REMOVED"] <= t):
                continue  # skip if the agent wasn't born yet or has been removed

            age_at_t /= 52  # convert back to years
            level = min(num_boxes-1,int(math.floor( age_at_t / box_size)));
            demographic[level] += 1;  # ...and add them to their delineations level

        #add the delineations to the data
        data.append(demographic)
    return data

def demographics_graph(s,time_granularity = 4,num_boxes = 7,box_size = 10):
    num_weeks = min(s.time,int(math.ceil(52*s.NUMBER_OF_YEARS)))
    demographics = demographics_data(s,time_granularity,num_boxes,box_size)
    colors = ['b','g','r','c','m','y']
    bottom = [0]*len(demographics)
    plt.figure()
    legend = []
    for l in range(num_boxes):
        legend.append(str(l*box_size) + " - " + str((l+1)*box_size))
        data = []
        for t in range(len(demographics)):
            data.append(demographics[t][l])
        plt.bar(left = range(0, num_weeks ,time_granularity), height = data,
                bottom=bottom, width=time_granularity,
                color=colors[l%len(colors)], linewidth=0.0, zorder=0.0)
        bottom = [data[i] + bottom[i] for i in range(len(bottom))]

    #make the figure
    plt.xlim(0,num_weeks)
    plt.ylim(1,max(bottom))
    plt.xlabel("Time (weeks)")
    plt.legend(legend,title = 'Age Groups')
    plt.ylabel("Number (count)")
    plt.title("Demographics")

def sexual_network_graph(s):
    #rebuild the graph for visualization
    G = nx.Graph()
    for r in s.relationships:
        if r[0].gender: male=r[1]; female=r[0];
        else: female=r[1]; male=r[0];

        G.add_edge(str(male.attributes["NAME"])+"M",str(female.attributes["NAME"])+"F")

    #actually draw the thng
    pos = nx.spring_layout(G)
#    nx.draw_networkx_nodes(G, pos, nodelist=[n for n in G.nodes() if 'F' in n], node_color='r')
#    nx.draw_networkx_nodes(G, pos, nodelist=[n for n in G.nodes() if 'M' in n], node_color='b')
#    nx.draw_networkx_edges(G, pos, with_labels = True)
    colors = []
    for n in G.nodes():
        if "M" in n: colors.append('c')
        if "F" in n: colors.append('r')
    nx.draw(G, pos, node_color = colors, node_size = 800)
