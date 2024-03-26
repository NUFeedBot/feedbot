import json
import asyncio


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

DEFAULT_PROMPTS = {
    'general':'Give feedback on the following code written in the Beginning'
        + ' Student Language Dialect of Racket in terms of its'
        + ' adherence to the Design Recipe from the textbook How to Design Programs.\n',
    'statement':'The problem statement given to the student was:\n',
    'code':'The student\'s code for this problem was:\n\n',


    'data_design': 'Give feedback on the following code written in the Beginning'
        + ' Student Language Dialect of Racket in terms of its'
        + ' adherence to the Data Design Recipe from the textbook How to Design Programs:\n\n',
    'implementation': 'Give feedback on the following code written in the Beginning'
        + ' Student Language Dialect of Racket in terms of how well it follows'
        + ' the Design Recipe from the textbook How to Design Programs:\n\n',
    'list_abstraction': 'Give feedback on these Racket list abstractions:\n\n',
}

# Makes an API request with the given string prompt
# (OpenAI, str) -> str
async def make_api_request(client, prompt):
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
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
async def get_comment(client, config, sub, probs=None):
    res = []
    if probs is None:
        probs = range(len(config["assignment"].problems))

    return await asyncio.gather(*[get_comment_on_prob(client, config, sub, i) for i in probs])

# Gets a response from OpenAI for a particular problem number, given the OpenAI client, a prompt, and code
# (OpenAI, dict, Submission, int) -> dict
async def get_comment_on_prob(client, config, sub, problem_no):
    statement = get_problem(config, problem_no)
    prob = get_problem_code(sub, problem_no)

    if "FD" in statement.tags:
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

        prompt = get_prompt(statement, prob["code"])
        
        res["text"] = await make_api_request(client, prompt)

    return res

# Gets the problem statement for the given problem_no in the config
# (dict, int) -> ProblemStatement
def get_problem(config, problem_no):
    return config['assignment'].problems[problem_no]

# Gets the student's code for the given problem
# (Submission, int) -> str
def get_problem_code(code, problem_no):
    return code.get_problem(problem_no)

# Creates a prompt for OpenAI from a problem statement and code
# (ProblemStatement, str) -> str
def get_prompt(problem, code):
    return DEFAULT_PROMPTS['general'] \
        + DEFAULT_PROMPTS['statement'] \
        + problem.statement + '\n\n' \
        + DEFAULT_PROMPTS['code'] \
        + code
