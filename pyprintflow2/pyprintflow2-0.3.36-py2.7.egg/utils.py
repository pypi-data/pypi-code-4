'''
Created on Sep 21, 2013

@author: "Colin Manning"
'''
import os
import shutil

short_month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
long_month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

STYLE_DATE_TIME_NUMBERS = 'date_time_numbers'
STYLE_DATE_TIME_SHORT_MONTH = 'date_time_short_month'
STYLE_DATE_TIME_LONG_MONTH = 'date_time_long_month'
STYLE_DATE_TIME_DEFAULT = STYLE_DATE_TIME_NUMBERS

def parse_date_time_numbers(s):
    return s[6:8] + '-' + s[4:6] + '-' + s[0:4] + ' ' + s[8:10] + ':' + s[10:12] + ':' + s[12:]

def parse_date_time_short_month(s):
    return s[6:8] + ' ' + short_month_names[int(s[4:6])-1] + ' ' + s[0:4] + ' ' + s[8:10] + ':' + s[10:12] + ':' + s[12:]

def parse_date_time_long_month(s):
    return s[6:8] + ' ' + long_month_names[int(s[4:6])-1] + ' ' + s[0:4] + ' ' + s[8:10] + ':' + s[10:12] + ':' + s[12:]

parse_date_time_functions = {
                             STYLE_DATE_TIME_NUMBERS : parse_date_time_numbers,
                             STYLE_DATE_TIME_SHORT_MONTH : parse_date_time_short_month,
                             STYLE_DATE_TIME_LONG_MONTH : parse_date_time_long_month
}

def get_email_company_footer(logo, web_address):
    return ('<br /> \
<div><img alt="" src="%s" (="" 62="" in="1.57" m)=" 113="" height="62" width="113"></div> \
<div><span style="font-family: Calibri;">Print Outsource International (POINT) </span></div> \
<div><span style="font-family: Calibri;">Leaders in Managed Print Solutions </span></div> \
<div><span style="font-family: Calibri;"><a href="http://%s">%s</a></div>'
    % (logo, web_address, web_address))

# our time format is YYYYMMDDHHMMSS
def parse_time(s, style=STYLE_DATE_TIME_NUMBERS):
    return parse_date_time_functions.get(style, STYLE_DATE_TIME_NUMBERS)(s)

def ensureDirectoryExists(path):
    if not os.path.exists(path):
        os.makedirs(path, mode=0o755)
        
def ensureDirectoryExistsForUser(path, userid, groupid, permissions):
    #print 'COLIN>>>>> ensuring path: ', path
    if not os.path.exists(path):
        os.makedirs(path, mode=permissions)
        os.chown(path, userid, groupid)

def safe_file_move(source_file, destination_folder):
    path_bits = source_file.split('/')
    file_name = path_bits[-1]
    new_file_path = os.path.join(destination_folder, file_name)
    if os.path.exists(new_file_path):
        name_bits = file_name.split('.')
        if len(name_bits) > 1:
            ext = name_bits[-1]
        else:
            ext = None
        nfw_file_version = 0
        while os.path.exists(new_file_path):
            nfw_file_version += 1
            new_file_name = name_bits[0] + '_' + str(nfw_file_version)
            if ext is not None:
                new_file_name += '.' + ext
            new_file_path = os.path.join(destination_folder, new_file_name)
    shutil.move(source_file, new_file_path)

def get_guid_path(parent, guid):
    return os.path.join(parent, guid.replace('-', '/'))

def get_guid_url(parent, guid):
    return parent + '/' + guid.replace('-', '/')

                        