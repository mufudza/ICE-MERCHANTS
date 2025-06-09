# Ice Business Management System

A Django-based web application for managing ice production, sales, inventory, expenses, and business analytics for ice merchants.

## Features
- User authentication (login/logout)
- Profile management (profile picture, password change)
- Production and sales tracking
- Inventory management
- Expense tracking and categorization
- Business reports with interactive charts (production, sales, expenses, profit)
- Responsive, modern UI

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js (for frontend assets, if using Vite/Tailwind)
- pip (Python package manager)

### Installation
1. **Clone the repository**
   ```pwsh
   git clone <your-repo-url>
   cd "ICE MERCHANTS"
   ```
2. **Install Python dependencies**
   ```pwsh
   pip install -r requirements.txt
   ```
3. **Apply migrations**
   ```pwsh
   python manage.py migrate
   ```
4. **Create a superuser (admin account)**
   ```pwsh
   python manage.py createsuperuser
   ```
5. **(Optional) Build frontend assets**
   If you modify frontend code (e.g., Tailwind CSS):
   ```pwsh
   npm install
   npm run build
   ```
6. **Run the development server**
   ```pwsh
   python manage.py runserver
   ```
7. **Access the app**
   Open your browser and go to [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Project Structure
- `ice_business/` - Django project settings and URLs
- `inventory/` - Main app: models, views, forms, admin, templates
- `media/` - Uploaded media files (profile pictures, etc.)
- `static/` - Static files (JS, CSS)
- `templates/` - HTML templates
- `src/` - (Optional) Frontend source (if using Vite/React)

## Customization
- Update business logic in `inventory/models.py` and `inventory/views.py`
- Modify UI in `templates/inventory/` and `static/js/`
- Configure static/media paths in `ice_business/settings.py`

## License
MIT License

---

For questions or support, contact the project maintainer.
