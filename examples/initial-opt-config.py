#! /usr/bin/env python

"""
This experiment runs the "initial" optimal tuning configuration on some STRIPS
domains. In addition to the standard absolute reports, it writes a python
module containing the solved problems.
"""

import os

from downward.experiment import DownwardExperiment
from downward.checkouts import Translator, Preprocessor, Planner
from downward.reports.absolute import AbsoluteReport
from downward.reports.suite import SuiteReport
from lab.environments import LocalEnvironment, GkiGridEnvironment
from lab.steps import Step

import standard_exp


# On the grid it is good practice to start the job's name with your initials.
EXPNAME = 'js-initial-opt-config'

if standard_exp.REMOTE:
    # On the grid
    EXPPATH = os.path.join('/home/downward/jendrik/experiments/', EXPNAME)
    REPO = '/home/downward/jendrik/downward'
    SUITE = 'LMCUT_DOMAINS'
    ENV = GkiGridEnvironment(priority=-2, queue='xeon_core.q')
else:
    # Local testing
    EXPPATH = os.path.join('/home/jendrik/lab/experiments', EXPNAME)
    REPO = '/home/jendrik/projects/Downward/downward'
    SUITE = 'gripper:prob01.pddl'
    ENV = LocalEnvironment(processes=2)

ATTRIBUTES = ['coverage', 'expansions', 'total_time']
# The time and memory limits can be changed for translate, preprocess and search.
LIMITS = {'search_time': 1800}
# Use the working copy versions of all three components.
COMBINATIONS = [(Translator(repo=REPO), Preprocessor(repo=REPO), Planner(repo=REPO))]

# Fast Downward configuration as a list of strings.
CONFIG = ["--landmarks", "lmg=lm_rhw(only_causal_landmarks=false,"
                         "disjunctive_landmarks=true,"
                         "conjunctive_landmarks=true,no_orders=false)",
          "--heuristic", "hLMCut=lmcut()",
          "--heuristic", "hLM=lmcount(lmg,admissible=true)",
          "--heuristic", "hCombinedMax=max([hLM,hLMCut])",
          "--search", "astar(hCombinedMax,mpd=true,pathmax=false,cost_type=0)"]

exp = DownwardExperiment(path=EXPPATH, environment=ENV, repo=REPO,
                         combinations=COMBINATIONS, limits=LIMITS)

exp.add_suite(SUITE)
# This method requires a nickname and the real config.
exp.add_config('opt-initial', CONFIG)

# Create two absolute reports. One has a line for each domain, and one has a
# line for each problem.
abs_domain_report_file = os.path.join(exp.eval_dir, '%s-abs-d.html' % EXPNAME)
abs_problem_report_file = os.path.join(exp.eval_dir, '%s-abs-p.html' % EXPNAME)
exp.add_step(Step('report-abs-d', AbsoluteReport('domain', attributes=ATTRIBUTES),
                                                 exp.eval_dir, abs_domain_report_file))
exp.add_step(Step('report-abs-p', AbsoluteReport('problem', attributes=ATTRIBUTES),
                                                 exp.eval_dir, abs_problem_report_file))

# Write suite with solved problems
def solved(run):
    return run['coverage'] == 1
suite_file = os.path.join(exp.eval_dir, '%s_solved_suite.py' % EXPNAME)
exp.add_step(Step('report-suite', SuiteReport(filter=solved), exp.eval_dir, suite_file))

# Copy the results
exp.add_step(Step.publish_reports(abs_domain_report_file, abs_problem_report_file))

# Compress the experiment directory
exp.add_step(Step.zip_exp_dir(exp))

# Remove the experiment directory
exp.add_step(Step.remove_exp_dir(exp))

# This method parses the commandline. We assume this file is called exp.py.
# Supported styles:
# ./exp.py 1
# ./exp.py 4 5 6
exp()
