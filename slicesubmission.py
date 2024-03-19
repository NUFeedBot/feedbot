from assignmentdata import *
from pprint import pprint

def slice_submission(subpath):
    with open(subpath) as subfile:
        all_code = ""

        secs = []
        content = ""
        prob_num = -1
        linenum = 1

        def add_sec():
            nonlocal secs, content, prob_num, linenum
            if prob_num != -1 or content.strip() != "":
                secs.append({
                    "prob": -1 if prob_num == -1 else prob_num - 1,
                    "code": content,
                    "linenum": linenum
                })
            content = ""

        for line in subfile:
            all_code += line
            sline = line.strip()

            if sline.startswith(PROB_START):
                add_sec()
                if prob_num != -1: raise InvalidSubmission("Can't start a new problem within another problem", linenum)
                numstr = sline[len(PROB_START):].split(':')[0].strip().split(' ')[0]
                if not numstr.isdigit(): raise InvalidSubmission(f"Invalid problem number: {numstr}", linenum)
                prob_num = int(numstr)
                if prob_num <= 0: raise InvalidSubmission(f"Problem number must be at least 1: {prob_num}", linenum)

            elif sline.startswith(PROB_END):
                add_sec()
                if prob_num == -1: raise InvalidSubmission("Can't end a problem when none has started", linenum)
                numstr = sline[len(PROB_END):].split(':')[0].strip().split(' ')[0]
                if not numstr.isdigit(): raise InvalidSubmission(f"Invalid problem number: {numstr}", linenum)
                new_num = int(numstr)
                if new_num != prob_num: raise InvalidSubmission("Can't end a problem that wasn't the last one started", linenum)
                prob_num = -1

            else:
                content += line

            linenum += 1
        
        if prob_num != -1: raise InvalidSubmission("Didn't end final problem", linenum)
        add_sec()
        
        return Submission(all_code, secs)

# Example
# pprint(slice_submission("example-submission.rkt").all_sections)
        