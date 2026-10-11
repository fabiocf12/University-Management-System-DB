# Academic Management System API

**Python · Flask · PostgreSQL · SQL/PLpgSQL · JWT**

A REST API for managing university academic data, built with Python, Flask, and PostgreSQL. The project combines relational database operations with JWT authentication and role-based authorization.

Originally developed for a university database course, the project was later revisited to refactor parts of the backend and improve its authentication and authorization mechanisms.

## Overview

The API provides a backend for university management workflows, including user authentication, academic data access, and selected registration and enrollment operations.

The project focuses on:

- **REST API development** using Python and Flask.
- **Relational database management** with PostgreSQL.
- **Direct SQL queries** using `psycopg2`, without an ORM.
- **Authentication and authorization** using JWT and role-based access control.
- **Database logic** implemented through SQL, triggers, and stored procedures.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3 | Backend development |
| Flask | REST API framework |
| PostgreSQL | Relational database |
| psycopg2 | PostgreSQL connectivity |
| SQL / PL/pgSQL | Queries and database-side logic |
| PyJWT | JWT handling |
| python-dotenv | Environment configuration |
| Postman | API testing |

## Key Features

### Authentication and Authorization

- JWT-based user authentication.
- Role-based access control for staff, students, and instructors.
- Flask decorators to validate tokens and restrict access to protected endpoints.
- User identity and role information made available to request handlers through Flask's request context.

The authentication flow returns a JWT that clients can use when accessing protected endpoints.

### Database Integration

- PostgreSQL integration through `psycopg2`.
- SQL queries executed directly from the Python backend.
- Relational schema with entities and relationships for university administration.
- Database-side logic defined through SQL scripts, including triggers and stored procedures.

### Academic Management

The API includes selected operations for user registration, enrollment, and access to academic information. The implemented functionality reflects the current state of the project rather than complete coverage of every originally specified endpoint.

## Authentication

### Login

**Endpoint:** `PUT /dbproj/user`

**Request body:**

```json
{
  "username": "user_name",
  "password": "password"
}
```

**Example response:**

```json
{
  "status": 200,
  "errors": null,
  "results": "<jwt_token>"
}
```

### Using the JWT

Include the returned token in the `Authorization` header of subsequent requests:

```http
Authorization: Bearer <jwt_token>
```

The token contains user-related claims, including the user ID, role, and expiration time.

### Role-Based Access Control

Protected endpoints use decorators such as `@token_required` and `@role_required(...)` to validate authentication and enforce role restrictions.

This approach centralizes access-control logic and reduces duplication across route handlers.

## Database

The database uses a relational model with entities such as:

- `person`, `staff`, `instructor`, and student-related tables.
- `degree`, `course`, and `courseedition`.
- Enrollment and association tables representing relationships between academic entities.

The initialization script defines the database schema and its database-side logic, and inserts a staff user and a small set of sample academic data.

The schema retains parts of the original academic project design, including association tables generated during the modeling process.

## Project Structure

```text
.
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── conceptual_diagram/
│   └── Conceptual_Diagram.json
├── postman/
│   └── University_API_Stubs.postman_collection.json
└── sql_script/
    └── script_init.sql
```

## Getting Started

### Prerequisites

- Python 3
- PostgreSQL
- pip

Postman or another HTTP client is recommended for testing the API.

### 1. Clone the Repository

```bash
git clone https://github.com/fabiocf12/University-Management-System-DB.git
cd University-Management-System-DB
```

Replace the placeholders with your repository URL and directory name.

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
```

### 3. Activate the Virtual Environment

On Windows using PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On Windows using Command Prompt (CMD):

```cmd
.venv\Scripts\activate.bat
```

### 4. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the repository root using `.env.example` as a template:

```dotenv
JWT_SECRET_KEY=your_secret_key
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_database_user
DB_PASSWORD=your_database_password
```

Replace the example values with your local configuration. Use a strong, private JWT secret and do not commit the `.env` file.

### 6. Initialize the Database

Create a PostgreSQL database, then execute `sql_script/script_init.sql` against it.

The script initializes the schema, database-side logic, and sample data. Review the script before running it against any database containing data you want to preserve.

### 7. Run the API

From the repository root, with the virtual environment activated, run:

```bash
python app.py
```

### 8. Test the Endpoints

Import `postman/University_API_Stubs.postman_collection.json` into Postman to access the API request collection.

You can also interact with the API using curl or another HTTP client. For protected endpoints, include a valid JWT in the `Authorization` header.

## Project Status and Limitations

This repository is a learning-focused backend project and is **not production-ready**.

- Core authentication and authorization mechanisms are implemented.
- Selected registration and enrollment operations are available.
- Some originally specified endpoints and complex database interactions remain incomplete.
- Data seeding and consistency across all operations are not fully implemented.

The project is being maintained as a practical exercise in backend development, SQL, relational database design, and API security.

## Background

This project originated as a university assignment focused on databases and distributed systems. It was subsequently revisited to improve selected parts of the backend and consolidate practical experience with Flask, PostgreSQL, SQL, and authentication.

The repository reflects the current implementation and its limitations rather than claiming complete implementation of the original specification.
