import googlemaps
from googlemaps.convert import decode_polyline, encode_polyline
import json
from datetime import datetime
import math
import numpy
from collections import OrderedDict
import sys
import web3 as y
from web3 import Web3
import json
from eth_abi import encode_abi

web3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))  # Verify if your Ganache is at 7545 too, should be
with open('contract1.json') as f:
    contractDetails = json.load(f)
    contractAddress = (contractDetails["address"])
    abi = contractDetails["abi"]

Contract = web3.eth.contract(bytecode=contractAddress, abi=abi)


def updateStatus(dest_lat, dest_long, curr_lat, curr_long):
    print(dest_lat, dest_long, curr_lat, curr_long)
    _company = web3.eth.accounts[1]
    _cost = 1000000000000000000
    _lat = dest_lat
    _long = dest_long

    tx_hash = Contract.constructor(_company=_company, _cost=_cost, _lat=_lat, _long=_long).transact(
        transaction={'from': web3.eth.accounts[0], 'gas': 410000})

    # Get tx receipt to get contract address
    tx_receipt = web3.eth.getTransactionReceipt(tx_hash)
    contract = web3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=abi,
    )
    contract.functions.updateStatus(curr_lat, curr_long).transact(
        transaction={'from': web3.eth.accounts[0], 'gas': 410000, 'value': 10000000000000000000})



def _calculate_distance(origin, destination):
    """
    Calculate the Haversine distance.
    This isn't accurate for large distances, but for our purposes it is good enough
    """
    lat1, lon1 = origin['lat'], origin['lng']
    lat2, lon2 = destination['lat'], destination['lng']
    radius = 6371000  # metres

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d


def _round_up_time(time, period):
    """
    Rounds up time to the higher multiple of period
    For example, if period=5, then time=16s will be rounded to 20s
    if time=15, then time will remain 15
    """
    # If time is an exact multiple of period, don't round up
    if time % period == 0:
        return time

    time = round(time)
    return time + period - (time % period)


def _fill_missing_times(times, lats, lngs, period):
    start_time = times[0]
    end_time = times[-1]

    new_times = range(start_time, end_time + 1, period)
    new_lats = numpy.interp(new_times, times, lats).tolist()
    new_lngs = numpy.interp(new_times, times, lngs).tolist()

    return new_times, new_lats, new_lngs



def get_points_along_path(maps_api_key, _from, _to, departure_time=None, period=5):
    """
    Generates a series of points along the route, such that it would take approx `period` seconds to travel between consecutive points

    This function is primarily meant to simulate a car along a route. The output of this function is equivalent to the geo coordinates
    of the car every 5 seconds (assuming period = 5)

    _from = human friendly from address that google maps can understand
    _to = human friendly to address that google maps can understand
    departure_time - primarily used to identify traffic model, defaults to current time
    period = how frequently should co-ordinates be tracked? Defaults to 5 seconds

    The output is an OrderedDict. Key is the time in seconds since trip start, value is a tuple representing (lat, long) in float

    # >>> python vehicles.py "hashedin technologies, bangalore" "cubbon park"
    """
    if not departure_time:
        departure_time = datetime.now()

    gmaps = googlemaps.Client(key=maps_api_key)
    directions = gmaps.directions(_from, _to, departure_time=departure_time)

    steps = directions[0]['legs'][0]['steps']
    all_lats = []
    all_lngs = []
    all_times = []

    step_start_duration = 0
    step_end_duration = 0

    for step in steps:
        step_end_duration += step['duration']['value']
        points = decode_polyline(step['polyline']['points'])
        distances = []
        lats = []
        lngs = []
        start = None
        for point in points:
            if not start:
                start = point
                distance = 0
            else:
                distance = _calculate_distance(start, point)
            distances.append(distance)
            lats.append(point['lat'])
            lngs.append(point['lng'])

        missing_times = numpy.interp(distances[1:-1], [distances[0], distances[-1]],
                                     [step_start_duration, step_end_duration]).tolist()
        times = [step_start_duration] + missing_times + [step_end_duration]
        times = [_round_up_time(t, period) for t in times]

        times, lats, lngs = _fill_missing_times(times, lats, lngs, period)

        all_lats += lats
        all_lngs += lngs
        all_times += times

        step_start_duration = step_end_duration

    points = OrderedDict()
    for p in zip(all_times, all_lats, all_lngs):
        points[p[0]] = (round(p[1], 5), round(p[2], 5))

    return points


def generate_polyline(points):
    return encode_polyline(points.values())


stops = [(18.52067, 73.856), (18.92059, 73.17141)]

from math import sin, cos, sqrt, atan2, radians

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python ' + sys.argv[0] + ' <Google Maps API key> "From Address"  "To Address"')
        print('For example')
        print('Usage: python ' + sys.argv[
            0] + ' AJGHJ23242hBdDAXJDOSS "HashedIn Technologies, Bangalore"  "World Trade Centre, Bangalore"')
        exit(-1)

    points = get_points_along_path(sys.argv[1], sys.argv[2], sys.argv[3])
    polyline = generate_polyline(points)

    print("List of points along the route")
    print("------------------------------")
    flag1 = 0
    flag2 = 0
    for time, geo in points.items():
        print(time, geo)

        # approximate radius of earth in km
        R = 6373.0

        lat1 = radians(stops[0][0])
        lon1 = radians(stops[0][1])
        lat2 = radians(geo[0])
        lon2 = radians(geo[1])
        lat3 = radians(stops[1][0])
        lon3 = radians(stops[1][1])

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c

        if distance <= 0.5 and flag1==0:
            print("Contract Triggered")
            print(y.__version__)
            print(int(stops[0][0]*100000), int(stops[0][1]*100000), int(geo[0]*100000), int(geo[1]*100000), "*********************************", stops[0][0], stops[0][1], geo[0], geo[1])
            updateStatus(int(stops[0][0]*100000), int(stops[0][1]*100000), int(geo[0]*100000), int(geo[1]*100000))
            flag1 = 1
        elif distance>0.5:
            flag1=0

        dlon = lon2 - lon3
        dlat = lat2 - lat3

        a = sin(dlat / 2) ** 2 + cos(lat3) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c

        if distance <= 0.5 and flag2==0:
            print("Contract Triggered")
            print(y.__version__)

            updateStatus(int(stops[1][0]*100000), int(stops[1][1]*100000), int(geo[0]*100000), int(geo[1]*100000))
            flag2 = 1
        elif distance>0.5:
            flag2 = 0

print("Polyline for this route")
print(polyline)
print("")
print("Hint: To visualize this route, copy the polyline and paste it in the textfield called Encoded Polyline over here - https://developers.google.com/maps/documentation/utilities/polylineutility")
# print(web3.__version__
# updateStatus(10,10,10,10)

