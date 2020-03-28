import os
import subprocess

import fabric
import sysrsync


def send_source_files():
    ssh_destination = 'personal-site'
    destination = "/home/gabriel/worker-scheduler/src"
    repo_base_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_files_root = os.path.join(repo_base_folder, "src")

    create_destination_folder(destination, ssh_destination)
    ignored_patterns = get_ignored_patterns(repo_base_folder, "src")

    sysrsync.run(
        source=source_files_root,
        destination=destination,
        destination_ssh="personal-site",
        exclusions=ignored_patterns,
        verbose=True,
        options=["-a"])


def create_destination_folder(destination_folder, ssh_host):
    connection = fabric.Connection(ssh_host)
    connection.run(f'mkdir -p {destination_folder}')
    connection.close()


def get_ignored_patterns(repo_base_folder, work_tree):
    git_get_ignored_command = f'git -C {repo_base_folder} ls-files --exclude-standard -oi --directory'
    ignored_prefixes = (subprocess.check_output(
        git_get_ignored_command.split(),
        universal_newlines=True)
        .strip()
        .split('\n'))

    return [
        prefix[len(work_tree):]
        for prefix in ignored_prefixes
        if prefix.startswith(work_tree)
    ]


if __name__ == "__main__":
    send_source_files()
