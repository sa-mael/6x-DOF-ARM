import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  const navLinks = [
    { to: '/',           label: 'Home' },
    { to: '/technology', label: 'Technology' },
    { to: '/ik-demo',    label: 'IK Demo' },
    { to: '/build-log',  label: 'Build Log' },
    { to: '/preorder',   label: 'Pre-Order' },
  ];

  return (
    <header style={s.header}>
      <div style={s.inner}>

        <Link to="/" style={s.logo}>
          <div style={s.logoDot} />
          6-DOF SYSTEM
        </Link>

        <nav style={s.nav}>
          {navLinks.map(({ to, label }) => (
            <Link key={to} to={to} style={isActive(to) ? s.linkActive : s.link}>
              {label}
            </Link>
          ))}
        </nav>

        <div style={s.authRow}>
          {user ? (
            <>
              <Link to="/dashboard" style={s.userPill}>
                <div style={s.userDot} />
                {user.name}
                <span style={s.roleBadge}>{user.role}</span>
              </Link>
              <button onClick={handleLogout} style={s.btnOutline}>
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login"    style={s.btnOutline}>Login</Link>
              <Link to="/preorder" style={s.btnFill}>Reserve →</Link>
            </>
          )}
        </div>

        <button
          style={s.burger}
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle menu"
        >
          {menuOpen ? '✕' : '☰'}
        </button>
      </div>

      {menuOpen && (
        <div style={s.mobileMenu}>
          {navLinks.map(({ to, label }) => (
            <Link key={to} to={to} style={s.mobileLink} onClick={() => setMenuOpen(false)}>
              {label}
            </Link>
          ))}
          {user ? (
            <button onClick={handleLogout} style={s.mobileLink}>Logout</button>
          ) : (
            <Link to="/login" style={s.mobileLink} onClick={() => setMenuOpen(false)}>Login</Link>
          )}
        </div>
      )}
    </header>
  );
};

const s = {
  header:     { position: 'fixed', top: 0, left: 0, right: 0, zIndex: 1000, height: 72, background: 'rgba(255,255,255,0.88)', backdropFilter: 'blur(12px)', borderBottom: '1px solid #e2e2e2', display: 'flex', alignItems: 'center' },
  inner:      { width: '100%', maxWidth: 1400, margin: '0 auto', padding: '0 48px', display: 'flex', alignItems: 'center', gap: 32 },
  logo:       { display: 'flex', alignItems: 'center', gap: 10, fontFamily: 'Space Mono, monospace', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.08em', textDecoration: 'none', color: '#0e0e0e', whiteSpace: 'nowrap' },
  logoDot:    { width: 7, height: 7, background: '#0047bb', borderRadius: '50%' },
  nav:        { display: 'flex', gap: 28, flex: 1 },
  link:       { fontFamily: 'Space Mono, monospace', fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.12em', textDecoration: 'none', color: '#888' },
  linkActive: { fontFamily: 'Space Mono, monospace', fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.12em', textDecoration: 'none', color: '#0047bb', borderBottom: '2px solid #0047bb', paddingBottom: 2 },
  authRow:    { display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 },
  userPill:   { display: 'flex', alignItems: 'center', gap: 8, fontFamily: 'Space Mono, monospace', fontSize: '0.65rem', textDecoration: 'none', color: '#0e0e0e', background: '#f5f4f1', padding: '6px 12px', borderRadius: 40 },
  userDot:    { width: 6, height: 6, background: '#22c55e', borderRadius: '50%' },
  roleBadge:  { background: '#d6e4ff', color: '#0047bb', fontSize: '0.55rem', padding: '2px 8px', borderRadius: 20, textTransform: 'uppercase', letterSpacing: '0.08em' },
  btnOutline: { fontFamily: 'Space Mono, monospace', fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.1em', textDecoration: 'none', color: '#0e0e0e', background: 'none', border: '1px solid #e2e2e2', padding: '8px 16px', cursor: 'pointer' },
  btnFill:    { fontFamily: 'Space Mono, monospace', fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.1em', textDecoration: 'none', color: '#fff', background: '#0047bb', padding: '8px 16px' },
  burger:     { display: 'none', background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer', marginLeft: 'auto' },
  mobileMenu: { position: 'absolute', top: 72, left: 0, right: 0, background: '#fff', borderBottom: '1px solid #e2e2e2', display: 'flex', flexDirection: 'column', padding: '16px 32px', gap: 16 },
  mobileLink: { fontFamily: 'Space Mono, monospace', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.1em', textDecoration: 'none', color: '#0e0e0e', background: 'none', border: 'none', cursor: 'pointer', textAlign: 'left' },
};

export default Header;
