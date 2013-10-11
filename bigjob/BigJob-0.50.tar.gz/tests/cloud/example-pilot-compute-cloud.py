import sys
import os
import time
import logging
import uuid
#logging.basicConfig(level=logging.DEBUG)

#sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from pilot import PilotComputeService, PilotDataService, ComputeDataService, State
from bigjob import logger 

COORDINATION_URL = "redis://ILikeBigJob_wITH-REdIS@gw68.quarry.iu.teragrid.org:6379"

if __name__ == "__main__":      
     
    pilot_compute_service = PilotComputeService(coordination_url=COORDINATION_URL)

    # create pilot job service and initiate a pilot job
    pilot_compute_description_amazon = {
                             "service_url": 'ec2+ssh://aws.amazon.com',
                             "number_of_processes": 1,                             
                             # cloud specific attributes
                             "vm_id":"ami-d0f89fb9",
                             "vm_ssh_username":"ubuntu",
                             "vm_ssh_keyname":"luckow",
                             "vm_ssh_keyfile":"/Users/luckow/.ssh/id_rsa",
                             "vm_type":"m1.small",
                             "access_key_id":"AKIAIEXAFM6C6HRSDOFA",
                             "secret_access_key":"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"
                            }
    
    
    pilotjob = pilot_compute_service.create_pilot(pilot_compute_description_amazon)
    
    compute_data_service = ComputeDataService()
    compute_data_service.add_pilot_compute_service(pilot_compute_service)
    
    
    # start work unit
    compute_unit_description = {
            "executable": "/bin/date",
            "arguments": [],
            "number_of_processes": 1,
            "output": "stdout.txt",
            "error": "stderr.txt",   
            "input_data": [],
            "output_data": []
    }    
    
    compute_unit = compute_data_service.submit_compute_unit(compute_unit_description)
    logging.info("Finished setup of ComputeDataService. Waiting for scheduling of PD")
    compute_data_service.wait()
    
    
    logging.info("Terminate Pilot Compute/Data Service")
    compute_data_service.cancel()
    pilot_compute_service.cancel()
