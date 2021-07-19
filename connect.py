'''
    connect.py

    Establishes a connection from FS2020 to the FltPlan Go app.
'''
import socket
import logging
import sys
import threading
from math import *
import struct

from SimConnect import *
from SimConnect.Enum import *

XPLANE_PORT = 49003
UPDATE_RATE = 5     # in Hz
REFRESH_TIME = 1 / UPDATE_RATE

# Data Vector Bytes Initialization
speed_vector = []
attitude_vector = []
gps_vector = []

# List of addresses on the network that will receive updates
receivers = []

# The network socket
fpgSock = None

# Will send an XGPS message when this equals 0
# shouldUpdatePos = 0

# Sim var key, minimum range, maximum range
simVarKeys = [
    ['PLANE_LATITUDE',-90,90],
    ['PLANE_LONGITUDE',-180,180],
    ['PLANE_ALTITUDE',-1360, 99999],
    ['INDICATED_ALTITUDE',-1360, 99999],
    ['PLANE_ALT_ABOVE_GROUND',-1360, 99999],
    ['PLANE_HEADING_DEGREES_TRUE',-6.283185,6.283185],
    ['PLANE_HEADING_DEGREES_MAGNETIC',-6.283185,6.283185],
    ['GROUND_VELOCITY',0,800],
    ['AIRSPEED_INDICATED',0,800],
    ['AIRSPEED_TRUE',0,800],
    ['AIRSPEED_TRUE_CALIBRATE',0,800],
    ['PLANE_PITCH_DEGREES',-6.283185,6.283185],
    ['PLANE_BANK_DEGREES',-6.283185,6.283185] ]

# List of registered simvars
simvars = {}

def fatalError(msg):
    print(msg)
    RUNNING = False
    sm.exit()

def sendToFltplan(msg):
    packet = bytes(msg,'utf-8')
    for dest in receivers:
        try:
            fpgSock.sendto(packet, dest)
        except socket.error as msg:
            fatalError(msg)

def sendToeWac(msg):
    packet = msg
    for dest in receivers:
        try:
            fpgSock.sendto(packet, dest)
        except socket.error as msg:
            fatalError(msg)
            
def numFormat(num,r=5):
    return str(round(num,r))

def outsideRange(val, small, big):
    return (val < small) or (val > big)

def getSimvar(key):
    sv = simvars[key]
    try:
        val = sv.value
    except:
        fatalError("Can't refresh sim variable: " + key)
    if outsideRange(val, sv.minRange, sv.maxRange):
        # if failed to update, use previously cached value
        val = sv.cachedVal
    sv.cachedVal = val
    return val

def nextUpdate():
    global RUNNING

    if RUNNING and not sm.quit:
        vT = threading.Timer(REFRESH_TIME, refreshVars)
        vT.start()
        return vT
    return None

