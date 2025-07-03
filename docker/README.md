# Docker Deployment Guide for Bittensor Subnet

This guide explains how to deploy the Bittensor subnet services (manager, miner, validator) using Docker in a distributed environment.

## Overview

The deployment is designed to support:
- **Manager**: Deployed on a dedicated server
- **Miners**: Can be deployed on multiple servers or multiple instances on the same server
- **Validators**: Can be deployed on multiple servers or multiple instances on the same server

## File Structure

```
├── Dockerfile                    # Universal Docker image for all services
├── docker-compose.manager.yml    # Manager service configuration
├── docker-compose.miner.yml      # Miner service configuration
├── docker-compose.validator.yml  # Validator service configuration
├── docker-manager.sh             # Manager service management script
├── docker-miner.sh               # Miner service management script
├── docker-validator.sh           # Validator service management script
├── deploy.sh                     # Main deployment script
├── version.sh                    # Version management script
├── logs/                         # Log directory
└── DOCKER_README.md              # This file
```

## Prerequisites

1. **Docker**: Install Docker on all target servers
2. **Docker Compose**: Install Docker Compose on all target servers
3. **Bittensor Wallet**: Ensure you have a Bittensor wallet configured on each server

## Quick Start

### 1. Setup Environment

Create a `.env` file in the project root directory:

```bash
# Copy from example if available, or create manually
# cp env.example .env

# Basic configuration
CHAIN_NETWORK=local
CHAIN_NETUID=1
CHAIN_ENDPOINT=ws://127.0.0.1:9944

# Service ports (will be auto-configured if not present)
MANAGER_PORT=8000
MINER_PORT=8091
VALIDATOR_PORT=8092

# Service names (will be auto-configured based on directory name)
MINER_NAME=your-miner-name
VALIDATOR_NAME=your-validator-name
```

### 2. Deploy Services

#### Deploy Manager (on manager server)
```bash
# Make scripts executable
chmod +x docker/*.sh

# Deploy manager service
./docker/deploy.sh manager

# Or with force rebuild
./docker/deploy.sh manager force-build
```

#### Deploy Miners (on miner servers)
```bash
# Deploy miner service
./docker/deploy.sh miner

# Or with force rebuild
./docker/deploy.sh miner force-build
```

#### Deploy Validators (on validator servers)
```bash
# Deploy validator service
./docker/deploy.sh validator

# Or with force rebuild
./docker/deploy.sh validator force-build
```

## Service Management

### Using Individual Service Scripts

Each service has its own management script with the following commands:

#### Manager Service (`docker-manager.sh`)
```bash
# Build manager image
./docker/docker-manager.sh build

# Run manager container
./docker/docker-manager.sh run

# Stop manager service
./docker/docker-manager.sh stop

# Start manager service
./docker/docker-manager.sh start

# Restart manager service
./docker/docker-manager.sh restart

# Stop and remove manager container
./docker/docker-manager.sh down

# Check if manager image exists
./docker/docker-manager.sh check

# Follow manager logs in real-time
./docker/docker-manager.sh logs
```

#### Miner Service (`docker-miner.sh`)
```bash
# Build miner image
./docker/docker-miner.sh build

# Run miner container
./docker/docker-miner.sh run

# Stop miner service
./docker/docker-miner.sh stop

# Start miner service
./docker/docker-miner.sh start

# Restart miner service
./docker/docker-miner.sh restart

# Stop and remove miner container
./docker/docker-miner.sh down

# Check if miner image exists
./docker/docker-miner.sh check

# Follow miner logs in real-time
./docker/docker-miner.sh logs
```

#### Validator Service (`docker-validator.sh`)
```bash
# Build validator image
./docker/docker-validator.sh build

# Run validator container
./docker/docker-validator.sh run

# Stop validator service
./docker/docker-validator.sh stop

# Start validator service
./docker/docker-validator.sh start

# Restart validator service
./docker/docker-validator.sh restart

# Stop and remove validator container
./docker/docker-validator.sh down

# Check if validator image exists
./docker/docker-validator.sh check

# Follow validator logs in real-time
./docker/docker-validator.sh logs
```

### Using Docker Compose Directly

You can also use Docker Compose commands directly:

```bash
# Manager
docker-compose --env-file .env -f docker/docker-compose.manager.yml up -d
docker-compose --env-file .env -f docker/docker-compose.manager.yml down
docker-compose --env-file .env -f docker/docker-compose.manager.yml logs -f

# Miner
docker-compose --env-file .env -f docker/docker-compose.miner.yml up -d
docker-compose --env-file .env -f docker/docker-compose.miner.yml down
docker-compose --env-file .env -f docker/docker-compose.miner.yml logs -f

# Validator
docker-compose --env-file .env -f docker/docker-compose.validator.yml up -d
docker-compose --env-file .env -f docker/docker-compose.validator.yml down
docker-compose --env-file .env -f docker/docker-compose.validator.yml logs -f
```

## Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Network Configuration
CHAIN_NETWORK=local                    # Network type (local, test, main)
CHAIN_NETUID=1                        # Subnet UID
CHAIN_ENDPOINT=ws://127.0.0.1:9944    # Chain endpoint

# Service Configuration
MANAGER_PORT=8000                     # Manager service port
MINER_PORT=8091                       # Miner service port
VALIDATOR_PORT=8092                   # Validator service port

# Service Names (auto-configured based on directory name)
MINER_NAME=your-miner-name            # Miner instance name
VALIDATOR_NAME=your-validator-name    # Validator instance name

# Version (auto-configured from version.sh)
VERSION=0.0.1                         # Service version
```

### Auto-Configuration

The scripts automatically configure the following in your `.env` file:
- `MANAGER_PORT`: Set to 8000 if not present
- `MINER_PORT`: Set to 8091 if not present
- `VALIDATOR_PORT`: Set to 8092 if not present
- `MINER_NAME`: Set to the parent directory name
- `VALIDATOR_NAME`: Set to the parent directory name
- `VERSION`: Set to the version from `version.sh`

### Volume Mounts

The services mount the following volumes:
- `~/.bittensor`: Bittensor wallet and configuration
- `./logs`: Application logs
- `../.env`: Environment configuration file

## Deployment Scenarios

### Scenario 1: Single Server Deployment
All services on one server:
```bash
# Server 1
./docker/deploy.sh manager
./docker/deploy.sh miner
./docker/deploy.sh validator
```

### Scenario 2: Distributed Deployment
Services across multiple servers:

**Manager Server:**
```bash
./docker/deploy.sh manager
```

**Miner Server:**
```bash
./docker/deploy.sh miner
```

**Validator Server:**
```bash
./docker/deploy.sh validator
```

## Monitoring and Logs

### Health Checks
- Manager: HTTP health check on configured port
- Miners: Process check for miner.py
- Validators: Process check for validator.py

### Logs
View logs for any service:
```bash
# Follow logs in real-time
docker-compose --env-file .env -f docker/docker-compose.manager.yml logs -f
docker-compose --env-file .env -f docker/docker-compose.miner.yml logs -f
docker-compose --env-file .env -f docker/docker-compose.validator.yml logs -f

# View recent logs
docker-compose --env-file .env -f docker/docker-compose.manager.yml logs --tail=100
docker-compose --env-file .env -f docker/docker-compose.miner.yml logs --tail=100
docker-compose --env-file .env -f docker/docker-compose.validator.yml logs --tail=100
```

### Status Monitoring
Check service status:
```bash
# Check running containers
docker ps

# Check specific service
docker ps | grep bst-manager
docker ps | grep bst-miner
docker ps | grep bst-validator
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Ensure ports are not already in use
2. **Wallet Issues**: Verify Bittensor wallet is properly configured
3. **Network Issues**: Check chain endpoint connectivity
4. **Permission Issues**: Ensure scripts are executable

### Debug Commands

```bash
# Check container status
docker ps -a

# Check container logs
docker logs <container_name>

# Check container health
docker inspect <container_name> | grep Health -A 10

# Enter container for debugging
docker exec -it <container_name> /bin/bash

# Check environment variables
docker exec <container_name> env
```

### Updating Services

To update services with new code:

```bash
# Force rebuild and deploy
./docker/deploy.sh manager force-build
./docker/deploy.sh miner force-build
./docker/deploy.sh validator force-build

# Or rebuild individual services
./docker/docker-manager.sh build
./docker/docker-miner.sh build
./docker/docker-validator.sh build

# Then restart services
./docker/docker-manager.sh restart
./docker/docker-miner.sh restart
./docker/docker-validator.sh restart
```

## Security Considerations

1. **Network Security**: Use firewalls to restrict access to service ports
2. **Volume Security**: Ensure proper permissions on mounted volumes
3. **Environment Variables**: Keep sensitive data in environment variables, not in code
4. **Regular Updates**: Keep Docker images and dependencies updated

## Performance Optimization

1. **Resource Limits**: Set appropriate CPU and memory limits in docker-compose files
2. **Volume Optimization**: Use appropriate volume drivers for your storage backend
3. **Network Optimization**: Use host networking for high-performance scenarios
4. **Monitoring**: Implement proper monitoring and alerting

## Support

For issues and questions:
1. Check the logs first: `docker-compose --env-file .env -f docker/docker-compose.<service>.yml logs`
2. Verify configuration in `.env` file
3. Check Docker and Docker Compose versions
4. Review the troubleshooting section above 