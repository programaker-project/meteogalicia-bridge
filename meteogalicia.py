import os
import logging
import json
import urllib.request

from plaza_bridge import (
    PlazaBridge,  # Import bridge functionality
    CallbackBlockArgument,  # Needed for argument definition
)

bridge = PlazaBridge(
    name="Meteogalicia",
    endpoint=os.environ['BRIDGE_ENDPOINT'],
    is_public=True,
)

# Get location codes
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "locations.txt")) as f:
    LOCATIONS = {}
    LOCATIONS_FORM_NAME = {}
    for line in f.read().strip().split('\n'):
        id, place = line.strip().split(" ", 1)
        LOCATIONS[id] = {"name": place}


@bridge.callback
def get_locations(extra_data):
    return LOCATIONS

@bridge.getter(
    id="get_today_max_in_place",
    message="Get today's max temperature for %1",
    arguments=[
        CallbackBlockArgument(str, get_locations),
    ],
    block_result_type=str,  # The result is another integer
)
def get_prediction(place_code, extra_data):
    # Getter logic
    r = urllib.request.urlopen("http://servizos.meteogalicia.gal/rss/predicion/jsonPredConcellos.action?idConc={}".format(place_code))
    data = json.loads(r.read())
    return data['predConcello']['listaPredDiaConcello'][0]['tMax']

@bridge.getter(
    id="get_today_min_in_place",
    message="Get today's min temperature for %1",
    arguments=[
        CallbackBlockArgument(str, get_locations),
    ],
    block_result_type=str,  # The result is another integer
)
def get_prediction(place_code, extra_data):
    # Getter logic
    r = urllib.request.urlopen("http://servizos.meteogalicia.gal/rss/predicion/jsonPredConcellos.action?idConc={}".format(place_code))
    data = json.loads(r.read())
    return data['predConcello']['listaPredDiaConcello'][0]['tMin']


if __name__ == '__main__':
   logging.basicConfig(format="%(asctime)s - %(levelname)s [%(filename)s] %(message)s")
   logging.getLogger().setLevel(logging.INFO)

   logging.info('Starting bridge')
   bridge.run()
