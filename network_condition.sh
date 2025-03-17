#!/bin/bash

# Network interface to apply rules
INTERFACE="eth0"

# Function to apply traffic control rules
apply_tc() {
    sudo tc qdisc del dev $INTERFACE root 2>/dev/null
    sudo tc qdisc add dev $INTERFACE root netem $1
    echo "[INFO] Applied: tc qdisc add dev $INTERFACE root netem $1"
}

# Menu for different network conditions
echo "Select a network condition to simulate:"
echo "1) Normal (No issues)"
echo "2) Fiber (Low latency, minimal loss)"
echo "3) Starlink (High latency, slight loss)"
echo "4) 3G/4G (Moderate latency, jitter, and loss)"
echo "5) Satellite (High latency, jitter, and packet loss)"
echo "6) Congested Network (Bandwidth limit with high latency)"
echo "7) Custom Configuration"
echo "8) Reset all traffic control rules"
read -p "Enter your choice (1-8): " CHOICE

# Apply selected network condition
case $CHOICE in
    1) apply_tc "" ;;
    2) apply_tc "delay 5ms 1ms loss 0.01%" ;;
    3) apply_tc "delay 200ms 30ms loss 1% rate 5mbit" ;;
    4) apply_tc "delay 120ms 20ms loss 3% rate 3mbit" ;;
    5) apply_tc "delay 350ms 50ms loss 5% duplicate 1%" ;;
    6) apply_tc "delay 150ms 30ms loss 3% rate 1mbit" ;;
    7) 
       read -p "Enter your custom rule (e.g., 'delay 100ms loss 2% rate 5mbit'): " CUSTOM_RULE
       apply_tc "$CUSTOM_RULE"
       ;;
    8) 
       sudo tc qdisc del dev $INTERFACE root
       echo "[INFO] All traffic control rules have been reset."
       ;;
    *)
       echo "[ERROR] Invalid choice. Please select a valid option."
       ;;
esac

# Display active rules
echo "[INFO] Active Traffic Control Rules:"
sudo tc qdisc show dev $INTERFACE
