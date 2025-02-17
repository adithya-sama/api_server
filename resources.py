import json
import redis


from geopy.geocoders import Nominatim


SRC = {}
COORDINATES = {}
REDIS = None
GEOLOCATOR = Nominatim(user_agent='cowinmap')


def init():
    global REDIS
    REDIS = redis.Redis()
    pull_data()


def pull_data():
    global SRC, COORDINATES
    SRC = REDIS.get('resources')
    COORDINATES = REDIS.get('coordinates')

    SRC = {} if SRC is None else json.loads(SRC)
    COORDINATES = {} if COORDINATES is None else json.loads(COORDINATES)


def get():
    resources = {}

    for city, resource_map in SRC.items():
        if resource_map != {}:
            resources[city] = []

            for resource, _ in resource_map.items():
                resources[city].append(resource)

    return resources


def get_details():
    pull_data()
    return COORDINATES


def update(city, resource, link):
    global SRC, COORDINATES
    coordinates = GEOLOCATOR.geocode('%s,India' % city)
    pull_data()

    if city not in SRC:
        SRC[city] = {}

    if city not in COORDINATES:
        COORDINATES[city] = {}

    SRC[city][resource] = link

    if 'resources' not in COORDINATES[city]:
        COORDINATES[city]['resources'] = []

    if resource not in COORDINATES[city]['resources']:
        COORDINATES[city]['resources'].append(resource)

    COORDINATES[city]['lat'] = coordinates.latitude
    COORDINATES[city]['lng'] = coordinates.longitude

    tokens = str(coordinates).split(',')
    tokens = [token.strip() for token in tokens]

    COORDINATES[city]['state'] = tokens[-3]
    COORDINATES[city]['country'] = tokens[-1]

    try:
        int(tokens[-2])
    except:
        COORDINATES[city]['state'] = tokens[-2]

    REDIS.set('resources', json.dumps(SRC))
    REDIS.set('coordinates', json.dumps(COORDINATES))


def get_sheet_link(city, resource):
    pull_data()

    if city not in SRC:
        return None
    if resource not in SRC[city]:
        return None

    return SRC[city][resource]


def get_resource_map():
    return SRC