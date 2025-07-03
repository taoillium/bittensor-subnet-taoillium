#!/usr/bin/env python3
"""
Test script to verify network connectivity from Docker container
"""

import asyncio
import aiohttp
import socket
import subprocess
import sys

async def test_network_connectivity():
    """Test network connectivity from Docker container"""
    
    print("🔍 TESTING DOCKER CONTAINER NETWORK CONNECTIVITY")
    print("=" * 60)
    
    # Test 1: DNS resolution
    print("\n1️⃣ DNS Resolution Test:")
    try:
        ip = socket.gethostbyname("test.finney.opentensor.ai")
        print(f"   ✅ test.finney.opentensor.ai resolves to: {ip}")
    except Exception as e:
        print(f"   ❌ DNS resolution failed: {e}")
    
    # Test 2: Direct IP connection
    print("\n2️⃣ Direct IP Connection Test:")
    target_ip = "47.129.35.160"
    ports = [8091, 8092]
    
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((target_ip, port))
            sock.close()
            
            if result == 0:
                print(f"   ✅ {target_ip}:{port} - Connection successful")
            else:
                print(f"   ❌ {target_ip}:{port} - Connection failed (error code: {result})")
        except Exception as e:
            print(f"   ❌ {target_ip}:{port} - Connection error: {e}")
    
    # Test 3: HTTP connection to manager
    print("\n3️⃣ HTTP Connection Test:")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health", timeout=5) as response:
                if response.status == 200:
                    print("   ✅ Manager health endpoint accessible")
                else:
                    print(f"   ⚠️ Manager health endpoint returned status: {response.status}")
    except Exception as e:
        print(f"   ❌ Manager health endpoint error: {e}")
    
    # Test 4: Network interface information
    print("\n4️⃣ Network Interface Test:")
    try:
        result = subprocess.run(["ip", "addr"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("   ✅ Network interfaces:")
            for line in result.stdout.split('\n'):
                if 'inet ' in line and '127.0.0.1' not in line:
                    print(f"      {line.strip()}")
        else:
            print("   ❌ Failed to get network interfaces")
    except Exception as e:
        print(f"   ❌ Network interface error: {e}")
    
    # Test 5: Route information
    print("\n5️⃣ Route Information Test:")
    try:
        result = subprocess.run(["ip", "route"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("   ✅ Routing table:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    print(f"      {line.strip()}")
        else:
            print("   ❌ Failed to get routing information")
    except Exception as e:
        print(f"   ❌ Route information error: {e}")

if __name__ == "__main__":
    asyncio.run(test_network_connectivity()) 