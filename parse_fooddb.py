from __future__ import print_function

import time
from pprint import pprint

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
    if page.status_code == 404:
        return None
    else:
        return page.json()


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


def read_json(file_name):
    with open(file_name, 'r') as json_file:
        return json.load(json_file)

def write_json(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f)




def relative_intensity(num_of_molecules, cluster_dict):
    for cluster in cluster_dict:
        cluster_dict[cluster] = round(cluster_dict[cluster] / num_of_molecules, 2)
    return cluster_dict


def chef_map_histogram(hist):
    pass


def map_histogram(data, method, unknown_flavor):
    """
    Takes a histogram of words as they appear ({"sweet": 40, "green": 30 ...}) and
    maps them to the relevant aroma cluster
    :param data: dict() - cluster counting depend the method
    :param method: ACADEMIC | CHEF_LEVEL_1 | CHEF_LEVEL_2
    :param unknown_flavor: pointer to list of unknown flavor
    :return: counting fo cluster dict (depend the method)
    """
    cluster_count_dict = {}
    if method == CLASSIFICATION_METHOD.ACADEMIC:
        cluster_keywords = read_json('academic_simple.json')
    elif method == CLASSIFICATION_METHOD.CHEF_LEVEL_1:
        cluster_keywords = read_json('opposite_chef_table_level_1.json')
    elif method == CLASSIFICATION_METHOD.CHEF_LEVEL_2:
        cluster_keywords = read_json('opposite_chef_table_level_2.json')

    # take each flavor
    flavor_profiles_counts = data
    for flavor in flavor_profiles_counts:
        # check cluster
        if flavor in cluster_keywords:
            if cluster_keywords[flavor] in cluster_count_dict:
                cluster_count_dict[cluster_keywords[flavor]] += flavor_profiles_counts[flavor]
            else:
                cluster_count_dict[cluster_keywords[flavor]] = flavor_profiles_counts[flavor]
        else:
            unknown_flavor.add(flavor)

    return cluster_count_dict


def calculate_aroma_profile(data, method, hist):
    filtered_hist = {}
    for title, total_count in hist.items():
        if title not in ["Uncategorised"]:
            filtered_hist[title] = total_count
    if method == CLASSIFICATION_METHOD.RELATIVE_INTENSITY:
        return relative_intensity(sum(filtered_hist.values()), filtered_hist)
    else:
        pass


def calculate_limits(molecule_cluster_counts_dict, min_max_dict):
    """
    this function get pointer to min_max_dict and check if this molecule has count of cluster name which
    higher/lower than values in min_max_dict
    :param molecule_cluster_counts_dict: dictionary of clusters count
    :param min_max_dict: dictionary fo min/max counts value of all molecules
    :return: no return , min_max_dict change by pointer
    """
    for cluster_name, count in molecule_cluster_counts_dict.items():
        if cluster_name in min_max_dict:
            if count > min_max_dict[cluster_name]['max']:
                min_max_dict[cluster_name]['max'] = count
            elif count < min_max_dict[cluster_name]['min']:
                min_max_dict[cluster_name]['min'] = count
        else:
            min_max_dict[cluster_name] = {'max': count, 'min': count}


