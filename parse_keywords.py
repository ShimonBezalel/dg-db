import json
from pprint import pprint


def read_json(file_name):
    with open(file_name, 'r') as json_file:
        return json.load(json_file)


def write_json(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f)
    print("file: " + file_name + " was created")


def modified_keywords_academic():
    with open('assets/original_data/statistical_keywords.json', 'r') as f:
        academic = json.load(f)

    for cluster in academic['clusters']:
        if cluster['title'] == "Floral":
            all_keys = process_keywords(cluster['keywords'])
            # print(all_keys)
            cluster['keywords'] = all_keys

    with open('assets/original_data/statistical_keywords.json', 'w') as f:
        json.dump(academic, f)


def process_keywords(str):
    keywords = str.split(",")
    keys_arr = []
    for i in range(len(keywords)):
        if keywords[i].endswith(" -"):
            keywords[i] = keywords[i][:-2]
        keys_arr += [keywords[i]]
    return keys_arr


""" note: make sure your csv not include merge cell for titles """

def read_chef():
    chef_csv = open("assets/original_data/chef-map-v2.csv", "r")
    chef_table = [l_ing for l_ing in [line.split(",") for line in chef_csv]]
    # print(chef_table)

    chef_table_dict = {}
    chef_table_dict['clusters'] = []
    opposite_chef_table_level_1 = {}
    opposite_chef_table_level_2 = {}
    level_2_to_level_1 = {}

    cluster = {}
    j = 0
    for line in chef_table:
        keywords = []
        if line is not None:
            title = ''
            subtitle = ''
            for i in range(0, len(line)):
                col = line[i]
                if i == 0:
                    title = col
                    if 'title' not in cluster:  # init
                        cluster = {'id': j, 'title': title, 'level': 1, 'sub_cluster': []}
                        chef_table_dict['clusters'].append(cluster)
                        j += 1
                    else:
                        if cluster['title'] != title:
                            cluster = {'id': j, 'title': title, 'level': 1, 'sub_cluster': []}
                            chef_table_dict['clusters'].append(cluster)
                            j += 1
                elif i == 1:
                    subtitle = col
                    level_2_to_level_1[subtitle] = title
                    # print(title + "->" + subtitle, end=': ')
                elif col == '\n' or col == '':
                    break
                else:
                    print(line[i], end=' ')
                    keywords.append(col)
                    opposite_chef_table_level_1[col] = title
                    opposite_chef_table_level_2[col] = subtitle
            sub_cluster = {"title": subtitle, "level": 2, "keywords": keywords}
            cluster['sub_cluster'].append(sub_cluster)

    #  Do once -
    write_json("assets/opposite_culinary_table_level_1.json", opposite_chef_table_level_1)
    write_json("assets/opposite_culinary_table_level_2.json", opposite_chef_table_level_2)
    write_json("assets/level_2_to_level_1.json", level_2_to_level_1)

    write_json("assets/original_data/chef_table.json", chef_table_dict)


def read_academic():
    with open('assets/original_data/statistical_keywords.json', 'r') as f:
        academic = json.load(f)

    for cluster in academic['clusters']:
        if "berry" in cluster['keywords']:
            print(cluster['title'] + ', num of keys ' + str(len(cluster['keywords'])))


def id_to_mol():
    downloads = read_json('results/downloads_up_to_1050.json')
    ingredient_to_mol = {}
    for ing in downloads['ingredients']:
        mol_ing = list({item['pubchem_id']  for item in ing["molecules"]})
        key = str((ing['entity_id'], ing['entity_alias_readable'])) # id + name
        ingredient_to_mol[key] = mol_ing
        # pprint(ingredient_to_mol)
    # pprint(ingredient_to_mol)
    write_json('assets/ingredient_to_mol.json', ingredient_to_mol)


# modified_keywords_academic()
# process_keywords()
# id_to_mol()
# read_chef()
