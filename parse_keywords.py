import json


def modified_keywords_academic():
    with open('academic_keywords.json', 'r') as f:
        academic = json.load(f)

    for cluster in academic['clusters']:
        if cluster['title'] == "Floral":
            all_keys = process_keywords(cluster['keywords'])
            # print(all_keys)
            cluster['keywords'] = all_keys

    with open('academic_keywords.json', 'w') as f:
        json.dump(academic,f)



def process_keywords(str):
    keywords = str.split(",")
    keys_arr = []
    for i in range(len(keywords)):
        if keywords[i].endswith(" -"):
            keywords[i] = keywords[i][:-2]
        keys_arr += [keywords[i]]
    return keys_arr

def read_academic():
    with open('academic_keywords.json', 'r') as f:
        academic = json.load(f)

    for cluster in academic['clusters']:
        if "berry" in cluster['keywords']:
            print (cluster['title'] + ', num of keys ' + str(len(cluster['keywords'])))

# modified_keywords_academic()
# process_keywords()






