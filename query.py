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

# Gets a response from OpenAI, given the OpenAI client, a prompt, and code
# probs is a list of problems to check. If omitted, all problems are tested
# (OpenAI, dict, Submission, probs=list[int]) -> list[dict]
async def get_comment(client, assignment, submission, config, prob=None):
    if prob is None:
        probs = assignment.problems
    else:
        probs = [assignment.problems[prob]]
    return await asyncio.gather(*[get_comment_on_prob(client, assignment, submission, p, config) for p in probs])

# Gets a response from OpenAI for a particular problem number, given the OpenAI client, a prompt, and code
# (OpenAI, Assignment, Submission, Problem, dict) -> dict
async def get_comment_on_prob(client, assignment, submission, problem, config):
    code = submission.at(problem.path).contents()

    res = {
        "path" : problem.path,
        "line_number" : "0",
        "text" : "none",
        "code" : code
    }

    prompt = get_prompt_using_config(problem, code, assignment, config)
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
