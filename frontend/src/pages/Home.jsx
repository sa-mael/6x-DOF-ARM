import { useState } from 'react';
import { Link } from 'react-router-dom';
import SecureModal from '../components/SecureModal';

const Home = () => {
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <div style={s.page}>

      {/* HERO */}
      <section style={s.hero}>
        <div style={s.heroText}>
          <div style={s.pill}>
            <div style={s.pillDot} />
            System Status: Online
          </div>
          <h1 style={s.h1}>
            Precision<br />
            <em style={{ fontStyle: 'italic', color: '#888' }}>at Scale</em>
          </h1>
          <div style={s.dataGrid}>
            {[
              { label: 'Max Reach',       val: '1.0 m' },
              { label: 'Payload',         val: '2.0 kg' },
              { label: 'Backlash',        val: 'Zero',  gold: true },
              { label: 'Reduction',       val: '1:100' },
            ].map(({ label, val, gold }) => (
              <div key={label} style={s.dataItem}>
                <div style={s.dataLabel}>{label}</div>
                <div style={{ ...s.dataVal, color: gold ? '#bda365' : '#0e0e0e' }}>{val}</div>
              </div>
            ))}
          </div>
          <div style={s.heroBtns}>
            <Link to="/ik-demo"  style={s.btnDark}>Try IK Demo →</Link>
            <Link to="/preorder" style={s.btnGold}>Reserve a Unit</Link>
          </div>
        </div>

        <div style={s.heroVisual}>
          <div style={s.ring1} />
          <div style={s.ring2} />
          <div style={s.ring3} />
          <div style={s.heroCircle}>6-DOF</div>
          <span style={{ ...s.coord, top: 16, left: 16 }}>X: 0.00 / Y: 0.00 / Z: 1.00m</span>
          <span style={{ ...s.coord, bottom: 16, right: 16 }}>DOF: 6 AXES // ACTIVE</span>
        </div>
      </section>

      {/* STATS */}
      <section style={s.statsRow}>
        {[
          { num: '8×',    label: 'Cost advantage vs UR5e' },
          { num: '1:100', label: 'Cycloidal reduction ratio' },
          { num: '14×',   label: 'CF truss vs AL stiffness' },
          { num: '€4,500',label: 'Kit starting price' },
        ].map(({ num, label }) => (
          <div key={label} style={s.statItem}>
            <div style={s.statNum}>{num}</div>
            <div style={s.statLabel}>{label}</div>
          </div>
        ))}
      </section>

      {/* FEATURES */}
      <section style={s.features}>
        {[
          { num: '01', title: 'Zero-Backlash Cycloidal', body: 'Custom dual-stage cycloidal drives with pin-bearing rollers. 1:100 reduction, sub-arcminute backlash, zero sliding friction.' },
          { num: '02', title: 'Aerospace Truss Structure', body: '4× carbon fiber tubes in rectangular truss — 14× stiffer than standard aluminum at 40% of the weight.' },
          { num: '03', title: 'Live IK Simulator', body: 'Drag the TCP in your browser. The arm solves inverse kinematics in real time. No install required.' },
          { num: '04', title: 'Self-Replicating Design', body: 'Version 1 (CF) manufactures the CNC-milled aluminum parts for Version 2. Every unit shipped compounds manufacturing capability.' },
        ].map(({ num, title, body }) => (
          <div key={num} style={s.featureCard}>
            <div style={s.featureNum}>{num}</div>
            <div style={s.featureTitle}>{title}</div>
            <div style={s.featureBody}>{body}</div>
          </div>
        ))}
      </section>

      {/* CTA STRIP */}
      <section style={s.ctaStrip}>
        <div style={s.ctaLeft}>
          <div style={s.ctaTitle}>Ready to build?</div>
          <div style={s.ctaSub}>Join 47 engineers already on the waitlist.</div>
        </div>
        <div style={s.ctaBtns}>
          <Link to="/preorder"   style={s.btnGold}>Reserve a Unit →</Link>
          <button onClick={() => setModalOpen(true)} style={s.btnOutline}>Sign In</button>
        </div>
      </section>

      <SecureModal isOpen={modalOpen} onClose={() => setModalOpen(false)} />
    </div>
  );
};

