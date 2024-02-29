from assignmentdata import *

def generate_stub(aspath, outpath):
    with open(aspath) as asfile, open(outpath, mode="w") as outfile:
        assignment = AssignmentStatement(json.load(asfile))
        outstr = f"{assignment.lang} \n\n"
        i = 0
        for prob in assignment.problems:
            i += 1
            outstr += f"{PROB_START}{i}: {prob.title}"
            outstr += f"\n\n{prob.stub}\n\n"
            outstr += f"{PROB_END}{i}\n\n"

        outfile.write(outstr)

# Example
# generate_stub("example-problem-statement.json", "example-stub.rkt")