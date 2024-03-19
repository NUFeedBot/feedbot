import json


COMMENT_STARTER = ";;!"
PROB_START = f"{COMMENT_STARTER} Begin Problem "
PROB_END = f"{COMMENT_STARTER} End Problem "

def json_has(jsondata, field, type):
    return field in jsondata and isinstance(jsondata[field], type)

def json_has_or(jsondata, field, type, default):
    return jsondata[field] if json_has(jsondata, field, type) else default

class InvalidData(BaseException):
    def __init__(self, str):
        self.str = str

class InvalidSubmission(BaseException):
    def __init__(self, str, line):
        self.str = str
        self.line = line

class ProblemStatement:
    def __init__(self, jsondata):
        if not isinstance(jsondata, dict): raise InvalidData("Problem must be a dict")
        if not json_has(jsondata, "statement", str): raise InvalidData("Problem must have a statement")

        self.statement = jsondata["statement"]
        self.title = json_has_or(jsondata, "title", str, "")
        self.stub = json_has_or(jsondata, "stub", str, "")
        self.tags = json_has_or(jsondata, "tags", list, [])
        self.dependencies = json_has_or(jsondata, "dependencies", list, [])

        for tag in self.tags:
            if not isinstance(tag, str): raise InvalidData("Tags must be strings")
        for dep in self.dependencies:
            if not isinstance(dep, int): raise InvalidData("Dependencies must be ints")

class AssignmentStatement:
    def __init__(self, jsondata):
        if not isinstance(jsondata, dict): raise InvalidData("Top level JSON must be a dict")
        if not json_has(jsondata, "title", str): raise InvalidData("Assignment must have title")
        if not json_has(jsondata, "problems", list): raise InvalidData("Assignment must have problems")

        self.lang = json_has_or(jsondata, "lang", str, "#lang htdp/bsl") # Maybe don't need lang if we want language-agnosticism?
        self.title = jsondata["title"]
        self.problems = [ProblemStatement(prob) for prob in jsondata["problems"]]

class Submission:
    def __init__(self, code, secs):
        # the entire code
        self.full_code = code
        # the entire code, split into sections
        # {prob: int, code: str, linenum: int}
        # where prob is the problem index or -1 if it's outside of a problem
        self.all_sections = secs
    
    def has_problem(self, no):
        return any(map(lambda sec: sec['prob'] == no, self.all_sections))
    
    def has_all_problems(self, nos):
        return all(map(self.has_problem, nos))
    
    def get_problem(self, no):
        for sec in self.all_sections:
            if sec['prob'] == no: return sec

        return "[Problem not found]" # TODO: throw an error?
    


    