def refreshVars():
    #global shouldUpdatePos

    # Get crucial simvars via SimConnect
    #if shouldUpdatePos == 0:
    lat = getSimvar('PLANE_LATITUDE')
    lon = getSimvar('PLANE_LONGITUDE')
    alt_msl = getSimvar('PLANE_ALTITUDE')
    alt_agl = getSimvar('PLANE_ALT_ABOVE_GROUND')
    alt_ind = getSimvar('INDICATED_ALTITUDE')

    hdg_true = degrees( getSimvar('PLANE_HEADING_DEGREES_TRUE') )
    hdg_mag = degrees( getSimvar('PLANE_HEADING_DEGREES_MAGNETIC'))

    pitch = -degrees( getSimvar('PLANE_PITCH_DEGREES') )    # X-Plane flips the sign
    bank = -degrees( getSimvar('PLANE_BANK_DEGREES') )      
    
    spd_gs = getSimvar('GROUND_VELOCITY')
    spd_ind = getSimvar("AIRSPEED_INDICATED")
    spd_tas = getSimvar("AIRSPEED_TRUE")
    spd_cal = getSimvar("AIRSPEED_TRUE_CALIBRATE")

    # Send pseudo-NMEA sentences masquerading as X-Plane.
    # X-Plane uses a modified version of the ForeFlight protocol: 
    # https://www.foreflight.com/support/network-gps/

    #b'XGPS1,-73.878280,40.782172,2.2004,122.2988,0.0692'
    #if shouldUpdatePos == 0:
        # XGPS messages sent once per second
        #sendToFltplan( "XGPS1," + numFormat(lon) + "," + numFormat(lat) + "," + numFormat(alt,2) + "," + numFormat(hdg,2) + "," + numFormat(spd,2) )

    #b'XATT1,122.3,-6.1,0.3,-0.0014,0.0629,-0.0003,-0.0,0.1,-0.0,-0.02,1.86,0.21'
    # XATT messages sent at the current update rate (per protocol, anywhere from 4-10 Hz)
    #sendToFltplan( "XATT1," + numFormat(hdg,2) + "," + numFormat(pitch,2) + "," + numFormat(bank,2) + ",0,0,0," + numFormat(-spd,2)+","+numFormat(pitch,2)+",0,0,0,0" )

    #Send to EWAC (old DATA format Xplane)
    # ex: b"DATA*\x03\x00\x00\x00\xba\xe0\xf3B\x1c%\xf4B\x7f\x10\xfeB\x84\xad\xf1B\x00\xc0y\xc4'S\x0cC\xa2/\x12C3L\x0bC\x11\x00\x00\x00\x08\xcf\xff?\x0f\x9c\x97\xc0\xa7\xdamC\x15\x9c\x81C\x00\xc0y\xc4\x00\xc0y\xc4\x00\xc0y\xc4\x00\xc0y\xc4\x14\x00\x00\x00\xa9\xa5\xb9\xc1\xdb\xd3;\xc2\xf9\xc4\xacD@d\xacD\x00\x00\x00\x00\r\x1c\x99D\x00\x00\xbc\xc1\x00\x00<\xc2"
    
    # XPlane Speed Vector (DATA FORMAT)
    speed_vector.clear()

    speed_vector.append(spd_ind)
    speed_vector.append(spd_cal)
    speed_vector.append(spd_tas)
    speed_vector.append(spd_gs)
    speed_vector.append(-999.0)
    speed_vector.append(spd_ind * 1.1578)
    speed_vector.append(spd_tas * 1.1578)
    speed_vector.append(spd_gs * 1.1578)

    speed = struct.pack("<iffffffff", 3, speed_vector[0], speed_vector[1], speed_vector[2], speed_vector[3], speed_vector[4], speed_vector[5], speed_vector[6], speed_vector[7])

    # XPlane Attitude Vector (DATA FORMAT)
    attitude_vector.clear()

    attitude_vector.append(pitch)
    attitude_vector.append(bank)
    attitude_vector.append(hdg_true)
    attitude_vector.append(hdg_mag)
    attitude_vector.append(-999.0)
    attitude_vector.append(-999.0)
    attitude_vector.append(-999.0)
    attitude_vector.append(-999.0)

    attitude = struct.pack("<iffffffff", 17,  attitude_vector[0], attitude_vector[1], attitude_vector[2], attitude_vector[3], attitude_vector[4], attitude_vector[5], attitude_vector[6], attitude_vector[7])
    
    #XPLane GPS Vector (DATA FORMAT)
    gps_vector.clear()

    gps_vector.append(lat)
    gps_vector.append(lon)
    gps_vector.append(alt_msl)
    gps_vector.append(alt_agl)
    gps_vector.append(0.0)
    gps_vector.append(alt_ind)
    gps_vector.append(lat)
    gps_vector.append(lon)

    gps = struct.pack("<iffffffff", 20, gps_vector[0], gps_vector[1], gps_vector[2], gps_vector[3], gps_vector[4], gps_vector[5], gps_vector[6], gps_vector[7])
    
    #Join Bytes and Send (DATA FORMAT)
    inicio = bytes("DATA*",'ascii')
    full_message = inicio + speed + attitude + gps
    #print(full_message)

    #Debug Print
    #print()
    #print("Latitude: " + str(int(lat)) + "° " + str(abs(int((lat-int(lat))*60))) + "'")
    #print("Longitude: " + str(int(lon)) + "° " + str(abs(int((lon-int(lon))*60))) + "'")
    #print("Ground Speed: " + str(int(spd_gs)) + " kt")
    #print("Altitude (MSL): " + f"{int(alt_msl):,d}" + " ft")
    #print("Heading (mag): " + str(int(hdg_mag)) + "°")

    sendToeWac(full_message)
    
    #shouldUpdatePos = ( shouldUpdatePos + 1 ) % UPDATE_RATE

    # Continue to refresh if still running
    if nextUpdate() == None:
        sm.exit()

# Program begins here
RUNNING = True

print("")
print("--- eWac Connect for MSFS 2020 ---")

numIPs = len(sys.argv)-1
if numIPs == 0:
    sys.exit("Must specify the IP address of the eWac app!")
else:
    for i in range(numIPs):
        addr = sys.argv[i+1]
        receivers.append((addr, XPLANE_PORT))
        print("Connecting to " + addr + "...")

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)
LOGGER.info("START")

# connect to MSFS
sm = SimConnect()
aq = AircraftRequests(sm, _time=0)

# Create the UDP socket to communicate with FltPlan Go
try:
    fpgSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error as msg:
    fatalError(msg)

# Register simvars for updates
for k in simVarKeys:
    key, minRange, maxRange = k[0],k[1],k[2]
    sv = aq.find(key)
    if sv != None:
        sv.cachedVal = 0
        sv.minRange = minRange
        sv.maxRange = maxRange
        simvars[key] = sv
    else:
        fatalError("Can't access sim variable: " + key)

# Start refreshing on a thread
nextUpdate()
if RUNNING:
    input("Press Return to stop.\n")

# Flag the thread to stop when done
RUNNING = False
