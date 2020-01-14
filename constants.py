from enum import Enum

class API_GATEWAY(Enum):
    FLAVOR_DB = "https://cosylab.iiitd.edu.in/flavordb/entities_json"


class CLASSIFICATION_METHOD:
    ACADEMIC = 'academic',
    CHEF     = 'chef'
    RELATIVE_INTENSITY = 'relative_intensity'

class INTENSITY_MODEL:
    HIST    = 'hist' # counts the number of apearances of each descriptive word
