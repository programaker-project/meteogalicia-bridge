import json
import logging
import os

from programaker_bridge import \
    CallbackBlockArgument  # Needed for argument definition
from programaker_bridge import ProgramakerBridge  # Import bridge functionality
from programaker_bridge import BlockContext, VariableBlockArgument
from request_cache import SimpleRequestCache

CACHE_TIME = os.getenv("CACHE_TIME", 10 * 60)  # By default reset every 10 minutes

REQUEST_CACHE = SimpleRequestCache(CACHE_TIME)

ASSET_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

bridge = ProgramakerBridge(
    name="Meteogalicia",
    endpoint=(
        os.getenv("BRIDGE_ENDPOINT", None) or open("bridge_url.txt").read().strip()
    ),
    token=(
        os.getenv("PROGRAMAKER_BRIDGE_AUTH_TOKEN", None)
        or open("token.txt").read().strip()
    ),
    icon=open(os.path.join(ASSET_DIRECTORY, "logo_meteogalicia.png"), "rb"),
    is_public=True,
)

# Get location codes
with open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "locations.txt")
) as f:
    LOCATIONS = []
    LOCATIONS_FORM_NAME = {}
    for line in f.read().strip().split("\n"):
        id, place = line.strip().split(" ", 1)
        LOCATIONS.append({"id": id, "name": place})

    LOCATIONS.sort(key=lambda x: x["name"])


def sky_code_to_emoji(sky_code):
    return {
        -9999: "🚫",
        101: "🌞",  # Despexado
        102: "🌤",  # Nubes altas
        103: "⛅",  # Nubes e claros
        104: "🌥️",  # Anubrado 75%
        105: "☁️",  # Cuberto
        106: "🌫️",  # Néboas
        107: "🌦️",  # Chuvasco
        108: "️️🌦️",  # Chuvasco (75%)
        109: "🌦️",  # Chuvasco neve
        110: "🌧️",  # Orballo
        111: "🌧",  # Choiva
        112: "🌨️",  # Neve
        113: "🌩️",  # Treboada
        114: "🌫️",  # Brétema
        115: "🌫️",  # Bancos de néboa
        116: "☁️",  # Nubes medias
        117: "🌧️",  # Choiva débil
        118: "️️🌦️",  # Chuvascos débiles
        119: "⚡",  # Treboada con poucas nubes
        120: "🌨️",  # Auga neve
        121: "🌨️",  # Saraiba
        201: "🌛",  # Despexado
        202: "🌤",  # Nubes altas
        203: "⛅",  # Nubes e claros
        204: "🌥️",  # Anubrado 75%
        205: "☁️",  # Cuberto
        206: "🌫️",  # Néboas
        207: "🌦️",  # Chuvasco
        208: "️️🌦️",  # Chuvasco (75%)
        209: "🌦️",  # Chuvasco neve
        210: "🌧️",  # Orballo
        211: "🌧",  # Choiva
        212: "🌨️",  # Neve
        213: "🌩️",  # Treboada
        214: "🌫️",  # Brétema
        215: "🌫️",  # Bancos de néboa
        216: "☁️",  # Nubes medias
        217: "🌧️",  # Choiva débil
        218: "️️🌦️",  # Chuvascos débiles
        219: "⚡",  # Treboada con poucas nubes
        220: "🌨️",  # Auga neve
        221: "🌨️",  # Saraiba
    }.get(sky_code, "❓")


@bridge.callback
def get_locations(extra_data):
    logging.debug("[CBK] GET locations")
    return LOCATIONS


@bridge.getter(
    id="get_today_max_in_place",
    message="Get today's max temperature for %1",
    arguments=[CallbackBlockArgument(str, get_locations),],
    block_result_type=str,
)
def get_max_prediction(place_code, extra_data):
    # Getter logic
    logging.info("[GET] GET max prediction")
    return get_all_prediction(place_code, extra_data)[0]["tMax"]


