# Network Emulation of Production Code on NS3 Using Docker Containers

The files in this repository are the main configuration files to run NS3 simulations using the production code of [IPFS](https://ipfs.io) and [NDN](https://named-data.net) in Docker Containers. The main setup of importing Docker Containers into NS3 code is provided here: https://chepeftw.github.io/NS3DockerEmulator/ with all the required steps and supporting documentation.

This can be a very powerful tool to emulate the real behaviour of IPFS (or any other protocol (stack) for that matter), but in a simulation environment, which further means that it can scale up to thousands of nodes. This particular setup (see files above) has been used in the following paper, which came out of our team @UCL:

<strong> [Towards Peer-to-Peer Content Retrieval Markets: Enhancing IPFS with ICN](https://conferences.sigcomm.org/acm-icn/2019/proceedings/icn19-34.pdf)</strong>, ACM ICN 2019, Macau, SAR, China, September 2019.

The paper details all the setup parameters, as well as what configuration was used to produce the results. The complete compiled code with the NS3 files and the input to the siulations can be found here: https://www.ee.ucl.ac.uk./ipsaras/files/ipfs_ndn_ns3emulation.tgz

The simulation setup can be used as is, or can be modified as needed to evaluate different aspects of the protocol stacks.
