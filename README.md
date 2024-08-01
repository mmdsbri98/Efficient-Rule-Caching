# Efficient-Rule-Caching
# Project Title

## Description

Software-defined networks (SDNs) provide customizable traffic control by storing numerous rules in on-chip memories with minimal access latency. However, the current on-chip memory capacity falls short of meeting the growing demands of SDN control applications. While rule eviction and aggregation strategies address this challenge at the switch level, programmable data planes enable a more flexible approach through cooperative rule caching. However, current solutions rely on computationally intensive off-the-shelf solvers to perform rule placement across the network.

In this project, we implement a method for optimizing the management of switch capacity in SDNs through efficient collaborative rule caching, specifically exploring the pairing of P4 switches to enhance performance. We present an efficient solution for the cooperative rule caching problem by designing a resource-efficient switch capable of caching rules for its neighbors, alongside a lightweight protocol for retrieving cached rules. Additionally, we introduce RaSe, an approximation algorithm for minimizing rule lookup latency across the network through optimized cooperation-aware rule placement. Our approach includes:

### 1. Emulation
A setup for testing and demonstrating our approach on a small scale.

### 2. Simulation
A framework for evaluating the performance and scalability of our solution on a larger scale.

Our theoretical analysis of RaSe, combined with a P4-based proof-of-concept assessment in Mininet and a large-scale numerical evaluation using real-world network topology, shows that our approach runs about 160 times faster than solver-based solutions and improves the average rule lookup latency by about 21% compared to several algorithmic baselines.

Our primary focus here is on the implementation details. For a comprehensive understanding of the theoretical foundations and in-depth analysis, please refer to our published paper, which provides detailed explanations and insights into our work.
## Emulation

The **Emulation** component of this project is designed to test and demonstrate our approach on a small scale. This setup allows for the practical evaluation of our cooperative rule caching method within a controlled environment. In this section, we utilize [P4-Utils](https://nsg-ethz.github.io/p4-utils/introduction.html) to facilitate our emulation setup. P4-Utils provides a suite of tools designed to streamline the development and testing of P4-based network applications. By leveraging P4-Utils, we can efficiently simulate the behavior of P4 switches and validate our cooperative rule caching approach within a controlled environment.

Additionally, we create the network topology using [Mininet](http://mininet.org/), which allows us to design and deploy a virtual network to test our solution. Mininet provides a flexible platform for emulating network topologies and observing how our method performs under different configurations.


### Key Features:
- **Small-Scale Testing**: Simulates a limited network environment to validate the core functionalities of our solution. In this setup, we have a topology consisting of three switches, two hosts, and one controller. This topology is illustrated in Figure 1.

   ![Figure 1: Network Topology](images/figure1.jpg)
- **Demonstration**: Provides a proof-of-concept implementation that showcases how our method operates in a practical scenario.
- **Testing Setup**: Includes scripts and configurations to emulate the behavior of P4 switches and the cooperative caching mechanism.
## Packet Header for Switch Querying

We introduce a custom packet header, referred to as `cache_h`, to enable switches to query their peers and receive responses. The header structure is as follows:

0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23
protocol | type | action/owner | padding

- **Protocol Field:** This field backs up the IPv4 protocol field. The value `146` is used uniquely for `cache_h`, which is restored after processing.
- **Type Field:** This field has four values:
  - `TYPE L = 0`: Search local cache
  - `TYPE Q1 = 1`: Query other switches' caches
  - `TYPE Q2 = 2`: Query the controller
  - `TYPE R = 3`: Response
- **Action/Owner Field:** This field identifies the originator or response value. It specifies the port for packet forwarding.
- **Padding:** The last five bits are used for padding to ensure the header length is a multiple of eight bits.

### Switch Processing Overview

1. **Local Rule Search:**
   - When a switch finds no match in its local `forward_t` table, it adds `cache_h` with `type=TYPE L` and searches `cache_t`. If a match is found, the packet is forwarded accordingly.

2. **Querying Peers:**
   - If no match is found in `cache_t`, the switch uses `pairing_t` to send a `TYPE Q1` query to its pair. The switch sets the action to `query_pair` in `pairing_t`.

3. **Handling Queries:**
   - When a switch receives a `TYPE Q1` packet, it searches `cache_t` for a match:
     - **If a match is found:** The switch updates the packet with `TYPE R` and forwards it with the specified port.
     - **If no match is found:** The switch sets `type=TYPE Q2` and sends the packet to the controller using `send_2ctrl` in `pairing_t`.

4. **Processing Responses:**
   - Upon receiving a `TYPE R` packet, the switch restores the original IPv4 protocol value, removes `cache_h`, and forwards the packet based on the action/owner field.

**Figure 2** illustrates the proposed ingress processing for this header.

The emulation setup enables us to verify the effectiveness of our approach and make preliminary adjustments before scaling up to more extensive simulations and real-world applications.

For detailed instructions on how to run the emulation tests, please refer to the `README.md` file included in the `emulation` directory of this repository.



