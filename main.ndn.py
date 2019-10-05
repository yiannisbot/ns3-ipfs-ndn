#!/usr/bin/python

import sys
import subprocess
import os
import time
import argparse
import datetime
import yaml

__author__ = 'chepeftw'

numberOfNodesStr = '20'
emulationTimeStr = '600'
scenarioSize = '300'
noBuildCacheDocker = ''
timeoutStr = '800'
mode = 'single'
rootNode = '10.12.0.1'
nodeSpeed = '5'
nodePause = '1'
simulationCount = 0

numberOfNodes = 0
jobs = 1
nameList = []

baseContainerNameMin = 'ndn'
#baseContainerNameMin = 'networkstatic/iperf3'

pidsDirectory = "./var/pid/"
logsDirectory = "./var/log/"

ns3_home = '/home/srene/NS3DockerEmulator/bake/source/ns-3.26/'

def main():
    global numberOfNodesStr, \
        emulationTimeStr, \
        timeoutStr, \
        nodeSpeed, \
        nodePause, \
        simulationCount, \
        scenarioSize, \
        numberOfNodes, \
        nameList, \
        jobs
    print("Main ...")

    ###############################
    # n == number of nodes
    # t == simulation time in seconds
    ###############################
    parser = argparse.ArgumentParser()
    parser.add_argument("operationStr", action="store",
                        help="The name of the operation to perform, options: full, create, destroy")

    parser.add_argument("-n", "--number", action="store", help="The number of nodes to simulate")

    parser.add_argument("-t", "--time", action="store", help="The time in seconds of NS3 simulation")

    parser.add_argument("-to", "--timeout", action="store", help="The timeout in seconds of NS3 simulation")

    parser.add_argument("-s", "--size", action="store", help="The size in meters of NS3 network simulation")

    parser.add_argument("-ns", "--nodespeed", action="store", help="The speed of the nodes expressed in m/s")

    parser.add_argument("-np", "--nodepause", action="store", help="The pause of the nodes expressed in s")

    parser.add_argument("-c", "--count", action="store", help="The count of simulations")

    parser.add_argument("-j", "--jobs", action="store", help="The number of parallel jobs")

    parser.add_argument('-v', '--version', action='version', version='%(prog)s 2.0')
    args = parser.parse_args()

    if args.number:
        numberOfNodesStr = args.number
    if args.time:
        emulationTimeStr = args.time
    if args.timeout:
        timeoutStr = args.timeout
    if args.size:
        scenarioSize = args.size
    if args.nodespeed:
        nodeSpeed = args.nodespeed
    if args.nodepause:
        nodePause = args.nodepause
    if args.count:
        simulationCount = int(args.count)
    if args.jobs:
        jobs = int(args.jobs)

    operation = args.operationStr

    # Display input and output file name passed as the args
    print("Number of nodes : %s" % numberOfNodesStr)
    print("Emulation time : %s" % emulationTimeStr)
    print("Operation : %s" % operation)
    print("Timeout : %s" % timeoutStr)
    print("Node Speed : %s" % nodeSpeed)
    print("Node Pause : %s" % nodePause)
    print("Simulation Count : %s" % simulationCount)
    print("Scenario Size : %s x %s" % (scenarioSize, scenarioSize))

    numberOfNodes = int(numberOfNodesStr)

    base_name = "emu"

    for x in range(0, numberOfNodes):
        nameList.append(base_name + str(x + 1))

    if operation == "create":
        create()
    elif operation == "destroy":
        destroy()
    elif operation == "ns3":
        ns3()
    elif operation == "emulation":
        run_emu()
    else:
        print("Nothing to be done ...")


################################################################################
# error handling ()
################################################################################
def check_return_code(rcode, message):
    if rcode == 0:
        print("Success: %s" % message)
        return

    print("Error: %s" % message)
    # destroy()  # Adding this in case something goes wrong, at least we do some cleanup
    sys.exit(2)


def check_return_code_chill(rcode, message):
    if rcode == 0:
        print("Success: %s" % message)
        return

    print("Error: %s" % message)
    return


