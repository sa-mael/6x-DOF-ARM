const mongoose = require('mongoose');

const leadSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: [true, 'Name is required'],
      trim: true,
    },
    email: {
      type: String,
      required: [true, 'Email is required'],
      lowercase: true,
      trim: true,
    },
    organisation: {
      type: String,
      trim: true,
    },
    type: {
      type: String,
      enum: ['investor', 'partner', 'preorder', 'waitlist'],
      required: true,
    },
    config: {
      type: String,
      enum: ['kit', 'assembled', 'v2', 'waitlist'],
      default: 'waitlist',
    },
    message: {
      type: String,
      trim: true,
      maxlength: [1000, 'Message too long'],
    },
    status: {
      type: String,
      enum: ['new', 'contacted', 'qualified', 'closed'],
      default: 'new',
    },
  },
  { timestamps: true }
);

module.exports = mongoose.model('Lead', leadSchema);
