# 🩸 BloodDrop - Blood Donation Management System

A modern, full-stack blood donation management system that connects blood donors with patients in need. Built with Django REST Framework and vanilla JavaScript.

![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)
![Django](https://img.shields.io/badge/django-5.0+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🌟 Features

### For Donors
- 🔐 **User Registration & Authentication** - Secure account creation with profile management
- 🩸 **Donor Profile** - Track blood group, donation history, and eligibility
- 🔔 **Smart Notifications** - Get notified when someone nearby needs your blood type
- 📊 **Personal Dashboard** - View donation history, requests, and impact statistics
- ✅ **Eligibility Tracking** - Automatic 56-day donation interval tracking

### For Requesters
- 🚨 **Emergency Requests** - Submit urgent blood requests with priority levels
- 🔍 **Find Donors** - Search for compatible donors by blood group and location
- 📍 **Location-based Matching** - Find donors in your city
- 📞 **Direct Contact** - Get donor contact information (login required)

### For Admins
- 👥 **Donor Management** - View and manage all registered donors
- 📋 **Request Management** - Monitor and update blood request statuses
- 🏥 **Inventory Management** - Track blood bank inventory by blood group
- 📈 **Analytics Dashboard** - View system-wide statistics and trends

### Technical Features
- ✨ **Blood Compatibility Matching** - Automatic compatible blood group detection
- 🎯 **Smart Notifications** - Notify only compatible donors in the same city
- 📱 **Responsive Design** - Works seamlessly on mobile, tablet, and desktop
- 🎨 **Modern UI** - Glassmorphism design with smooth animations
- 🔒 **Secure** - CSRF protection, session authentication, input validation

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd BloodDonation
```

2. **Install backend dependencies**
```bash
cd server
pip install -r requirements.txt
```

3. **Run migrations**
```bash
python manage.py migrate
```

4. **Create a superuser (admin)**
```bash
python manage.py createsuperuser
```

5. **Start the Django server**
```bash
python manage.py runserver
```

6. **Start the client server** (in a new terminal)
```bash
cd client
python -m http.server 5500
```

7. **Access the application**
- Frontend: http://localhost:5500/
- Backend API: http://127.0.0.1:8000/api/
- Admin Panel: http://127.0.0.1:8000/admin/

## 📁 Project Structure

```
BloodDonation/
├── server/                 # Django backend
│   ├── api/               # Main API app
│   │   ├── models.py      # Database models
│   │   ├── views.py       # API endpoints
│   │   ├── serializers.py # Data serializers
│   │   ├── urls.py        # API routes
│   │   └── utils.py       # Helper functions
│   ├── bloodbank/         # Project settings
│   ├── db.sqlite3         # SQLite database
│   └── requirements.txt   # Python dependencies
│
├── client/                # Frontend
│   ├── css/
│   │   └── styles.css     # All styles
│   ├── js/
│   │   ├── api.js         # API client
│   │   ├── auth.js        # Authentication
│   │   ├── home.js        # Home page
│   │   ├── dashboard.js   # Dashboard
│   │   ├── find-blood.js  # Donor search
│   │   ├── request-blood.js # Blood requests
│   │   └── admin.js       # Admin panel
│   ├── index.html         # Home page
│   ├── login.html         # Login page
│   ├── register.html      # Registration
│   ├── dashboard.html     # User dashboard
│   ├── find-blood.html    # Find donors
│   ├── request-blood.html # Request blood
│   └── admin-panel.html   # Admin panel
│
└── README.md
```

## 🔌 API Endpoints

### Authentication
- `POST /api/register/` - Register new user
- `POST /api/login/` - Login
- `POST /api/logout/` - Logout
- `GET /api/auth/check/` - Check auth status

### Profile
- `GET /api/profile/` - Get user profile
- `PUT /api/profile/` - Update profile

### Donors
- `GET /api/donors/` - Search donors (filters: blood_group, city, available)

### Blood Requests
- `GET /api/requests/` - List requests
- `POST /api/requests/` - Create request
- `GET /api/requests/<id>/` - Get request
- `PUT /api/requests/<id>/` - Update request

### Donations
- `GET /api/donations/` - List donations
- `POST /api/donations/` - Record donation

### Notifications
- `GET /api/notifications/` - List notifications
- `PUT /api/notifications/<id>/read/` - Mark as read
- `PUT /api/notifications/read-all/` - Mark all as read

### Statistics
- `GET /api/stats/` - Get dashboard stats

### Admin (requires staff permission)
- `GET /api/admin/donors/` - List all donors
- `GET /api/admin/requests/` - List all requests
- `PUT /api/admin/inventory/<blood_group>/` - Update inventory

## 🎨 Blood Compatibility

The system automatically matches compatible blood types:

| Recipient | Can Receive From |
|-----------|------------------|
| A+ | A+, A-, O+, O- |
| A- | A-, O- |
| B+ | B+, B-, O+, O- |
| B- | B-, O- |
| AB+ | All blood types (Universal Recipient) |
| AB- | AB-, A-, B-, O- |
| O+ | O+, O- |
| O- | O- (Universal Donor) |

## 🔒 Security Features

- CSRF protection on all POST/PUT/DELETE requests
- Session-based authentication
- Password validation (minimum 6 characters)
- Admin-only endpoints protected
- Input validation and sanitization
- CORS configuration for cross-origin requests

## 📱 Screenshots

### Home Page
Modern landing page with live statistics and urgent blood requests.

### Dashboard
Personal dashboard showing donation history, eligibility status, and notifications.

### Find Donors
Search for compatible blood donors with advanced filtering.

### Admin Panel
Comprehensive admin interface for managing donors, requests, and inventory.

## 🛠️ Technology Stack

### Backend
- **Django 5.0+** - Web framework
- **Django REST Framework 3.15+** - API framework
- **django-cors-headers** - CORS handling
- **SQLite** - Database (development)

### Frontend
- **Vanilla JavaScript** - No frameworks, pure JS
- **HTML5 & CSS3** - Modern web standards
- **Fetch API** - HTTP requests
- **CSS Grid & Flexbox** - Responsive layouts

## 📊 Database Models

- **UserProfile** - Extended user information for donors
- **BloodRequest** - Blood request submissions
- **Donation** - Donation records
- **Notification** - User notifications
- **BloodInventory** - Blood bank inventory
- **ContactMessage** - Contact form submissions

## 🚀 Production Deployment

See [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) for detailed deployment instructions.

### Key Steps:
1. Change `SECRET_KEY` in settings.py
2. Set `DEBUG = False`
3. Configure `ALLOWED_HOSTS`
4. Switch to PostgreSQL/MySQL
5. Set up Gunicorn + Nginx
6. Configure HTTPS/SSL
7. Set up monitoring and logging

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Developer

Built with ❤️ for saving lives.

## 📞 Support

For support, email support@blooddrop.org or create an issue in the repository.

---

**Remember:** Every donation can save up to 3 lives. Be a hero! 🦸‍♂️