const s = {
  page:        { paddingTop: 72 },
  hero:        { display: 'flex', minHeight: 'calc(100vh - 72px)', borderBottom: '1px solid #e2e2e2' },
  heroText:    { flex: 0.9, padding: '80px 56px', display: 'flex', flexDirection: 'column', justifyContent: 'center', borderRight: '1px solid #e2e2e2' },
  pill:        { display: 'inline-flex', alignItems: 'center', gap: 8, background: '#d6e4ff', color: '#0047bb', fontFamily: 'Space Mono, monospace', fontSize: '0.62rem', letterSpacing: '0.15em', textTransform: 'uppercase', padding: '6px 14px', borderRadius: 40, marginBottom: '2rem', width: 'fit-content' },
  pillDot:     { width: 6, height: 6, background: '#0047bb', borderRadius: '50%' },
  h1:          { fontFamily: 'DM Serif Display, serif', fontSize: '4.2rem', fontWeight: 400, lineHeight: 1.05, marginBottom: '3rem' },
  dataGrid:    { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 0, marginBottom: '2.5rem', borderTop: '2px solid #0e0e0e' },
  dataItem:    { padding: '1.2rem 0', borderBottom: '1px solid #e2e2e2' },
  dataLabel:   { fontFamily: 'Space Mono, monospace', fontSize: '0.6rem', textTransform: 'uppercase', letterSpacing: '0.14em', color: '#888', marginBottom: 4 },
  dataVal:     { fontFamily: 'DM Serif Display, serif', fontSize: '1.8rem' },
  heroBtns:    { display: 'flex', gap: 12, flexWrap: 'wrap' },
  btnDark:     { display: 'inline-flex', alignItems: 'center', gap: 8, padding: '14px 28px', background: '#0e0e0e', color: '#fff', fontFamily: 'Space Mono, monospace', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.12em', textDecoration: 'none' },
  btnGold:     { display: 'inline-flex', alignItems: 'center', gap: 8, padding: '14px 28px', background: '#bda365', color: '#000', fontFamily: 'Space Mono, monospace', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.12em', textDecoration: 'none' },
  btnOutline:  { display: 'inline-flex', alignItems: 'center', gap: 8, padding: '14px 28px', background: 'none', border: '1px solid #e2e2e2', color: '#0e0e0e', fontFamily: 'Space Mono, monospace', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.12em', cursor: 'pointer' },
  heroVisual:  { flex: 1.1, background: '#faf9f7', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative', overflow: 'hidden' },
  ring1:       { position: 'absolute', width: 320, height: 320, borderRadius: '50%', border: '1px solid rgba(0,71,187,0.12)', animation: 'spin 14s linear infinite' },
  ring2:       { position: 'absolute', width: 420, height: 420, borderRadius: '50%', border: '1px solid rgba(189,163,101,0.1)', animation: 'spin 22s linear infinite reverse' },
  ring3:       { position: 'absolute', width: 510, height: 510, borderRadius: '50%', border: '1px solid rgba(0,71,187,0.06)', animation: 'spin 30s linear infinite' },
  heroCircle:  { width: 200, height: 200, borderRadius: '50%', background: '#ececec', border: '1px solid #e2e2e2', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Space Mono, monospace', fontSize: '0.9rem', color: '#888', zIndex: 2 },
  coord:       { position: 'absolute', fontFamily: 'Space Mono, monospace', fontSize: '0.6rem', color: '#888', letterSpacing: '0.1em' },
  statsRow:    { display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', borderBottom: '1px solid #e2e2e2' },
  statItem:    { padding: '40px 32px', borderRight: '1px solid #e2e2e2' },
  statNum:     { fontFamily: 'DM Serif Display, serif', fontSize: '2.4rem', marginBottom: 8 },
  statLabel:   { fontFamily: 'Space Mono, monospace', fontSize: '0.58rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#888' },
  features:    { display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', borderBottom: '1px solid #e2e2e2' },
  featureCard: { padding: '48px 32px', borderRight: '1px solid #e2e2e2', transition: 'background 0.3s' },
  featureNum:  { fontFamily: 'Space Mono, monospace', fontSize: '0.62rem', color: '#0047bb', letterSpacing: '0.15em', marginBottom: '1rem' },
  featureTitle:{ fontSize: '1.05rem', fontWeight: 600, marginBottom: '0.8rem' },
  featureBody: { color: '#888', fontSize: '0.88rem', lineHeight: 1.7 },
  ctaStrip:    { background: '#0e0e0e', padding: '64px 56px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '2rem' },
  ctaLeft:     {},
  ctaTitle:    { fontFamily: 'DM Serif Display, serif', fontSize: '2.4rem', color: '#fff', marginBottom: 8 },
  ctaSub:      { color: '#888', fontSize: '0.9rem' },
  ctaBtns:     { display: 'flex', gap: 12, flexWrap: 'wrap' },
};

export default Home;
