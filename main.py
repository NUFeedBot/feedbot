#!/usr/bin/env python3

import argparse
import asyncio
import json
import requests
from openai import AsyncOpenAI
import os
import sys
import logging
logger = logging.getLogger(__name__)

from starter_checker import submission_uses_starter
from submission import SubmissionTemplate
from assignment import ProblemStatement, AssignmentStatement
from query import get_comment

from dotenv import load_dotenv
load_dotenv()

def process(assignment_spec_path,
            assignment_template_path,
            submission_path,
            config_path,
            problem_number,
            post_url,
            results_path,
            submitter_email,
            post_key,
            dry_run):
    logger.info("\n\nprocessing submission {} with assignment {} and config {}\n".format(submission_path,assignment_template_path,config_path))

    with open(config_path, 'r') as config:
        key = os.environ["OPENAI_KEY"]
        config = json.load(config)

        output_lines = []
        if not submission_uses_starter(output_lines, submission_path, assignment_template_path):
            print("\n".join(output_lines)) 
            sys.exit(42) # TODO: Verify this error code can't come from other places.

        assignment = AssignmentStatement.load(assignment_spec_path, assignment_template_path)
        submission = SubmissionTemplate.load(submission_path)
        #subdata = slice_submission(submission_path)
        #if not subdata.has_all_problems(range(len(assignment.problems))):
        #    raise InvalidSubmission("Submission does not have all problems", -1)
        if dry_run:
            dummy_url = "dummy.url.io"
            print(dummy_url)
            return
        client = AsyncOpenAI(api_key=key)
        answer = asyncio.run(get_comment(client, assignment, submission, config, problem_number))
        output = {}

        if post_url or results_path:
            output = answer
        else:
            print("\n\n\n\nModel Output:")
            for part in answer:
                print(f"\n\n=============================\n")
                path = part['path'].split(", ")
                print(f"{submission_path}: {'=>'.join(path)}\n")
                print(part['code'])
                print(f"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
                print(part['text'])
                print(f"\n=============================\n\n")


        if post_url:
            response = send_request(
                post_url,
                post_key,
                answer,
                submitter_email
            )
            if response.status_code == 200:
                url = post_url + "/submission/" + json.loads(response.text)['msg'][4:]
                output["output"] = f"Feedbot automated feedback available at [{url}]({url})."
                output["output_format"] = "md"
                print(url)
            else:
                logger.error("Did not post successfully: " + response.text)
        
        if results_path:
            with open(results_path, 'w') as results_file:
                json.dump(output, results_file)

# Sends a POST request to the given URL, using the given list of comments
# (str (URL), List[Comment], str (Email)) -> Response
def send_request(url, key, comments, submitter_email):
    addendum = 'entry'

    request_obj = {
        'comments': json.dumps(
            {
                "comments": comments
            },
        ),
        'email': submitter_email,
        'key': key
    }

    return requests.post(url + "/" + addendum, params=request_obj)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='FeedBot autograder'
    )

    parser.add_argument('-u', '--url')
    parser.add_argument('-s', '--submission', required = True)
    parser.add_argument('-a', '--assignment', required = True)
    parser.add_argument('-j', '--spec', required = True)
    parser.add_argument('-c', '--config', default = "config.json")
    parser.add_argument('-r', '--result')
    parser.add_argument('-p', '--problem', type=int)
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-e', '--email', default = "")
    parser.add_argument('-k', '--key', default = os.environ.get("FEEDBOT_KEY",""))
    parser.add_argument('--disable-dry-run', dest='dry-run', action='store_true')
    parser.add_argument('--dry-run', action='store_true', default = False)

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.INFO)

    process(args.spec, args.assignment, args.submission, args.config, args.problem, args.url, args.result, args.email, args.key, args.dry_run)
