# ExtremeXP Policy Translator
![ExtremeXP](https://img.shields.io/badge/ExtremeXP-121011?style=for-the-badge&logo=extremexp&logoColor=black)
![Python](https://img.shields.io/badge/python-121011?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23121011.svg?style=for-the-badge&logo=flask&logoColor=white)
![Web3](https://img.shields.io/badge/web3-121011?style=for-the-badge&logo=web3.js&logoColor=white)
![Solidity](https://img.shields.io/badge/Solidity-%23121011.svg?style=for-the-badge&logo=solidity&logoColor=white)
![Hyperledger](https://img.shields.io/badge/hyperledger-121011?style=for-the-badge&logo=hyperledger&logoColor=white)
![Docker](https://img.shields.io/badge/docker-121011?style=for-the-badge&logo=docker&logoColor=white)
![Metamask](https://img.shields.io/badge/metamask-121011?style=for-the-badge&logo=metamask&logoColor=white)
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)

This project translates XACML policies to Solidity smart contracts.
The project is based on the [XACML](https://www.oasis-open.org/committees/xacml/) standard 
and the [Solidity](https://soliditylang.org/) programming language.
---
## Project Architecture
The code is only for the translator backend. The frontend can be anything that sends a POST request with the XACML policy to the backend as a JSON.
![Project Architecture](./docs/ExtremeXP-Translator.png "Project Architecture")

---
## Getting Started
```bash
# install the project development environment
make install
# run the project
make run
```
The server will be running on http://localhost:5521.
The Swagger documentation is available in the root page.

---
## Development Progress
#### Overall progress: 
![](https://geps.dev/progress/42)

#### Tasks:
- [x] Project Basic Structure (Flask API + Endpoints + kickoff script)
- [ ] XACML/JSON to the PolicyGraph structure (Structure Builder module)
- [ ] Map the XACML basic functions over the PolicyGraph (See: https://en.wikipedia.org/wiki/XACML#Functions)
- [ ] Translate the PolicyGraph to a Solidity Smart Contract (Solidity Policy Builder module)
- [x] Deploy the Smart Contract and retrieve the address (Blockchain Interface module)
- [ ] Register the Policy address to the database (Policy Address DB)
- [x] Integrate with the Keycloak Authorization Server (OAuth or MetaMask)


## Future Discussion
This project developed the Keycloak Middleware, referred to as Auth Middleware in the image,
as an internal module. In the future, this module should be accessible to other ExtremeXP modules,
especially those supporting the [Graphical Editor's](https://github.com/ExtremeXP-VU/ExtremeXP-graphical-editor) backend. There are two options to achieve this:

1. **Integrate into the same project**: Incorporate the translator project as one of the [Graphical Editor's](https://github.com/ExtremeXP-VU/ExtremeXP-graphical-editor) backends. This makes the module locally accessible and simplifies integration.  
2. **Create a standalone project**: Separate the Auth Middleware into its repository, convert it into a library, and make it installable via pip.

### Hints: 
1. [Using Git Submodule or Subtree](https://stackoverflow.com/questions/36554810/how-to-link-folder-from-a-git-repo-to-another-repo)
2. [Creating a Python Library](https://medium.com/analytics-vidhya/how-to-create-a-python-library-7d5aea80cc3f)