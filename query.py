import json
import asyncio
import re
import tiktoken
import logging
logger = logging.getLogger(__name__)

# Makes an API request with the given string prompt
# (OpenAI, str, str) -> str
async def make_api_request(model, client, prompt, prob_path, sysmsg=None):
    messages=[]
    if sysmsg is not None:
        messages.append({ "role": "system", "content": sysmsg })
    messages.append({ "role": "user", "content": prompt })



    logger.info(f"\n{prob_path}\n=================================================================================================\nUser: \n\{prompt}\n")

    tokenizer = tiktoken.encoding_for_model(model)

    # This is a little inaccurate, since it counts the role stuff, but should be okay
    ts = tokenizer.encode(str(messages))
    logger.info(f"\n--------------------------------------------\nTOKENS: {len(ts)}\n--------------------------------------------\n=================================================================================================\n\n\n")

    chat_completion = await client.chat.completions.create(
        messages=messages,
        model=model,
    )

    return chat_completion.choices[0].message.content

# Gets a response from OpenAI, given the OpenAI client, a prompt, and code
# probs is a list of problems to check. If omitted, all problems are tested
# (OpenAI, dict, Submission, probs=list[int]) -> list[dict]
async def get_comment(client, assignment, submission, config, prob=None):
    config_msg = config["system"]
    logger.info(f"\nCommon system message:\n--------------------------------------------\n{config_msg}\n--------------------------------------------\n")
    if prob is None:
        probs = assignment.problems
    else:
        probs = [assignment.problems[prob]]
    return await asyncio.gather(*[get_comment_on_prob(client, assignment, submission, p, config) for p in probs])

# Gets a response from OpenAI for a particular problem number, given the OpenAI client, a prompt, and code
# (OpenAI, Assignment, Submission, Problem, dict) -> dict
async def get_comment_on_prob(client, assignment, submission, problem, config):
    code = submission.at(problem.path).contents()
    dependencies_code = submission.extract_responses(problem.dependencies)

    res = {
        "path" : problem.path,
        "line_number" : "0",
        "text" : "none",
        "code" : code
    }

    prompt = get_prompt_using_config(problem, code, assignment, config, dependencies_code)
    res["text"] = await make_api_request(config["model"], client, prompt, "=>".join(problem.path), config["system"])
    res["text"] = redact_codeblocks(res["text"])

    return res

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
    grading_pretext = "\nThis specific problem has another additional grading note:\n" if has_grading_note else ""

    has_dependencies = (dep_code != "")
    dependencies_pretext = "\n This problem relies on the following student responses for some previous questions: \n" \
    if has_dependencies else ""

    return get_prompt_for("general", problem, config) \
        + get_prompt_for("pre_context", problem, config) \
        + assignment.context \
        + get_prompt_for("post_context", problem, config) \
        + get_prompt_for("pre_statement", problem, config) \
        + problem.statement \
        + get_prompt_for("post_statement", problem, config) \
        + dependencies_pretext \
        + dep_code \
        + grading_pretext \
        + problem.grading_note \
        + get_prompt_for("pre_code", problem, config) \
        + code \
        + get_prompt_for("post_code", problem, config)
        #+ problem.

# Gets the prompt info for a certain config attribute name
# names followed by #TAG will also be included if the problem has that tag
# (str, ProblemStatement, dict) -> str
def get_prompt_for(name, problem, config):
    text = config[name]
    for tag in problem.tags:
        if (name + "#" + tag) in config:
            text += config[name + "#" + tag]
    return text
