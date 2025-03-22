# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

WORKDIR /app

COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY api /app/api
COPY blockchain_interface /app/blockchain_interface
COPY contracts /app/contracts
COPY keycloak_interface /app/keycloak_interface
COPY models /app/models
COPY parser /app/parser
COPY person /app/person
COPY policy_builder /app/policy_builder
COPY structure_builder /app/structure_builder
COPY app.py /app

EXPOSE $FLASK_AC_APP_PORT

CMD ["python", "app.py"]

FROM builder as dev-envs

RUN <<EOF
apk update
apk add git
EOF

RUN <<EOF
addgroup -S docker
adduser -S --shell /bin/bash --ingroup docker vscode
EOF

# install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /
EXPOSE $FLASK_AC_APP_PORT
CMD ["python3", "app.py"]