# 6-DOF Business Platform

Full-stack web platform for the 6-DOF robotic arm project.
Built in public. Engineered with precision.

---

## Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| Frontend | React 18 + Vite + React Router v6   |
| Backend  | Node.js + Express                   |
| Database | MongoDB + Mongoose                  |
| Auth     | JWT (Access + Refresh tokens)       |
| Security | Helmet, CORS, bcryptjs, Rate limit  |

---

## Project Structure

```
6dof-platform/
├── backend/
│   ├── src/
│   │   ├── config/
│   │   │   └── db.js                  # MongoDB connection
│   │   ├── controllers/
│   │   │   ├── authController.js      # Register, login, refresh, logout
│   │   │   └── contactController.js   # Lead creation and CRM
│   │   ├── middlewares/
│   │   │   ├── verifyToken.js         # JWT validation + role guard
│   │   │   ├── rateLimiter.js         # DDoS protection
│   │   │   └── errorHandler.js        # Centralised error handling
│   │   ├── models/
│   │   │   ├── User.js                # User schema (hashed passwords)
│   │   │   └── Lead.js                # Investor / pre-order lead schema
│   │   ├── routes/
│   │   │   ├── authRoutes.js          # /api/auth/*
│   │   │   └── apiRoutes.js           # /api/* (protected + public)
│   │   ├── utils/
│   │   │   ├── generateToken.js       # Access + refresh token generation
│   │   │   └── hashPassword.js        # bcrypt helpers
│   │   └── server.js                  # Entry point
│   ├── .env.example
│   └── package.json
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── api/
│   │   │   └── axiosClient.js         # Axios + auto JWT + refresh queue
│   │   ├── components/
│   │   │   ├── Header.jsx
│   │   │   ├── Footer.jsx
│   │   │   └── SecureModal.jsx        # Login / register modal
│   │   ├── context/
│   │   │   └── AuthContext.jsx        # Global auth state
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Login.jsx
│   │   │   └── Dashboard.jsx          # Protected (user / partner / admin)
│   │   ├── utils/
│   │   │   └── tokenStorage.js        # In-memory token (XSS safe)
│   │   ├── App.jsx                    # Router + protected routes
│   │   └── main.jsx                   # React entry point
│   ├── .env.example
│   ├── vite.config.js
│   └── package.json
│
├── .gitignore
└── README.md
```

---

## Quick Start

### 1. Clone

```bash
git clone https://github.com/your-username/6dof-platform.git
cd 6dof-platform
```

### 2. Backend

```bash
cd backend
npm install
cp .env.example .env
# Edit .env — add MONGO_URI and generate JWT secrets
npm run dev
```

Generate JWT secrets:

```bash
node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
```

### 3. Frontend

```bash
cd ../frontend
npm install
cp .env.example .env
npm run dev
```

### 4. Open

```
http://localhost:5173
```

Health check:

```bash
curl http://localhost:5000/health
```

---

## API Reference

### Auth — `/api/auth`

| Method | Endpoint    | Auth   | Description          |
|--------|-------------|--------|----------------------|
| POST   | `/register` | Public | Create account       |
| POST   | `/login`    | Public | Sign in              |
| POST   | `/refresh`  | Cookie | Refresh access token |
| POST   | `/logout`   | Cookie | Sign out             |

### API — `/api`

| Method | Endpoint     | Auth       | Description        |
|--------|--------------|------------|--------------------|
| POST   | `/contact`   | Public     | Submit lead/order  |
| GET    | `/dashboard` | Any role   | Protected page     |
| GET    | `/leads`     | Admin only | List all leads     |
| PUT    | `/leads/:id` | Admin only | Update lead status |

---

## Security Model

```
Access Token  → memory only (never localStorage) → 15 min
Refresh Token → httpOnly cookie (JS cannot read) → 7 days
Passwords     → bcrypt (12 rounds)
Rate limiting → 100 req / 15 min (global)
               10 req / 15 min (auth routes)
```

---

## Environment Variables

### Backend (`backend/.env`)

| Variable                 | Description                     |
|--------------------------|---------------------------------|
| `PORT`                   | Server port (default 5000)      |
| `NODE_ENV`               | `development` or `production`   |
| `MONGO_URI`              | MongoDB Atlas connection string |
| `JWT_SECRET`             | Access token secret (64+ chars) |
| `JWT_EXPIRES_IN`         | Access token lifetime (`15m`)   |
| `JWT_REFRESH_SECRET`     | Refresh token secret (64+ chars)|
| `JWT_REFRESH_EXPIRES_IN` | Refresh token lifetime (`7d`)   |
| `BCRYPT_ROUNDS`          | bcrypt work factor (12)         |
| `CLIENT_URL`             | Frontend URL for CORS           |

### Frontend (`frontend/.env`)

| Variable        | Description          |
|-----------------|----------------------|
| `VITE_API_URL`  | Backend API base URL |

---

## Git Rules

```
NEVER commit:
  .env files
  node_modules/
  Any secrets or API keys
```

---

## Roadmap

- [x] Backend — Auth + JWT + MongoDB
- [x] Backend — Lead / CRM model
- [x] Frontend — React + Vite
- [x] Frontend — Auth context + protected routes
- [x] Frontend — Dashboard with CRM (admin)
- [ ] Email notifications on new lead
- [ ] Password reset flow
- [ ] Stripe deposit integration (€200)
- [ ] Deploy — Railway (backend) + Vercel (frontend)

---

## License

Private — All rights reserved.
© 2026 6-DOF System
