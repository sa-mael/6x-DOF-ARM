import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const SecureModal = ({ isOpen, onClose, defaultMode = 'login' }) => {
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const [mode, setMode]       = useState(defaultMode);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');
  const [form, setForm]       = useState({ name: '', email: '', password: '' });

  if (!isOpen) return null;

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      if (mode === 'login') await login(form.email, form.password);
      else await register(form.name, form.email, form.password);
      onClose();
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.message || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div style={s.backdrop} onClick={onClose} />
      <div style={s.modal}>

        <div style={s.header}>
          <div style={s.title}>{mode === 'login' ? 'Sign In' : 'Create Account'}</div>
          <button onClick={onClose} style={s.close}>✕</button>
        </div>

        <div style={s.tabs}>
          <button style={mode === 'login'    ? s.tabActive : s.tab} onClick={() => { setMode('login');    setError(''); }}>Login</button>
          <button style={mode === 'register' ? s.tabActive : s.tab} onClick={() => { setMode('register'); setError(''); }}>Register</button>
        </div>

        <form onSubmit={handleSubmit} style={s.form}>
          {mode === 'register' && (
            <div style={s.group}>
              <label style={s.label}>Full Name</label>
              <input name="name" type="text" value={form.name} onChange={handleChange} placeholder="Your name" required style={s.input} />
            </div>
          )}
          <div style={s.group}>
            <label style={s.label}>Email</label>
            <input name="email" type="email" value={form.email} onChange={handleChange} placeholder="engineer@company.com" required style={s.input} />
          </div>
          <div style={s.group}>
            <label style={s.label}>Password</label>
            <input name="password" type="password" value={form.password} onChange={handleChange} placeholder="••••••••" required minLength={8} style={s.input} />
          </div>
          {error && <div style={s.error}>{error}</div>}
          <button type="submit" disabled={loading} style={{ ...s.submit, opacity: loading ? 0.7 : 1 }}>
            {loading ? 'Please wait...' : mode === 'login' ? 'Sign In →' : 'Create Account →'}
          </button>
        </form>

      </div>
    </>
  );
};

const s = {
  backdrop: { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1100, backdropFilter: 'blur(4px)' },
  modal:    { position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', zIndex: 1200, background: '#fff', width: '100%', maxWidth: 440, padding: 40, boxShadow: '0 32px 80px rgba(0,0,0,0.15)' },
  header:   { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 },
  title:    { fontFamily: 'DM Serif Display, serif', fontSize: '1.6rem', fontWeight: 400 },
  close:    { background: 'none', border: 'none', fontSize: '1rem', cursor: 'pointer', color: '#888' },
  tabs:     { display: 'flex', borderBottom: '1px solid #e2e2e2', marginBottom: 24 },
  tab:      { flex: 1, padding: '10px 0', background: 'none', border: 'none', fontFamily: 'Space Mono, monospace', fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#888', cursor: 'pointer', borderBottom: '2px solid transparent' },
  tabActive:{ flex: 1, padding: '10px 0', background: 'none', border: 'none', fontFamily: 'Space Mono, monospace', fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#0047bb', cursor: 'pointer', borderBottom: '2px solid #0047bb' },
  form:     { display: 'flex', flexDirection: 'column', gap: 18 },
  group:    { display: 'flex', flexDirection: 'column', gap: 6 },
  label:    { fontFamily: 'Space Mono, monospace', fontSize: '0.6rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#888' },
  input:    { padding: '12px 14px', border: '1px solid #e2e2e2', fontFamily: 'DM Sans, sans-serif', fontSize: '0.9rem', outline: 'none', background: '#faf9f7' },
  error:    { background: '#fff0f0', border: '1px solid #fca5a5', color: '#dc2626', padding: '10px 14px', fontFamily: 'Space Mono, monospace', fontSize: '0.65rem' },
  submit:   { padding: 14, background: '#0047bb', color: '#fff', border: 'none', fontFamily: 'Space Mono, monospace', fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.12em', cursor: 'pointer' },
};

export default SecureModal;