################################################################################
# create ()
################################################################################
def create():
    print("Creating ...")

    #############################
    # First we make sure we are running the latest version of our Ubuntu container

    # docker build -t myubuntu docker/myubuntu/.

    # r_code = subprocess.call("docker build -t %s docker/mybase/." % baseContainerName0, shell=True)
    # check_return_code(r_code, "Building regular container %s" % baseContainerName0)

    #r_code = subprocess.call("docker build -t %s docker/minimal/." % baseContainerNameMin, shell=True)
    #r_code = subprocess.call("docker load < /home/uceesre/docker-ipfs.tar.gz" , shell=True)
    #check_return_code(r_code, "Building minimal container %s" % baseContainerNameMin)

    #r_code = subprocess.call("cd ns3 && bash update.sh tap-wifi-virtual-machine.cc", shell=True)
    #if r_code != 0:
    #    print("Error copying latest ns3 file")
    #else:
    #    print("NS3 up to date!")
    #    print("Go to NS3 folder, probably cd $NS3_HOME")

    #r_code = subprocess.call("cd $NS3_HOME && ./waf build -j {} -d optimized --disable-examples".format(jobs),
    #                         shell=True)
    #if r_code == 0:
    #    print("NS3 BUILD WIN!")
    #else:
    #    print("NS3 BUILD FAIL!")
    #
    #print('NS3 Build finished | Date now: %s' % datetime.datetime.now())

    #############################
    # First and a half ... we generate the configuration yaml files.

    write_conf(0, numberOfNodes, timeoutStr, 0, 10001, "conf1.yml")

    #############################
    # Second, we run the numberOfNodes of containers.
    # https://docs.docker.com/engine/reference/run/
    # They have to run as privileged (don't remember why, need to clarify but I read it in stackoverflow)
    # (Found it, it is to have access to all host devices, might be unsafe, will check later)
    # By default, Docker containers are "unprivileged" and cannot, for example,
    # run a Docker daemon inside a Docker container. This is because by default a container is not allowed to
    # access any devices, but a "privileged" container is given access to all devices.
    # -dit ... -d run as daemon, -i Keep STDIN open even if not attached, -t Allocate a pseudo-tty
    # --name the name of the container, using emuX
    # Finally the name of our own Ubuntu image.
    if not os.path.exists(logsDirectory):
        os.makedirs(logsDirectory)

    dir_path = os.path.dirname(os.path.realpath(__file__))

    acc_status = 0
    for x in range(0, numberOfNodes):
        if not os.path.exists(logsDirectory + nameList[x]):
            os.makedirs(logsDirectory + nameList[x])

        log_host_path = dir_path + logsDirectory[1:] + nameList[x]
        #conf_host_path = dir_path + "/conf"

        volumes = "-v " + log_host_path + ":/var/log/streaming "

        print("VOLUMES: " + volumes)

        '''
        if x==0:
            baseContainerName = baseContainerNameMin + "-server"
        else: 
            baseContainerName = baseContainerNameMin + "-client"
        '''
        baseContainerName = baseContainerNameMin

        acc_status += subprocess.call(
            "docker run --privileged -dit --net=none %s --name %s %s" % (volumes, nameList[x], baseContainerNameMin),
        #"docker run --privileged -dit --net=none %s --name %s --entrypoint '/bin/bash' %s" % (volumes, nameList[x],baseContainerName),
            shell=True)

            

    # If something went wrong running the docker containers, we panic and exit
    check_return_code(acc_status, "Running docker containers")

    time.sleep(1)
    print('Finished running containers | Date now: %s' % datetime.datetime.now())

    #############################
    # Third, we create the bridges and the tap interfaces for NS3
    # Based on NS3 scripts ... https://www.nsnam.org/docs/release/3.25/doxygen/tap-wifi-virtual-machine_8cc.html
    # But in the source you can find more examples in the same dir.
    acc_status = 0
    for x in range(0, numberOfNodes):
        acc_status += subprocess.call("bash net/singleSetup.sh %s" % (nameList[x]), shell=True)

    check_return_code(acc_status, "Creating bridge and tap interface")

    acc_status += subprocess.call("bash net/singleEndSetup.sh", shell=True)
    check_return_code(acc_status, "Finalizing bridges and tap interfaces")

    if not os.path.exists(pidsDirectory):
        os.makedirs(pidsDirectory)

    time.sleep(1)
    print('Finished creating bridges and taps | Date now: %s' % datetime.datetime.now())

    #############################
    # Fourth, we create the bridges for the docker containers
    # https://docs.docker.com/v1.7/articles/networking/
    acc_status = 0
    for x in range(0, numberOfNodes):
        cmd = ['docker', 'inspect', '--format', "'{{ .State.Pid }}'", nameList[x]]

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        pid = out[1:-2].strip()

        with open(pidsDirectory + nameList[x], "w") as text_file:
            text_file.write(str(pid, 'utf-8'))
        print("bash net/container.sh "+nameList[x]+" "+str(x))
        acc_status += subprocess.call("bash net/container.sh %s %s" % (nameList[x], x), shell=True)

    # If something went wrong creating the bridges and tap interfaces, we panic and exit
    # check_return_code( acc_status, "Creating bridge side-int-X and side-ext-X" )
    # Old behaviour, but I got situations where this failed, who knows why and basically stopped everything
    # therefore I changed it to passive, if one fails, who cares but keep on going so the next simulations
    # dont break
    check_return_code_chill(acc_status, "Creating bridge side-int-X and side-ext-X")

    print("Done.")
            
    #cmd = "docker exec -w /usr/src/app/video "+nameList[0]+" sh -c './publish.sh master >> /var/log/streaming/streaming.log'"
    #process3 = subprocess.Popen(cmd, shell=True)

    print('Finished setting up bridges | Date now: %s' % datetime.datetime.now())


    return


