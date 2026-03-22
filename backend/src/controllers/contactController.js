const Lead = require('../models/Lead');

// POST /api/contact — public, creates a new lead
const createLead = async (req, res, next) => {
  try {
    const { name, email, organisation, type, config, message } = req.body;

    if (!name || !email || !type) {
      return res.status(400).json({ message: 'Name, email and type are required.' });
    }

    const lead = await Lead.create({ name, email, organisation, type, config, message });

    res.status(201).json({
      message: 'Thank you. We will be in touch shortly.',
      leadId: lead._id,
    });
  } catch (error) {
    next(error);
  }
};

// GET /api/leads — admin only
const getAllLeads = async (req, res, next) => {
  try {
    const { type, status } = req.query;

    const filter = {};
    if (type) filter.type = type;
    if (status) filter.status = status;

    const leads = await Lead.find(filter).sort({ createdAt: -1 });

    res.status(200).json({ count: leads.length, leads });
  } catch (error) {
    next(error);
  }
};

// PUT /api/leads/:id — admin only
const updateLeadStatus = async (req, res, next) => {
  try {
    const { id } = req.params;
    const { status } = req.body;

    const validStatuses = ['new', 'contacted', 'qualified', 'closed'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json({ message: 'Invalid status.' });
    }

    const lead = await Lead.findByIdAndUpdate(
      id,
      { status },
      { new: true, runValidators: true }
    );

    if (!lead) {
      return res.status(404).json({ message: 'Lead not found.' });
    }

    res.status(200).json({ message: 'Status updated.', lead });
  } catch (error) {
    next(error);
  }
};

module.exports = { createLead, getAllLeads, updateLeadStatus };
