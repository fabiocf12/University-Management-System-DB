# 🎓 Academic Management System API (Flask + PostgreSQL)

This repository contains a backend REST API developed in Python (Flask) with PostgreSQL, originally created for an academic database project and later partially refactored and improved to better reflect clean architecture, authentication, and authorization practices.

The project focuses mainly on:

Authentication using JWT

Role-based access control

Relational database interaction with SQL

Clear separation of concerns in the backend

⚠️ Note: This project is not fully implemented. Some endpoints and database interactions were intentionally left unfinished, as the main goal of this revision was to improve core backend concepts rather than feature completeness.

🧠 Project Context

This project was initially developed as part of a university course on Databases and Distributed Systems.

Some time after the original submission, the project was revisited voluntarily in order to:

Improve authentication and authorization logic

Refactor poorly designed parts of the original solution

Apply better backend and security practices learned over time

As such, this repository represents a learning-focused refactor, not a production-ready system.

🛠️ Tech Stack

Python 3

Flask

PostgreSQL

psycopg2

JWT (JSON Web Tokens)

🔐 Authentication & Authorization
Login

Users authenticate via JWT:

PUT /dbproj/user


Request body

{
  "username": "user_name",
  "password": "password"
}


Response

{
  "status": 200,
  "errors": null,
  "results": "<jwt_token>"
}


The returned token must be included in subsequent requests.

JWT Usage

The token can be sent using the Authorization header:

Authorization: Bearer <jwt_token>


JWT payload includes:

user_id

role (staff | student | instructor)

expiration time (exp)

Role-Based Access Control

Authorization is enforced using Flask decorators, such as:

token_required

role_required(...)

These decorators:

Validate the JWT

Decode and store user information in flask.g.user

Restrict endpoint access based on user role

This approach avoids code duplication and keeps endpoints clean.

🗄️ Database Design

The database follows a relational model with entities such as:

person

staff

student_financialaccount

instructor

degree, course, courseedition

enrollment and association tables

Some tables were automatically generated from a modeling tool, resulting in:

Long table names

Association tables for many-to-many relationships

While not ideal, the schema was kept mostly intact to remain aligned with the original academic requirements.

📌 Implemented / Partially Implemented Features

✔️ JWT authentication
✔️ Role detection based on relational tables
✔️ Secure access control with decorators
✔️ Database connection handling
✔️ Some registration and enrollment endpoints

❌ Full endpoint coverage
❌ Complete data seeding
❌ Full consistency across all operations

🎓 Academic Management System API (Flask + PostgreSQL)

This repository contains a backend REST API developed in Python (Flask) with PostgreSQL, originally created for an academic database project and later partially refactored and improved to better reflect clean architecture, authentication, and authorization practices.

The project focuses mainly on:

Authentication using JWT

Role-based access control

Relational database interaction with SQL

Clear separation of concerns in the backend

⚠️ Note: This project is not fully implemented. Some endpoints and database interactions were intentionally left unfinished, as the main goal of this revision was to improve core backend concepts rather than feature completeness.

🧠 Project Context

This project was initially developed as part of a university course on Databases and Distributed Systems.

Some time after the original submission, the project was revisited voluntarily in order to:

Improve authentication and authorization logic

Refactor poorly designed parts of the original solution

Apply better backend and security practices learned over time

As such, this repository represents a learning-focused refactor, not a production-ready system.

🛠️ Tech Stack

Python 3

Flask

PostgreSQL

psycopg2

JWT (JSON Web Tokens)

🔐 Authentication & Authorization
Login

Users authenticate via JWT:

PUT /dbproj/user


Request body

{
  "username": "user_name",
  "password": "password"
}


Response

{
  "status": 200,
  "errors": null,
  "results": "<jwt_token>"
}


The returned token must be included in subsequent requests.

JWT Usage

The token can be sent using the Authorization header:

Authorization: Bearer <jwt_token>


JWT payload includes:

user_id

role (staff | student | instructor)

expiration time (exp)

Role-Based Access Control

Authorization is enforced using Flask decorators, such as:

token_required

role_required(...)

These decorators:

Validate the JWT

Decode and store user information in flask.g.user

Restrict endpoint access based on user role

This approach avoids code duplication and keeps endpoints clean.

🗄️ Database Design

The database follows a relational model with entities such as:

person

staff

student_financialaccount

instructor

degree, course, courseedition

enrollment and association tables

Some tables were automatically generated from a modeling tool, resulting in:

Long table names

Association tables for many-to-many relationships

While not ideal, the schema was kept mostly intact to remain aligned with the original academic requirements.

📌 Implemented / Partially Implemented Features

✔️ JWT authentication
✔️ Role detection based on relational tables
✔️ Secure access control with decorators
✔️ Database connection handling
✔️ Some registration and enrollment endpoints

❌ Full endpoint coverage
❌ Complete data seeding
❌ Full consistency across all operations