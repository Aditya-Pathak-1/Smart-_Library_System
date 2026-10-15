# Smart Library System

A modern, full-stack library management system built with React, FastAPI, PostgreSQL, and Tailwind CSS.

## Features

### Dashboard
- Real-time statistics: total books, available books, issued books, members, overdue books, fines
- Interactive charts: issue/return activity, popular categories
- Recent activity feed
- Overdue books alert

### Book Management
- Complete CRUD operations for books, authors, categories
- Search and filter by title, author, ISBN, category, availability, publication year
- Pagination and sorting
- Book copies management
- Availability badges (Available, Limited Copies, Unavailable)
- Cover image support

### Member Management
- Member registration with unique member ID generation
- Membership types: Standard, Premium, Student, Senior Citizen
- Status tracking: Active, Inactive, Suspended, Expired
- Borrowing history and current transactions
- Fine tracking per member

### Issue & Return
- Book issuing with member eligibility checks
- Automatic due date calculation
- Book returns with fine calculation
- Book renewals (configurable limits)
- Overdue status updates

### Fine Management
- Automatic fine calculation based on overdue days
- Configurable fine per day and grace period
- Payment recording with receipt generation
- Partial payments support
- Fine status tracking: Pending, Partial, Paid, Waived

### Reports
- Book inventory report
- Currently issued books report
- Overdue books report
- Member activity report
- Fine collection report
- Most borrowed books report
- CSV export for all reports
- Date range filtering

### Settings
- Library information (name, address, contact)
- Circulation rules (borrowing days, fine per day, max books, renewals)
- Notification settings
- Appearance and localization (currency, date format, timezone)

### Authentication & Authorization
- JWT-based authentication with access and refresh tokens
- Role-based access control:
  - **Admin**: Full system access
  - **Librarian**: Books, members, circulation, fines, reports
  - **Member**: Profile, personal transactions, fines
- Administrators can temporarily view the app as an active librarian/staff or member account from the account menu. While impersonating, administrator-only access is blocked; use the banner at the top of the page to return to the administrator account.

## Tech Stack

### Frontend
- React 18 with TypeScript
- Vite for fast development
- Tailwind CSS for styling
- shadcn/ui component library
- Recharts for data visualization
- React Hook Form + Zod for validation
- TanStack Query for data fetching
- React Router for navigation
- Lucide React for icons

### Backend
- FastAPI (Python 3.11+)
- SQLAlchemy 2.0 with async support
- PostgreSQL with asyncpg
- Alembic for migrations
- Pydantic v2 for validation
- python-jose for JWT
- passlib for password hashing

## Project Structure

```
smart-library-system/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # API routes
│   │   ├── core/                # Config, security
│   │   ├── db/                  # Database session, base
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   └── main.py              # FastAPI app
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Pytest tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── contexts/            # React contexts
│   │   ├── pages/               # Page components
│   │   ├── services/            # API services
│   │   ├── types/               # TypeScript types
│   │   ├── lib/                 # Utilities
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Or: Python 3.11+, Node.js 18+, PostgreSQL 14+

### Using Docker (Recommended)

```bash
cd smart-library-system
docker compose up --build -d
```

This starts:
- PostgreSQL on port 5432
- Backend API on port 8001 (mapped to port 8000 inside the container)
- Frontend on port 5173

Access the application at http://localhost:5173

The frontend uses `http://localhost:8001` for API requests when started with
Docker Compose. Check the backend at http://localhost:8001/health and open the
API documentation at http://localhost:8001/docs.

To load the demo accounts and sample library data into an empty database, run:

```bash
docker compose exec -w /app backend env PYTHONPATH=/app python scripts/seed.py
```

After seeding, sign in with one of the accounts in the Default Credentials
table below. The dashboard, catalog, member, circulation, fine, report, and
settings pages require a signed-in user.

### Manual Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Seed database (optional)
python scripts/seed.py

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install

# Set up environment
echo "VITE_API_URL=http://localhost:8000" > .env

# Start dev server
npm run dev
```

## Default Credentials

After seeding the database:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@library.com | admin123 |
| Librarian | librarian@library.com | librarian123 |
| Member | john.doe@email.com | member123 |
| Member | jane.smith@email.com | member123 |

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8001/docs (Docker Compose) or http://localhost:8000/docs (manual setup)
- ReDoc: http://localhost:8001/redoc (Docker Compose) or http://localhost:8000/redoc (manual setup)

## Configuration

### Backend Environment Variables (.env)

```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DEBUG=true
ENVIRONMENT=development

# Library defaults
DEFAULT_BORROWING_DAYS=14
DEFAULT_FINE_PER_DAY=5.00
MAX_BOOKS_PER_MEMBER=5
```

### Frontend Environment Variables (.env)

```env
VITE_API_URL=http://localhost:8000
```

For Docker Compose, use `http://localhost:8001` instead; `backend` is a
container-only hostname and cannot be resolved by the browser.

## Database Schema

Key tables:
- `users` - Authentication and roles
- `categories` - Book categories
- `authors` - Book authors
- `books` - Book catalog
- `book_copies` - Individual book copies
- `members` - Library members
- `issue_transactions` - Book issue/return records
- `fines` - Overdue fines
- `fine_payments` - Payment records
- `library_settings` - System configuration

## Testing

### Backend Tests
```bash
cd backend
# Requires test database
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## Development

### Code Style
- Backend: Ruff for linting, MyPy for type checking
- Frontend: ESLint, TypeScript strict mode

### Adding New Features
1. Create database migration: `alembic revision --autogenerate -m "description"`
2. Add models, schemas, services
3. Create API endpoints
4. Build frontend components
5. Add tests

## Deployment

### Production Checklist
- [ ] Set strong SECRET_KEY
- [ ] Use production PostgreSQL
- [ ] Configure CORS origins
- [ ] Set DEBUG=false
- [ ] Use HTTPS
- [ ] Configure reverse proxy (nginx)
- [ ] Set up database backups
- [ ] Configure monitoring

### Docker Production Build
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - feel free to use for your college project or any purpose.

## Support

For issues and questions, please open a GitHub issue.