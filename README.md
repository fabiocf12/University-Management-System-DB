# 🎓 Academic Management System API

**Flask · PostgreSQL · JWT**

---

## 📌 Overview

This repository contains a backend REST API developed in **Python (Flask)** with **PostgreSQL**, originally created for an academic database project and later partially refactored and improved.

The refactor focuses on improving architecture, authentication, and authorization, rather than completing all planned features.

> [!CAUTION]
> ### ⚠️ Important
> This project is not fully implemented. Some endpoints and database interactions were intentionally left unfinished.
> The goal of this revision was to strengthen core backend concepts, not feature completeness or production readiness.

---

## 🎯 Main Focus

* 🔐 **Authentication** using JWT
* 🧭 **Role-based access control**
* 🗄️ **Relational database interaction** using SQL
* 🧱 **Clear separation of concerns** in the backend

---

## 🧠 Project Context

This project was initially developed as part of a university course on **Databases and Distributed Systems**.

Some time after the original submission, it was voluntarily revisited in order to:
* Improve authentication and authorization logic
* Refactor poorly designed parts of the original solution
* Apply better backend and security practices learned over time

*As such, this repository represents a learning-focused refactor, not a production-ready system.*

---

## 🛠️ Tech Stack

| Technology | Role |
| :--- | :--- |
| **Python 3** | Core Language |
| **Flask** | Web Framework |
| **PostgreSQL** | Relational Database |
| **psycopg2** | Database Adapter |
| **JWT** | Authentication & Security |

---

## 🔐 Authentication & Authorization

### 🔑 Login
Users authenticate using JWT.

**Endpoint:** `PUT /dbproj/user`

**Request Body:**
json
{
  "username": "user_name",
  "password": "password"
}

**Response:**
json
{
  "status": 200,
  "errors": null,
  "results": "<jwt_token>"
}
[!NOTE] The returned token must be included in subsequent requests.

**🪪 JWT Usage**
The token must be sent in the Authorization header: Authorization: Bearer <jwt_token>

JWT Payload:

user_id
role (staff | student | instructor)
exp (expiration time)

## 🧩 Role-Based Access Control

Authorization is enforced using Flask decorators, such as:

@token_required

@role_required(...)

These decorators validate the JWT, decode and store user information in flask.g.user, and restrict endpoint access based on user role. This approach avoids code duplication and keeps route handlers clean.

**🗄️ Database Design** 
The database follows a relational model with entities such as:

person, staff, student_financialaccount, instructor

degree, course, courseedition

Enrollment and association tables

Note: Some tables were automatically generated from a modeling tool, resulting in long table names and multiple association tables for many-to-many relationships. While not ideal, the schema was kept mostly intact to remain aligned with the original academic requirements.

📌 Implemented / Partially Implemented Features
✅ Implemented
[x] JWT authentication

[x] Role detection based on relational tables

[x] Secure access control with decorators

[x] Database connection handling

[x] Some registration and enrollment endpoints

❌ Not Fully Implemented
[ ] Full endpoint coverage

[ ] Complete data seeding

[ ] Full consistency across all operations

**🧪 Running the Project**
This is an API-only project — there is no frontend. All interactions are performed via HTTP requests, using tools such as:

Postman

curl

Insomnia

Basic Steps
Create a PostgreSQL database.

Apply the provided SQL schema.

Configure database credentials and JWT secret.

Run the Flask application.

Interact with the API using an API client.