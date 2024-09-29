import asyncio
import re
import tiktoken
import logging
logger = logging.getLogger(__name__)
from validate import validateSubmissionProb, json_has, json_has_or

# Makes an API request with the given string prompt
# (OpenAI, str, str, str, str) -> str
async def make_api_request(model, client, prompt, prob_path, sysmsg=None):
    messages=[]
    if sysmsg is not None:
        messages.append({ "role": "system", "content": sysmsg })
    messages.append({ "role": "user", "content": prompt })



    logger.info(f"\n{prob_path}\n=================================================================================================\nUser: \n\{prompt}\n")

    tokenizer = tiktoken.encoding_for_model(model)

    # This is a little inaccurate, since it counts the role stuff, but should be okay
    ts = tokenizer.encode(str(messages))
    logger.info(f"\n--------------------------------------------\n INPUT TOKENS: {len(ts)}\n--------------------------------------------\n")

    chat_completion = await client.chat.completions.create(
        messages=messages,
        model=model,
        temperature=0.22
    )

    #Output token usage
    ts = tokenizer.encode(str(chat_completion.choices[0].message.content))
    logger.info(f"\n--------------------------------------------\n OUTPUT TOKENS: {len(ts)}\n--------------------------------------------\n")

    logger.info("=================================================================================================\n\n\n")
    
    return chat_completion.choices[0].message.content

# Gets a response from OpenAI, given the OpenAI client, the assignment, student submission, 
# and config. probs is an int index of a problem to check. 
# If omitted, all problems are tested.
# (OpenAI, dict, SubmissionTemplate, dict, probs=int) -> list[dict]
async def get_comment(client, assignment, submission, config, prob=None):
    config_msg = config["system"]
    logger.info(f"\nCommon system message:\n--------------------------------------------\n{config_msg}\n--------------------------------------------\n")
    if prob is None:
        probs = assignment.problems
    else:
        probs = [assignment.problems[prob]]
    return await asyncio.gather(*[get_comment_on_prob(client, assignment, submission, p, config) for p in probs])

# Gets a response from OpenAI for a particular problem number, 
# given the OpenAI client, asignment, student submission, the problem, and config 
# (OpenAI, Assignment, SubmissionTemplate, ProblemStatement, dict) -> dict
async def get_comment_on_prob(client, assignment, submission, problem, config):
    try:
        validateSubmissionProb(problem.path, submission)
        code = submission.at(problem.path, True).contents()
        dependencies_code = submission.extract_responses(problem.dependencies)

        res = {
            "path" : ", ".join(problem.path),
            "prompt" : "none",
            "text" : "none",
            "code" : code
        }

        prompt = get_prompt_using_config(problem, code, assignment, config, dependencies_code)
        res["prompt"] = prompt
        res["text"] = await make_api_request(config["model"], client, prompt, "=>".join(problem.path), config["system"])
        if json_has(config, "delimiter", str):
            res["text"] = cut_at_delimiter(res["text"], config["delimiter"])
        res["text"] = redact_codeblocks(res["text"])
        res["text"] = res["text"].strip()
    except:
        logging.exception('')
        res = {
            "path": "ERROR",
            "prompt": "ERROR",
            "text": "ERROR",
            "code": "ERROR"
        }

    return res

# Given a string and delimiter, returns the part of the string occuring after 
# the delimiter, or "[internal error]" if the delimiter is not present
# (str, str) -> str
def cut_at_delimiter(text, delimiter):
    sides = text.split(delimiter)
    if len(sides) < 2: return "[internal error]"
    return sides[-1]

# Given a string, replaces all markdown code blocks with "[CODE REDACTED]"
# str -> str
def redact_codeblocks(text):
    # Regular expression pattern to match markdown code blocks
    codeblock_pattern = r'```(?:.*)\n([\s\S]*?)```'
    redacted_text = re.sub(codeblock_pattern, "[CODE REDACTED]", text)
    return redacted_text

# Generates a prompt from the problem, code, config, and dependencies
# (ProblemStatement, str, dict, dict, str) -> str
def get_prompt_using_config(problem, code, assignment, config, dep_code):
    has_grading_note = (problem.grading_note != "")
    has_dependencies = (dep_code != "")
    has_context = (problem.context.strip() != "")
    has_code = (code.strip() != "")

    # general prompt
    prompt = get_prompt_for("general", problem, config)

    # context (i.e. if the instructor provided extra instructions or data definitions at the top of the code)
    if has_context:
        prompt += get_prompt_for("pre_context", problem, config) \
        + f"```\n{problem.context.strip()}\n```" \
        + get_prompt_for("post_context", problem, config)
    
    # the problem statement (for the specific part, i.e. Problem 1D, or Problem 7A)
    prompt += get_prompt_for("pre_statement", problem, config) \
        + f"```\n{problem.statement.strip()}\n```" \
        + get_prompt_for("post_statement", problem, config)
    
    # an additional grading note, if provided in the spec
    if has_grading_note:
        prompt += get_prompt_for("pre_gradenote", problem, config) \
        + f"```\n{problem.grading_note.strip()}\n```" \
        + get_prompt_for("post_gradenote", problem, config)


    # past code from the student, if it is relevant for this problem
    if has_dependencies:
        prompt += get_prompt_for("pre_dependencies", problem, config) \
        + f"```\n{dep_code.strip()}\n```" \
        + get_prompt_for("post_dependencies", problem, config)
    
    # finally, student code
    code = code if has_code else ";; blank response"
    prompt += get_prompt_for("pre_code", problem, config) \
        + f"```\n{code.strip()}\n```" \
        + get_prompt_for("post_code", problem, config)
    
    return prompt

# Gets the prompt info for a certain config attribute name
# names followed by #TAG will also be included if the problem has that tag
# (str, ProblemStatement, dict) -> str
def get_prompt_for(name, problem, config):
    text = config[name]
    for tag in problem.tags:
        if (name + "#" + tag) in config:
            text += config[name + "#" + tag]
    return text
