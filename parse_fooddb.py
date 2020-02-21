from __future__ import print_function

import time
from pprint import pprint

import pandas as pd

import constants
from constants import OPERATING_TYPES as ot
from common_function import read_json, write_json, get_entity, calculate_ratio, relative_intensity, print_status

ID_TOMATO = 364


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


def map_histogram(data, method, unknown_flavor):
    """
    Takes a histogram of words as they appear ({"sweet": 40, "green": 30 ...}) and
    maps them to the relevant aroma cluster
    :param data: dict() - cluster counting depend the method
    :param method: STATISTICAL | CULINARY_LEVEL_1 | CULINARY_LEVEL_2
    :param unknown_flavor: pointer to list of unknown flavor
    :return: counting fo cluster dict (depend the method)
    """
    cluster_count_dict = {}
    cluster_keywords = None
    if method == constants.CLASSIFICATION_METHOD.STATISTICAL:
        cluster_keywords = read_json('assets/statistical_simple.json')
    elif method == constants.CLASSIFICATION_METHOD.CULINARY_LEVEL_1:
        cluster_keywords = read_json('assets/opposite_culinary_table_level_1.json')
    elif method == constants.CLASSIFICATION_METHOD.CULINARY_LEVEL_2:
        cluster_keywords = read_json('assets/opposite_culinary_table_level_2.json')

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
    if method == constants.CLASSIFICATION_METHOD.RELATIVE_INTENSITY:
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


def download_flavor_db(n):
    """
    this function calculate :
        molecules counts per ingredients for each method : statistical ,culinary1,culinary2
        min and max values per cluster for each medthod
        write json files with calculation data
    :param n: int  - running until id = n in flavorDb server
    :return: no return, write thus json files
    """
    ingredients = {'ingredients': []}

    no_response = []
    for i in range(0, n):
        json_data = get_entity(i)
        if json_data is None:
            print("no response for = " + str(i))
            no_response.append(i)
            continue
        relevant_data = parse_entity(json_data)
        print("---- downloads entity: " + relevant_data['entity_alias_readable'] + " |  id: " + str(
            relevant_data['entity_id'])
              + "   ------")
        ingredients['ingredients'].append(relevant_data)
    write_json('results/downloads_up_to_' + str(n) + '.json', ingredients)

    if len(no_response) > 0:
        with open('results/no_response.txt', 'w') as no_r_file:
            no_r_file.write("\n".join(str(i) for i in no_response))


def calculate_aroma_profile_flavor_db(n):
    """
    this function read the json files with ingredients data, max and min value from statistical and culinary json file
    and calculate the aroma profile by this formula: (molecules count per cluster) / (max cluster value)
    :param n: int - running until id = n in flavorDb server
    :return: no return ,write to 'aroma_up_to_n.json' dictionary with all ingredients calculation data
    """
    ingredients = read_json('results/ingredients_up_to_' + str(n) + '.json')
    statistical_limits = read_json('assets/statistical_limits.json')
    culinary1_limits = read_json('assets/culinary1_limits.json')
    culinary2_limits = read_json('assets/culinary2_limits.json')
    statistical_aroma = {key: 0 for key in statistical_limits.keys()}
    culinary1_aroma = {key: 0 for key in culinary1_limits.keys()}
    culinary2_aroma = {key: 0 for key in culinary2_limits.keys()}

    print("calculate aroma")
    print("**************")
    for ingredient in ingredients['ingredients']:
        print("---- aroma  entity: " + ingredient['entity_alias_readable'] + " |  id: " + str(ingredient['entity_id'])
              + "   ------")

        for cluster, count in ingredient['cluster_count_statistical'].items():
            statistical_aroma[cluster] = round(count / statistical_limits[cluster]['max'], 2)
        ingredient['statistical_aroma'] = statistical_aroma.copy()

        for cluster, count in ingredient['cluster_count_culinary_1'].items():
            culinary1_aroma[cluster] = round(count / culinary1_limits[cluster]['max'], 2)
        ingredient['culinary_1_aroma'] = culinary1_aroma.copy()

        for cluster, count in ingredient['cluster_count_culinary_2'].items():
            culinary2_aroma[cluster] = round(count / culinary2_limits[cluster]['max'], 2)
        ingredient['culinary_2_aroma'] = culinary2_aroma.copy()

    write_json('results/aromas_up_to_' + str(n) + '.json', ingredients)


