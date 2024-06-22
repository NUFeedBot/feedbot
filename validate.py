#Returns if given json has the given field and if the data is of given type
def json_has(jsondata, field, type):
    return field in jsondata and isinstance(jsondata[field], type)

class InternalInconsistency(BaseException):
    def __init__(self, str):
        self.str = str


class MetaDataError:
    def __init__ (self, str):
        self.str = str


class SubmissionInconsistency(BaseException):
    def __init__(self, str):
        self.str = str


def validate():
    pass

def validateJson(jsondata):
    if not isinstance(jsondata, dict): raise MetaDataError("JSON metadata must be a dict")
    if not json_has(jsondata, "title", str): raise MetaDataError("Assignment must have title")
    if not json_has(jsondata, "problems", list): raise MetaDataError("Assignment must have problems")

def validateProb(prob_data): 
    if not isinstance(prob_data, dict): raise MetaDataError("Problem must be a dict")
    if not json_has(prob_data, "path", list): raise MetaDataError("Problem must have a path")

    for pathpart in prob_data["path"]:
        if not isinstance(pathpart, str): raise MetaDataError("Problem paths must be strings")

def validateResponse():
    pass 
