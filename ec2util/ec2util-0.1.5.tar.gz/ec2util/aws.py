#!/usr/bin/env

import time
import boto.ec2
import prettytable
from boto.exception import BotoServerError
from collections import namedtuple


State = namedtuple('State', 'code name')
SnapshotState = namedtuple('SnapshotState', 'state progress')

class aws:
	conn = None

	def __init__(self, key, secret, region):
		global conn

		conn = boto.ec2.connect_to_region(region_name = region, 
			aws_access_key_id = key, 
			aws_secret_access_key = secret)

	def getAccountId(self):
		instances = conn.get_all_instances()
		return instances[0].owner_id

	def getInstance(self, instance_id):
		instance = conn.get_all_instances(instance_ids=instance_id)
		return instance[0].instances[0]

	def getSnapshot(self, snapshot_id):
		snapshots = conn.get_all_snapshots(owner = self.getAccountId())
		selected = [s for s in snapshots if s.id == snapshot_id]
		return selected[0] if len(selected) > 0 else None

	def getAllSnapshots(self):
		return conn.get_all_snapshots(owner = self.getAccountId())
		
	def getVolume(self, volume_id):
		volumes = conn.get_all_volumes()
		selected = [v for v in volumes if v.id == volume_id]
		return selected[0] if len(selected) > 0 else None

	def checkInstanceState(self, instance):
		instance.update()
		return State(instance.state_code, instance.state)

	def checkInstanceStateById(self, instance_id):
		instance = getInstance(instance_id)
		return checkInstanceState(instance)

	def checkSnapshotState(self, snapshot):
		snapshot.update()
		return SnapshotState(snapshot.status, snapshot.progress)

	def checkVolumeState(self, volume):
		volume.update()
		return State("", volume.status)

	def getInstances(self):
		reservations = conn.get_all_instances()
		instances = []
		for reservation in reservations:
			for instance in reservation.instances:
				instances.append(instance)
		return instances	

	def startInstanceById(self, instance_id):
		print "Starting instance " + instance_id
		instance = self.getInstance(instance_id)
		instance.start() 
		self.checkForInstanceState(instance, "running")
		
	def stopInstanceById(self, instance_id):
		print "Stopping instance " + instance_id
		instance = self.getInstance(instance_id)
		instance.stop() 
		self.checkForInstanceState(instance, "stopped")

	def printInstances(self):
		table = prettytable.PrettyTable(['Id', 'Name', 'Type', 'State', 'IP'])
		table.padding_width = 1
		table.align["Name"] = "l" 
		instances = self.getInstances()
		for instance in instances:
			#print(instance.__dict__)
			table.add_row([instance.id, instance.tags['Name'], instance.instance_type, instance.state, instance.ip_address])
		print table

	def printImages(self):
		table = prettytable.PrettyTable(['Id', 'Name', 'Description', 'Root device'])
		table.padding_width = 1
		table.align["Name"] = "l"
		table.align["Description"] = "l"  
		images = conn.get_all_images(owners=['self'])
		for image in images:
			#print(image.__dict__)
			table.add_row([image.id, image.name, image.description, image.root_device_name])
		print table

	def printSnapshots(self):
		table = prettytable.PrettyTable(['Id', 'Name', 'Description', 'Status', 'Size'])
		table.padding_width = 1
		table.align["Name"] = "l"
		table.align["Description"] = "l"  
		snapshots = self.getAllSnapshots()
		for snapshot in snapshots:
			#print(snapshot.__dict__)
			table.add_row([snapshot.id, snapshot.tags.get('Name', ''), snapshot.description, snapshot.status, snapshot.volume_size])
		print table

	def printSecurityGroups(self):
		table = prettytable.PrettyTable(['Id', 'Name'])
		table.padding_width = 1
		table.align["Name"] = "l"
		table.align["Description"] = "l"  
		groups = conn.get_all_security_groups()
		for group in groups:
			#print(group.__dict__)
			table.add_row([group.id, group.name])
		print table

	def printVolumes(self, volumes = None):
		table = prettytable.PrettyTable(['Id', 'Status', 'Attached to', 'Mapping', 'Size', 'Created at', 'Snapshot'])
		table.padding_width = 1
		table.align["Name"] = "l" 
		table.align["Attached to"] = "l" 
		table.align["Size"] = "l" 
		
		if volumes is None:
			volumes = conn.get_all_volumes()
		
		for volume in volumes:
			#print(volume.__dict__)
			attachedTo = None
			if volume.attach_data.instance_id is not None:
				attachedTo = self.getInstance(str(volume.attach_data.instance_id)).tags['Name']
				attachedTo + "[" + volume.attach_data.instance_id + "]"
			table.add_row([volume.id, volume.status, attachedTo, volume.attach_data.device, volume.size, volume.create_time, volume.snapshot_id])
		print table


	def checkForInstanceState(self, instance, desiredState):
		while True:
			state = self.checkInstanceState(instance)
			if state.name == desiredState:
				print state.name
				return True
			else:
				print "..." + state.name
				time.sleep(5)

	def checkForSnapshotState(self, snapshot, desiredState):
		while True:
			state = self.checkSnapshotState(snapshot)
			if state.state == desiredState:
				print state.state
				return True
			else:
				progress = '0' if state.progress == '' else state.progress
				print "..." + state.state + " " + progress + "%" 
				time.sleep(5)

	def checkForVolumeState(self, volume, desiredState):
		while True:
			state = self.checkVolumeState(volume)
			if state.name == desiredState:
				print state.name
				return True
			else:
				print "..." + state.name
				time.sleep(5)

	def checkForInstanceStateById(self, instance_id, state):
		instance = self.getInstance(instance_id)
		return self.checkForInstanceState(instance, state)

	def printVolumesForInstance(self, instance_id):
		volumes = [v for v in conn.get_all_volumes() if v.attach_data.instance_id == instance_id]
		self.printVolumes(volumes)

	def createSnapshot(self, volume_id, name):
		print "Creating snapshot from volume: " + volume_id
		snapshot = conn.create_snapshot(volume_id, name)
		self.checkForSnapshotState(snapshot, "completed")
		print "Snapshot created: " + snapshot.id
		return snapshot

	def detachVolume(self, volume_id):
		print "Detaching " + volume_id
		volume = self.getVolume(volume_id)
		conn.detach_volume (volume_id)
		self.checkForVolumeState(volume, "available")
		print "Volume detached"
		return volume

	def attachVolume(self, volume_id, instance_id, mapping):
		print "Attaching " + volume_id + " to " + instance_id + ": " + mapping
		volume = self.getVolume(volume_id)
		conn.attach_volume (volume_id, instance_id, mapping)
		self.checkForVolumeState(volume, "in-use")
		print "Volume attached"
		return volume

	def deleteVolume(self, volume_id):
		answer = raw_input("Are you sure you want to delete volume " + volume_id + "? y/n [n]: ")
		if answer != 'y':
			print "canceling.."
			return
		print "Deleting " + volume_id
		volume = self.getVolume(volume_id)
		success = volume.delete()
		if success:
			print "Volume deleted"
		else:
			print "Action failed"

	def createVolume(self, size, az, snapshotId=None):
		print "Creating " + str(size) + "GB volume in " + az
		snapshot = None
		if snapshotId is not None:
			snapshot = self.getSnapshot(snapshotId)
			print "..from snapshot: " + snapshot.id
		volume = conn.create_volume(size, az, snapshot)
		self.checkForVolumeState(volume, "available")
		print "Volume created: " + volume.id
		return volume

	def enlargeVolume(self, volume_id, size):
		volume = self.getVolume(volume_id)
		az = volume.zone
		snapshot = self.createSnapshot(volume_id, "for " + volume_id + " enlargement")
		volume = self.createVolume(size, az, snapshot.id)
		print "Enlarged volume id: " + volume.id
