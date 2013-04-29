import math

earth_radius = 3960.0
degrees_to_radians = math.pi/180.0
radians_to_degrees = 180.0/math.pi
 
def change_in_latitude(miles):
    "Given a distance north, return the change in latitude."
    return (miles/earth_radius)*radians_to_degrees

def change_in_longitude(latitude, miles):
    "Given a latitude and a distance west, return the change in longitude."
    # Find the radius of a circle around the earth at given latitude.
    r = earth_radius*math.cos(latitude*degrees_to_radians)
    return (miles/r)*radians_to_degrees

def get_distance(lng1,lat1,lng2,lat2):
    radlat1 = lat1*degrees_to_radians
    radlat2 = lat2*degrees_to_radians
    a = radlat1 - radlat2
    b = lng1*degrees_to_radians - lng2*degrees_to_radians
    s = 2*math.asin(math.sqrt(math.pow(math.sin(a/2),2)+math.cos(radlat1)*math.cos(radlat2)*math.pow(math.sin(b/2),2)))
    earth_radius = 6378.137
    s = s * earth_radius * 1000
    if s < 0:
        return -s
    else:
        return s