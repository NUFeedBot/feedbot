import difflib
from pathlib import Path

def submission_uses_starter(output_lines, submission_path, template_path):
    """
    Helper for _precheck_submission. Checks that submission_file follows the
    template in template_file as follows;
    1. Extract the template lines from both files and check that the line contents
       are identical.
    2. Report the any extra/missing lines.
    """
    MESSAGE = "Does the submission follow the starter file?"
    template_lines = _extract_template_lines(Path(template_path))
    submission_lines = _extract_template_lines(Path(submission_path))

    if template_lines == submission_lines:
        output_lines.append(f"✅ {MESSAGE}")
        return True
    
    output_lines.append(f"❌ {MESSAGE}")

    differ = difflib.Differ()
    diff = differ.compare(template_lines, submission_lines)

    output_lines.append("The submission does not follow the starter code. Look at the output below.")
    output_lines.append("Lines starting with '-' are missing from your submission.")
    output_lines.append("Lines starting with '+' are extra lines in your submission.")
    output_lines.append("")
    output_lines.extend(diff)
    return False

def _extract_template_lines(file: Path):
    """
    Returns a list of the lines that begin with ";;!".
    """
    template_lines = []
    with file.open("rt") as f:
        for line in f:
            # Just a hack to ensure we can test with the homework master.
            if line.startswith(";;!hide"):
                continue
            if line.startswith(";;!show"):
                continue
            if line.startswith(";;!"):
                template_lines.append(line.rstrip())
    return template_lines
