import argparse
import logging
import os
import json
import html
import time
from main import process

# Escapes text for use in HTML, and replaces line breaks with <br>
def html_escape(txt):
    return html.escape(txt).replace("\n", "<br />")

# Gets feedback for each submission in a folder crossed with each config in a folder, count number of times
# Generates a simple HTML report for easy-ish reviewing of the responses
def batch_test(sub_folder_path, config_folder_path, result_folder_path, assignment_path, spec_path, count, prob_num):
    subs = os.listdir(sub_folder_path)
    subs = [f for f in subs if os.path.isfile(os.path.join(sub_folder_path, f))]

    configs = os.listdir(config_folder_path)
    configs = [f for f in configs if os.path.isfile(os.path.join(config_folder_path, f))]

    prob_log = f"problem {prob_num}" if prob_num else "all problems"
    test_log = f"Testing submissions {subs} with configs {configs}, {count} times each, on {prob_log}"
    logging.info(test_log)
    
    prob_data = {}

    for sub in subs:
        for config in configs:
            for i in range(count):
                sub_path = os.path.join(sub_folder_path, sub)
                sub_name = sub.split('.')[0]
                config_path = os.path.join(config_folder_path, config)
                config_name = config.split('.')[0]
                result_path = os.path.join(result_folder_path, f"{sub_name}---{config_name}---{i}.json")

                process(spec_path, assignment_path, sub_path, config_path, prob_num, None, result_path, None, None)
                time.sleep(10)

                with open(result_path, 'r') as result:
                    data = json.load(result)
                    for entry in data:
                        res_key = f"{entry['path']} ~ {sub}"
                        res_data = {
                            'config': config,
                            'prompt': entry['prompt'],
                            'text': entry['text']
                        }
                        if res_key in prob_data:
                            prob_data[res_key]['responses'].append(res_data)
                        else:
                            new_prob = {
                                'path': entry['path'],
                                'sub': sub,
                                'code': entry['code'],
                                'responses': [res_data]
                            }
                            prob_data[res_key] = new_prob
    
    prob_html = ""

    for res_key in prob_data:
        prob = prob_data[res_key]
        prob_html += f"<h1>{prob['path']}</h1><h3>{prob['sub']}</h3>"
        code_lines = len(prob['code'].split('\n'))
        prob_html += f"<pre>{prob['code']}</pre>"
        # todo: show prompt but put it in a drop-down that you click to expand
        prob_html += "<table>"
        for res in sorted(prob['responses'], key=lambda res: res['config']):
            text_lines = len(res['text'].split('\n'))
            prob_html += f"<tr><td><h3>{html_escape(res['config'])}</h3><div>{html_escape(res['text'])}</div></td></tr>"
        prob_html += "</table>"
    
    html_content = \
f"""
<html>
    <head>
        <title>Report</title>
        <style>
        table {{
            border-collapse: collapse;
            margin: 5px;
        }}
        td {{
            border: 2px solid black;
            padding: 5px;
        }}
        pre {{
            margin: 5px;
            font-family: monospace;
            background-color: light-gray;
            padding: 5px;
            border: 1px solid black;
        }}
        </style>
    </head>
    <body>
    <div>{test_log}</div>
    <div>{prob_html}</div>
    </body>
</html>
"""

    with open(os.path.join(result_folder_path, "report" + time.strftime("%Y-%m-%d-%H%M%S") + ".html"), 'w', encoding="utf-8") as report:
        report.write(html_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='FeedBot batch tester'
    )

    parser.add_argument('-s', '--submissions', required = True)
    parser.add_argument('-c', '--configs', required = True)
    parser.add_argument('-a', '--assignment', required = True)
    parser.add_argument('-j', '--spec', required = True)
    parser.add_argument('-r', '--results', required = True)
    parser.add_argument('-p', '--problem', type=int)
    parser.add_argument('-n', '--count', type=int, default=3)

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    batch_test(args.submissions, args.configs, args.results, args.assignment, args.spec, args.count, args.problem)
