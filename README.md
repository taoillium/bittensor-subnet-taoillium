<div align="center">

# **Bittensor Subnet Taoillium** <!-- omit in toc -->
[![Discord Chat](https://img.shields.io/discord/308323056592486420.svg)](https://discord.gg/bittensor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

---

## The Incentivized Internet <!-- omit in toc -->

[Discord](https://discord.gg/bittensor) • [Network](https://taostats.io/) • [Research](https://bittensor.com/whitepaper)
</div>

---
- [Quickstarter template](#quickstarter-template)
- [Introduction](#introduction)
  - [Example](#example)
- [Installation](#installation)
  - [Before you proceed](#before-you-proceed)
  - [Install](#install)
- [Project Structure Update](#project-structure-update)
  - [Key Directories](#key-directories)
    - [`neurons/`](#neurons)
    - [`services/`](#services)
  - [How to Extend](#how-to-extend)
  - [Example Flow](#example-flow)
- [Subnet Links](#subnet-links)
- [License](#license)

---
## Quickstarter template

This template contains all the required installation instructions, scripts, and files and functions for:
- Building Bittensor subnets.
- Creating custom incentive mechanisms and running these mechanisms on the subnets. 

In order to simplify the building of subnets, this template abstracts away the complexity of the underlying blockchain and other boilerplate code. While the default behavior of the template is sufficient for a simple subnet, you should customize the template in order to meet your specific requirements.
---

## Introduction

**IMPORTANT**: If you are new to Bittensor subnets, read this section before proceeding to [Installation](#installation) section. 

The Bittensor blockchain hosts multiple self-contained incentive mechanisms called **subnets**. Subnets are playing fields in which:
- Subnet miners who produce value, and
- Subnet validators who produce consensus

determine together the proper distribution of TAO for the purpose of incentivizing the creation of value, i.e., generating digital commodities, such as intelligence or data. 

Each subnet consists of:
- Subnet miners and subnet validators.
- A protocol using which the subnet miners and subnet validators interact with one another. This protocol is part of the incentive mechanism.
- The Bittensor API using which the subnet miners and subnet validators interact with Bittensor's onchain consensus engine [Yuma Consensus](https://bittensor.com/documentation/validating/yuma-consensus). The Yuma Consensus is designed to drive these actors: subnet validators and subnet miners, into agreement on who is creating value and what that value is worth. 

This starter template is split into three primary files. To write your own incentive mechanism, you should edit these files. These files are:
1. `template/protocol.py`: Contains the definition of the protocol used by subnet miners and subnet validators.
2. `neurons/miner.py`: Script that defines the subnet miner's behavior, i.e., how the subnet miner responds to requests from subnet validators.
3. `neurons/validator.py`: This script defines the subnet validator's behavior, i.e., how the subnet validator requests information from the subnet miners and determines the scores.

### Example

The Bittensor Subnet 1 for Text Prompting is built using this template. See [prompting](https://github.com/macrocosm-os/prompting) for how to configure the files and how to add monitoring and telemetry and support multiple miner types. Also see this Subnet 1 in action on [Taostats](https://taostats.io/subnets/netuid-1/) explorer.

---

## Installation

### Before you proceed
Before you proceed with the installation of the subnet, note the following: 

- Use these instructions to run your subnet locally for your development and testing, or on Bittensor testnet or on Bittensor mainnet. 
- **IMPORTANT**: We **strongly recommend** that you first run your subnet locally and complete your development and testing before running the subnet on Bittensor testnet. Furthermore, make sure that you next run your subnet on Bittensor testnet before running it on the Bittensor mainnet.
- You can run your subnet either as a subnet owner, or as a subnet validator or as a subnet miner. 
- **IMPORTANT:** Make sure you are aware of the minimum compute requirements for your subnet. See the [Minimum compute YAML configuration](./min_compute.yml).
- Note that installation instructions differ based on your situation: For example, installing for local development and testing will require a few additional steps compared to installing for testnet. Similarly, installation instructions differ for a subnet owner vs a validator or a miner. 

### Install

- **Running locally**: Follow the step-by-step instructions described in this section: [Running Subnet Locally](./docs/running_on_staging.md).
- **Running on Bittensor testnet**: Follow the step-by-step instructions described in this section: [Running on the Test Network](./docs/running_on_testnet.md).
- **Running on Bittensor mainnet**: Follow the step-by-step instructions described in this section: [Running on the Main Network](./docs/running_on_mainnet.md).

---

## Project Structure Update

### Key Directories

#### `neurons/`
This directory contains the main entry points for the two core roles in a Bittensor subnet:
- **`miner.py`**: Implements the logic for a subnet miner. The miner receives requests from validators, processes them (often by interacting with external APIs or services), and returns responses. The miner class inherits from a base class that handles most of the Bittensor-specific boilerplate, allowing you to focus on your custom logic.
- **`validator.py`**: Implements the logic for a subnet validator. The validator queries miners, evaluates their responses, and assigns scores or rewards. This implementation includes an HTTP server (using FastAPI) to expose endpoints for external interaction and uses JWT-based authentication for security.

Both files are designed for easy extension: override the `forward` method to define your custom behavior for processing and validating requests.

#### `services/`
This directory modularizes the supporting infrastructure for your subnet logic, separating concerns and making the codebase more maintainable and extensible:
- **`protocol.py`**: Defines the wire protocol (`ServiceProtocol`) used for communication between miners and validators. This protocol is based on Bittensor's `bt.Synapse` and specifies the request/response schema.
- **`api.py`**: Provides HTTP client classes (`MinerClient`, `ValidatorClient`) for interacting with external APIs or services. These clients handle authentication and simplify making requests to your service endpoints.
- **`security.py`**: Implements JWT-based authentication utilities, including token creation and verification, to secure API endpoints and inter-node communication.
- **`config.py`**: Centralizes configuration management using environment variables and Pydantic settings, making it easy to adjust deployment parameters and secrets.

### How to Extend

- To **customize miner or validator behavior**, edit `neurons/miner.py` and `neurons/validator.py`, focusing on the `forward` methods.
- To **change the protocol or add new message types**, update or extend `services/protocol.py`.
- To **integrate with new external services or APIs**, add or modify client classes in `services/api.py`.
- To **adjust authentication or security policies**, update `services/security.py`.
- To **change configuration options**, edit `services/config.py` and your `.env` file.

### Example Flow

1. **Validator** sends a request to a **Miner** using the `ServiceProtocol`.
2. **Miner** processes the request, possibly using a service client from `services/api.py`, and returns a response.
3. **Validator** evaluates the response, scores the miner, and may interact with external APIs for validation or reward logic.

---

This modular structure makes it easy to adapt the template for your own use case, whether you are building a new incentive mechanism, integrating with external APIs, or deploying on different environments.


## License
This repository is licensed under the MIT License.
```text
# The MIT License (MIT)
# Copyright © 2024 Opentensor Foundation
# Copyright © 2025 Taoillium Foundation

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
```
