import json
import asyncio
import re

tools = [
    {
        "type": "function",
        "function": {
            "name": "function_design_recipe_step",
            "description": "Function to call with a string indicating the first step of the Function Design Recipe from the textbook How To Design Programs where the code needs improvement.",
            "parameters": {
                "type": "object",
                "properties": {
                    "step": {
                        "type": "string",
                        "enum": ["nocode", "signature", "purpose", "tests", "implementation", "done"],
                        "description": "'nocode' if there is no code, or the code has no relation to the problem statement, 'signature' if there are problems in the Signatures of functions, 'purpose' if the Signatures are all perfect but the descriptive purpose statements are imprecise or vague, 'tests' if the Signatures and Purposes are perfect but the tests are missing important cases, 'implementation' if the Signature, Purpose, and Tests are perfect but the code has issues, including not passing its tests, and 'done' if all steps of the Design Recipe have been followed and working code has been produced."
                    }
                },
                "required": ["satisfies"]
            },
        }
    }]

def lookup_screening_fun(typ):
    if typ == "function":
        return "function_design_recipe_step"
    else:
        return "general_design_recipe"

DEFAULT_PROMPT_CONFIG = {
    "system": "Give feedback to a student in a programming class. DO NOT answer with code. Address the student using \"you\", \"your\", etc.",

    "general": "Give feedback on the following code written in the Beginning Student Language Dialect of Racket in terms of its adherence to the Design Recipe from the textbook How to Design Programs. The sturent was instructed to respond to the following problem statement:\n",
    "general#DD": "Note that this problem focuses specifically on data design.",
    "general#LA": "Note that this problem focuses specifically on the correct use of list abstractions.",

    "pre_statement": "The student was instructed to respond to the following problem statement:\n",
    "post_statement": "\n\n",

    "pre_code": "The student's code for this problem was:\n",
    "post_code": "\n\nRemember, do not write any code for the student"
}

# Makes an API request with the given string prompt
# (OpenAI, str, str) -> str
async def make_api_request(client, prompt, sysmsg=None):
    messages=[]
    if sysmsg is not None:
        messages.append({ "role": "system", "content": sysmsg })
    messages.append({ "role": "user", "content": prompt })
    chat_completion = await client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo-preview",
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
async def get_comment(client, config, sub, probs=None, prompt_config=None):
    if probs is None:
        probs = range(len(config["assignment"].problems))

    return await asyncio.gather(*[get_comment_on_prob(client, config, sub, i, prompt_config) for i in probs])

# Gets a response from OpenAI for a particular problem number, given the OpenAI client, a prompt, and code
# (OpenAI, dict, Submission, int) -> dict
async def get_comment_on_prob(client, config, sub, problem_no, prompt_config):
    statement = get_problem(config, problem_no)
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

        if prompt_config is None:
            prompt_config = DEFAULT_PROMPT_CONFIG

        prompt = get_prompt_using_config(statement, prob["code"], config, prompt_config)
        res["text"] = await make_api_request(client, prompt, prompt_config["system"])
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
def get_problem(config, problem_no):
    return config['assignment'].problems[problem_no]

# Gets the student's code for the given problem
# (Submission, int) -> str
def get_problem_code(code, problem_no):
    return code.get_problem(problem_no)

# Generates a prompt from the problem, code, and config
# (ProblemStatement, str, dict, dict) -> str
def get_prompt_using_config(problem, code, config, prompt_config):
    return get_prompt_for("general", problem, prompt_config) \
        + get_prompt_for("pre_context", problem, prompt_config) \
        + config['assignment'].context \
        + get_prompt_for("post_context", problem, prompt_config) \
        + get_prompt_for("pre_statement", problem, prompt_config) \
        + problem.statement \
        + get_prompt_for("post_statement", problem, prompt_config) \
        + get_prompt_for("pre_code", problem, prompt_config) \
        + code \
        + get_prompt_for("post_code", problem, prompt_config)

# Gets the prompt info for a certain config attribute name
# names followed by #TAG will also be included if the problem has that tag
# (str, ProblemStatement, dict) -> str
def get_prompt_for(name, problem, prompt_config):
    text = prompt_config[name]
    for tag in problem.tags:
        if (name + "#" + tag) in prompt_config:
            text += prompt_config[name + "#" + tag]
    return text
