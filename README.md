
# IS601 Module 11 — SQLAlchemy Calculator Application

**Course:** IS601 — Python for Web API Development  
**Institution:** New Jersey Institute of Technology (NJIT)  
**Student:** Md Navidul Islam  
**Repository:** https://github.com/islamnavid/module11_is601  
**Docker Hub:** https://hub.docker.com/r/navidislam/module11_is601

## 1. Project Overview

This project extends a Python calculator application with SQLAlchemy database models, Pydantic validation, automated testing, and a CI/CD pipeline.

The application uses FastAPI to provide arithmetic operations and PostgreSQL to support database persistence testing.

The project also includes Docker containerization, GitHub Actions automation, and Trivy vulnerability scanning.

### Main Features

- Addition, subtraction, multiplication, and division
- FastAPI REST endpoints
- Request and response validation using Pydantic
- SQLAlchemy database models
- PostgreSQL integration testing
- Unit and integration tests using pytest
- Test coverage reporting using pytest-cov
- Docker containerization
- Automated GitHub Actions CI/CD
- Trivy Docker image security scanning
- Automated Docker Hub image publishing

## 2. Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.11 | Programming language |
| FastAPI | Web API framework |
| SQLAlchemy | Object-relational mapping |
| PostgreSQL | Relational database |
| Pydantic | Data validation and schemas |
| pytest | Automated testing |
| pytest-cov | Code coverage reporting |
| Docker | Containerization |
| GitHub Actions | Continuous integration and deployment |
| Trivy | Container vulnerability scanning |
| Docker Hub | Container image registry |

## 3. Repository Setup

Clone the repository:

```bash
git clone https://github.com/islamnavid/module11_is601.git
cd module11_is601
```

Create a Python virtual environment:

```bash
python3.11 -m venv venv
```

Activate the virtual environment.

macOS/Linux:

```bash
source venv/bin/activate
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## 4. Database Configuration

The application uses SQLAlchemy for database configuration, session management, and ORM models.

The database configuration is implemented in:

```text
app/database.py
```

The module provides:

- A SQLAlchemy engine
- A session factory
- A declarative model base
- A database dependency for session management
- Helper functions for creating engines and session factories

Database connections are configured through the `DATABASE_URL` environment variable.

For local PostgreSQL testing, a Docker container can be started using:

```bash
docker run -d \
  --name module11-test-db \
  -e POSTGRES_USER=module11 \
  -e POSTGRES_PASSWORD=module11password \
  -e POSTGRES_DB=module11_test \
  -p 5433:5432 \
  postgres:16
```

Configure the database URLs on macOS/Linux:

```bash
export DATABASE_URL="postgresql://module11:module11password@localhost:5433/module11_test"
export TEST_DATABASE_URL="postgresql://module11:module11password@localhost:5433/module11_test"
```

These credentials are intended for local development and testing only. Production credentials should be managed securely.

## 5. Running the Application

Start the FastAPI application:

```bash
uvicorn main:app --reload
```

The application is available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

Expected health response:

```json
{
  "status": "healthy"
}
```

## 6. Calculator API Endpoints

The application provides four arithmetic endpoints.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/add` | Adds two numbers |
| POST | `/subtract` | Subtracts two numbers |
| POST | `/multiply` | Multiplies two numbers |
| POST | `/divide` | Divides two numbers |
| GET | `/health` | Application health check |
| GET | `/` | Application homepage |

Example addition request:

```bash
curl -X POST http://127.0.0.1:8000/add \
  -H "Content-Type: application/json" \
  -d '{"a":10,"b":5}'
```

Expected response:

```json
{
  "result": 15.0
}
```

The API validates incoming requests and returns structured error responses for invalid operations.

Division by zero is handled as an error.

## 7. SQLAlchemy Models and Pydantic Schemas

The application includes SQLAlchemy models for calculations and users.

Important files include:

```text
app/models/calculation.py
app/models/user.py
app/schemas/calculation.py
```

SQLAlchemy provides database model definitions and persistence support.

Pydantic provides validation and serialization for calculation-related data.

The application also uses an arithmetic operation factory pattern to organize calculation behavior.

Database model functionality is tested independently from the calculator's existing API endpoints.

## 8. Automated Testing

The project uses pytest for unit and integration testing.

The test suite covers:

- Arithmetic operations
- Invalid inputs and division by zero
- FastAPI request validation
- API error handling
- SQLAlchemy calculation models
- Pydantic schemas
- PostgreSQL database persistence
- Database session lifecycle management
- Database engine and session factory helpers

