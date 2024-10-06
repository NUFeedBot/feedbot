import json

from submission import SubmissionTemplate, MARKER
from validate import validateJson, validateAssignmentProb, json_has, json_has_or


#Represents a single problem in an assignment along with its metadata
class ProblemStatement:
    def __init__(self, prob_data, template):
        self.path = prob_data["path"]
        self.context = self.retrieve_problem_context(template)
        validateAssignmentProb(self.path, template)
        self.statement = template.at(self.path, False).contents()
        self.title = json_has_or(prob_data, "title", str, "") # What is the purpose of title?
        self.stub = json_has_or(prob_data, "stub", str, "")
        self.tags = json_has_or(prob_data, "tags", list, [])
        self.dependencies = json_has_or(prob_data, "dependencies", list, [])
        self.grading_note = json_has_or(prob_data, "grading_note", str, "")
    
    def retrieve_problem_context(self, template): 
        """
        Returns the context for this problem (instructions in outer problems), given the template
        """

        prob_context = "\n"
        for i in range(1, len(self.path)):
            prob_context += template.at(self.path[0:-i], False).contents()
            prob_context += "\n\n"
        return prob_context

        



#Represents an entire assignment (a list of problems) along with its metadata
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
        self.problems = []
        for prob in jsondata["problems"]:
            self.problems.append(ProblemStatement(prob, template))