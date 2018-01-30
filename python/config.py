# config.py ---
#
# Filename: config.py
# Description:
# Author: Kwang Moo Yi
# Maintainer:
# Created: Mon Jan 29 17:57:59 2018 (-0800)
# Version:
# Package-Requires: ()
# URL:
# Doc URL:
# Keywords:
# Compatibility:
#
#

# Commentary:
#
#
#
#

# Change Log:
#
#
#

# Code:


import argparse


# ----------------------------------------
# Global variables within this script
arg_lists = []
parser = argparse.ArgumentParser()


def add_argument_group(name):
    arg = parser.add_argument_group(name)
    arg_lists.append(arg)
    return arg


# ----------------------------------------
# Arguments for training
global_arg = add_argument_group("Global")


global_arg.add_argument("--account", type=str,
                        default="def-kyi",
                        help="")

global_arg.add_argument("--todo_dir", type=str,
                        default="./jobs/todo",
                        help="")

global_arg.add_argument("--done_dir", type=str,
                        default="./jobs/done",
                        help="")

global_arg.add_argument("--output_dir", type=str,
                        default="./jobs/output",
                        help="")

# ----------------------------------------
# Arguments for model
job_arg = add_argument_group("Job")


job_arg.add_argument("--num_jobs", type=int,
                     default=1,
                     help="")
job_arg.add_argument("--num_runs", type=int,
                     default=5,
                     help="")
job_arg.add_argument("--num_gpu", type=int,
                     default=1,
                     help="")
job_arg.add_argument("--num_cpu", type=str,
                     default="auto",
                     help="")
job_arg.add_argument("--mem", type=str,
                     default="auto",
                     help="")
job_arg.add_argument("--time_limit", type=str,
                     default="0-03:00",
                     help="")
job_arg.add_argument("--depends_key", type=str,
                     default="none",
                     help="")


def get_config():
    config, unparsed = parser.parse_known_args()

    return config, unparsed


def print_usage():
    parser.print_usage()


#
# config.py ends here
