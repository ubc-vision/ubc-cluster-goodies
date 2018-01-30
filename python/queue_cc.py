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

import getpass
import os
import shutil
import socket
import subprocess

from config import get_config, print_usage


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
    else:
        raise ValueError("Unknown cluster {}".format(hostname))

    # Get gpu usage statistics
    num_gpu = config.num_gpu

    # Set options or automatically infer CPU and MEM
    num_cpu = config.num_cpu
    if num_cpu.lower() == "auto":
        if num_gpu > 0:
            if cluster == "cedar":
                num_cpu = str(24 // 4 * num_gpu)
            elif cluster == "graham":
                num_cpu = str(32 // 2 * num_gpu)
    mem = config.mem
    if mem.lower() == "auto":
        if num_gpu > 0:
            if cluster == "cedar":
                mem = str(31500 * num_gpu) + "M"
            elif cluster == "graham":
                mem = str(63500 * num_gpu) + "M"

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
                job_depends += [int(_str.split()[0])]

    # Run jobs
    for idx_job in range(config.num_jobs):
        # Grab a job from the list of jobs
        for _f in os.listdir(config.todo_dir):
            if _f.endswith(".sh"):
                job_script = _f
                print("Queueing script {}".format(
                    os.path.join(config.todo_dir, job_script)
                ))
                break
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
            com += ["--dependency=afterany:{}".format(dep_str)]
            com += ["--account={}".format(config.account)]
            com += ["--output={}/%x-%j.out".format(config.output_dir)]
            com += ["--export=ALL"]
            com += [os.path.join(config.done_dir, job_script)]
            slurm_res = subprocess.run(com, stdout=subprocess.PIPE)
            print(slurm_res.stdout)
            # Get job ID
            import IPython
            IPython.embed()
            job_id = slurm_res.stdout.decode().split(" ")[4]
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
