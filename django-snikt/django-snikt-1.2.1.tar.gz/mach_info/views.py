from django.shortcuts import *
from django.db.models import Max
from mach_info.models import *
from django.http import HttpResponse
from time import *
from datetime import datetime
import json

def demo_status(request,svc_tag):
    if request.method =='GET':
        # run loop that changes the status of a job periodically until it is 
        #  done
        isDone = False
        done = Step.objects.all().aggregate(Max('id')).values()[0]
        while(isDone == False):
            job = JobTracker.objects.get(svctag=svc_tag)
            if(job.status.id != done):
                sleep(29)
                job.status = Step.objects.get(id=job.status.id+1)
                job.save()
            else:
                isDone = True
        
        data = {'message':"updated fully"}
        return HttpResponse(json.dumps(data))
                

def delete(request,num, svc_tag):
    if request.method == 'GET':
        # delete specified machine from the machine table
        machine = Machine.objects.get(svctag=svc_tag)
        machine.delete()
        message = "Success"
        data = {'num':num,'message':message}
        return HttpResponse(json.dumps(data))

def allstatus(request):
    # get status of all the jobs that are running at the moment
    # need to take into account machines that have been deleted from the 
    #  UI, the job will remain but the machine will be deleted from
    #  the machine table 
    if request.method =='GET':
        done = Step.objects.all().aggregate(Max('id')).values()[0]
        inprogress = JobTracker.objects.all()
        
        jobs = [{'name':job.svctag,'status':job.status.id,
                 'message':job.status.description} for job in inprogress 
                if Machine.objects.filter(svctag=job.svctag).exists()]
        data = {'jobs':jobs,'done':done}
        return HttpResponse(json.dumps(data))


def sent(request,num):
    if request.method == 'POST':
        message = "Request Started"
        
        host_name = "hostname"+num
        vlan_name = "vlan"+num
        os_name = "os"+num
        app_prof_name = "app_prof"+num
    
        host = request.POST[host_name]
        vlan = request.POST[vlan_name]
        os = request.POST[os_name]
        app_prof = request.POST[app_prof_name]
        
        svc_tag = request.POST['svctag'+num]        
        os_fam, os_ver = os.split(":")
         
        currenttime = datetime.now()
        # add a new job to the job_tracker table
        new_job = JobTracker(svctag=svc_tag,status=Step.objects.get(id=1),
                  mod_time=currenttime,started=currenttime,
                  os_id=Os.objects.get(family=os_fam,version=os_ver), 
                  net_info_id=NetInfo.objects.get(vlan=vlan), 
                  profile=Profile.objects.get(name=app_prof),hostname=host)
        
        new_job.save()
        
        message = Step.objects.get(id=1).description
        done = Step.objects.all().aggregate(Max('id')).values()[0]
        data = {'status':1,'done':done, 'message':message, 'num': num}
        return HttpResponse(json.dumps(data))
       

def home(request):
    svctag_values = Machine.objects.values_list('svctag',flat=True)
    
    exclude = ['svctag','hw_model_id','mac']
    extra_fields = [field.name 
                    for field in Machine._meta.fields 
                    if field.name not in exclude]
    hw_fields = [field.name for field in HwModel._meta.fields]
    
    hw_values = [[HwModel.objects.filter(
                model=Machine.objects.get(
                svctag=svc_tag).hw_model_id.model).values_list(
                hw,flat=True)[0]
                for hw in hw_fields]
                for svc_tag in svctag_values]
    extra_values = [[Machine.objects.filter( 
                   svctag=svc_tag).values_list(extra,flat=True)[0] 
                   for extra in extra_fields]
                   for svc_tag in svctag_values]
    # only get the names and ports of the switch if a MAC address of a 
    #  machine has an entry in the switch_port table otherwise use ""
    sw_names=[]
    for svc_tag in svctag_values:
        if SwitchPort.objects.filter(mac__iexact=Machine.objects.get(
           svctag=svc_tag).mac).exists():
            sw_names.append(SwitchPort.objects.get(
            mac__iexact=Machine.objects.get(svctag=svc_tag).mac).name)
        else:
            sw_names.append("Unavailable")
    sw_ports=[]
    for svc_tag in svctag_values:
        if SwitchPort.objects.filter(mac__iexact=Machine.objects.get(
           svctag=svc_tag).mac).exists():
            sw_ports.append("Gi"+str(SwitchPort.objects.get(
                mac__iexact=Machine.objects.get(svctag=svc_tag).mac).module)
                +"/"+str(SwitchPort.objects.get(
                mac__iexact=Machine.objects.get(svctag=svc_tag).mac).port))
        else:
            sw_ports.append("Unavailable")
    vlans = [list(Switch.objects.filter(sw_name=sw).values_list(
            'vlan',flat=True).distinct()) for sw in sw_names]
    
    
    headers = ['Service Tag'] + extra_fields + hw_fields
             
    table_values = [extra+hw for extra,hw in zip(extra_values,hw_values)]
    other = [zip(extra_fields+hw_fields,vals) for vals in table_values]
    data = [dict(svctag=svc_tag,
                 sw_name=sw,
                 sw_port=port,
                 vlans=v,
                 values=vals,
                 other=o_val) 
            for svc_tag,sw,port,v,vals,o_val in 
            zip(svctag_values,sw_names,sw_ports,vlans,table_values,other)]
    

    
    # lists of potential user input, meant for drop down lists    
    avail_os = [family+':'+version for (family,version) in
                Os.objects.values_list('family','version').distinct()]
    avail_profiles = list(Profile.objects.values_list(
                     'name', flat=True).distinct())
    
    # create list of currently running jobs in order to display in progress/
    #  completed jobs when the home view is started or refreshed, so they  
    #  cannot be submitted again
    svctags = JobTracker.objects.values_list('svctag',flat=True)
    # only take jobs for machines that have not been deleted from the 
    #  machine table
    job_svctags = [svc for svc in svctags 
                   if Machine.objects.filter(svctag=svc).exists()]
    job_hosts = [JobTracker.objects.get(svctag=svc_tag).hostname 
                 for svc_tag in job_svctags]
    job_os = [JobTracker.objects.get(svctag=svc_tag).os_id.family+':'+
              JobTracker.objects.get(svctag=svc_tag).os_id.version 
              for svc_tag in job_svctags]
    job_profs = [JobTracker.objects.get(svctag=svc_tag).profile.name 
                 for svc_tag in job_svctags
                 if JobTracker.objects.get(svctag=svc_tag).profile != ""]
    job_vlans = [JobTracker.objects.get(svctag=svc_tag).net_info_id.vlan 
                 for svc_tag in job_svctags]
    
    current_jobs=[dict(svctag=svc_tag,hostname=host,os=o,prof=pr,vlan=v) 
                  for svc_tag,host,o,pr,v in 
                  zip(job_svctags,job_hosts,job_os,job_profs,job_vlans)]
    
    # build up history of completed jobs
    done = Step.objects.all().aggregate(Max('id')).values()[0]
    
    finished_jobs = [job for job in JobTracker.objects.all() 
                     if job.status.id == done]
    history = [{'svctag':job.svctag,
                'os':job.os_id.family+":"+job.os_id.version,
                'vlan':job.net_info_id.vlan,
                'app_prof':job.profile.name,
                'hostname':job.hostname,
                'started':job.started,
                'elap_time':str(job.mod_time-job.started)}
               for job in finished_jobs]
    
    context = {'data': data,
               'headers': headers,
               'avail_os': avail_os,
               'avail_profiles':avail_profiles,
               'current_jobs': current_jobs,
               'history':history,
               }
    
    return render(request, 'mach_info/home.html',context)