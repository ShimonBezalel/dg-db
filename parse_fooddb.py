import requests
from constants import API_GATEWAY

PARAM_ID = "id"

ID_TOMATO = 364


def get_entity(flavordb_id):
    """
    Retrieves the data for a given entity by ID. The data is returned in json format.
    :param flavordb_id:
    :return:
    """
    page = requests.get(url=API_GATEWAY.FLAVOR_DB, params={PARAM_ID: flavordb_id})
    pass

def parse_entity(data):
    """
    Returns PubChemID,
    :param data:
    :return:
    """
    pass

def gen_desc_dict(data):
    """
    Generates a dictionary
    :param data:
    :return:
    """
    pass

def calculate_auroma_profile(data, method, model ):
    pass

def main():
    json_data = get_entity(ID_TOMATO)
    relevant_data = parse_entity(json_data)

    auroma_profile = calculate_auroma_profile()

if __name__ == '__main__':
    main()
