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


global_arg.add_argument(
    "--account", type=str,
    default="def-kyi",
    help="Slurm account to use. "
    "Please change this to your compute canada account")

global_arg.add_argument(
    "--todo_dir", type=str,
    default="./jobs/todo",
    help="Path to directory containing shell scripts to run.")

global_arg.add_argument(
    "--done_dir", type=str,
    default="./jobs/done",
    help="Path to directory that the program will move queued scripts.")

global_arg.add_argument(
    "--output_dir", type=str,
    default="./jobs/output",
    help="Directory that will contain job outputs.")

# ----------------------------------------
# Arguments for model
job_arg = add_argument_group("Job")


job_arg.add_argument(
    "--num_jobs", type=int,
    default=1,
    help="Number of shell scripts to queue from the TODO_DIR.")
job_arg.add_argument(
    "--num_runs", type=int,
    default=5,
    help="Number of times this shell script will be executed. "
    "This is useful when running 3 hour jobs that run multiple times.")
job_arg.add_argument(
    "--num_gpu", type=int,
    default=1,
    help="Number of GPUs to use. Set zero to not use the gpu node.")
job_arg.add_argument(
    "--num_cpu", type=str,
    default="auto",
    help="Number of CPU cores to use. Can be infered from the GPU."
    "Set 'auto' to do that.")
job_arg.add_argument(
    "--mem", type=str,
    default="auto",
    help="Amount of memory to use. See compute canada wiki for details "
    "on large memory nodes. Typically, you don't want to go over 8G per "
    "CPU core")
job_arg.add_argument(
    "--time_limit", type=str,
    default="0-03:00",
    help="Time limit on the jobs. If you can, 3 hours give you the best "
    "turn around.")
job_arg.add_argument(
    "--depends_key", type=str,
    default="none",
    help="In case you want to schedule your jobs depending on something. "
    "Set to 'none' if not wanted.")


def get_config():
    config, unparsed = parser.parse_known_args()

    return config, unparsed


def print_usage():
    parser.print_usage()


#
# config.py ends here
