ARG BASE_REPO=gradescope/autograder-base
ARG TAG=latest

FROM ${BASE_REPO}:${TAG}

RUN apt-get update -y && \
    apt install -y software-properties-common xvfb libcairo2 libpango1.0-0 libgtk2.0-0 jq && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN wget https://download.racket-lang.org/releases/8.11.1/installers/racket-8.11.1-x86_64-linux-cs.sh && \
    sh racket-8.11.1-x86_64-linux-cs.sh  --unix-style --dest /usr/ --create-dir

ADD source /autograder/source

RUN cp /autograder/source/run_autograder /autograder/run_autograder

RUN cd /autograder/source && pip3 install -r requirements.txt

# Ensure that scripts are Unix-friendly and executable
RUN dos2unix /autograder/run_autograder
RUN chmod +x /autograder/run_autograder
