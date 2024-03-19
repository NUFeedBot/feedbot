import json

tools = [
    {
        "type": "function",
        "function": {
            "name": "htdp_design_recipe",
            "description": "Function to call with a boolean indicating whether the code satisfies the Design Recipe from the textbook How To Design Programs",
            "parameters": {
                "type": "object",
                "properties": {
                    "satisfies": {
                        "type": "string",
                        "enum": ["true", "false"],
                        "description": "'true' if the source code written in the Beginning Student Language Dialect of Racket satisfies the Design Recipe, 'false' if it does not satisfy the design recipe"
                    }
                },
                "required": ["satisfies"]
            },
        }
    }]


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
def make_api_request(client, prompt):
    chat_completion = client.chat.completions.create(
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
def screen_code(client, code):
    messages = []
    messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
    messages.append({"role": "user", "content": "Call the appropriate function with the following student code: \n\n" + code})
    chat_response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "htdp_design_recipe"}}
    )
    return 'true' == json.loads(chat_response.choices[0].message.tool_calls[0].function.arguments)['satisfies']

# Gets a response from OpenAI, given the OpenAI client, a prompt, and code
# (OpenAI, dict, Submission) -> str
def get_comment(client, config, sub):
    problem_no = 0 # currently hardcoded single problem number
    statement = get_problem(config, problem_no)
    code = get_problem_code(sub, problem_no)

    screened = screen_code(client,code)

    if screened:
        return "Code looks good"
    else:
        prompt = get_prompt(statement, code)

        return make_api_request(client, prompt)

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
