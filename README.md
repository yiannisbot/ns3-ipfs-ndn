# Network Emulation of Production Code on NS3 Using Docker Containers

The files in this repository are the main configuration files to run NS3 simulations using the production code of [IPFS](https://ipfs.io) and [NDN](https://named-data.net) in Docker Containers. The main setup of importing Docker Containers into NS3 code is provided here: https://chepeftw.github.io/NS3DockerEmulator/ with all the required steps and supporting documentation.

This can be a very powerful tool to emulate the real behaviour of IPFS (or any other protocol (stack) for that matter), but in a simulation environment, which further means that it can scale up to thousands of nodes. This particular setup (see files above) has been used in the following paper, which came out of our team @UCL:

<strong> [Towards Peer-to-Peer Content Retrieval Markets: Enhancing IPFS with ICN](https://conferences.sigcomm.org/acm-icn/2019/proceedings/icn19-34.pdf)</strong>, ACM ICN 2019, Macau, SAR, China, September 2019.

The paper details all the setup parameters, as well as what configuration was used to produce the results. The complete compiled code with the NS3 files and the input to the siulations can be found here: https://www.ee.ucl.ac.uk./ipsaras/files/ipfs_ndn_ns3emulation.tgz (~230MB).

The simulation setup can be used as is, or can be modified as needed to evaluate different aspects of the protocol stacks.

Below a step-by-step guide to get the simulation/emulation started with a basic star topology.

# NS3 Docker Emulator HOWTO
  
<strong> Preliminaries: </strong>

Run the install.sh script to install ns3, Docker and other tools for the emulator to work.
You can also read the docs to learn about the NS3 docker emulator: https://chepeftw.github.io/NS3DockerEmulator/

Configuration:

Open main.new.ipfs.py and modify ns3_home and docker_home variables with paths to ns3 and ipfs docker image.

<strong> Run: </strong>

Use -n option to set the number of nodes in the topology and -t option to set the simulation time in seconds.

Example:

$ sudo python main.new.ipfs.py -n 10 -t 100 create  ---> builds ns3, loads ipfs Docker image and sets up the emulator

$ sudo python main.new.ipfs.py -n 10 -t 100 ns3     ---> starts ns3 and connects with containers

$ sudo python main.new.ipfs.py -n 10 -t 100 emulate ---> starts the experiment

<strong> Setting ns3 simulation scenario: </strong>

Currently, by default the simulator runs the scenario called tap-vm2. You can find tap-vm2 under the scratch folder of ns-3 (see: bake/source/ns-3.26/scratch/). tap-vm2 creates a star topology with a configurable number of nodes. In order to create different topologies, please refer to ns3 documentation: https://www.nsnam.org/documentation/