def cluster_counts(n, limit_calculation=False):
    print("*************")
    ingredients = read_json('results/downloads_up_to_' + str(n) + '.json')
    statistical_limits = {}
    culinary1_limits = {}
    culinary2_limits = {}
    unknown_flavor = set()
    for ingredient in ingredients['ingredients']:
        print("---- cluster count entity: " + ingredient['entity_alias_readable'] + " |  id: " + str(
            ingredient['entity_id'])
              + "   ------")

        flavor_profiles_counts = gen_desc_histogram(ingredient)
        # print(flavor_profiles_counts)
        ingredient['flavor_profiles_counts'] = flavor_profiles_counts
        ingredient['cluster_count_statistical'] = map_histogram(flavor_profiles_counts,
                                                                constants.CLASSIFICATION_METHOD.STATISTICAL,
                                                                unknown_flavor)
        ingredient['cluster_count_culinary_1'] = map_histogram(flavor_profiles_counts,
                                                               constants.CLASSIFICATION_METHOD.CULINARY_LEVEL_1,
                                                               unknown_flavor)
        ingredient['cluster_count_culinary_2'] = map_histogram(flavor_profiles_counts,
                                                               constants.CLASSIFICATION_METHOD.CULINARY_LEVEL_2,
                                                               unknown_flavor)
        del ingredient['molecules']
        if limit_calculation:
            calculate_limits(ingredient['cluster_count_statistical'], statistical_limits)
            calculate_limits(ingredient['cluster_count_culinary_1'], culinary1_limits)
            calculate_limits(ingredient['cluster_count_culinary_2'], culinary2_limits)

    # write results and assets:
    write_json('results/ingredients_up_to_' + str(n) + '.json', ingredients)
    with open('results/unknown_flavor.txt', 'w') as uf_file:
        uf_file.write("\n".join(str(flavor) for flavor in unknown_flavor))

    if limit_calculation:
        write_json('assets/statistical_limits.json', statistical_limits)
        write_json('assets/culinary1_limits.json', culinary1_limits)
        write_json('assets/culinary2_limits.json', culinary2_limits)


def create_cluster_matrix(method):
    ingredients = read_json('results/aromas_up_to_1050.json')

    data = {}
    for ingredient in ingredients['ingredients']:
        print_status(ingredient, "cluster matrix: " + method)

        cluster_aroma_vals = list(ingredient[method].values())
        idx = ingredient['entity_id']
        data[idx] = cluster_aroma_vals

    random_ingredient = next(iter(ingredients['ingredients']))
    keys = random_ingredient[method].keys()
    df = pd.DataFrame(data, index=list(keys))
    df_result = df.transpose()
    df_result.to_csv('results/csv_files/' + method + '_matrix.csv', sep='\t', encoding='utf-8')


def generate_correlation_matrix():
    id_to_molecules = read_json('assets/ingredient_to_mol.json')
    data = []
    for ing_id_base in id_to_molecules:
        if int(ing_id_base) % 50 == 0:
            print("ing_id_base: " + ing_id_base)
        mol_ing_base = id_to_molecules[ing_id_base]
        line = {}
        for ing_id_2 in id_to_molecules:
            mol_ing = id_to_molecules[ing_id_2]
            ratio = round(calculate_ratio(mol_ing_base, mol_ing), 3)
            line[int(ing_id_2)] = ratio
        data.append(line.copy())

    df = pd.DataFrame(data, index=list(id_to_molecules.keys()))
    df_result = df.transpose()
    pprint(df_result)
    df_result.to_csv('results/pair_matrix.csv', sep='\t', encoding='utf-8')


def main():
    start_time = time.time()

    DOWNLOAD = ot.OFF
    CLUSTER_COUNTS = ot.OFF
    AROMA_CALCULATION = ot.OFF
    CORRELATION_MATRIX = ot.OFF

    CLUSTER_MATRIX = ot.ON
    n =1

    #      ----------- NOTE -------------
    # running whole process require change  read/write_file to 'results' dir
    #  in all function
    if DOWNLOAD:
        print("Download ...")
        download_flavor_db(n)
    if CLUSTER_COUNTS:
        print("cluster counts ...")
        cluster_counts(n, ot.KEEP_CALCULATION_LIMITS)
    if AROMA_CALCULATION:
        print("Start aroma calculation ...")
        calculate_aroma_profile_flavor_db(n)
    if CLUSTER_MATRIX:
        print("generate cluster matrix ...")
        # create_cluster_matrix('statistical_aroma')
        # create_cluster_matrix('culinary_1_aroma')
        # create_cluster_matrix('culinary_2_aroma')
    if CORRELATION_MATRIX:
        print("generate correlation matrix ...")
        generate_correlation_matrix()

    print("*************** %s minuets ***********" % str((time.time() - start_time) / 60))


if __name__ == '__main__':
    main()
