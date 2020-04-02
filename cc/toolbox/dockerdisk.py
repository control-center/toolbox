#!/usr/bin/env python

import argparse
import glob
import operator
import os.path
import subprocess
import sys

DEVNULL = open(os.devnull, "w")


def fail(msg):
    print >> sys.stderr, msg
    sys.exit(1)


def human_readable(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)


def under_docker(*args):
    return "/" + os.path.join("var", "lib", "docker", *args)


def btrfs(*args):
    """
    Utility function to run a btrfs subcommand and return its output.
    """
    cmd = ["btrfs"]
    cmd.extend(args)
    return subprocess.check_output(cmd, stderr=DEVNULL)


class Container(object):
    """
    Represents a Docker container.
    """

    def __init__(self, id_):
        self._id = id_
        self.subvol_id = None
        self._log_file_size = 0
        self.btrfs_total = 0
        self.btrfs_exclusive = 0

    def in_container_dir(self, *args):
        return under_docker("containers", self._id, *args)

    def log_files(self):
        return glob.glob(self.in_container_dir("*-json.log*"))

    def log_file_size(self):
        if not self._log_file_size:
            files = self.log_files()
            self._log_file_size = sum(os.path.getsize(f) for f in files)
        return self._log_file_size

    @property
    def id(self):
        return self._id[:12]

    @property
    def log(self):
        """
        Exists for sorting purposes.
        """
        return self.log_file_size()

    @property
    def disk(self):
        """
        Exists for sorting purposes.
        """
        return self.btrfs_exclusive

    @property
    def total(self):
        """
        Exists for sorting purposes.
        """
        return self.disk + self.log


class ContainerInfo(object):
    def __init__(self):
        self._containers = {}
        self._containers_by_subvol = {}

    def _populate_containers(self, historical=False):
        """
        Looks up Docker container ids and populates our internal map with
        Container objects.
        """
        cmd = ["docker", "ps", "--no-trunc", "-q"]
        if historical:
            cmd.append("-a")
        try:
            ids = subprocess.check_output(cmd, stderr=DEVNULL).splitlines()
        except subprocess.CalledProcessError:
            fail("Unable to get container information from Docker.")
        for s in ids:
            s = s.strip()
            self._containers[s] = Container(s)

    def _populate_subvolume_info(self):
        """
        Populates Containers in our internal map with subvolume ids.
        """
        try:
            info = btrfs(
                "subvolume", "list", under_docker("btrfs", "subvolumes")
            )
        except subprocess.CalledProcessError:
            fail("Unable to retrieve btrfs subvolume info.")
        for line in info.splitlines():
            _, subvol_id, _, _, _, _, _, _, path = line.split()
            container = self._containers.get(os.path.split(path)[-1])
            if container is not None:
                container.subvol_id = subvol_id
                self._containers_by_subvol[subvol_id] = container

    def _populate_qgroup_sizes(self):
        try:
            for line in btrfs(
                "qgroup", "show", under_docker("btrfs", "subvolumes")
            ).splitlines():
                args = [x for x in line.split() if x]
                subvol_id = args[0].split("/")[-1]
                container = self._containers_by_subvol.get(subvol_id)
                if container is not None:
                    container.btrfs_total = int(args[1])
                    container.btrfs_exclusive = int(args[2])
        except subprocess.CalledProcessError:
            fail("Unable to retrieve btrfs container sizes.")

    def populate(self, historical=False):
        self._populate_containers(historical)
        self._populate_subvolume_info()
        self._populate_qgroup_sizes()

    def sorted(self, sortfunc, reverse=False):
        return sorted(
            self._containers.itervalues(), key=sortfunc, reverse=reverse
        )


def get_args():
    parser = argparse.ArgumentParser(
        "Print the disk usage of individual containers", add_help=False
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Show all Docker containers, rather than just running ones",
        dest="all_",
    )
    parser.add_argument(
        "-h",
        "--human",
        dest="not_human",
        action="store_false",
        help="Print sizes in human readable format",
    )
    parser.add_argument(
        "--sort",
        choices=["id", "log", "disk", "total"],
        help="Value to sort by",
        default="total",
    )
    parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        help="Sort results in descending order",
    )
    parser.add_argument(
        "--initialize",
        action="store_true",
        help="Initialize Docker's btrfs volume to report sizes and "
        "begin a scan (note: scan may take a few minutes)",
    )
    parser.add_argument("--help", action="store_true", help="Print usage")
    args = parser.parse_args()
    if args.help:
        parser.print_help()
        sys.exit(0)
    return args


def main():
    args = get_args()
    if args.initialize:
        btrfs("quota", "enable", under_docker("btrfs", "subvolumes"))
        sys.exit(0)
    info = ContainerInfo()
    info.populate(args.all_)
    row_format = "{:>12}" * 4
    print row_format.format("CONTAINER ID", "LOGS", "DISK", "TOTAL")
    readability = (lambda x: x) if args.not_human else human_readable
    for container in info.sorted(
        operator.attrgetter(args.sort), reverse=args.reverse
    ):
        print row_format.format(
            container.id,
            readability(container.log),
            readability(container.disk),
            readability(container.total),
        )


if __name__ == "__main__":
    main()
