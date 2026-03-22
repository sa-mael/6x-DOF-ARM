const express = require('express');
const mongoose = require('mongoose');
const helmet = require('helmet');
const cors = require('cors');
const cookieParser = require('cookie-parser');
const dotenv = require('dotenv');

const connectDB = require('./config/db');
const authRoutes = require('./routes/authRoutes');
const apiRoutes = require('./routes/apiRoutes');
const { globalLimiter } = require('./middlewares/rateLimiter');
const errorHandler = require('./middlewares/errorHandler');

dotenv.config();

const app = express();

// ── SECURITY ──────────────────────────────────────────
app.use(helmet());
app.use(globalLimiter);

// ── CORS ──────────────────────────────────────────────
app.use(
  cors({
    origin: process.env.CLIENT_URL,
    credentials: true,
  })
);

// ── PARSERS ───────────────────────────────────────────
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// ── ROUTES ────────────────────────────────────────────
app.use('/api/auth', authRoutes);
app.use('/api', apiRoutes);

// ── HEALTH CHECK ──────────────────────────────────────
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    environment: process.env.NODE_ENV,
    db: mongoose.connection.readyState === 1 ? 'connected' : 'disconnected',
  });
});

// ── 404 ───────────────────────────────────────────────
app.use((req, res) => {
  res.status(404).json({ message: `Route ${req.originalUrl} not found.` });
});

// ── ERROR HANDLER (must be last) ──────────────────────
app.use(errorHandler);

// ── START ─────────────────────────────────────────────
const PORT = process.env.PORT || 5000;

const start = async () => {
  await connectDB();
  app.listen(PORT, () => {
    console.log(`🚀 Server running on port ${PORT} [${process.env.NODE_ENV}]`);
  });
};

start();
