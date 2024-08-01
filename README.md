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



