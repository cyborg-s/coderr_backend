# Coderr

**Coderr** is a Django-based Backend for a platform designed for managing offers, orders, user profiles, and reviews. It enables business users to create detailed offers and customers to place orders, leave reviews, and interact with business profiles.

---

## Installation

1. Clone the repository:
    ```bash
   git clone https://github.com/cyborg-s/coderr_backend.git
   cd coderr_backend

2. Create and activate a virtual environment:
    ```bash
    python -m venv env
    env\Scripts\activate (Windows)

3. Install dependencies:
    ```bash
    pip install -r requirements.txt

4. Apply database migrations:
    ```bash
    python manage.py migrate

5. Start the development server:
    ```bash
    python manage.py runserver


## Frontend

1. The frontend is located at 
    https://github.com/cyborg-s/coderr_frontend.git

## Tests

1. This project uses the Django test environment (`unittest`) for automated tests.

### Execute tests

2. Execute the following commands to start the tests:
    python manage.py test or python manage.py test --verbosity=2


## Features

- **User Profiles:** Differentiate between business and customer users with extended profile data including contact details, location, working hours, and profile images.
- **Offers Management:** Business users can create offers with multiple detailed options including pricing, delivery time, revisions, and features.
- **Order System:** Customers can place orders based on offer details. Orders track status (`in_progress`, `completed`, `cancelled`), pricing, and associated users.
- **Reviews:** Customers can leave ratings and reviews on business users. Reviews support filtering, ordering, and ownership validation.
- **Role-based API permissions:** Business users have specific rights to update orders and reviews; staff users can delete orders.
- **REST API:** Fully functioning API endpoints with authentication and permission checks for all main models.

---

## Project Structure Overview

- `users_app/` - user profiles, extended user data and logic for authentication.
- `offers_app/` - Models and APIs for the creation and management of offers.
- `orders_app/` - Logic for order processing, including order creation, updating and status tracking.
- `reviews_app/` - Management of customer reviews with authorizations.
- `auth_app/` - Management of registration and login data.
- `baseinfo_app`- Returns general information about offers and reviews.
- `core/` - Main project settings and configurations.

Translated with www.DeepL.com/Translator (free version)

---

## Models

### UserProfile

- One-to-one extension of Django’s built-in User model.
- Fields for user type (`business` or `customer`), contact info, description, working hours, and profile image.

### Offer & OfferDetail

- `Offer`: Core offer data linked to a business user.
- `OfferDetail`: Multiple detailed offer options linked to a single `Offer`, including price, delivery time, revisions, and features.

### Order

- Links customer and business user through an ordered `OfferDetail`.
- Tracks order status and price.
- Supports order management by business users and staff.

### Review

- Stores customer reviews on business users.
- Supports rating, description, and timestamps.
- Permissions enforced so that only the reviewer can update or delete their review.

---

## API Endpoints

### Authentication & User Profiles

- `GET /api/user_profiles/<user_id>/` — Retrieve user profile.
- `PATCH /api/user_profiles/<user_id>/` — Update user profile (authenticated).
- `GET /api/business_profiles/` — List all business profiles.
- `GET /api/customer_profiles/` — List all customer profiles.

### Offers

- Create, read, update, and delete offers and offer details (business users only).
- Nested JSON support for creating offers with multiple details.

### Orders

- `GET /api/orders/` — List orders for authenticated user (business or customer).
- `POST /api/orders/` — Create order linked to an offer detail.
- `GET /api/orders/<id>/` — Retrieve order detail.
- `PATCH /api/orders/<id>/` — Update order status (business users).
- `DELETE /api/orders/<id>/` — Delete order (staff only).
- Additional endpoints for counting orders by status.

### Reviews

- `GET /api/reviews/` — List all reviews with filtering by business user or reviewer and ordering.
- `POST /api/reviews/` — Create a review (authenticated).
- `GET /api/reviews/<id>/` — Retrieve review detail.
- `PATCH /api/reviews/<id>/` — Update review (only reviewer).
- `DELETE /api/reviews/<id>/` — Delete review (only reviewer).