import json
import asyncio
import re
import logging
logger = logging.getLogger(__name__)

# Makes an API request with the given string prompt
# (OpenAI, str, str) -> str
async def make_api_request(model, client, prompt, sysmsg=None):
    messages=[]
    if sysmsg is not None:
        messages.append({ "role": "system", "content": sysmsg })
    messages.append({ "role": "user", "content": prompt })

    logger.info(messages)

    chat_completion = await client.chat.completions.create(
        messages=messages,
        model=model,
    )



    return chat_completion.choices[0].message.content

# Checks if code satisfies DR
async def screen_code(client, typ, code):
    messages = []
    messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
    messages.append({"role": "user", "content": "Call the appropriate function with the following student code: \n\n" + code})
    chat_response = await client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": lookup_screening_fun(typ)}}
    )
    return json.loads(chat_response.choices[0].message.tool_calls[0].function.arguments)['step']

# Gets a response from OpenAI, given the OpenAI client, a prompt, and code
# probs is a list of problems to check. If omitted, all problems are tested
# (OpenAI, dict, Submission, probs=list[int]) -> list[dict]
async def get_comment(client, assignment, sub, config, probs=None):
    if probs is None:
        probs = range(len(assignment.problems))

    return await asyncio.gather(*[get_comment_on_prob(client, assignment, sub, i, config) for i in probs])

# Gets a response from OpenAI for a particular problem number, given the OpenAI client, a prompt, and code
# (OpenAI, dict, Submission, int) -> dict
async def get_comment_on_prob(client, assignment, sub, problem_no, config):
    statement = get_problem(assignment, problem_no)
    prob = get_problem_code(sub, problem_no)

    if False and "FD" in statement.tags:
        screened = await screen_code(client, "function", prob["code"])
        res = {
            "prob": problem_no,
            "line_number": prob["linenum"],
            "text": screened
        }
    else:
        res = {
            "prob": problem_no,
            "line_number": prob["linenum"],
            "text": "none"
        }

        prompt = get_prompt_using_config(statement, prob["code"], assignment, config)
        res["text"] = await make_api_request(config["model"], client, prompt, config["system"])
        res["text"] = redact_codeblocks(res["text"])

    return res

# Given a string, replaces all markdown code blocks with "[CODE REDACTED]"
# str -> str
def redact_codeblocks(text):
    # Regular expression pattern to match markdown code blocks
    codeblock_pattern = r'```(?:.*)\n([\s\S]*?)```'
    redacted_text = re.sub(codeblock_pattern, "[CODE REDACTED]", text)
    return redacted_text

# Gets the problem statement for the given problem_no in the config
# (dict, int) -> ProblemStatement
def get_problem(assignment, problem_no):
    return assignment.problems[problem_no]

# Gets the student's code for the given problem
# (Submission, int) -> str
def get_problem_code(code, problem_no):
    return code.get_problem(problem_no)

# Generates a prompt from the problem, code, and config
# (ProblemStatement, str, dict, dict) -> str
def get_prompt_using_config(problem, code, assignment, config):
    return get_prompt_for("general", problem, config) \
        + get_prompt_for("pre_context", problem, config) \
        + assignment.context \
        + get_prompt_for("post_context", problem, config) \
        + get_prompt_for("pre_statement", problem, config) \
        + problem.statement \
        + get_prompt_for("post_statement", problem, config) \
        + get_prompt_for("pre_code", problem, config) \
        + code \
        + get_prompt_for("post_code", problem, config)

# Gets the prompt info for a certain config attribute name
# names followed by #TAG will also be included if the problem has that tag
# (str, ProblemStatement, dict) -> str
def get_prompt_for(name, problem, config):
    text = config[name]
    for tag in problem.tags:
        if (name + "#" + tag) in config:
            text += config[name + "#" + tag]
    return text
