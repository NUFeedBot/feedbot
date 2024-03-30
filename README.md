# FeedBot

## setup

in order to generate comments, you'll need to make an OpenAI API key and put it in a file named `key` in the root of the project directory. `key` is already gitignored.

you'll also need to install the requests and openai python packages.

## running

### local

to run the autograder locally, tack the `--local` option. you also likely want to tack `--url` in order to specify a locally running version of the server.

### args

tacking `--src` specifies the file to use as student submission (default `test_src.rkt`)

tacking `--config` specifies the file to use as problem config (default `config.json`)

tacking `--prompt` specifies the file to use as prompt config (default `promptconfigs/system_role.json`)

### gradescope

to run the autograder, zip the entire directory and choose the "upload as zip" option on gradescope.

## info

- setup.sh is the gradescope install script
- test_src.rkt is the file that the autograder will use if you choose the local option
