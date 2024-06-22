import json

from submission import SubmissionTemplate
from validate import validate, validateJson, validateResponse, validateProb

#Returns if given json has the given field and if the data is of given type
def json_has(jsondata, field, type):
    return field in jsondata and isinstance(jsondata[field], type)

#Returns data if json_has, else returns provided default fallback value
def json_has_or(jsondata, field, type, default):
    return jsondata[field] if json_has(jsondata, field, type) else default


#Represents a single problem in an assignment along with its metadata
class ProblemStatement:
    def __init__(self, prob_data, template):
        validateProb(prob_data)

        self.path = prob_data["path"]
        statement = template.at(self.path)

        if statement == []: raise InvalidData(f"Problem statement {self.path} must exist in template")
        self.statement = statement.contents()
        self.title = json_has_or(prob_data, "title", str, "")
        self.stub = json_has_or(prob_data, "stub", str, "")
        self.tags = json_has_or(prob_data, "tags", list, [])
        self.dependencies = json_has_or(prob_data, "dependencies", list, [])
        self.grading_note = json_has_or(prob_data, "grading_note", str, "")

        for tag in self.tags:
            if not isinstance(tag, str): raise InvalidData("Tags must be strings")
        for dep in self.dependencies:
            if not isinstance(dep, list): raise InvalidData("Dependencies must be strings")
            
            for path_section in dep:
                if not isinstance(path_section, str): raise InvalidData("Dependency path must consist of strings")

#Represents an entire assignment (a list of problems)
class AssignmentStatement:
    @staticmethod
    def load(spec_path, template_path):
        template = SubmissionTemplate.load(template_path)
        with open(spec_path,'r') as f:
            c = json.load(f)
            c.setdefault('assignment', {})
            return AssignmentStatement(c['assignment'], template)

    def __init__(self, jsondata, template):

        validateJson(jsondata)
        
        self.title = jsondata["title"]
        self.context = json_has_or(jsondata, "context", str, "")
        self.problems = [ProblemStatement(prob, template) for prob in jsondata["problems"]]
