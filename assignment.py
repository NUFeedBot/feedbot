import json

def json_has(jsondata, field, type):
    return field in jsondata and isinstance(jsondata[field], type)

def json_has_or(jsondata, field, type, default):
    return jsondata[field] if json_has(jsondata, field, type) else default


class ProblemStatement:
    def __init__(self, jsondata):
        if not isinstance(jsondata, dict): raise InvalidData("Problem must be a dict")

        if not json_has(jsondata, "path", list): raise InvalidData("Problem must have a path")
        self.path = jsondata["path"]
        for pathpart in self.path:
            if not isinstance(pathpart, str): raise InvalidData("Path must be strings")

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
    @staticmethod
    def load(path):
        with open(path,'r') as f:
            c = json.load(f)
            c.setdefault('assignment', {})
            return AssignmentStatement(c['assignment'])

    def __init__(self, jsondata):
        if not isinstance(jsondata, dict): raise InvalidData("Top level JSON must be a dict")
        if not json_has(jsondata, "title", str): raise InvalidData("Assignment must have title")
        if not json_has(jsondata, "problems", list): raise InvalidData("Assignment must have problems")

        self.title = jsondata["title"]
        self.context = json_has_or(jsondata, "context", str, "")
        self.problems = [ProblemStatement(prob) for prob in jsondata["problems"]]
