# ExtremeXP Policy Access Control
![ExtremeXP](https://img.shields.io/badge/ExtremeXP-121011?style=for-the-badge&logo=extremexp&logoColor=black)
![Python](https://img.shields.io/badge/python-121011?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23121011.svg?style=for-the-badge&logo=flask&logoColor=white)
![Web3](https://img.shields.io/badge/web3-121011?style=for-the-badge&logo=web3.js&logoColor=white)
![Solidity](https://img.shields.io/badge/Solidity-%23121011.svg?style=for-the-badge&logo=solidity&logoColor=white)
![Hyperledger](https://img.shields.io/badge/hyperledger-121011?style=for-the-badge&logo=hyperledger&logoColor=white)
![Docker](https://img.shields.io/badge/docker-121011?style=for-the-badge&logo=docker&logoColor=white)
![Metamask](https://img.shields.io/badge/metamask-121011?style=for-the-badge&logo=metamask&logoColor=white)
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)

This project provides an interface for the ExtremeXP Access Control module,
enabling the translation of XACML policies into Solidity smart contracts.
The module's key responsibilities include:

- Acting as the backend for the ExtremeXP security layer.  
- Translating XACML policies into Solidity smart contracts.  
- Deploying the generated smart contracts onto the blockchain.  

> Note: The translator project is based on the [XACML](https://www.oasis-open.org/committees/xacml/) standard 
and the [Solidity](https://soliditylang.org/) programming language.

## Project Architecture

![Project Architecture](./docs/ExtremeXP-Translator.png "Project Architecture")


## Getting Started
```bash
# install the project development environment
make install
# run the project
make run
```
The server will be running on http://localhost:5521.
The Swagger documentation is available on the root page.


## Development Progress
#### Overall progress: 
![](https://geps.dev/progress/33)

#### Tasks:
- [x] Project Basic Structure (Flask API + Endpoints + kickoff script)
- [ ] XACML/JSON to the PolicyGraph structure (Structure Builder module)
- [ ] Map the XACML basic functions over the PolicyGraph (See: https://en.wikipedia.org/wiki/XACML#Functions)
- [ ] Translate the PolicyGraph to a Solidity Smart Contract (Solidity Policy Builder module)
- [x] Deploy the Smart Contract and retrieve the address (Blockchain Interface module)
- [ ] Register the Policy address to some database (Policy Address DB)
- [x] Integrate with the Keycloak Authorization Server (OAuth or MetaMask)
- [ ] Integrate with the [ExtremeXP Portal](https://github.com/ExtremeXP-VU/ExtremeXP-portal)
- [ ] Add the Smart Contracts used for the ABAC module in the project for documentation purposes
