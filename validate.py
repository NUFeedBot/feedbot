#Returns if given json has the given field and if the data is of given type
def json_has(jsondata, field, type):
    return field in jsondata and isinstance(jsondata[field], type)

#Returns data if json_has, else returns provided default fallback value
def json_has_or(jsondata, field, type, default):
    return jsondata[field] if json_has(jsondata, field, type) else default

class InternalInconsistency(BaseException):
    def __init__(self, str):
        self.str = str


class MetaDataError(BaseException):
    def __init__ (self, str):
        self.str = str


class SubmissionInconsistency(BaseException):
    def __init__(self, str):
        self.str = str



def validateJson(jsondata):
    """
    Ensures that the entire json metadata file has required fields with correct types
    """

    if not isinstance(jsondata, dict): raise MetaDataError("JSON metadata must be a dict")
    if not json_has(jsondata, "contexts", list): raise MetaDataError("Assignment must have problem contexts")
    if not json_has(jsondata, "title", str): raise MetaDataError("Assignment must have title")
    if not json_has(jsondata, "problems", list): raise MetaDataError("Assignment must have problems")
    for prob in jsondata["problems"]: 
        validateJsonProb(prob)


def validateJsonProb(prob_data):
    """
    Ensures that all the problem data (required and optional) is provided in the correct types
    """
    #Required data
    if not isinstance(prob_data, dict): raise MetaDataError("Problem must be a dict")
    if not json_has(prob_data, "path", list): raise MetaDataError("Problem must have a path that is a list")

    path = prob_data["path"]
    for pathpart in path:
        if not isinstance(pathpart, str): raise MetaDataError("Problem paths must be strings")


    #Optional data: Validates tags, dependencies, stub, grading_note, title if the problem has them
    if "tags" in prob_data: 
        if not isinstance(prob_data["tags"], list):
            raise MetaDataError("Problem tags must be a list")
        
        tags = prob_data["tags"]
        for tag in tags:
            if not isinstance(tag, str): raise MetaDataError("Each problem tag must be a string")


    if "dependencies" in prob_data:
        if not isinstance(prob_data["dependencies"], list):
            raise MetaDataError("Problem dependencies must be a list")
        
        dependencies = prob_data["dependencies"]
        for dep in dependencies:
            if not isinstance(dep, list): raise MetaDataError("Dependency must be a path (list of strings)")
            for pathpart in dep: 
                if not isinstance(pathpart, str): raise MetaDataError("Each path in dependency must be a string")
    
    if "stub" in prob_data: 
        if not isinstance(prob_data["stub"], str): raise MetaDataError("Problem stub must be a string")

    if "grading_note" in prob_data: 
        if not isinstance(prob_data["grading_note"], str): raise MetaDataError("Grading note must be a string")
    
    if "title" in prob_data:
        if not isinstance(prob_data["title"], str): raise MetaDataError("Problem title must be a string")




def validateAssignmentProb(prob_path, assignment): 
    """
    Ensures that the problem actually exists in the template
    """

    if not assignment.at(prob_path, False).has_data(): raise InternalInconsistency(f"Problem path {prob_path} must exist in template")



def validateSubmissionProb(prob_path, submission):
    """
    Ensures that a submission for the given problem actually exists
    """

    if not submission.at(prob_path, False).has_data(): raise SubmissionInconsistency(f"Problem path {prob_path} must exist in submission")