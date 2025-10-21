# ExtremeXP Access Control API Documentation

## Overview
ExtremeXP Access Control is a modular system for managing access policies, user authentication, and resource authorization using blockchain and Keycloak integration. It provides RESTful endpoints for policy evaluation, resource management, and organizational access control.

## Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd ExtremeXPAccessControl
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Use Docker:
   ```bash
   docker-compose up --build
   ```

## Usage

Start the API server:
```bash
python app.py
```

## Main Endpoints

### 1. Policy Evaluation
- **POST /api/evaluate**
  - **Description:** Evaluate access policy for a user and resource.
  - **Body:**
    - `user_id` (string): User identifier
    - `resource_id` (string): Resource identifier
    - `action` (string): Action to evaluate (e.g., "read", "write")
  - **Response:**
    - `result` (bool): Access granted or denied
    - `details` (object): Evaluation details

### 2. Resource Management
- **GET /api/resources**
  - **Description:** List all resources
  - **Response:** Array of resource objects

- **POST /api/resources**
  - **Description:** Create a new resource
  - **Body:**
    - `name` (string): Resource name
    - `type` (string): Resource type
  - **Response:** Resource object

### 3. Organization Access
- **GET /api/orgs**
  - **Description:** List organizations
  - **Response:** Array of organization objects

- **POST /api/orgs/access**
  - **Description:** Check user access to organization
  - **Body:**
    - `user_id` (string): User identifier
    - `org_id` (string): Organization identifier
  - **Response:**
    - `has_access` (bool): Access status

## Authentication

Authentication is managed via Keycloak. Configure Keycloak settings in `api/settings.py`.

## Error Handling

Errors are returned as JSON objects with an `error` field and appropriate HTTP status code.

## Example Request

```bash
curl -X POST http://localhost:8000/api/evaluate \
     -H "Content-Type: application/json" \
     -d '{"user_id": "user123", "resource_id": "res456", "action": "read"}'
```

## OpenAPI Documentation

To generate and serve OpenAPI documentation:

1. Write your OpenAPI spec (e.g., `openapi.yaml`).
2. Install OpenAPI Generator:
   ```bash
   npm install @openapitools/openapi-generator-cli -g
   ```
3. Generate HTML docs:
   ```bash
   openapi-generator-cli generate -i openapi.yaml -g html -o docs/
   ```
4. Commit the generated HTML files to the `docs/` folder.
5. Enable GitHub Pages in repository settings, pointing to the `docs/` folder.

---

For more details, see the source code and contract files in the `contracts/` directory.

