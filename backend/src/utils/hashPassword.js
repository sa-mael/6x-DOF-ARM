const bcrypt = require('bcryptjs');

const hashPassword = async (plainPassword) => {
  return await bcrypt.hash(
    plainPassword,
    parseInt(process.env.BCRYPT_ROUNDS)
  );
};

const comparePassword = async (plainPassword, hashedPassword) => {
  return await bcrypt.compare(plainPassword, hashedPassword);
};

module.exports = { hashPassword, comparePassword };
