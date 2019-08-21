import os
import logging
import json
import urllib.request

from plaza_bridge import (
    PlazaBridge,  # Import bridge functionality
    CallbackBlockArgument,  # Needed for argument definition
    VariableBlockArgument,
    BlockContext,
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


def sky_code_to_emoji(sky_code):
    return {
        -9999: '🚫',

        101: '🌞',  # Despexado
        102: '🌤',  # Nubes altas
        103: '⛅',  # Nubes e claros
        104: '🌥️',  # Anubrado 75%
        105: '☁️',   # Cuberto
        106: '🌫️',  # Néboas
        107: '🌦️',  # Chuvasco
        108: '️️🌦️',  # Chuvasco (75%)
        109: '🌦️',  # Chuvasco neve
        110: '🌧️',  # Orballo
        111: '🌧',  # Choiva
        112: '🌨️',  # Neve
        113: '🌩️',  # Treboada
        114: '🌫️',  # Brétema
        115: '🌫️',  # Bancos de néboa
        116: '☁️',  # Nubes medias
        117: '🌧️',  # Choiva débil
        118: '️️🌦️',  # Chuvascos débiles
        119: '⚡',  # Treboada con poucas nubes
        120: '🌨️',  # Auga neve
        121: '🌨️',  # Saraiba

        201: '🌛',  # Despexado
        202: '🌤',  # Nubes altas
        203: '⛅',  # Nubes e claros
        204: '🌥️',  # Anubrado 75%
        205: '☁️',   # Cuberto
        206: '🌫️',  # Néboas
        207: '🌦️',  # Chuvasco
        208: '️️🌦️',  # Chuvasco (75%)
        209: '🌦️',  # Chuvasco neve
        210: '🌧️',  # Orballo
        211: '🌧',  # Choiva
        212: '🌨️',  # Neve
        213: '🌩️',  # Treboada
        214: '🌫️',  # Brétema
        215: '🌫️',  # Bancos de néboa
        216: '☁️',  # Nubes medias
        217: '🌧️',  # Choiva débil
        218: '️️🌦️',  # Chuvascos débiles
        219: '⚡',  # Treboada con poucas nubes
        220: '🌨️',  # Auga neve
        221: '🌨️',  # Saraiba
    }.get(sky_code, '❓')

@bridge.callback
def get_locations(extra_data):
    return LOCATIONS

@bridge.getter(
    id="get_today_max_in_place",
    message="Get today's max temperature for %1",
    arguments=[
        CallbackBlockArgument(str, get_locations),
    ],
    block_result_type=str,
)
def get_max_prediction(place_code, extra_data):
    # Getter logic
    return get_all_prediction(place_code, extra_data)[0]['tMax']

@bridge.getter(
    id="get_today_min_in_place",
    message="Get today's min temperature for %1",
    arguments=[
        CallbackBlockArgument(str, get_locations),
    ],
    block_result_type=str,
)
def get_min_prediction(place_code, extra_data):
    return get_all_prediction(place_code, extra_data)[0]['tMin']

@bridge.getter(
    id="formatted_prediction_in_place",
    message="Format today's prediction %1",
    arguments=[
        CallbackBlockArgument(str, get_locations),
    ],
    block_result_type=str,
)
def get_formatted_prediction(place_code, extra_data):
    r = urllib.request.urlopen("http://servizos.meteogalicia.gal/rss/predicion/jsonPredConcellos.action?idConc={}".format(place_code))
    data = json.loads(r.read())['predConcello']
    pred = data['listaPredDiaConcello'][0]
    return (
        "Predicción para hoxe en {location}:\n"
        "Min: {min_temp}ºC - Max: {max_temp}ºC\n"
        "Ceo: {sky_morning} - {sky_noon} - {sky_night}\n"
        "Prob choiva: {rain_morning}% - {rain_evening}% - {rain_night}%\n"
        "____________________________\n" # Max characters with 28 
        "Información obtida de https://www.meteogalicia.gal"
    ).format(
        location=data['nome'],
        min_temp=pred['tMin'],
        max_temp=pred['tMax'],
        rain_morning=pred['pchoiva']['manha'],
        rain_evening=pred['pchoiva']['tarde'],
        rain_night=pred['pchoiva']['noite'],
        sky_morning=sky_code_to_emoji(pred['ceo']['manha']),
        sky_noon=sky_code_to_emoji(pred['ceo']['tarde']),
        sky_night=sky_code_to_emoji(pred['ceo']['noite']),
    )


@bridge.operation(
    id="get_all_data_from_place",
    message="Get all data for %1. Save to %2",
    arguments=[
        CallbackBlockArgument(str, get_locations),
        VariableBlockArgument(list),
    ],
    save_to=BlockContext.ARGUMENTS[1],
)
def get_all_prediction(place_code, extra_data):
    # Getter logic
    r = urllib.request.urlopen("http://servizos.meteogalicia.gal/rss/predicion/jsonPredConcellos.action?idConc={}".format(place_code))
    data = json.loads(r.read())
    return data['predConcello']['listaPredDiaConcello']


if __name__ == '__main__':
   logging.basicConfig(format="%(asctime)s - %(levelname)s [%(filename)s] %(message)s")
   logging.getLogger().setLevel(logging.INFO)

   logging.info('Starting bridge')
   bridge.run()
