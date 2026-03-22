import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const Login = () => {
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const [mode, setMode]       = useState('login');
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');
  const [form, setForm]       = useState({ name: '', email: '', password: '' });

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
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.message || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={s.page}>

      {/* LEFT — branding */}
      <div style={s.left}>
        <div style={s.leftInner}>
          <div style={s.leftNum}>AUTH-01</div>
          <div style={s.leftTitle}>
            Industrial precision<br />
            <em style={{ color: '#bda365', fontStyle: 'italic' }}>starts here.</em>
          </div>
          <div style={s.leftSub}>
            Access the partner portal, track your order,
            and follow the build in real time.
          </div>
          <div style={s.stats}>
            {[['47', 'On Waitlist'], ['13', 'Beta Slots Left'], ['€4,500', 'Kit Price']].map(([n, l]) => (
              <div key={l}>
                <div style={s.statNum}>{n}</div>
                <div style={s.statLabel}>{l}</div>
              </div>
            ))}
          </div>
          <Link to="/preorder" style={s.leftCta}>Reserve a Unit →</Link>
        </div>
      </div>

      {/* RIGHT — form */}
      <div style={s.right}>
        <div style={s.formWrap}>

          <div style={s.tabs}>
            <button style={mode === 'login'    ? s.tabActive : s.tab} onClick={() => { setMode('login');    setError(''); }}>Sign In</button>
            <button style={mode === 'register' ? s.tabActive : s.tab} onClick={() => { setMode('register'); setError(''); }}>Register</button>
          </div>

          <div style={s.formTitle}>
            {mode === 'login' ? 'Welcome back.' : 'Join the build.'}
          </div>

          <form onSubmit={handleSubmit} style={s.form}>
            {mode === 'register' && (
              <div style={s.group}>
                <label style={s.label}>Full Name</label>
                <input name="name" type="text" value={form.name} onChange={handleChange} placeholder="Your name" required style={s.input} />
              </div>
            )}
            <div style={s.group}>
              <label style={s.label}>Email Address</label>
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

          <div style={s.formFooter}>
            {mode === 'login'
              ? <><span>No account? </span><button style={s.switchBtn} onClick={() => setMode('register')}>Register here</button></>
              : <><span>Already registered? </span><button style={s.switchBtn} onClick={() => setMode('login')}>Sign in</button></>
            }
          </div>

        </div>
      </div>

    </div>
  );
};

const s = {
  page:      { display: 'grid', gridTemplateColumns: '1fr 1fr', minHeight: '100vh', paddingTop: 72 },
  left:      { background: '#0a0f1e', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '80px 56px' },
  leftInner: { maxWidth: 440 },
  leftNum:   { fontFamily: 'Space Mono, monospace', fontSize: '0.62rem', textTransform: 'uppercase', letterSpacing: '0.15em', color: '#00c8ff', marginBottom: '1rem' },
  leftTitle: { fontFamily: 'DM Serif Display, serif', fontSize: '3rem', fontWeight: 400, lineHeight: 1.1, color: '#fff', marginBottom: '1.2rem' },
  leftSub:   { color: 'rgba(255,255,255,0.5)', fontSize: '0.92rem', lineHeight: 1.75, marginBottom: '2.5rem' },
  stats:     { display: 'flex', gap: 32, marginBottom: '2.5rem', paddingBottom: '2.5rem', borderBottom: '1px solid rgba(255,255,255,0.08)' },
  statNum:   { fontFamily: 'DM Serif Display, serif', fontSize: '1.8rem', color: '#fff', marginBottom: 4 },
  statLabel: { fontFamily: 'Space Mono, monospace', fontSize: '0.55rem', textTransform: 'uppercase', letterSpacing: '0.12em', color: 'rgba(255,255,255,0.4)' },
  leftCta:   { display: 'inline-flex', alignItems: 'center', padding: '12px 24px', background: '#bda365', color: '#000', fontFamily: 'Space Mono, monospace', fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.12em', textDecoration: 'none' },
  right:     { display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '80px 56px', background: '#faf9f7' },
  formWrap:  { width: '100%', maxWidth: 400 },
  tabs:      { display: 'flex', borderBottom: '1px solid #e2e2e2', marginBottom: 28 },
  tab:       { flex: 1, padding: '10px 0', background: 'none', border: 'none', fontFamily: 'Space Mono, monospace', fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#888', cursor: 'pointer', borderBottom: '2px solid transparent' },
  tabActive: { flex: 1, padding: '10px 0', background: 'none', border: 'none', fontFamily: 'Space Mono, monospace', fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#0047bb', cursor: 'pointer', borderBottom: '2px solid #0047bb' },
  formTitle: { fontFamily: 'DM Serif Display, serif', fontSize: '2rem', fontWeight: 400, marginBottom: 28 },
  form:      { display: 'flex', flexDirection: 'column', gap: 18 },
  group:     { display: 'flex', flexDirection: 'column', gap: 6 },
  label:     { fontFamily: 'Space Mono, monospace', fontSize: '0.6rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#888' },
  input:     { padding: '13px 14px', border: '1px solid #e2e2e2', fontFamily: 'DM Sans, sans-serif', fontSize: '0.92rem', outline: 'none', background: '#fff' },
  error:     { background: '#fff0f0', border: '1px solid #fca5a5', color: '#dc2626', padding: '10px 14px', fontFamily: 'Space Mono, monospace', fontSize: '0.65rem' },
  submit:    { padding: 14, background: '#0047bb', color: '#fff', border: 'none', fontFamily: 'Space Mono, monospace', fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.12em', cursor: 'pointer' },
  formFooter:{ marginTop: 20, fontFamily: 'Space Mono, monospace', fontSize: '0.62rem', color: '#888', textAlign: 'center' },
  switchBtn: { background: 'none', border: 'none', color: '#0047bb', fontFamily: 'Space Mono, monospace', fontSize: '0.62rem', cursor: 'pointer', textDecoration: 'underline' },
};

export default Login;