@bridge.getter(
    id="get_today_min_in_place",
    message="Get today's min temperature for %1",
    arguments=[CallbackBlockArgument(str, get_locations),],
    block_result_type=str,
)
def get_min_prediction(place_code, extra_data):
    logging.info("[GET] GET min prediction")
    return get_all_prediction(place_code, extra_data)[0]["tMin"]


@bridge.callback
def get_map_days_from_now(extra_data):
    logging.debug("[CBK] GET days from now")
    return [
        {"id": "0", "name": "Today"},
        {"id": "1", "name": "Tomorrow"},
        {"id": "2", "name": "In two days"},
        {"id": "3", "name": "In three days"},
    ]


@bridge.callback
def get_map_day_time(extra_data):
    logging.debug("[CBK] GET days time")
    return [
        {"id": "1", "name": "Morning"},
        {"id": "2", "name": "Noon"},
        {"id": "3", "name": "Night"},
    ]


@bridge.getter(
    id="get_today_map",
    message="Get map for %1 %2",
    arguments=[
        CallbackBlockArgument(str, get_map_days_from_now),
        CallbackBlockArgument(str, get_map_day_time),
    ],
    block_result_type=str,
)
def get_total_map(days_from_now, day_time, extra_data):
    logging.info("[GET] GET today map")
    code_from_day_time = {"1": "M", "2": "T", "3": "N",}[day_time]

    return (
        "https://servizos.meteogalicia.gal/rss/predicion/cprazo/getImaxe"
        + code_from_day_time
        + ".action?dia="
        + str(days_from_now)
    )


@bridge.getter(
    id="formatted_prediction_in_place",
    message="Format today's prediction %1",
    arguments=[CallbackBlockArgument(str, get_locations),],
    block_result_type=str,
)
def get_formatted_prediction(place_code, extra_data):
    logging.info("[GET] GET formatted prediction")

    r = REQUEST_CACHE.request(
        "https://servizos.meteogalicia.gal/rss/predicion/jsonPredConcellos.action?idConc={}".format(
            place_code
        )
    )
    data = json.loads(r)["predConcello"]
    pred = data["listaPredDiaConcello"][0]

    return (
        "Predicción para hoxe en {location}:\n"
        "Min: {min_temp}ºC - Max: {max_temp}ºC\n"
        "Ceo: {sky_morning} - {sky_noon} - {sky_night}\n"
        "Prob choiva: {rain_morning}% - {rain_evening}% - {rain_night}%\n"
        "____________________________\n"  # Max characters with 28
        "Información obtida de https://www.meteogalicia.gal"
    ).format(
        location=data["nome"],
        min_temp=pred["tMin"],
        max_temp=pred["tMax"],
        rain_morning=in_range(pred["pchoiva"]["manha"], 0, 100),
        rain_evening=in_range(pred["pchoiva"]["tarde"], 0, 100),
        rain_night=in_range(pred["pchoiva"]["noite"], 0, 100),
        sky_morning=sky_code_to_emoji(pred["ceo"]["manha"]),
        sky_noon=sky_code_to_emoji(pred["ceo"]["tarde"]),
        sky_night=sky_code_to_emoji(pred["ceo"]["noite"]),
    )


@bridge.operation(
    id="get_all_data_from_place",
    message="Get all data for %1. Save to %2",
    arguments=[CallbackBlockArgument(str, get_locations), VariableBlockArgument(list),],
    save_to=BlockContext.ARGUMENTS[1],
)
def get_all_prediction(place_code, extra_data):
    logging.info("[GET] GET full prediction")
    # Getter logic
    r = REQUEST_CACHE.request(
        "https://servizos.meteogalicia.gal/rss/predicion/jsonPredConcellos.action?idConc={}".format(
            place_code
        )
    )
    data = json.loads(r)
    return data["predConcello"]["listaPredDiaConcello"]


### Utils
def in_range(data, range_min, range_max, out_of_range_value="[erro]"):
    if data < range_min or data > range_max:
        return out_of_range_value
    return data


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s [%(filename)s] %(message)s")
    logging.getLogger().setLevel(logging.INFO)

    logging.info("Starting bridge")
    bridge.run()
