import requests
import json


class AlexandriaUploadException(Exception):
	pass

def get_api_auth(user_name, api_key):
	return "ApiKey %s:%s" % (user_name, api_key)


def upload_file(filename, build_id, artifact_type, 
				archive_url, upload_user, api_key):
	post_data = {'type': artifact_type, 'build_number': build_id}

	post_url = archive_url + "/upload/"
	
	try:
		payload_data = open(filename, 'rb')
	except:
		raise AlexandriaUploadException("Error opening file: %s" % filename)

	auth_header = get_api_auth(upload_user, api_key)

	r = requests.post(	post_url, 
						data=post_data, 
						headers={'Authorization': auth_header},
						files={'payload': open(filename, 'rb')})
	
	if r.status_code > 300:
		raise AlexandriaUploadException("Error uploading %s: %s" % (artifact_type, r.text))


def create_build_and_upload(build_data, archive_url, upload_user, api_key):
	build_name = build_data['name']
	build_metadata = build_data['metadata']
	build_extradata = build_data['extra_data']
	
	metadata_list = []
	for k, v in build_metadata.iteritems():
		metadata_list.append({'category': k, 'value': v})

	extradata_list = []
	for k, v in build_extradata.iteritems():
		extradata_list.append({'ed_type': k, 'value': v})
		
	build_post_data = {'name': build_name, 
						'metadata': metadata_list,
						'extra_data': extradata_list,
						'artifacts':[]}

	build_post_url = "%s/api/v0/build/?username=%s&api_key=%s" % (archive_url, upload_user, api_key)
	
	auth_header = get_api_auth(upload_user, api_key)

	r = requests.post(	build_post_url,
						data=json.dumps(build_post_data), 
						headers={"Authorization": auth_header, 
								'content-type': 'application/json'})

	try:
		build_id = r.json()["id"]
	except:
		raise AlexandriaUploadException(
					"Build creation was unsuccessful: %s" %(r.text))
	
	
	
	artifacts = build_data["artifacts"]
	for k, v in artifacts.iteritems():
		upload_file(v, build_id, k, archive_url, upload_user, api_key)


def upload_with_build_file(filename, archive_url, upload_user, api_key):
	build_data = json.load(open(filename))
	create_build_and_upload(build_data, archive_url, upload_user, api_key)