Run unit and integration tests:

```bash
python -m pytest tests/unit/ tests/integration/ -q
```

Run tests with application-code coverage:

```bash
python -m pytest tests/unit/ tests/integration/ \
  --cov=app \
  --cov=main \
  --cov-report=term-missing \
  --cov-report=html \
  -q
```

Latest verified local results:

```text
94 passed
Application-code coverage: 96%
```

The HTML coverage report is generated in:

```text
htmlcov/index.html
```

The test suite includes real PostgreSQL integration tests to verify database persistence behavior.

## 9. Docker Containerization

The application uses a multi-stage Dockerfile.

The build stage installs dependencies into a Python virtual environment.

The runtime stage copies the installed dependencies and application code into a separate image.

The runtime container:

- Uses Python 3.11
- Runs as a non-root user
- Exposes port 8000
- Includes an HTTP health check
- Removes unnecessary build and packaging components

Build the Docker image:

```bash
docker build -t navidislam/module11_is601:latest .
```

Run the application:

```bash
docker run --rm \
  --name module11-app \
  -p 8001:8000 \
  navidislam/module11_is601:latest
```

Check the health endpoint:

```bash
curl http://localhost:8001/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

Published Docker image:

https://hub.docker.com/r/navidislam/module11_is601

## 10. CI/CD with GitHub Actions

The GitHub Actions workflow is defined in:

```text
.github/workflows/test.yml
```

The pipeline contains three jobs.

### Test

- Starts a PostgreSQL service
- Installs Python dependencies
- Runs unit and integration tests
- Uploads test result artifacts

### Security

- Builds the Docker image
- Runs Trivy vulnerability scanning
- Checks HIGH and CRITICAL vulnerabilities
- Fails the job when qualifying vulnerabilities are detected

### Deploy

- Runs after successful testing and security checks
- Authenticates with Docker Hub using GitHub Actions secrets
- Builds the Docker image
- Pushes the `latest` tag
- Pushes an image tag based on the Git commit SHA

The deployment job runs for pushes to the main branch.

Pull requests run validation without publishing a Docker image.

GitHub Actions:

https://github.com/islamnavid/module11_is601/actions

## 11. Security Scanning

Trivy is used to scan the Docker image for known vulnerabilities.

The security scan focuses on HIGH and CRITICAL severity findings.

The Dockerfile was improved to remove unnecessary packaging tools from the runtime image and reduce vulnerability exposure.

Run a local scan:

```bash
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image \
  --scanners vuln \
  --severity HIGH,CRITICAL \
  --ignore-unfixed \
  navidislam/module11_is601:latest
```

The latest verified local scan reported zero HIGH and zero CRITICAL vulnerabilities under the configured scan settings.

Security scan results can change as vulnerability databases are updated.

## 12. Development and Verification Results

The completed project was verified through:

1. Unit and integration testing
2. Application-code coverage measurement
3. PostgreSQL database integration testing
4. Docker image building
5. Container health checking
6. Trivy vulnerability scanning
7. GitHub Actions CI/CD execution
8. Docker Hub image publishing

Verified local results:

| Check | Result |
|---|---|
| Unit and integration tests | 94 passed |
| Application-code coverage | 96% |
| Database module coverage | 100% |
| Docker image build | Successful |
| Container health check | Successful |
| Trivy HIGH findings | 0 |
| Trivy CRITICAL findings | 0 |

## 13. Scope of Module 11

This module focuses on database models, schemas, testing, and CI/CD automation.

Database-backed BREAD (Browse, Read, Edit, Add, Delete) API endpoints are not implemented as part of this module because they are reserved for Module 12.

## 14. Useful Links

- GitHub Repository: https://github.com/islamnavid/module11_is601
- GitHub Actions: https://github.com/islamnavid/module11_is601/actions
- Docker Hub: https://hub.docker.com/r/navidislam/module11_is601
- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- pytest Documentation: https://docs.pytest.org/
- Trivy Documentation: https://trivy.dev/

## 15. Conclusion

This project demonstrates the integration of SQLAlchemy database models and Pydantic schemas into an existing FastAPI calculator application.

It also demonstrates automated testing, PostgreSQL integration, Docker containerization, vulnerability scanning, and continuous integration and deployment using GitHub Actions.

The completed implementation provides a foundation for the database-backed API functionality planned for the next module.
