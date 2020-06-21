import json
import sys
import requests
import constants

PARAM_ID = "id"


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def read_json(file_name):
    with open(file_name, 'r') as json_file:
        return json.load(json_file)


def write_json(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f)


def get_entity(flavordb_id):
    """
    Retrieves the data for a given entity by ID. The data is returned in json format.
    :param flavordb_id:
    :return:
    """
    page = requests.get(url=constants.API_GATEWAY.FLAVOR_DB.value, params={PARAM_ID: flavordb_id})
    if page.status_code == 404:
        return None
    else:
        return page.json()


def calculate_ratio(mol_ing1, mol_ing2):
    a = set(mol_ing1)
    b = set(mol_ing2)
    a_intersection_b = a.intersection(b)
    return len(a_intersection_b) / (len(a) + len(b) - len(a_intersection_b))




def get_aroma_of(id):
    ingredients = read_json('assets/aromas_up_to_1050.json')
    ingredient = [item for item in ingredients["ingredients"] if item["entity_id"] == id]
    write_json('results/ingredient_' + str(id) + '.json', ingredient[0])
    return ingredient


def get_download_of(id):
    ingredients = read_json('results/downloads_up_to_1050.json')
    download_item = [item for item in ingredients["ingredients"] if item["entity_id"] == id]
    # write_json('results/download_' + str(id) + '.json', download_item[0])
    return download_item[0]


def relative_intensity(num_of_molecules, cluster_dict):
    for cluster in cluster_dict:
        cluster_dict[cluster] = round(cluster_dict[cluster] / num_of_molecules, 2)
    return cluster_dict


def print_status(ingredient, status):
    print("---- " + status + "  entity: " + ingredient['entity_alias_readable'] + " |  id: " + str(
        ingredient['entity_id'])
          + "   ------")
