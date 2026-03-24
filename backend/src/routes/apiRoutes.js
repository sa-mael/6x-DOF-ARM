const express = require('express');
const router = express.Router();
const { verifyToken, requireRole } = require('../middlewares/verifyToken');
const { createLead, getAllLeads, updateLeadStatus } = require('../controllers/contactController');

// ── PUBLIC ────────────────────────────────────────────

// POST /api/contact
router.post('/contact', createLead);

// ── PROTECTED ─────────────────────────────────────────

// GET /api/dashboard
router.get(
  '/dashboard',
  verifyToken,
  requireRole('user', 'partner', 'admin'),
  (req, res) => {
    res.status(200).json({
      message: `Welcome, ${req.user.role}.`,
      userId: req.user.id,
    });
  }
);

// GET /api/leads — admin only
router.get(
  '/leads',
  verifyToken,
  requireRole('admin'),
  getAllLeads
);

// PUT /api/leads/:id — admin only
router.put(
  '/leads/:id',
  verifyToken,
  requireRole('admin'),
  updateLeadStatus
);

module.exports = router;
