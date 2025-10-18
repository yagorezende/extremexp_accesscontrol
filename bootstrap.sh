#!/bin/bash

# This script is used to bootstrap the environment for the project.
source .venv/bin/activate
source .env.prod

echo "Bootstrapping the environment..."
echo "Creating Blockchain User..."
python3 -m blockchain_interface.user --username "$BLOCKCHAIN_USER" --password "$BLOCKCHAIN_PASSWORD"