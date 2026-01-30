#!/bin/bash

# Download and extract the start-network package
curl -#SL https://github.com/RBBNet/start-network/releases/download/v0.4.1+permv1/start-network.tar.gz | tar xz
cd start-network

# [BEGIN OF VALIDATION NODE CONFIGURATION]
# Create Validation Node
./rbb-cli node create validator

# Set the Validation Node network port
./rbb-cli config set nodes.validator.ports+=[\"10001:8545\"]

# Set the Validation Node network address
./rbb-cli config set nodes.validator.address=\"127.0.0.1:10303\"
# NOTE: for external connections change the address to your server's public IP
# [END OF VALIDATION NODE CONFIGURATION]

# [BEGIN OF BOOT NODE CONFIGURATION]
# Create Boot Node
./rbb-cli node create boot

# Set the Boot Node network port
./rbb-cli config set nodes.boot.ports+=[\"10002:8545\"]

# Set the Boot Node network address
./rbb-cli config set nodes.boot.address=\"127.0.0.1:10304\"
# [END OF BOOT NODE CONFIGURATION]

# Create Genesis Block
./rbb-cli genesis create --validators validator

# Render docker-compose file
./rbb-cli config render-templates

echo "Configuration complete. Copy the manager private key and press enter to continue."
cat .env.configs/nodes/validator/key
read -r

# Start the Boot and Validation nodes
docker compose up --build boot validator
