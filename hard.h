6dof-business-platform/
│
├── backend/                       # BACKEND (API and Business Logic)
│   ├── src/
│   │   ├── config/                # Database and environment configuration
│   │   │   └── db.js              
│   │   ├── controllers/           # Business logic (what happens on request)
│   │   │   ├── authController.js  # Login, registration, token issuance logic
│   │   │   └── contactController.js # Logic for processing investor inquiries
│   │   ├── middlewares/           # SECURITY AND CHECKS (Middleware)
│   │   │   ├── verifyToken.js     # JWT validation (allow or deny access)
│   │   │   ├── rateLimiter.js     # Protection against spam requests (DDoS)
│   │   │   └── errorHandler.js    # Secure error interception
│   │   ├── models/                # Data schemas (e.g., Mongoose for MongoDB)
│   │   │   ├── User.js            # User model (with hashed passwords)
│   │   │   └── Lead.js            # Sponsor/investor inquiry model
│   │   ├── routes/                # API Routing
│   │   │   ├── authRoutes.js      # Endpoints: /api/login, /api/register
│   │   │   └── apiRoutes.js       # Protected endpoints (require token)
│   │   ├── utils/                 # Helper functions
│   │   │   ├── generateToken.js   # Access and Refresh token generation
│   │   │   └── hashPassword.js    # Password hashing via bcrypt
│   │   └── server.js              # Main server entry point (CORS, Helmet setup)
│   ├── .env                       # SECRETS: Tokens (JWT_SECRET), DB passwords (DO NOT PUSH TO GIT!)
│   └── package.json               # Backend dependencies
│
├── frontend/                      # FRONTEND (UI and Interaction)
│   ├── public/                    # Static files
│   │   ├── index.html             # Main HTML file
│   │   └── assets/                # Your 3D renders, blueprints, and icons
│   ├── src/
│   │   ├── api/                   # Backend request configuration
│   │   │   └── axiosClient.js     # Axios setup (automatically attaches JWT to requests)
│   │   ├── components/            # Reusable UI elements
│   │   │   ├── Header.jsx         
│   │   │   ├── Footer.jsx
│   │   │   └── SecureModal.jsx    # Modal window for login/data submission
│   │   ├── pages/                 # Website pages
│   │   │   ├── Home.jsx           # The landing page we just built
│   │   │   ├── Login.jsx          # Authentication page
│   │   │   └── Dashboard.jsx      # PROTECTED PAGE (Accessible only with token)
│   │   ├── context/               # Global state
│   │   │   └── AuthContext.jsx    # Stores user authentication state in memory
│   │   ├── utils/
│   │   │   └── tokenStorage.js    # Secure token storage (localStorage or cookies)
│   │   ├── App.jsx                # Main React component, router setup
│   │   └── main.jsx               # React entry point
│   ├── .env                       # Public variables (e.g., your API URL)
│   └── package.json               # Frontend dependencies
│
├── .gitignore                     # Git exclusions (hides node_modules and .env files)
└── README.md                      # Project documentation and run instructions