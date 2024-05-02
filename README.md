This repository has moved to a our groups repository!
[https://github.com/vcg-uvic/compute-canada-goodies](https://github.com/vcg-uvic/compute-canada-goodies)

# compute-canada-goodies
Automation scripts for compute canada

This script is to simplify queueing jobs on Compute Canada.
Simply run `./queue_cc.py` and it will queue your jobs in jobs/todo folder.
Your jobs should be a shell script with proper shebang.

Also try `./queue_cc.py --help`, or see `config.py` for more details.

# Tutorial on how to setup Compute Canada for TensorFlow

This tutorial assumes that you have setup a computecanada account, either through your advisor as your sponsor, or me. If you do not have one, simply create a computecanada account by visiting the [CCDB website](https://ccdb.computecanada.ca). I strongly suggest to ask your advisor to create the CCDB account, and tell him to be a supervisor. My CCDB account is already either given to you personally, or on the Lecture Slides.

## IMPORTANT NOTES BEFORE WE DIVE IN

ComputeCanada is shared across researchers in Canada. Also, the login-nodes are not meant to run **any computationally demanding** job. This includes **compiling** and launching **TensorBoard**. Do **NOT** do them. They may crash the login-node, thus crashing the **ENTIRE SYSTEM**. This will get recorded and may cause you to get banned. So for running these jobs, make sure that you

- Compile on compute nodes
- Run TensorBoard locally, after downloading the logs from the server.

## About the file system

Another thing is that the file system on ComputeCanada is NFS, with dedicated purposes. `project` is for shared projects. You will **NOT** need to use them unless you are saving results for **shared projects**. `home` is where you store your stuff, but **NOT** the code. `scratch` is where you want to have everything. Use `scratch/<login-id>` to store your code, and the results, and then copy only the **IMPORTANT** ones to your home or projects. `scratch` has the **FASTEST** access delay. So you really want to do everything here. For more details visit [here](https://docs.computecanada.ca/wiki/Storage_and_file_management)

## Resources (pr-kmyi group only)
1. 187 core-years on the cedar-compute system
2. 8.0 RGU-years on the cedar-gpu system
3. 24.0 RGU-years on the narval-gpu system
4. 100 TB of /project storage on the narval-storage system
5. 40 TB of /nearline storage on the narval-storage system
6. 200 TB of /project storage on the cedar-storage system
7. 8.0 Millions /project inodes on the cedar-storage system

## The module system

One very interesting thing about the ComputeCanada setup is that you can simply load the modules on-demand. These modules could be `CUDA`, `CUDNN`, `GCC`, `OpenCV` or whatever you would like. You can also specify their versions. To see which modules are loaded, do
```
$ module list
```
So to have proper modules we need for our case, simply do the following:
```
$ module load cudnn cuda eigen python/3
```
In my case, I also unload some of the modules that I won't be using, so I have the following lines in my `.bashrc` -- **NOTE THAT THIS IS STRONGLY DISCOURAGED. IT WILL CAUSE ISSUES**
```
module unload icc gcccore ifort intel imkl openmpi
module load gcc/5.4.0 cuda cudnn eigen python/3
module unload icc gcccore ifort intel imkl openmpi jasper java
```

## Installing TensorFlow
One very important thing in ComputeCanada, is that some of the libraries, including TensorFlow, will not come from standard `pip`. They use a custom `wheelhouse`. So you need to **specifically use their virtualenv**. So please carefully follow the instructions at [their wiki page](https://docs.computecanada.ca/wiki/Tensorflow). If you are usig `virtualenvwrapper` you **must** point to the correct `virtualenv` binary, or it will not work. I suggest you stick to the ComputeCanada instructions to keep your life simple.

## Using salloc
The following command will give you access to one of the interactive nodes for you to debug your code. Notice that I set the account to my account `def-kyi`, but you probably want to replace that with your advisor's.
```
salloc --time=03:00:00 --gres=gpu:1 --cpus-per-task=6 --account=def-kyi --mem=31000M
```
Note the 3 hour limit and 1 GPU, 6Cores, 32G MEM. This is for cedar, where each GPU node has 24 cores and 128G MEM. You want to access a *virtual* node with 1 GPU, so we divide the resource equally with four. For Graham, the setting will be a bit different. See [here for Cedar](https://docs.computecanada.ca/wiki/Cedar) and [here for Graham](https://docs.computecanada.ca/wiki/Graham).

Use these interactive nodes for debugging and then launch your batch jobs, once you are sure that it will work. The current `queue_cc.py` script expects your jobs to be located at `jobs/todo/`. So in fact, you can simply emulate what will happen with your batch job by running
```
./jobs/todo/<your_job_script>.sh
```

## Launching scripts
Once you are sure that your script runs, run `queue_cc.py` **IN YOUR VIRTUAL ENVIRONMENT** to queue your jobs as batch jobs. Note that your current `shell` environment will get carried on to your batch jobs. So you want to be in the virtual environment that you want your jobs to run in.

## Monitoring the job queue
Once your jobs is in the queue, you can type
```
squeue -u <your-login-id>
```
to see how it's doing. **BE PREPARED TO WAIT**. Your jobs will be in the queue for possibly many days before it runs. If it's there for more than 5 days, contact me. However, the scheduling policy prefers 3 hour jobs, as they can fit between long hour jobs. Since we will be using TF, saving and restoring is trivial. Do make your jobs save roughly 15 minutes, so that your job **dies** on three hour time limit, and restarts using dependencies. The `queue_cc.py` actually will take care of that for you. To make it even more efficient, a good way for you is that whenever you save your model, monitor the time you have left (roughly) and quit your training when you don't think the next save interval cannot fit in the 3 hour limit. This way, you can maximize the turn-around in the cluster. [Here's more info on the job scheduling policy](https://docs.computecanada.ca/wiki/Job_scheduling_policies)

### Switching back and forth between Cedar and Graham

Cedar and Graham do not share queues. They are independent. In fact, you can possibly code so that the two clusters are identical in their setup and bounce back between your clusters. The job scheduling is based on priority, and this is set according to your latest two week window. So if you were not running on one cluster, in fact, your priority on that cluster is probably quite good. So it is worth bouncing back and forth. However, this is per CCDB account. So you might want to check who else is running on your advisor's account by doing
```
squeue -A def-kyi_gpu
```
Here, `def-kyi_gpu` is my CCDB account for the gpu machines. Your advisor's account would be different.

## Monitoring your job outputs
Be aware that your shell outputs will be forwarded in `jobs/output/` but they **are not guaranteed to be up-to-date**. The outputs there are not very trustworthy. You probably want to look at TensorBoard outputs, which will be up to date. **AGAIN DO NOT RUN TENSORBOARD IN LOGIN NODES**.



