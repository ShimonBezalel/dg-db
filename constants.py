from enum import Enum

class API_GATEWAY(Enum):
    FLAVOR_DB = "https://cosylab.iiitd.edu.in/flavordb/entities_json"


class CLASSIFICATION_METHOD:
    STATISTICAL = 'statistical',
    CULINARY_LEVEL_1     = 'chef_level_1'
    CULINARY_LEVEL_2     = 'chef_level_2'
    RELATIVE_INTENSITY = 'relative_intensity'

class INTENSITY_MODEL:
    HIST    = 'hist' # counts the number of apearances of each descriptive word

class OPERATING_TYPES:
    NEW_CALCULATION_LIMITS = True
    KEEP_CALCULATION_LIMITS = False
