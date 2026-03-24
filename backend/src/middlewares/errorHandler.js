const errorHandler = (err, req, res, next) => {
  console.error(`[ERROR] ${err.message}`);

  // Mongoose — invalid ObjectId
  if (err.name === 'CastError') {
    return res.status(400).json({ message: 'Invalid ID format.' });
  }

  // Mongoose — duplicate unique field (e.g. email)
  if (err.code === 11000) {
    const field = Object.keys(err.keyValue)[0];
    return res.status(409).json({ message: `${field} already exists.` });
  }

  // Mongoose — validation error
  if (err.name === 'ValidationError') {
    const messages = Object.values(err.errors).map((e) => e.message);
    return res.status(400).json({ message: messages.join('. ') });
  }

  // JWT — invalid token
  if (err.name === 'JsonWebTokenError') {
    return res.status(401).json({ message: 'Invalid token.' });
  }

  // All other errors
  res.status(err.status || 500).json({
    message:
      process.env.NODE_ENV === 'production'
        ? 'Internal server error.'
        : err.message,
  });
};

module.exports = errorHandler;
