from typing import List

MARKER = ";;!"

# Represents an rkt file/txt file that is either a student submitted file, assignment file, or a specific assignment problem
class SubmissionTemplate:
    @staticmethod
    def load(path):
        return SubmissionTemplate([l.rstrip("\n") for l in open(path).readlines()])

    def __init__(self, lines: List[str]):
        self.lines = lines

    def after(self, marker: str):
        """
        Returns the contents of this submission after a line starting with the marker
        
        """
        for i, line in enumerate(self.lines):
            if line.startswith(marker):
                return SubmissionTemplate(self.lines[i + 1 :])
        return SubmissionTemplate([])

    def before(self, marker: str):
        """
        Returns the contents of this submission before the marker

        """
        for i, line in enumerate(self.lines):
            if line.startswith(marker):
                return SubmissionTemplate(self.lines[:i])
        return SubmissionTemplate(self.lines)

    def contents(self):
        """
        Returns the contents as a single string

        """
        return "\n".join(self.lines)

    def at(self, path):
        """
        Returns the contents indexed by the given path of marker strings

        """
        if path == []:
            return self.before(MARKER)
        else:
            return self.after(MARKER + " " + path[0]).at(path[1:])
    

    def extract_responses(self, problem_paths):
        """
        Given problem paths, extracts all student responses for these problem paths (to be used as dependencies)
        
        """
        dependencies = ""

        for path in problem_paths:
            path_str = ",".join(path)
            dependencies += f"Student response for {path_str}: \n" + self.at(path).contents()
        
        
        return dependencies
    
    def has_data(self):
        """
        Returns if this submission template has any lines
        
        """
        return (self.lines != [])
