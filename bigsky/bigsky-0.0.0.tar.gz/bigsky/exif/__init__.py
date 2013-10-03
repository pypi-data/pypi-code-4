from bigsky.inputs.flickr import flickr_api
from flickrapi import Exif

import gflags
FLAGS = gflags.FLAGS

gflags.DEFINE_string('source', None, 'SQS source')
gflags.DEFINE_string('target', None, 'SQS target')

def main(argv=None, stdin=None, stdout=None, stderr=None):
    import sys
    argv = argv or sys.argv
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr

    try:
        argv = FLAGS(argv)[1:]
    except gflags.FlagsError, e:
        stderr.write("%s\\nUsage: %s update_id_addresses\\n%s\n" %
                     (e, sys.argv[0], FLAGS))
        return 1

    print Exif(flickr_api().photos_getexif(photo_id='9917281896', secret='d1de8886ea'))

# {'geo_is_public': '1', 'place_id': 'EVTg26FTVrrKlJUJ', 'owner': '98691973@N03', 'id': '9917281896', 'url_o': 'http://farm3.staticflickr.com/2843/9917281896_846681218a_o.jpg', 'height_o': '612', 'title': '#ParkThursdays presents The NFL Dinner Party | Happy Hour (5-7) Dinner (5-10) #Rama vs 49ers | Who do you have winning?', 'woeid': '2407011', 'geo_is_friend': '0', 'geo_is_contact': '0', 'farm': '3', 'secret': 'd1de8886ea', 'latitude': '38.90198', 'accuracy': '16', 'isfamily': '0', 'machine_tags': 'uploaded:by=instagram foursquare:venue=49e1a56af964a520e4611fe3', 'ispublic': '1', 'tags': 'square squareformat iphoneography instagramapp uploaded:by=instagram foursquare:venue=49e1a56af964a520e4611fe3', 'isfriend': '0', 'geo_is_family': '0', 'width_o': '612', 'url_z': 'http://farm3.staticflickr.com/2843/9917281896_d1de8886ea_z.jpg', 'url_t': 'http://farm3.staticflickr.com/2843/9917281896_d1de8886ea_t.jpg', 'url_s': 'http://farm3.staticflickr.com/2843/9917281896_d1de8886ea_m.jpg', 'longitude': '-77.031947', 'server': '2843', 'height_t': '100', 'width_z': '612', 'context': '0', 'height_s': '240', 'width_t': '100', 'width_s': '240', 'height_z': '612'}
# {'geo_is_public': '1', 'place_id': 'UIOIJfZTUbNG5tEI', 'owner': '46738730@N04', 'id': '9917408293', 'url_o': 'http://farm6.staticflickr.com/5535/9917408293_02392b6499_o.jpg', 'height_o': '612', 'title': '', 'woeid': '2396940', 'geo_is_friend': '0', 'geo_is_contact': '0', 'farm': '6', 'secret': '6fe38d556c', 'latitude': '43.055123', 'accuracy': '16', 'isfamily': '0', 'machine_tags': 'uploaded:by=instagram foursquare:venue=4b6aeb13f964a520d5e62be3', 'ispublic': '1', 'tags': 'valencia square squareformat iphoneography instagramapp uploaded:by=instagram foursquare:venue=4b6aeb13f964a520d5e62be3', 'isfriend': '0', 'geo_is_family': '0', 'width_o': '612', 'url_z': 'http://farm6.staticflickr.com/5535/9917408293_6fe38d556c_z.jpg', 'url_t': 'http://farm6.staticflickr.com/5535/9917408293_6fe38d556c_t.jpg', 'url_s': 'http://farm6.staticflickr.com/5535/9917408293_6fe38d556c_m.jpg', 'longitude': '-73.796367', 'server': '5535', 'height_t': '100', 'width_z': '612', 'context': '0', 'height_s': '240', 'width_t': '100', 'width_s': '240', 'height_z': '612'}
# {'isfamily': '0', 'machine_tags': '', 'geo_is_public': '1', 'tags': 'raleighbailbondsman bailbondsmanraleigh', 'isfriend': '0', 'url_s': 'http://farm8.staticflickr.com/7338/9911604453_24d4727579_m.jpg', 'place_id': 'v1jrmF5TVr3pkRpu', 'geo_is_family': '0', 'ispublic': '1', 'owner': '96587227@N06', 'id': '9911604453', 'width_o': '350', 'height_o': '300', 'title': 'Raleigh bail bonds', 'woeid': '2478307', 'url_t': 'http://farm8.staticflickr.com/7338/9911604453_24d4727579_t.jpg', 'geo_is_friend': '0', 'geo_is_contact': '0', 'longitude': '-78.745285', 'server': '7338', 'height_t': '86', 'farm': '8', 'secret': '24d4727579', 'context': '0', 'height_s': '206', 'latitude': '35.722591', 'url_o': 'http://farm8.staticflickr.com/7338/9911604453_39a0922032_o.jpg', 'width_t': '100', 'width_s': '240', 'accuracy': '16'}
# {'isfamily': '0', 'machine_tags': '', 'geo_is_public': '1', 'tags': 'raleighbailbondsman bailbondsmanraleigh', 'isfriend': '0', 'url_s': 'http://farm8.staticflickr.com/7321/9911513804_c599d365b1_m.jpg', 'place_id': 'v1jrmF5TVr3pkRpu', 'geo_is_family': '0', 'ispublic': '1', 'owner': '96587227@N06', 'id': '9911513804', 'width_o': '350', 'height_o': '300', 'title': 'Raleigh bail bonds', 'woeid': '2478307', 'url_t': 'http://farm8.staticflickr.com/7321/9911513804_c599d365b1_t.jpg', 'geo_is_friend': '0', 'geo_is_contact': '0', 'longitude': '-78.745285', 'server': '7321', 'height_t': '86', 'farm': '8', 'secret': 'c599d365b1', 'context': '0', 'height_s': '206', 'latitude': '35.722591', 'url_o': 'http://farm8.staticflickr.com/7321/9911513804_0f7c0b27d2_o.jpg', 'width_t': '100', 'width_s': '240', 'accuracy': '16'}
# {'isfamily': '0', 'machine_tags': '', 'geo_is_public': '1', 'tags': 'raleighbailbondsman bailbondsmanraleigh', 'isfriend': '0', 'url_s': 'http://farm4.staticflickr.com/3819/9911604973_55fd86d104_m.jpg', 'place_id': 'v1jrmF5TVr3pkRpu', 'geo_is_family': '0', 'ispublic': '1', 'owner': '96587227@N06', 'id': '9911604973', 'width_o': '350', 'height_o': '300', 'title': 'Raleigh bail bonds', 'woeid': '2478307', 'url_t': 'http://farm4.staticflickr.com/3819/9911604973_55fd86d104_t.jpg', 'geo_is_friend': '0', 'geo_is_contact': '0', 'longitude': '-78.745285', 'server': '3819', 'height_t': '86', 'farm': '4', 'secret': '55fd86d104', 'context': '0', 'height_s': '206', 'latitude': '35.722591', 'url_o': 'http://farm4.staticflickr.com/3819/9911604973_be1a182d2b_o.jpg', 'width_t': '100', 'width_s': '240', 'accuracy': '16'}