################################################################################
# end create ()
################################################################################


################################################################################
# ns3 ()
################################################################################
def ns3():
    print("NS3 ...")

    #total_emu_time = (5 * 60) * numberOfNodes
    total_emu_time = emulationTimeStr
    print('About to start NS3 RUN  with total emulation time of %s' % str(total_emu_time))

    tmp = 'cd '+ns3_home+' && '
    tmp += './waf -j {0} --run "scratch/tap-vm2 --NumNodes={1} --TotalTime={2} --TapBaseName=emu"'
    #tmp += '--SizeX={3} --SizeY={3} --MobilitySpeed={4} --MobilityPause={5}"'
    ns3_cmd = tmp.format(jobs, numberOfNodesStr, total_emu_time)

    print(ns3_cmd)
    proc1 = subprocess.Popen(ns3_cmd, shell=True)

    time.sleep(5)
    print('proc1 = %s' % proc1.pid)

    with open(pidsDirectory + "ns3", "w") as text_file:
        text_file.write(str(proc1.pid))

    print('Finished running NS3 in the background | Date now: %s' % datetime.datetime.now())

    return


################################################################################
# run_emu ()
################################################################################
def run_emu():
    print("RUN SIM ...")

    print('About to start RUN SIM | Date now: %s' % datetime.datetime.now())

    if os.path.exists(pidsDirectory + "ns3"):
        with open(pidsDirectory + "ns3", "rt") as in_file:
            text = in_file.read()
            if os.path.exists("/proc/" + text.strip()):
                print('NS3 is still running with pid = ' + text.strip())
            else:
                print('NS3 is NOT running')
                ns3()

    container_name_list = ""
    for x in range(0, numberOfNodes):
        container_name_list += nameList[x]
        container_name_list += " "

    acc_status = subprocess.call("docker restart -t 0 %s" % container_name_list, shell=True)
    check_return_code_chill(acc_status, "Restarting containers")

    for x in range(0, numberOfNodes):
        if os.path.exists(pidsDirectory + nameList[x]):
            with open(pidsDirectory + nameList[x], "rt") as in_file:
                text = in_file.read()
                r_code = subprocess.call("rm -rf /var/run/netns/%s" % (text.strip()), shell=True)
                check_return_code_chill(r_code, "Destroying docker bridges %s" % (nameList[x]))

        cmd = ['docker', 'inspect', '--format', "'{{ .State.Pid }}'", nameList[x]]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        pid = out[1:-2].strip()

        with open(pidsDirectory + nameList[x], "w") as text_file:
            text_file.write(str(pid, 'utf-8'))

    # syncConfigTime (s) = seconds + ~seconds
    sync_config_time = int(time.time()) + numberOfNodes
    write_conf(sync_config_time, numberOfNodes, timeoutStr, 1, 10001, "conf1.yml")

    acc_status = 0
    for x in range(0, numberOfNodes):
        acc_status += subprocess.call("bash net/container.sh %s %s" % (nameList[x], x), shell=True)

    check_return_code_chill(acc_status, "Cleaning old netns and setting up new")

    print('Finished RUN SIM | Date now: %s' % datetime.datetime.now())
    print('Letting the simulation run for %s' % emulationTimeStr)

    cmd = "docker exec -w /usr/src/app/video "+nameList[0]+" sh -c './publish.sh master >> /var/log/streaming/streaming.log'"
    process3 = subprocess.Popen(cmd, shell=True)

    #cmd = ['docker', 'exec', nameList[0], "ipfs", "add","-r video"]
    #proc3 = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #out, err = proc3.communicate()
    #print(cmd)
    #hash = id[1:-1].strip()


    for x in range(1,numberOfNodes):
        cmd = "docker exec "+nameList[x]+" sh -c 'nfdc face create tcp://10.2.0.2'"
        process4 = subprocess.Popen(cmd, shell=True)
        time.sleep(1)
        cmd = "docker exec "+nameList[x]+" sh -c 'nfdc route add /video tcp://10.2.0.2'"
        process5 = subprocess.Popen(cmd, shell=True)
  
