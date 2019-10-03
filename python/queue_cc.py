#!/usr/bin/env python3
# queue_cc.py ---
#
# Filename: queue_cc.py
# Description:
# Author: Kwang Moo Yi
# Maintainer:
# Created: Mon Jan 29 17:56:38 2018 (-0800)
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
import getpass
import os
import shutil
import socket
import subprocess

# ----------------------------------------
# Global variables within this script
arg_lists = []
parser = argparse.ArgumentParser()
cluster_config = {
    "cedar":
        {
            "gpu_model": "p100",
            "gpus_per_node": 4,
            "cpu_cores_per_node": 24,
            "threads_per_node": 48,
            "cpu_cores_per_gpu": 6,
            "threads_per_gpu": 12,
            "ram_per_node": 128000,
            "ram_per_gpu": 31500,
        },
    "graham":
        {
            "gpu_model": "p100",
            "gpus_per_node": 2,
            "cpu_cores_per_node": 32,
            "threads_per_node": 64,
            "cpu_cores_per_gpu": 16,
            "threads_per_gpu": 32,
            "ram_per_node": 127518,
            "ram_per_gpu": 63500,
        },
    "beluga":
        {
            "gpu_model": "v100",
            "gpus_per_node": 4,
            "cpu_cores_per_node": 40,
            "threads_per_node": 80,
            "cpu_cores_per_gpu": 10,
            "threads_per_gpu": 20,
            "ram_per_node": 191000,
            "ram_per_gpu": 47500,
        },
    "moo":
        {
            "gpu_model": "v100",
            "gpus_per_node": 8,
            "cpu_cores_per_node": 28,
            "threads_per_node": 56,
            "cpu_cores_per_gpu": 3,
            "threads_per_gpu": 7,
            "ram_per_node": 191000,
            "ram_per_gpu": 23875,
        }
}


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


def main(config):
    """Main Function"""

    # Check if directories exist and create them if necessary
    if not os.path.exists(config.todo_dir):
        os.makedirs(config.todo_dir)
    if not os.path.exists(config.done_dir):
        os.makedirs(config.done_dir)
    if not os.path.exists(config.output_dir):
        os.makedirs(config.output_dir)

    # Get hostname and user name
    username = getpass.getuser()
    hostname = socket.gethostname()

    # Identify cluster
    if hostname.startswith("gra"):
        cluster = "graham"
    elif hostname.startswith("cedar") or hostname.startswith("cdr"):
        cluster = "cedar"
    elif hostname.startswith("beluga") or hostname.startswith("blg"):
        cluster = "beluga"
    elif hostname.startswith("stirk"):
        cluster = "moo"
    else:
        raise ValueError("Unknown cluster {}".format(hostname))

    # Get gpu usage statistics
    num_gpu = config.num_gpu

    # Set options or automatically infer CPU and MEM
    num_cpu = config.num_cpu
    if num_cpu.lower() == "auto":
        if num_gpu > 0:
            num_cores_per_gpu = cluster_config[cluster]["cpu_cores_per_gpu"]
            num_cpu = str(num_cores_per_gpu * num_gpu)
    mem = config.mem
    if mem.lower() == "auto":
        if num_gpu > 0:
            ram_per_gpu = cluster_config[cluster]["ram_per_gpu"]
            mem = str(ram_per_gpu * num_gpu) + "M"

    # Set time limit
    time_limit = config.time_limit

    # Get jobs that this new job should depend on.
    job_depends = []
    if config.depends_key != "none":
        squeue_res = subprocess.run(
            ["squeue", "-u", username],
            stdout=subprocess.PIPE
        )
        job_details = squeue_res.stdout.decode().split("\n")[1:]
        # For each job create a list of IDs
        for _str in job_details:
            # Look for job dependency keys in string
            if config.depends_key in _str:
                # Add to the list of dependent jobs
                job_depends += [str(int(_str.split()[0]))]

    # Run jobs
    for idx_job in range(config.num_jobs):
        # Grab a job from the list of jobs
        found_job = False
        # Sort -- Just in case
        list_files = os.listdir(config.todo_dir)
        list_files.sort()
        for _f in list_files:
            if _f.endswith(".sh"):
                job_script = _f
                print("Queueing script {}".format(
                    os.path.join(config.todo_dir, job_script)
                ))
                found_job = True
                break
        if not found_job:
            raise RuntimeError("No job found in {}".format(config.todo_dir))
        # Move that job to the done folder
        shutil.move(
            os.path.join(config.todo_dir, job_script),
            os.path.join(config.done_dir, job_script),
        )
        # Build Initial dependency (from the job_depends)
        dep_str = ":".join(job_depends)
        # Run job N times
        for idx_run in range(config.num_runs):
            com = ["sbatch"]
            com += ["--cpus-per-task={}".format(num_cpu)]
            if num_gpu > 0:
                com += ["--gres=gpu:{}".format(num_gpu)]
            com += ["--mem={}".format(mem)]
            com += ["--time={}".format(time_limit)]
            if len(dep_str) > 0:
                com += ["--dependency=afterany:{}".format(dep_str)]
            com += ["--account={}".format(config.account)]
            com += ["--output={}/%x-%j.out".format(config.output_dir)]
            com += ["--export=ALL"]
            com += [os.path.join(config.done_dir, job_script)]
            slurm_res = subprocess.run(com, stdout=subprocess.PIPE)
            print(slurm_res.stdout.decode())
            # Get job ID
            if slurm_res.returncode != 0:
                raise RuntimeError("Slurm error!")
            job_id = slurm_res.stdout.decode().split()[-1]
            dep_str = str(job_id)


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
# queue_cc.py ends here
