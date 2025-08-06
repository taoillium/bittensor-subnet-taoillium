<div align="center">

# **Bittensor Subnet Taoillium** <!-- omit in toc -->
[![Discord Chat](https://img.shields.io/discord/308323056592486420.svg)](https://discord.gg/bittensor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

---

## The Incentivized Internet <!-- omit in toc -->

[Discord](https://discord.gg/bittensor) • [Network](https://taostats.io/) • [Research](https://bittensor.com/whitepaper)
</div>

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Deployment Options](#deployment-options)
- [Project Structure](#project-structure)
  - [Core Components](#core-components)
  - [Documentation](#documentation)
  - [Configuration](#configuration)
- [Development](#development)
  - [Extending the Subnet](#extending-the-subnet)
  - [Testing](#testing)
  - [Contributing](#contributing)
- [Deployment](#deployment)
- [License](#license)

---

## Overview

**Bittensor Subnet Taoillium** is a comprehensive framework for building and deploying incentivized subnets on the Bittensor blockchain. This project provides a complete template that abstracts away the complexity of blockchain interactions while offering powerful tools for creating custom incentive mechanisms.

The Bittensor blockchain hosts multiple self-contained incentive mechanisms called **subnets**, where:
- **Subnet Miners** produce value through computational work
- **Subnet Validators** produce consensus and evaluate miner contributions
- Together they determine the proper distribution of TAO tokens to incentivize value creation

Each subnet consists of:
- Subnet miners and validators
- A communication protocol for miner-validator interactions
- Integration with Bittensor's [Yuma Consensus](https://bittensor.com/documentation/validating/yuma-consensus) engine

## Features

### 🚀 **Core Functionality**
- **Modular Architecture**: Clean separation of miners, validators, and service layers
- **Custom Protocols**: Flexible protocol definition for miner-validator communication
- **Streaming Support**: Built-in streaming data transmission capabilities
- **API Management**: FastAPI-driven management server with comprehensive endpoints

### 🔐 **Security & Authentication**
- **JWT Authentication**: Secure token-based authentication system
- **Wallet Management**: Integrated Bittensor wallet operations
- **API Security**: Protected endpoints with role-based access control

### 🐳 **Deployment & Operations**
- **Docker Support**: Complete containerized deployment solution
- **Multi-Environment**: Support for local, testnet, and mainnet deployments
- **Management API**: RESTful API for subnet operations and monitoring

### 📚 **Documentation & Testing**
- **Comprehensive Docs**: Complete documentation from setup to production
- **Test Suite**: Extensive testing framework with automated validation
- **Tutorials**: Step-by-step guides for various use cases

## Quick Start

### Prerequisites
- Python 3.8+
- Docker (for containerized deployment)
- Bittensor wallet
- Minimum compute requirements (see [min_compute.yml](./min_compute.yml))

### Basic Setup
```bash
# Clone the repository
git clone <repository-url>
cd bittensor-subnet-taoillium

# Install dependencies
python -m pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration
```

### Run Locally
```bash
# Start miner
python neurons/miner.py --netuid 1 --wallet.name default --wallet.hotkey miner

# Start validator
python neurons/validator.py --netuid 1 --wallet.name default --wallet.hotkey validator
```

## Installation

### Prerequisites
Before proceeding with installation, ensure you have:
- **Python 3.8+** installed
- **Docker** (for containerized deployment)
- **Bittensor wallet** configured
- **Minimum compute resources** as specified in [min_compute.yml](./min_compute.yml)

### Deployment Options

#### 🏠 **Local Development**
For development and testing, follow the [Local Development Guide](./docs/running_on_staging.md).

#### 🧪 **Test Network**
For testing on Bittensor testnet, follow the [Test Network Guide](./docs/running_on_testnet.md).

#### 🌐 **Main Network**
For production deployment on Bittensor mainnet, follow the [Main Network Guide](./docs/running_on_mainnet.md).

#### 🐳 **Docker Deployment**
For containerized deployment, see the [Docker Deployment Guide](./docker/README.md).

## Project Structure

### Core Components

#### `neurons/` - Core Node Implementation
- **[`miner.py`](./neurons/miner.py)**: Subnet miner implementation that processes validator requests
- **[`validator.py`](./neurons/validator.py)**: Subnet validator implementation that queries miners and evaluates responses

#### `services/` - Service Layer
- **[`protocol.py`](./services/protocol.py)**: Communication protocol definition between miners and validators
- **[`api.py`](./services/api.py)**: HTTP client classes for external API interactions
- **[`security.py`](./services/security.py)**: JWT authentication utilities
- **[`config.py`](./services/config.py)**: Centralized configuration management
- **[`cli.py`](./services/cli.py)**: Command-line interface tools

#### `template/` - Base Components
- **[`protocol.py`](./template/protocol.py)**: Base protocol definitions
- **[`mock.py`](./template/mock.py)**: Mock service implementations
- **[`subnet_links.py`](./template/subnet_links.py)**: Subnet link management

#### `manage/` - Management API
- **[Management Server](./manage/README.md)**: FastAPI-based management server with wallet and subnet operations

### Documentation

#### 📖 **User Guides**
- **[Local Development](./docs/running_on_staging.md)**: Complete local setup and development guide
- **[Test Network Deployment](./docs/running_on_testnet.md)**: Step-by-step testnet deployment
- **[Main Network Deployment](./docs/running_on_mainnet.md)**: Production deployment guide
- **[Remote Wallet Setup](./docs/remote_wallet_setup.md)**: Remote wallet configuration
- **[Management Usage](./docs/manage_usage.md)**: Management service usage guide

#### 🔧 **Technical Documentation**
- **[Token Refresh Design](./docs/token_refresh_design.md)**: Token refresh mechanism design
- **[Streaming Tutorial](./docs/stream_tutorial/README.md)**: Complete streaming integration guide
- **[Docker Deployment](./docker/README.md)**: Containerized deployment guide
- **[Testing Documentation](./tests/README.md)**: Test suite documentation

#### 👥 **Contributor Resources**
- **[Contributing Guidelines](./contrib/CONTRIBUTING.md)**: How to contribute to the project
- **[Development Workflow](./contrib/DEVELOPMENT_WORKFLOW.md)**: Development processes and best practices
- **[Code Style Guide](./contrib/STYLE.md)**: Coding standards and conventions
- **[Code Review Guidelines](./contrib/CODE_REVIEW_DOCS.md)**: Code review process and standards

### Configuration

The project uses environment-based configuration through `services/config.py`. Key configuration areas include:

- **Network Settings**: Chain endpoints, netuid, network type
- **Service Ports**: Manager, miner, and validator port configurations
- **Authentication**: JWT tokens and wallet credentials
- **Compute Requirements**: Minimum resource specifications

For detailed environment variable documentation, see [Environment Variables Guide](./docs/environment_variables.md).

## Development

### Extending the Subnet

#### Customizing Behavior
- **Miner Logic**: Override the `forward` method in `neurons/miner.py`
- **Validator Logic**: Override the `forward` method in `neurons/validator.py`
- **Protocol Changes**: Modify `services/protocol.py` for new message types
- **API Integration**: Add client classes in `services/api.py`
- **Security Policies**: Update `services/security.py` for authentication changes

#### Example Workflow
1. **Validator** sends request to **Miner** using `ServiceProtocol`
2. **Miner** processes request (optionally using external APIs) and returns response
3. **Validator** evaluates response, scores miner, and may interact with external APIs

### Testing

Run the comprehensive test suite:
```bash
# Run all tests
cd tests
python run_new_tests.py

# Run specific test files
python -m unittest test_api_fix.py -v
python -m unittest test_miner_detection.py -v
python -m unittest test_subnet_api.py -v
```

### Contributing

We welcome contributions! Please see our [Contributing Guidelines](./contrib/CONTRIBUTING.md) for:
- Code contribution process
- Development workflow
- Code style standards
- Pull request guidelines

## Deployment

### Docker Deployment
For production deployments, use our comprehensive Docker setup:

```bash
# Deploy manager service
./docker/deploy.sh manager

# Deploy miner service
./docker/deploy.sh miner

# Deploy validator service
./docker/deploy.sh validator
```

### Management API
The management server provides RESTful APIs for:
- **Wallet Operations**: Sign messages, verify signatures, manage wallets
- **Subnet Interactions**: Query network, receive tasks, monitor health
- **Authentication**: JWT-based secure access

Access the interactive API documentation at `/docs` when running the management server.

## Example Use Cases

### Text Prompting Subnet
The Bittensor Subnet 1 for Text Prompting is built using this template. See [prompting](https://github.com/macrocosm-os/prompting) for configuration examples and [Taostats](https://taostats.io/subnets/netuid-1/) for live network data.

### Streaming Applications
For streaming data applications, see the [Streaming Tutorial](./docs/stream_tutorial/README.md) for complete implementation examples.

## Support & Community

- **Discord**: Join our [Discord community](https://discord.gg/bittensor)
- **Documentation**: Comprehensive guides in the `docs/` directory
- **Issues**: Report bugs and request features via GitHub issues
- **Discussions**: Use GitHub discussions for questions and ideas

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

```text
Copyright © 2024 Opentensor Foundation
Copyright © 2025 Taoillium Foundation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
