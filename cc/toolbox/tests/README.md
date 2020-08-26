### Testing

Tests are written using unittest.mock(python3), but will also run on python2 with mock module installed.

#### Requirements for running tests

 * Docker Engine - Community
 * zenoss/isvcs-zookeeper:v11 docker image running.
 
##### isvcs-zookeeper docker run options:

```bash
docker run  -d -p 127.0.0.1:2181:2181 -p 127.0.0.1:12181:12181 --name serviced-isvcs_zookeper-test --mount type=bind,source="/path/to/zookeeper/data",target="/var/zookeeper" --mount type=bind,source="/path/to/serviced/resources",target="/usr/local/serviced/resources" zenoss/isvcs-zookeeper:v11 /bin/sh /usr/bin/start-zookeeper 
```

##### Run tests from cc directory:

###### python3:

```bash
python -m unittest -v
```

###### python2:

```bash
python -m unittest discover -v
```
