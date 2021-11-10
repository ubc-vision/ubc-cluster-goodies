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
import datetime

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
            "job_system": "slurm",
            "default_account": "rrg-kyi",
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
            "job_system": "slurm",
            "default_account": "def-kyi-ab",
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
            "job_system": "slurm",
            "default_account": "def-kyi-ab",
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
            "job_system": "slurm",
            "default_account": "def-kyi",
        },
    "sockeye":
        {
            "gpu_model": "v100",
            "gpus_per_node": 4,
            "cpu_cores_per_node": 24,
            "threads_per_node": None,
            "cpu_cores_per_gpu": 6,
            "threads_per_gpu": None,
            "ram_per_node": 191000,
            "ram_per_gpu": 47750,
            "job_system": "PBS",
            "default_account": "pr-kmyi-1",
            "default_gpu_account": "pr-kmyi-1-gpu",
        },
    "narval":
        {
            "gpu_model": "a100",
            "gpus_per_node": 4,
            "cpu_cores_per_node": 48,
            "threads_per_node": 96,
            "cpu_cores_per_gpu": 12,
            "threads_per_gpu": 24,
            "ram_per_node": 510000,
            "ram_per_gpu": 127500,
            "job_system": "slurm",
            "default_account": "def-kyi-ab",
        },
    "snubfin":
        {
            "cpu_cores_per_gpu": 10,
            "ram_per_gpu": 23785,
            "job_system": "slurm",
            "partition": "snubfin",
        },
}


def slurm_command(num_cpu, num_gpu, mem, time_limit, dep_str, account, output_dir, job, partition, nodelist):
    com = ["sbatch"]
    com += ["--cpus-per-task={}".format(num_cpu)]
    if num_gpu > 0:
        com += ["--gres=gpu:{}".format(num_gpu)]
    com += ["--mem={}".format(mem)]
    com += ["--time={}".format(time_limit)]
    if len(dep_str) > 0:
        com += ["--dependency=afterany:{}".format(dep_str)]
    if len(account) > 0:
        com += ["--account={}".format(account)]
    if partition and len(partition) > 0:
        com += ["--partition={}".format(partition)]
    if nodelist and len(nodelist) > 0:
        com += ["--nodelist={}".format(nodelist)]
    com += ["--output={}/%x-%j.out".format(output_dir)]
    com += ["--export=ALL"]
    com += [job]
    return com


def PBS_command(num_cpu, num_gpu, mem, time_limit, dep_str, account, output_dir, job, partition, nodelist):
    com = ["qsub"]
    if num_gpu > 0:
        com += ["-l", "walltime={0},select=1:ncpus={1}:mem={2}:ngpus={3}".format(time_limit, num_cpu, mem, num_gpu)]
    else:
        com += ["-l", "walltime={0},select=1:ncpus={1}:mem={2}".format(time_limit, num_cpu, mem)]
    if len(dep_str) > 0:
        com += ["-W", "depend=afterany:{}".format(dep_str)]
    com += ["-A", "{}".format(account)]
    com += ["-o", "{0}/{1}_{2}.out".format(output_dir,
                                           os.path.basename(job),
                                           str(datetime.datetime.now()).replace(" ", "_").replace(":", "_"),
                                           )]
    com += ["-e", "{0}/{1}_{2}.err".format(output_dir,
                                           os.path.basename(job),
                                           str(datetime.datetime.now()).replace(" ", "_").replace(":", "_"),
                                           )]
    com += [job]
    return com


def add_argument_group(name):
    arg = parser.add_argument_group(name)
    arg_lists.append(arg)
    return arg


# ----------------------------------------
# Arguments for training
global_arg = add_argument_group("Global")

global_arg.add_argument(
    "--account", type=str,
    default=None,
    help="Slurm account to use. "
         "Please change this to your compute canada account")


global_arg.add_argument(
    "--cluster", type=str,
    default=None,
    help="Name of the cluster.")


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
    default="03:00:00",
    help="Time limit on the jobs. If you can, 3 hours give you the best "
         "turn around. Hours:Minutes:Seconds")
job_arg.add_argument(
    "--depends_key", type=str,
    default="none",
    help="In case you want to schedule your jobs depending on something. "
         "Set to 'none' if not wanted.")
job_arg.add_argument(
    "--partition", type=str,
    default=None,
    help="Partition to be used.")
job_arg.add_argument(
    "--nodelist", type=str,
    default=None,
    help="List of nodes to be used.")


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
    if config.cluster is None:
        if hostname.startswith("gra"):
            cluster = "graham"
        elif hostname.startswith("cedar") or hostname.startswith("cdr"):
            cluster = "cedar"
        elif hostname.startswith("beluga") or hostname.startswith("blg"):
            cluster = "beluga"
        elif hostname.startswith("stirk"):
            cluster = "moo"
        elif hostname.startswith("se"):
            cluster = "sockeye"
        elif hostname.startswith("narval"):
            cluster = "narval"
        elif hostname.startswith("borg"):
            cluster = "snubfin"
        else:
            raise ValueError("Unknown cluster {}".format(hostname))
    else:
        cluster = config.cluster

    # Get gpu usage statistics
    num_gpu = config.num_gpu

    # Apply default account if not specified
    if config.account is None:
        if "default_gpu_account" not in cluster_config[cluster] and "default_account" not in cluster_config[cluster]:
            config.account = ""
        elif num_gpu > 0 and "default_gpu_account" in cluster_config[cluster]:
            config.account = cluster_config[cluster]["default_gpu_account"]
        else:
            config.account = cluster_config[cluster]["default_account"]
    if config.partition is None and "partition" in cluster_config[cluster]:
        config.partition = cluster_config[cluster]["partition"]
    if config.nodelist is None and "nodelist" in cluster_config[cluster]:
        config.nodelist = cluster_config[cluster]["nodelist"]

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
        assert cluster_config[cluster]["job_system"] == "slurm"
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
            if cluster_config[cluster]["job_system"] == "slurm":
                com = slurm_command(num_cpu,
                                    num_gpu,
                                    mem,
                                    time_limit,
                                    dep_str,
                                    config.account,
                                    config.output_dir,
                                    os.path.join(config.done_dir, job_script),
                                    config.partition,
                                    config.nodelist)
            elif cluster_config[cluster]["job_system"] == "PBS":
                com = PBS_command(num_cpu,
                                  num_gpu,
                                  mem,
                                  time_limit,
                                  dep_str,
                                  config.account,
                                  config.output_dir,
                                  os.path.join(config.done_dir, job_script),
                                  config.partition,
                                  config.nodelist)
            slurm_res = subprocess.run(com, stdout=subprocess.PIPE)
            print(slurm_res.stdout.decode())
            # Get job ID
            if slurm_res.returncode != 0:
                raise RuntimeError("Slurm/PBS error!")
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
