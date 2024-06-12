# FeedBot

## setup

in order to generate comments, you'll need to make an OpenAI API key and put it in a file named `key` in the root of the project directory. `key` is already gitignored.

you'll also need to install the requests and openai python packages.

Easiest is to set up a virtual environment with:

``` python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## running

To run locally, printing to stdout:

``` python
python main.py -d -s test_src.rkt -a test_assign.json -c config.json 
```

To run locally, printing to `results.json`

``` python
python main.py -s test_src.rkt -a test_assign.json -c config.json -r results.json 
```

To post to a server:


``` python
python main.py -s test_src.rkt -a test_assign.json -c config.json -r results.json -u https://feedbot.dbp.io 
```

### args

tacking `--src` or `-s` specifies the file to use as student submission

tacking `--assignment` or `-s` specifies the file to use as assignment specification

tacking `--config` or `-c` specifies the file to use as system & prompt config, defaults to `config.json` in current directory

tacking `--result` or `-r` specifies the file to store output to, and not to print it

tacking `--url` or `-u` specifies the url where results should be sent, in addition to being printed or storing to a local file.

tacking `--problem` or `-p` specifies the (base 0) index of the (single) problem to get feedback on, rather than doing all the problems. Most likely useful during debugging.

tacking `--debug` or `-d` specifies debug more logging than normal

### gradescope

TBD
