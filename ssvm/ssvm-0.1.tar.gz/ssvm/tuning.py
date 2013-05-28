from SSVMTrainer import *
from LoadData import *
import numpy
import pp
import time


def hibiscus():
    pass

"""
def GridSearch(trainer,start_exp,end_exp):
    value=0
    record=[1,1]
    C_point=2**start_exp
    EndPoint=2**end_exp

    while C_point<=EndPoint:
        G_point=2**start_exp
        while G_point <=EndPoint:
            trainer.setting(C_point,G_point,1)
            temp=trainer.start()
            if temp[1]>value:
                value=temp[1]
                record[0]=C_point
                record[1]=G_point
            G_point=G_point*2
        C_point=C_point*2


    return record
"""

def GridSearch(trainer, C_start, C_end ,G_start ,k,s):
    #job_server = pp.Server()
    job_server=pp.Server(ppservers=("localhost",))
    value = 0
    C = 1
    G = 1
    task = []
    C_point = 2**C_start
    G_point = 2**G_start
    EndPoint= 2**C_end
    if k == 1:
        while C_point <= EndPoint:
            G_point = 2**G_start
            while G_point <= 1:
                trainer.setting( C_point, G_point, 1, s )
                task.append( job_server.submit( trainer.train, (), (), ('numpy','SSVMTrainer',) ) )
                G_point = G_point * 2
            C_point = C_point * 2

    elif k == 0:
        while C_point <= EndPoint:
            trainer.setting( C_point, G_point, 0, s )
            task.append( job_server.submit( trainer.train, (), (), ('numpy','SSVMTrainer',) ) )
            C_point = C_point * 2


    else:
        print 'YA'

    count = 0
    C_point = 2**C_start
    if k == 1:
        while C_point <= EndPoint: 
            G_point =2**G_start
            while G_point <= 1:
                print count
                if task[count]()[1] > value:
                    value = task[count]()[1]
                    C = C_point
                    G = G_point
                G_point = G_point * 2
                count = count + 1
            C_point = C_point * 2

    elif k == 0:
        while C_point <= EndPoint: 
            print count
            if task[count]()[1] > value:
                value = task[count]()[1]
                C = C_point
            count = count + 1
            C_point = C_point * 2

    else:
        print 'YA'

    return [C,G]



##########################################Test Area##########################################


csv_file = open( 'pen.csv', 'rb' )
data = numpy.loadtxt( csv_file, delimiter = ';', skiprows = 1 )
trainer=SSVMTrainer(data,16)
trainer.initialize(r=0.1,v=10)

start=time.time()
record=GridSearch(trainer,-10,7,-8,0,1)
stop=time.time()
print stop-start

trainer.setting(record[0],record[1],0,1)
print record
print trainer.train()

