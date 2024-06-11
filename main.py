import argparse
import asyncio
import json
from openai import AsyncOpenAI
import logging
logger = logging.getLogger(__name__)


from assignmentdata import AssignmentStatement, InvalidSubmission
from slicesubmission import slice_submission
from query import get_comment



def process(assignment_path,
            submission_path,
            config_path,
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
        answer = asyncio.run(get_comment(client, assignment, subdata, config))

        output = {"score": 1.0}

        if results_path:
            output["feedback"] = answer
        else:
            for part in answer:
                print(f"\n\nProb: {part['prob']}")
                print(f"\nLinenum: {part['line_number']}")
                print(f"\nResponse: \n\n{part['text']}")

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
                json.dump(output, results_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='FeedBot autograder'
    )

    parser.add_argument(
        '-u',
        '--url'
    )
    parser.add_argument('-s', '--submission')
    parser.add_argument('-a', '--assignment')
    parser.add_argument('-c', '--config', default="config.json")
    parser.add_argument('-r', '--result')
    parser.add_argument('-d', '--debug', action='store_true')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.INFO)

    process(args.assignment, args.submission, args.config, args.url, args.result)
