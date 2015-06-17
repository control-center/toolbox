# cc.toolbox

Tools for operating and debugging Zenoss Control Center

## dockerdisk

```
dockerdisk: Print the disk usage of individual containers [-a] [-h]
                                                          [--sort {id,log,disk,total}]
                                                          [-r] [--initialize]
                                                          [--help]

optional arguments:
  -a, --all             Show all Docker containers, rather than just running
                        ones
  -h, --human           Print sizes in human readable format
  --sort {id,log,disk,total}
                        Value to sort by
  -r, --reverse         Sort results in descending order
  --initialize          Initialize Docker's btrfs volume to report sizes and
                        begin a scan (note: scan may take a few minutes)
  --help                Print usage
```

```dockerdisk``` prints disk usage information about Docker containers on your
system. In particular, it will report the amount of disk space taken up by
container logs (stdout/stderr from the container itself) and the amount taken
up exclusively by the container itself (and not the underlying image).
