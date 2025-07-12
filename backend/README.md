# Hunter Campus Backend

## Overview
This is the backend for the Hunter Campus platform, built with Django and Django REST Framework. It provides APIs for user management, teams, events, tournaments, shop, notifications, messaging, forum, analytics, and more.

## Setup
1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd hunter-campus/backend
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Run migrations:**
   ```sh
   python manage.py migrate
   ```
4. **Create a superuser:**
   ```sh
   python manage.py createsuperuser
   ```
5. **Run the development server:**
   ```sh
   python manage.py runserver
   ```

## API Documentation
- **Swagger/OpenAPI:**
  - [Swagger UI](http://localhost:8000/api/schema/swagger-ui/)
  - [Redoc](http://localhost:8000/api/schema/redoc/)
- All endpoints are documented and grouped by feature.

## Running Tests
- Run all tests:
  ```sh
  python manage.py test
  ```
- Tests cover notifications, messaging, forum, shop, events, and more.

## Key Features
- User registration, login, profile, admin approval
- Teams, tournaments, live brackets, invitations
- Events, calendar aggregation, filtering
- Shop, cosmetics, inventory, purchases
- Notifications (real-time and persistent)
- Messaging (direct, team chat)
- Forum (posts, comments, mentions)
- Analytics dashboard
- Admin tools for approvals and management

## Contribution Guidelines
- Use feature branches for new features or fixes.
- Write tests for new endpoints and business logic.
- Ensure all API responses use DRF serializers.
- Document new endpoints in code and Swagger/OpenAPI.
- Run tests and ensure CI passes before submitting a PR.

## Contact
For questions or contributions, open an issue or contact the maintainers.
