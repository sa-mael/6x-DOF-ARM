import { Link } from 'react-router-dom';

const Footer = () => (
  <footer style={s.footer}>
    <div style={s.inner}>

      <div style={s.top}>
        <div style={s.tagline}>
          Bridging industrial automation<br />
          with <em style={{ color: '#bda365', fontStyle: 'italic' }}>desktop precision.</em>
        </div>
        <Link to="/preorder" style={s.cta}>Reserve a Unit →</Link>
      </div>

      <div style={s.grid}>
        <div style={s.col}>
          <div style={s.colTitle}>Contact</div>
          <a href="mailto:hello@6dof-system.com"  style={s.colLink}>hello@6dof-system.com</a>
          <a href="mailto:invest@6dof-system.com" style={s.colLink}>invest@6dof-system.com</a>
        </div>
        <div style={s.col}>
          <div style={s.colTitle}>Navigation</div>
          <Link to="/technology" style={s.colLink}>Technology</Link>
          <Link to="/ik-demo"    style={s.colLink}>IK Demo</Link>
          <Link to="/build-log"  style={s.colLink}>Build Log</Link>
          <Link to="/preorder"   style={s.colLink}>Pre-Order</Link>
        </div>
        <div style={s.col}>
          <div style={s.colTitle}>Explore</div>
          <a href="https://github.com" target="_blank" rel="noreferrer" style={s.colLink}>GitHub</a>
          <Link to="/about"  style={s.colLink}>About</Link>
          <Link to="/portal" style={s.colLink}>Partner Portal</Link>
        </div>
        <div style={s.col}>
          <div style={s.colTitle}>Location</div>
          <p style={s.colText}>Strathroy, ON, Canada</p>
          <p style={s.colText}>London, UK</p>
        </div>
      </div>

      <div style={s.bottom}>
        <span>© 2026 6-DOF System</span>
        <span>Industrial Desktop Robotics — Engineered with Precision</span>
        <span>Rev 2.0</span>
      </div>

    </div>
  </footer>
);

const s = {
  footer:   { background: '#0a0a0c', color: '#fff', borderTop: '1px solid #1a1a1a' },
  inner:    { maxWidth: 1400, margin: '0 auto', padding: '72px 48px' },
  top:      { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 56, paddingBottom: 56, borderBottom: '1px solid #1e1e1e' },
  tagline:  { fontFamily: 'DM Serif Display, serif', fontSize: '2.2rem', fontWeight: 400, maxWidth: 480, lineHeight: 1.2, color: '#fff' },
  cta:      { display: 'inline-flex', alignItems: 'center', padding: '14px 28px', background: '#bda365', color: '#000', fontFamily: 'Space Mono, monospace', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.12em', textDecoration: 'none', flexShrink: 0 },
  grid:     { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 48, marginBottom: 48 },
  col:      { display: 'flex', flexDirection: 'column', gap: 10 },
  colTitle: { fontFamily: 'Space Mono, monospace', fontSize: '0.6rem', textTransform: 'uppercase', letterSpacing: '0.15em', color: '#555', marginBottom: 6 },
  colLink:  { color: '#888', fontSize: '0.85rem', textDecoration: 'none', lineHeight: 1.6 },
  colText:  { color: '#888', fontSize: '0.85rem', lineHeight: 1.6 },
  bottom:   { borderTop: '1px solid #1e1e1e', paddingTop: 24, display: 'flex', justifyContent: 'space-between', fontFamily: 'Space Mono, monospace', fontSize: '0.6rem', color: '#444', textTransform: 'uppercase', letterSpacing: '0.1em' },
};

export default Footer;
