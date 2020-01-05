import requests

API_URL = "https://cosylab.iiitd.edu.in/flavordb/entities_json"

PARAM_ID = "id"


def get_entity(flavordb_id):
    """
    Retrieves the data for a given entity by ID. The data is returned in json format.
    :param flavordb_id:
    :return:
    """
    page = requests.get(url=API_URL, params={PARAM_ID: flavordb_id})
    pass

def parse_entity(data):
    pass


