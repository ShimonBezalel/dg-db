from __future__ import print_function

import time

import matplotlib.pyplot as plt

import sys
import json

"""
Q:
1. 
"""


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


import requests
from constants import API_GATEWAY, CLASSIFICATION_METHOD

PARAM_ID = "id"
ID_TOMATO = 364


def get_entity(flavordb_id):
    """
    Retrieves the data for a given entity by ID. The data is returned in json format.
    :param flavordb_id:
    :return:
    """
    page = requests.get(url=API_GATEWAY.FLAVOR_DB.value, params={PARAM_ID: flavordb_id})
    return page.json()

    # with open('test.json', 'w') as f:
    #     json.dump(page.json(), f)


def parse_entity(data):
    """
    Returns PubChemID,
    :param data:
    :return:
    """
    relevant_data = {}
    relevant_key = ["category", "entity_id", "entity_alias_readable", "molecules"]

    for (key, val) in data.items():
        if key in relevant_key:
            relevant_data[key] = val
        else:
            continue
    return relevant_data


def gen_desc_histogram(data):
    """
    Generates a dictionary
    :param data:
    :return:
    """
    keywords_hist = {}
    for mol in data['molecules']:
        if mol['flavor_profile'] != '':
            flavors = mol['flavor_profile'].split('@')
            for flavor in flavors:
                if flavor in keywords_hist:
                    keywords_hist[flavor] += 1
                else:
                    keywords_hist[flavor] = 1
    return keywords_hist

    # return data

def read_json(file_name):
    with open(file_name, 'r') as json_file:
        return json.load(json_file)


def write_json(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f)



def academic_map_histogram(data):
    academic_keywords = read_json('academic_keywords.json')
    cluster_count_dict = {}
    # take each flavor
    flavor_profiles_counts = data
    for flavor in flavor_profiles_counts:
        # ceac cluster
        for cluster in academic_keywords['clusters']:
            if flavor in cluster['keywords']:
                if cluster['title'] in cluster_count_dict:
                    cluster_count_dict[cluster['title']] += flavor_profiles_counts[flavor]
                else:
                    cluster_count_dict[cluster['title']] = flavor_profiles_counts[flavor]

    return cluster_count_dict


def relative_intensity(num_of_molecules, cluster_dict):
    for cluster in cluster_dict:
        cluster_dict[cluster] = round(cluster_dict[cluster] / num_of_molecules, 2)
    return cluster_dict


def chef_map_histogram(hist):
    pass


def map_histogram(data, method):
    """
    Takes a histogram of words as they appear ({"sweet": 40, "green": 30 ...}) and
    maps them to the relevant auroma cluster
    :param hist:
    :return:
    """
    cluster_count_dict = {}
    if method == CLASSIFICATION_METHOD.ACADEMIC:
        cluster_count_dict = academic_map_histogram(data)
    elif method == CLASSIFICATION_METHOD.CHEF:
       # cluster_count_dict = chef_map_histogram(data)
        pass
    return cluster_count_dict


def calculate_auroma_profile(data, method, hist):
    filtered_hist= {}
    for title, total_count in hist.items():
        if title not in ["Uncategorised"]:
            filtered_hist[title] = total_count
    if method == CLASSIFICATION_METHOD.RELATIVE_INTENSITY:
        return relative_intensity(sum(filtered_hist.values()), filtered_hist)
    else:
        pass


def main():
    ingredients = {'ingredients': []}
    start_time = time.time()
    for i in range(ID_TOMATO - 1, ID_TOMATO):
        json_data = get_entity(i)
        relevant_data = parse_entity(json_data)

        flavor_profiles_counts = gen_desc_histogram(relevant_data)
        relevant_data['flavor_profiles_counts'] = flavor_profiles_counts

        cluster_count_dict = map_histogram(flavor_profiles_counts, CLASSIFICATION_METHOD.ACADEMIC)
        relevant_data['cluster_count_dict'] = cluster_count_dict

        aromas_profile_dict = calculate_auroma_profile(relevant_data, CLASSIFICATION_METHOD.RELATIVE_INTENSITY, cluster_count_dict)
        relevant_data['aromas_profile_dict'] = aromas_profile_dict

        print("----  entity: " + relevant_data['entity_alias_readable'] + "   ------")
        print(aromas_profile_dict)
        ingredients['ingredients'].append(relevant_data)
        print (sum(aromas_profile_dict.values()))
    write_json('ingredients_up_to_0.json', ingredients)
    print("*************** %s seconds ***********" % (time.time() - start_time))
    print("*************** %s minuets ***********" % str((time.time() - start_time) / 60))

    #
    # auroma_profile = calculate_auroma_profile()


if __name__ == '__main__':
    main()
