import json

from submission import SubmissionTemplate, MARKER
from validate import validateJson, validateAssignmentProb, json_has, json_has_or


#Represents a single problem in an assignment along with its metadata
class ProblemStatement:
    def __init__(self, prob_data, template, prob_context):
        self.context = prob_context
        self.path = prob_data["path"]
        validateAssignmentProb(self.path, template)
        self.statement = template.at(self.path, False).contents()
        self.title = json_has_or(prob_data, "title", str, "") # What is the purpose of title?
        self.stub = json_has_or(prob_data, "stub", str, "")
        self.tags = json_has_or(prob_data, "tags", list, [])
        self.dependencies = json_has_or(prob_data, "dependencies", list, [])
        self.grading_note = json_has_or(prob_data, "grading_note", str, "")


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
        self.problem_contexts = jsondata["contexts"] # The list of (path+context) for each path
        self.problems = []
        for prob in jsondata["problems"]:
            prob_context = self.get_problem_context(prob["path"])
            self.problems.append(ProblemStatement(prob, template, prob_context))
   
    #Returns the problem context for the given path
    # returns common context for paths that are deeper that context paths
    # ie. context for Problem 1 will be returned as the context for Problem 1, Part A 
    def get_problem_context(self, prob_path):
        context_str = "\n"
        for context in self.problem_contexts:
            context_path = context["path"]
            if prob_path[:len(context_path)] == context_path:  
                context_str += context["code"] + "\n\n"
        
        return context_str