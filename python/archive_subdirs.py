#!/usr/bin/env python3
# archive_subdirs.py ---
#
# Filename: archive_subdirs.py
# Description:
# Author: Kwang Moo Yi
# Maintainer:
# Created: Mon Feb 26 18:51:27 2018 (-0800)
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
import os
import socket
import subprocess

# ----------------------------------------
# Global variables within this script
arg_lists = []
parser = argparse.ArgumentParser()


def add_argument_group(name):
    arg = parser.add_argument_group(name)
    arg_lists.append(arg)
    return arg


# ----------------------------------------
# Arguments for gloabal settings
global_arg = add_argument_group("Global")


global_arg.add_argument(
    "--account", type=str,
    default="def-kyi",
    help="Slurm account to use. "
    "Please change this to your compute canada account")

# ----------------------------------------
# Arguments for model
job_arg = add_argument_group("Job")

job_arg.add_argument(
    "--archive_dir", type=str,
    default=None,
    help="Path to the parent directory which we will archive all "
    "its subdirectories to individual tar.gz files")
job_arg.add_argument(
    "--num_gpu", type=int,
    default=0,
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
    default="0-12:00",
    help="Time limit on the jobs. If you can, 3 hours give you the best "
    "turn around.")


def get_config():
    config, unparsed = parser.parse_known_args()

    return config, unparsed


def print_usage():
    parser.print_usage()


def main(config):
    """Main Function"""

    # Get hostname to identify the cluster
    hostname = socket.gethostname()

    # Identify cluster
    if hostname.startswith("gra"):
        cluster = "graham"
    elif hostname.startswith("cedar") or hostname.startswith("cdr"):
        cluster = "cedar"
    else:
        raise ValueError("Unknown cluster {}".format(hostname))

    # # Get gpu usage statistics
    # num_gpu = config.num_gpu

    # For this opeation we will consume a full node
    num_cpu = config.num_cpu
    if num_cpu.lower() == "auto":
        if cluster == "cedar":
            num_cpu = 32
        elif cluster == "graham":
            num_cpu = 32
    mem = config.mem
    if mem.lower() == "auto":
        if cluster == "cedar":
            mem = "128000M"
        elif cluster == "graham":
            mem = "128000M"

    # Set time limit
    time_limit = config.time_limit

    if config.archive_dir is None:
        print_usage()
        exit(1)

    # For each file in the archive directory
    for _f in os.listdir(config.archive_dir):
        cur_dir = os.path.join(config.archive_dir, _f)
        # If not a dir continue to next one
        if not os.path.isdir(cur_dir):
            continue
        # If out file already exists, then simply skip
        if os.path.exists(cur_dir + "tar.gz"):
            continue
        # If it is a directory now queue the archive job
        com = ["sbatch"]
        com += ["--cpus-per-task={}".format(num_cpu)]
        com += ["--mem={}".format(mem)]
        com += ["--time={}".format(time_limit)]
        com += ["--account={}".format(config.account)]
        com += ["--output={}.out".format(cur_dir + ".tar.gz.out")]
        com += ["--export=ALL"]
        com += ["../bash/archive_dir.sh"]
        slurm_res = subprocess.run(com, stdout=subprocess.PIPE)
        print(slurm_res.stdout.decode())
        # Get job ID
        if slurm_res.returncode != 0:
            raise RuntimeError("Slurm error!")


if __name__ == "__main__":

    # ----------------------------------------
    # Parse configuration
    config, unparsed = get_config()
    # If we have unparsed arguments, print usage and exit
    if len(unparsed) > 0:
        print_usage()
        exit(1)

    main(config)


#
# archive_subdirs.py ends here
