from enum import Enum

class API_GATEWAY(Enum):
    FLAVOR_DB = "https://cosylab.iiitd.edu.in/flavordb/entities_json"


class CLASSIFICATION_METHOD:
    ACADEMIC = 'academic',
    CHEF     = 'chef'