#    acc_status += subprocess.call("docker exec %s %s -w /usr/src/app/video ./publish.sh" % (volumes, emu1),shell=True)
    for x in range(1, numberOfNodes):
        #cmd = ['docker', 'exec', nameList[x],'sh -c "node --harmony streaming.js',videoHash,'/ip4/10.2.0.2/tcp/4001/ipfs/'+id+' >> /var/log/streaming.log"']
        #proc4 = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #print(cmd)
        #out, err = proc4.communicate()
        #print(id[1:-1].strip())
        #r_code = subprocess.call("docker exec "+nameList[x]+" sh -c 'node --harmony streaming.js "+videoHash+" /ip4/10.2.0.2/tcp/4001/ipfs/"+hash+" >> /var/log/streaming/streaming.log'", shell=True)
        #print("docker exec "+nameList[x]+" sh -c 'node --harmony streaming.js "+videoHash+" /ip4/10.2.0.2/tcp/4001/ipfs/"+hash+" >> /var/log/streaming/streaming.log'")
        #check_return_code_chill(r_code, "Client executed") cmd = ['docker', 'inspect', '--format', "'{{ .State.Pid }}'", nameList[x]]

        cmd = "docker exec "+nameList[x]+" sh -c 'node  streaming-ndn.js  >> /var/log/streaming/streaming.log'"
        process3 = subprocess.Popen(cmd, shell=True)
        time.sleep(3)
        out, err = process3.communicate()

    print("client execution done")
    time.sleep(int(emulationTimeStr))

    print('Finished RUN SIM 2 | Date now: %s' % datetime.datetime.now())

    return


def write_conf(target, nodes, timeout, root, port, filename):
    config = {
        'target': target,
        'nodes': nodes,
        'timeout': int(timeout),
        'rootnode': root,
        'port': port
    }
    filename = "conf/" + filename
    with open(filename, 'w') as yaml_file:
        yaml.dump(config, yaml_file, default_flow_style=False)


################################################################################
# end ns3 ()
################################################################################


################################################################################
# destroy ()
################################################################################
def destroy():
    print("Destroying ...")

    print("DESTROYING ALL CONTAINERS")
    r_code = subprocess.call("docker stop $(docker ps -a -q) && docker rm $(docker ps -a -q)", shell=True)
    check_return_code_chill(r_code, "Destroying ALL containers")

    for x in range(0, numberOfNodes):

        r_code = subprocess.call("bash net/singleDestroy.sh %s" % (nameList[x]), shell=True)
        check_return_code_chill(r_code, "Destroying bridge and tap interface %s" % (nameList[x]))

        if os.path.exists(pidsDirectory + nameList[x]):
            with open(pidsDirectory + nameList[x], "rt") as in_file:
                text = in_file.read()
                r_code = subprocess.call("rm -rf /var/run/netns/%s" % (text.strip()), shell=True)
                check_return_code_chill(r_code, "Destroying docker bridges %s" % (nameList[x]))

        r_code = subprocess.call("rm -rf %s" % (pidsDirectory + nameList[x]), shell=True)
        check_return_code_chill(r_code, "Removing pids directory")

    return


################################################################################
# end destroy ()
################################################################################


if __name__ == '__main__':
    main()
