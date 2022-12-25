# POI filtering along route
Filters KML files and keeps all the interesting points that are within a specified distance to a route.

A number of routes and a number of POI files can be specified.

## Usage
`python3 poi-route-filter.py --help`

### Examples:
All campings within 1km from a hiking route
`python3 poi-route-filter.py --distance 1km --poi campings.kml --routes trail1.kml trail2.kml`

## Limitations
- It is intended to work on .kml files, but no extensive testing has been done.
- Distances are calculated without considering altitude
- Distances are calculated from POI to the closest point along in the route files. If there are segments along the route where the two points are far apart, some POIs may get removed unintentionally.


## Future Improvements
- Be able to use GPX files
