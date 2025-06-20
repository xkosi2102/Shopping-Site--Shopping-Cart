# Shopping-Site--Shopping-Cart
Python Project 
Flask web app with Jinja2 templates, sessionbased shopping cart, product browsing, checkout form with order persistence, and Docker containerization.

## Overview
LuxShop is a Flask-based e-commerce web application that allows users to browse products, add them to a shopping cart, and place orders. It includes features like user authentication, product filtering, and a checkout process.

## Features
- **Product Listing**: Displays a list of products with filtering and sorting options.
- **Product Details**: Individual product pages with detailed information.
- **Shopping Cart**: Add, update, and remove items from the cart.
- **Checkout**: Place orders with user details and payment method.
- **User Authentication**: Register, login, and logout functionality.
- **Persistent Cart**: User's cart is persistent, if the user logs out, the cart auto-clean all the products saved.
- **Contact Page**: A form for users to send inquiries.

## Structure
- **server.py**: Flask app entrypoint
- **products.py**: Sample product data
- **templates/**: Jinja2 HTML templates
- **static/**: Static assets (css, js, images)
- **Dockerfile**: Docker build instructions
- **requirements.txt**: Flask dependencies

## Running

docker build -t iap1-tema .
docker run -p 5000:5000 iap1-tema


## Bonuses
- Per-product dynamic pages
- User authentication with login/logout and persistent sessions
- Cart autocompletion with logged-in user details
- Product search functionality
- Product filtering by price and category
