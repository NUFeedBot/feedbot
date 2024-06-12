from typing import List

MARKER = ";;!"


class Submission:
    @staticmethod
    def load(path):
        return Submission([l.rstrip("\n") for l in open(path).readlines()])

    def __init__(self, lines: List[str]):
        self.lines = lines

    def after(self, marker: str):
        """
        Returns the contents of this submission after a line starting with the marker
        """
        for i, line in enumerate(self.lines):
            if line.startswith(marker):
                return Submission(self.lines[i + 1 :])
        return Submission([])

    def before(self, marker: str):
        """
        Returns the contents of this submission before the marker
        """
        for i, line in enumerate(self.lines):
            if line.startswith(marker):
                return Submission(self.lines[:i])
        return Submission(self.lines)

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
