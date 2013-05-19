from nimbus._n7t import reader_n7t
from datetime import datetime

def read_totalO3_n7t_l3(fname):
    dt,lon,lat,o3 = reader_n7t(fname)
    dt = datetime.strptime(dt,'%b %d, %Y')
    return dt, lon, lat, o3