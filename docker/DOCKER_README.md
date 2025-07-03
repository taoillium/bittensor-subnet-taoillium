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
├── docker-compose.miner.yml      # Miner services configuration (multiple instances)
├── docker-compose.validator.yml  # Validator services configuration (multiple instances)
├── env.example                   # Environment variables template
├── scripts/
│   ├── deploy.sh                 # Deployment script
│   └── manage.sh                 # Service management script
└── DOCKER_README.md              # This file
```

## Prerequisites

1. **Docker**: Install Docker on all target servers
2. **Docker Compose**: Install Docker Compose on all target servers
3. **Bittensor Wallet**: Ensure you have a Bittensor wallet configured on each server

## Quick Start

### 1. Setup Environment

Copy the environment template and configure it:

```bash
cp env.example .env
# Edit .env with your specific configuration
```

### 2. Deploy Services

#### Deploy Manager (on manager server)
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Deploy manager service
./scripts/deploy.sh manager
```

#### Deploy Miners (on miner servers)
```bash
# Deploy miner instance 1
./scripts/deploy.sh miner 1

# Deploy miner instance 2 (on same or different server)
./scripts/deploy.sh miner 2

# Deploy miner instance 3 (on same or different server)
./scripts/deploy.sh miner 3
```

#### Deploy Validators (on validator servers)
```bash
# Deploy validator instance 1
./scripts/deploy.sh validator 1

# Deploy validator instance 2 (on same or different server)
./scripts/deploy.sh validator 2

# Deploy validator instance 3 (on same or different server)
./scripts/deploy.sh validator 3
```

## Service Management

### Using the Management Script

The `manage.sh` script provides easy management of all services:

```bash
# Show service status
./scripts/manage.sh manager status
./scripts/manage.sh miner status
./scripts/manage.sh validator status

# Start services
./scripts/manage.sh manager start
./scripts/manage.sh miner start 1
./scripts/manage.sh validator start 2

# Stop services
./scripts/manage.sh manager stop
./scripts/manage.sh miner stop 1
./scripts/manage.sh validator stop 2

# Restart services
./scripts/manage.sh manager restart
./scripts/manage.sh miner restart 1
./scripts/manage.sh validator restart 2

# View logs
./scripts/manage.sh manager logs
./scripts/manage.sh miner logs 1
./scripts/manage.sh validator logs 2

# Build services
./scripts/manage.sh manager build
./scripts/manage.sh miner build
./scripts/manage.sh validator build
```

### Using Docker Compose Directly

You can also use Docker Compose commands directly:

```bash
# Manager
docker-compose -f docker-compose.manager.yml up -d
docker-compose -f docker-compose.manager.yml down
docker-compose -f docker-compose.manager.yml logs -f

# Miners
docker-compose -f docker-compose.miner.yml up -d miner-1
docker-compose -f docker-compose.miner.yml up -d miner-2
docker-compose -f docker-compose.miner.yml down

# Validators
docker-compose -f docker-compose.validator.yml up -d validator-1
docker-compose -f docker-compose.validator.yml up -d validator-2
docker-compose -f docker-compose.validator.yml down
```

## Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Network Configuration
CHAIN_NETWORK=local                    # Network type (local, test, main)
CHAIN_NETUID=1                        # Subnet UID
CHAIN_ENDPOINT=ws://127.0.0.1:9944  # Chain endpoint

# Manager Configuration
MANAGER_PORT=8000               # Manager service port
MANAGER_DEBUG=INFO              # Log level
MANAGER_RELOAD=false            # Auto-reload on code changes

```

### Volume Mounts

The services mount the following volumes:
- `~/.bittensor`: Bittensor wallet and configuration
- `./logs`: Application logs
- `./data/{service}-{instance}`: Service-specific data

## Deployment Scenarios

### Scenario 1: Single Server Deployment
All services on one server:
```bash
# Server 1
./scripts/deploy.sh manager
./scripts/deploy.sh miner 1
./scripts/deploy.sh miner 2
./scripts/deploy.sh validator 1
./scripts/deploy.sh validator 2
```

### Scenario 2: Distributed Deployment
Services across multiple servers:

**Manager Server:**
```bash
./scripts/deploy.sh manager
```

**Miner Server 1:**
```bash
./scripts/deploy.sh miner 1
./scripts/deploy.sh miner 2
```

**Miner Server 2:**
```bash
./scripts/deploy.sh miner 3
./scripts/deploy.sh miner 4
```

**Validator Server 1:**
```bash
./scripts/deploy.sh validator 1
./scripts/deploy.sh validator 2
```

**Validator Server 2:**
```bash
./scripts/deploy.sh validator 3
./scripts/deploy.sh validator 4
```

## Monitoring and Logs

### Health Checks
All services include health checks:
- Manager: HTTP health check on port 5000
- Miners: Process check for miner.py
- Validators: Process check for validator.py

### Logs
View logs for any service:
```bash
# All logs
./scripts/manage.sh manager logs
./scripts/manage.sh miner logs 1
./scripts/manage.sh validator logs 1

# Follow logs in real-time
docker-compose -f docker-compose.manager.yml logs -f
docker-compose -f docker-compose.miner.yml logs -f miner-1
docker-compose -f docker-compose.validator.yml logs -f validator-1
```

### Status Monitoring
Check service status:
```bash
./scripts/manage.sh manager status
./scripts/manage.sh miner status
./scripts/manage.sh validator status
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
```

### Updating Services

To update services with new code:

```bash
# Pull latest changes and rebuild
./scripts/manage.sh manager build
./scripts/manage.sh miner build
./scripts/manage.sh validator build

# Restart services
./scripts/manage.sh manager restart
./scripts/manage.sh miner restart 1
./scripts/manage.sh validator restart 1
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
1. Check the logs first: `./scripts/manage.sh <service> logs`
2. Verify configuration in `.env` file
3. Check Docker and Docker Compose versions
4. Review the troubleshooting section above 