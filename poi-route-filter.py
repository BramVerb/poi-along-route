from xml.dom.minidom import parse
from tqdm import tqdm
import re
import numpy as np
from sklearn.neighbors import BallTree
import os
import re
from argparse import ArgumentParser
import argparse

def to_coordinate(point: tuple[str, str]):
    lat, long = tuple(map(float, point))
    return np.deg2rad([lat, long])

def get_route_points(routefiles: list[str]):
    route_points = []
    for routefile in routefiles:
        document = parse(routefile)
        for c in document.getElementsByTagName("coordinates"):
            d  = c.childNodes[0]._data
            for point in re.finditer(r'(-?\d+.\d+),(-?\d+.\d+),', d):
                route_points.append(to_coordinate(point.groups()))
    return np.array(route_points)


def min_distance(point, tree):
    v, _ = tree.query(np.array([point]), k = 1)
    earth_radius_km = 6371
    return v[0]*earth_radius_km

def remove_from(filename: str, tree: BallTree, distance_m: int):
    document = parse(filename)
    doc = document.childNodes[0].childNodes[1]
    places = doc.getElementsByTagName("Placemark")
    removed = 0
    for place in tqdm(places, desc=filename):
        coordinate = place.getElementsByTagName("coordinates")[0]
        coordinate = coordinate.childNodes[0]._data
        coordinate = to_coordinate(coordinate.split(','))
        assert len(coordinate) == 2
        d = min_distance(coordinate, tree)
        if d*1000 > distance_m:
            place.parentNode.removeChild(place)
            removed += 1
    print(f'removed {removed}/{len(places)}, keeping {len(places) - removed}')

    name, ext = os.path.splitext(filename)
    with open(f"{name}_on_route{ext}","w") as fs:
        fs.write(document.toxml())
        fs.close()



def is_valid_file(parser, arg: str):
    if not os.path.isfile(arg):
        parser.error(f"The file '{arg}' does not exist!")
    else:
        return arg

def distance(string):
    # Check if the string is in the correct format
    match = re.match(r'(\d+)(m|km)', string)
    if not match:
        raise argparse.ArgumentTypeError("Invalid distance format")
    value, unit = match.groups()
    # Convert the value to a float
    value = int(value)
    if unit == 'km':
        value *= 1000
    # Return the value and unit
    return value

if __name__ == '__main__':
    description = 'POI route filter: Filter POI in kml files that are within a certain distance from a route'
    parser = ArgumentParser(description=description)
    parser.add_argument("-r", "--routes", nargs="+", dest="routefiles", required=True, help="One or multiple kml route files", metavar="FILE", type=lambda x: is_valid_file(parser, x))
    parser.add_argument("-p", "--poi", nargs="+", dest="pois", required=True, help="One or multiple poi files", metavar="FILE", type=lambda x: is_valid_file(parser, x))
    parser.add_argument("-d", "--distance", type=distance, help="distance including unit (e.g. 1km or 10m)", required=True)

    args = parser.parse_args()
    route_points = get_route_points(args.routefiles)
    tree = BallTree(route_points, metric='haversine')
    for f in args.pois:
        if 'on_route' in f:
            continue
        remove_from(f, tree, distance_m=args.distance)
