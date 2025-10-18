# syntax=docker/dockerfile:1.4

##############################
# Stage 1 - Download solc binary
##############################
FROM ubuntu:22.04 as solc-builder

ARG SOLC_VERSION=0.8.18

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && \
    curl -L -o /usr/bin/solc https://github.com/ethereum/solidity/releases/download/v${SOLC_VERSION}/solc-static-linux && \
    chmod +x /usr/bin/solc && \
    solc --version && \
    rm -rf /var/lib/apt/lists/*


################################
# Stage 2 - Python + system solc
################################
FROM --platform=$BUILDPLATFORM python:3.12-alpine AS builder

ARG SOLC_VERSION=0.8.18

WORKDIR /app

# Copy solc binary from Stage 1
COPY --from=solc-builder /usr/bin/solc /usr/bin/solc
COPY --from=solc-builder /usr/bin/solc /usr/bin/solc-v${SOLC_VERSION}

ENV SOLCX_BINARY_PATH=/usr/bin

# Install Python deps
COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

RUN python3 -m solcx.install v${SOLC_VERSION}

# Copy app code
COPY api /app/api
COPY blockchain_interface /app/blockchain_interface
COPY contracts /app/contracts
COPY keycloak_interface /app/keycloak_interface
COPY models /app/models
COPY orgs /app/orgs
COPY parser /app/parser
COPY person /app/person
COPY policy_builder /app/policy_builder
COPY resource /app/resource
COPY structure_builder /app/structure_builder
COPY app.py /app
COPY cli.py /app

EXPOSE $FLASK_AC_APP_PORT

CMD ["python", "app.py"]

##############################
# Stage 3 - Dev environment
##############################
FROM builder as dev-envs

RUN apk update && apk add git

RUN addgroup -S docker && \
    adduser -S --shell /bin/bash --ingroup docker vscode

# install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /

EXPOSE $FLASK_AC_APP_PORT
CMD ["python3", "app.py"]
