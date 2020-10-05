# CloudZero Take Home Exercise

We love working at CloudZero. We are looking for new friends to join our growing team.

## Concept

No one likes in-person interview problems. The goal of this take home problem is to give you the space to create something in the comfort of your own home or coffee shop that you can walk us through together. We ask that you take a few hours (~4 hours max) in the hammock with the problem below and code up a working solution.

## Problem

Given this URL http://s3.amazonaws.com/alexa-static/top-1m.csv.zip that links to a static snapshot of Alexa Top Sites data, please write a program that analyzes HTTP responses from the top **1000** sites in that list.

The analysis should include:

  - The **top 10 HTTP response headers** and the **percentage of sites in which each of those 10 headers appeared**
  - **Total Duration** of the Program

Your solution should use **Python 3.6+** and should run to completion within **15 Minutes**.

## Getting Started

We don't want you to get hung up on setting up the python project so we've provided this basic directory structure and `Makefile`. The only thing you need before using this repository is Python 3.6+. With that installed you can simply:

```bash
make virtualenv                 # create virtualenv
source virtualenv/bin/activate  # optionally set virtualenv in your shell
make init                       # install requirements.txt into virtualenv
make test                       # run `pytest tests`
make run                        # finds and runs `main.py` in the `src` directory
```

You don't have to write tests. In fact, you don't have to use this `Makefile`. This is just a guide. Feel free to choose your own adventure. All we ask is that you please document how you want us to run your program.

## Submitting Your Solution

When you are done, please submit your solution by:

- **Emailing bill.buckley@cloudzero.com** a zipfile containing your solution (no need to include the virtualenv in your zip)
