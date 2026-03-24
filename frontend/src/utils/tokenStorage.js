// Access token lives in memory only — never in localStorage
// This protects against XSS attacks
let accessToken = null;

const tokenStorage = {
  get: () => accessToken,
  set: (token) => { accessToken = token; },
  clear: () => { accessToken = null; },
};

export default tokenStorage;
