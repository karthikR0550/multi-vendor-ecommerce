# Multi-Vendor E-Commerce Platform

A full-stack Multi-Vendor E-Commerce Web Application developed using **Django REST Framework and React**.

## Project Overview

This platform allows multiple shop owners to manage their own shops and products while customers can browse products, place orders, and track deliveries. An administrator manages platform activities, shop approvals, users, and delivery assignments.

## Technologies Used

**Backend**
- Python
- Django
- Django REST Framework
- PostgreSQL
- JWT Authentication

**Frontend**
- React.js
- JavaScript
- HTML
- CSS
- Axios

**Tools**
- Git and GitHub
- Visual Studio Code
- pgAdmin 4

## Main Features

### 1. Customer Module
- User registration and login
- Browse products and shops
- Add products to cart
- Place orders
- View order history
- Track order status

### 2. Shop Owner Module
- Shop registration
- Manage shop information
- Add, update and manage products
- View incoming orders
- Accept and pack orders

### 3. Admin Module
- Admin dashboard
- Manage users and shops
- Approve or reject shop registrations
- Manage products and orders
- Assign delivery personnel

### 4. Delivery Module
- View assigned deliveries
- Update delivery status
- Track order progress through pickup, out for delivery and delivered stages

## Project Structure

```text
multi-vendor-ecommerce/
│
├── backend/
│   ├── apps/
│   ├── config/
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── .gitignore
└── README.md
```

## Installation and Setup

### Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file using `.env.example` and configure your database credentials.

Run migrations:

```bash
python manage.py migrate
```

Start the Django server:

```bash
python manage.py runserver
```

### Frontend Setup

Open another terminal:

```bash
cd frontend

npm install

npm run dev
```

## Application Access

- Backend: http://127.0.0.1:8000/
- Frontend: Use the local URL displayed by Vite in your terminal.

## Project Purpose

This project was developed to gain practical experience in full-stack web development, REST API integration, database management, authentication, role-based access control, and e-commerce order management.

## Author

**Karthik R Nair**

GitHub: https://github.com/karthikR0550