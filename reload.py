#!/usr/bin/env python
import logging
import os
import sys
import subprocess
import time
import signal

import platform
 

def file_filter(name):
    return (not name.startswith(".")) and (not name.endswith(".swp"))

def file_times(path):
    if os.path.isfile(path):
        yield os.stat(path).st_mtime
        return

    for root, dirs, files in os.walk(path):
        for file in filter(file_filter, files):
            yield os.stat(os.path.join(root, file)).st_mtime


def print_stdout(process):
    stdout = process.stdout
    if stdout != None:
        print(stdout)

try:
    curpath = os.path.dirname(__file__)
    # The path to watch
    path = sys.argv[1]
    if not path.startswith("/") and not (len(path) > 1 and path[1] == ":"):
        path = os.path.join(curpath, path)

    # We concatenate all of the arguments together, and treat that as the command to run
    command = " ".join(sys.argv[2:])

    # How often we check the filesystem for changes (in seconds)
    wait = 1

    # The process to autoreload
    # process = subprocess.Popen(command, shell=True)
    process = subprocess.Popen(command.split(), shell=False)
    # process = subprocess.run(*sys.argv[2:], shell=False)

    # The current maximum file modified time under the watched directory
    last_mtime = max(file_times(path), default=0)

    while True:
        max_mtime = max(file_times(path), default=0)
        print_stdout(process)
        if max_mtime > last_mtime:
            last_mtime = max_mtime
            logging.warning("Restarting process.")
            # os.kill(process.pid, signal.SIGINT)
            sys = platform.system()
            if sys == "Windows":
                logging.warning("windows kill id = {}".format(process.pid))
                os.system("taskkill /t /f /pid %s" % process.pid)
            else:
                process.terminate()
                # os.system(f"kill -15 {process.pid}")
                code = process.wait()
                logging.warning("process.pid={process.pid}, terminate code = {code}")
            process = subprocess.Popen(command.split(), shell=False)
            # process = subprocess.Popen(command, shell=True)
            # process = subprocess.run(*sys.argv[2:], shell=False)
        try:
            time.sleep(wait)
        except KeyboardInterrupt:
            break
except Exception as e:
    print(e)