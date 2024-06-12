import argparse
import asyncio
import json
import requests
from openai import AsyncOpenAI
import logging
logger = logging.getLogger(__name__)


from assignmentdata import AssignmentStatement, InvalidSubmission
from slicesubmission import slice_submission
from query import get_comment


# Sends a POST request to the given URL, using the given list of comments
# (str (URL), List[Comment]) -> Response
def send_request(url, code, comments):
    addendum = 'entry'

    request_obj = {
        'code': code,
        'comments': json.dumps(
            {
                "comments": comments
            }
        ),
    }

    return requests.post(url + "/" + addendum, params=request_obj)


def process(assignment_path,
            submission_path,
            config_path,
            problem_number,
            post_url,
            results_path):
    logger.info("processing submission {} with assignment {} and config {}".format(submission_path,assignment_path,config_path))

    with open("key", 'r') as key,\
         open(config_path, 'r') as config:
        client = AsyncOpenAI(api_key=key.read().rstrip())
        config = json.load(config)
        assignment = AssignmentStatement.load(assignment_path)
        subdata = slice_submission(submission_path)
        if not subdata.has_all_problems(range(len(assignment.problems))):
            raise InvalidSubmission("Submission does not have all problems", -1)
        answer = asyncio.run(get_comment(client, assignment, subdata, config, problem_number))

        output = {"score": 1.0}

        if results_path:
            output["feedback"] = answer
        else:
            for part in answer:
                print(f"\n\n=============================\n")
                print(f"Problem: {part['prob']} ({submission_path}#L{part['line_number']})\n")
                print(part['code'])
                print(f"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
                print(part['text'])
                print(f"\n=============================\n\n")


        if post_url:
            response = send_request(
                post_url,
                subdata.full_code,
                answer
            )
            output["tests"] = [{"output" : response.text}]
            print(post_url + "/submission/" + json.loads(response.text)['msg'][4:])
        if results_path:
            with open(results_path, 'w') as results_file:
                json.dump(output, results_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='FeedBot autograder'
    )

    parser.add_argument(
        '-u',
        '--url'
    )
    parser.add_argument('-s', '--submission', required = True)
    parser.add_argument('-a', '--assignment', required = True)
    parser.add_argument('-c', '--config', default = "config.json")
    parser.add_argument('-r', '--result')
    parser.add_argument('-p', '--problem', type=int)
    parser.add_argument('-d', '--debug', action='store_true')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.INFO)

    process(args.assignment, args.submission, args.config, args.problem, args.url, args.result)