def download_and_analyze_cluster_counts_flavor_db(n):
    """
    this function calculate :
        molecules counts per ingredients for each method : academic ,chef1,chef2
        min and max values per cluster for each medthod
        write json files with calculation data
    :param n: int  - running until id = n in flavorDb server
    :return: no return, write thus json files
    """
    ingredients = {'ingredients': []}
    academic_limits = {}
    chef1_limits = {}
    chef2_limits = {}
    no_response = []

    unknown_flavor = set()
    for i in range(0, n):
        json_data = get_entity(i)
        if json_data is None:
            print("no response for = " + str(i))
            no_response.append(i)
            continue
        relevant_data = parse_entity(json_data)
        flavor_profiles_counts = gen_desc_histogram(relevant_data)
        # print(flavor_profiles_counts)
        relevant_data['flavor_profiles_counts'] = flavor_profiles_counts
        relevant_data['cluster_count_academic'] = map_histogram(flavor_profiles_counts, CLASSIFICATION_METHOD.ACADEMIC,
                                                                unknown_flavor)
        relevant_data['cluster_count_chef_1'] = map_histogram(flavor_profiles_counts,
                                                              CLASSIFICATION_METHOD.CHEF_LEVEL_1, unknown_flavor)
        relevant_data['cluster_count_chef_2'] = map_histogram(flavor_profiles_counts,
                                                              CLASSIFICATION_METHOD.CHEF_LEVEL_2, unknown_flavor)
        del relevant_data['molecules']

        calculate_limits(relevant_data['cluster_count_academic'], academic_limits)
        calculate_limits(relevant_data['cluster_count_chef_1'], chef1_limits)
        calculate_limits(relevant_data['cluster_count_chef_2'], chef2_limits)

        # aromas_profile_dict = calculate_auroma_profile(relevant_data, CLASSIFICATION_METHOD.RELATIVE_INTENSITY)

        print("----  entity: " + relevant_data['entity_alias_readable'] + " |  id: " + str(relevant_data['entity_id'])
              + "   ------")
        ingredients['ingredients'].append(relevant_data)
    write_json('ingredients_up_to_' + str(n) + '.json', ingredients)
    write_json('academic_limits.json', academic_limits)
    write_json('chef1_limits.json', chef1_limits)
    write_json('chef2_limits.json', chef2_limits)
    print("*************")
    with open('unknown_flavor.txt', 'w') as uf_file:
        uf_file.write("\n".join(str(flavor) for flavor in unknown_flavor))
    if len(no_response) > 0:
        with open('no_response.txt', 'w') as no_r_file:
            no_r_file.write("\n".join(str(i) for i in no_response))


def calculate_aroma_profile_flavor_db(n):
    """
    this function read the json files with ingredients data, max and min value from academic and chef json file
    and calculate the aroma profile by this formula: (molecules count per cluster) / (max cluster value)
    :param n: int - running until id = n in flavorDb server
    :return: no return ,write to 'aroma_up_to_n.json' dictionary with all ingredients calculation data
    """
    ingredients = read_json('ingredients_up_to_' + str(n) + '.json')
    academic_limits = read_json('academic_limits.json')
    chef1_limits = read_json('chef1_limits.json')
    chef2_limits = read_json('chef2_limits.json')
    academic_aroma = {key: 0 for key in academic_limits.keys()}
    chef1_aroma = {key: 0 for key in chef1_limits.keys()}
    chef2_aroma = {key: 0 for key in chef2_limits.keys()}

    for ingredient in ingredients['ingredients']:
        print("----  entity: " + ingredient['entity_alias_readable'] + " |  id: " + str(ingredient['entity_id'])
              + "   ------")

        for cluster, count in ingredient['cluster_count_academic'].items():
            academic_aroma[cluster] = count / academic_limits[cluster]['max']
        ingredient['academic_aroma'] = academic_aroma

        for cluster, count in ingredient['cluster_count_chef_1'].items():
            chef1_aroma[cluster] = count / chef1_limits[cluster]['max']
        ingredient['chef_1_aroma'] = chef1_aroma

        for cluster, count in ingredient['cluster_count_chef_2'].items():
            chef2_aroma[cluster] = count / chef2_limits[cluster]['max']
        ingredient['chef_2_aroma'] = chef2_aroma

    write_json('aromas_up_to_' + str(n) + '.json', ingredients)


def main():
    start_time = time.time()

    n = 1000
    print("Download and analyze ...")
    download_and_analyze_cluster_counts_flavor_db(n)
    print("Start aroma calculation ...")
    calculate_aroma_profile_flavor_db(n)

    print("*************** %s minuets ***********" % str((time.time() - start_time) / 60))


if __name__ == '__main__':
    main()
