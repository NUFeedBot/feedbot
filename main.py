import argparse
import asyncio
import json
import requests
from openai import AsyncOpenAI
import logging
logger = logging.getLogger(__name__)

from submission import SubmissionTemplate
from assignment import ProblemStatement, AssignmentStatement
from query import get_comment


# Sends a POST request to the given URL, using the given list of comments
# (str (URL), List[Comment]) -> Response
def send_request(url, comments):
    addendum = 'entry'

    request_obj = {
        'comments': json.dumps(
            {
                "comments": comments
            }
        ),
    }

    return requests.post(url + "/" + addendum, params=request_obj)


def process(assignment_spec_path,
            assignment_template_path,
            submission_path,
            config_path,
            problem_number,
            post_url,
            results_path):
    logger.info("\n\nprocessing submission {} with assignment {} and config {}\n".format(submission_path,assignment_template_path,config_path))

    with open("key", 'r') as key,\
         open(config_path, 'r') as config:
        client = AsyncOpenAI(api_key=key.read().rstrip())
        config = json.load(config)
        assignment = AssignmentStatement.load(assignment_spec_path, assignment_template_path)
        submission = SubmissionTemplate.load(submission_path)
        #subdata = slice_submission(submission_path)
        #if not subdata.has_all_problems(range(len(assignment.problems))):
        #    raise InvalidSubmission("Submission does not have all problems", -1)

        answer = asyncio.run(get_comment(client, assignment, submission, config, problem_number))

        #Default score of 0, needed for gradescope scoring
        output = {"score": 0.0}

        if results_path:
            output["feedback"] = answer
        else:
            print("\n\n\n\nModel Output:")
            for part in answer:
                print(f"\n\n=============================\n")
                print(f"{submission_path}: {'=>'.join(part['path'])}\n")
                print(part['code'])
                print(f"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
                print(part['text'])
                print(f"\n=============================\n\n")


        if post_url:
            response = send_request(
                post_url,
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
    parser.add_argument('-j', '--spec', required = True)
    parser.add_argument('-c', '--config', default = "config.json")
    parser.add_argument('-r', '--result')
    parser.add_argument('-p', '--problem', type=int)
    parser.add_argument('-d', '--debug', action='store_true')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.INFO)

    process(args.spec, args.assignment, args.submission, args.config, args.problem, args.url, args.result)
