import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../api/axiosClient';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [leads, setLeads]     = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setTab]   = useState('overview');

  useEffect(() => {
    if (user?.role === 'admin') fetchLeads();
  }, [user]);

  const fetchLeads = async () => {
    setLoading(true);
    try {
      const res = await api.get('/leads');
      setLeads(res.data.leads);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (id, status) => {
    try {
      await api.put(`/leads/${id}`, { status });
      setLeads(leads.map((l) => (l._id === id ? { ...l, status } : l)));
    } catch (err) {
      console.error(err);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const roleColor = { admin: '#0047bb', partner: '#bda365', user: '#22c55e' };
  const statusColor = { new: '#0047bb', contacted: '#bda365', qualified: '#22c55e', closed: '#888' };

  const tabs = [
    { key: 'overview', label: 'Overview' },
    { key: 'orders',   label: 'My Orders' },
    ...(user?.role === 'admin' ? [{ key: 'leads', label: 'CRM / Leads' }] : []),
    { key: 'settings', label: 'Settings' },
  ];

  return (
    <div style={s.page}>

      {/* SIDEBAR */}
      <div style={s.sidebar}>
        <div style={s.sideTop}>
          <div style={s.userCard}>
            <div style={{ ...s.avatar, background: roleColor[user?.role] || '#888' }}>
              {user?.name?.[0]?.toUpperCase()}
            </div>
            <div>
              <div style={s.userName}>{user?.name}</div>
              <div style={{ ...s.userRole, color: roleColor[user?.role] }}>{user?.role}</div>
            </div>
          </div>
          <nav style={s.sideNav}>
            {tabs.map(({ key, label }) => (
              <button
                key={key}
                style={activeTab === key ? s.navActive : s.nav}
                onClick={() => setTab(key)}
              >
                {label}
              </button>
            ))}
          </nav>
        </div>
        <button onClick={handleLogout} style={s.logoutBtn}>← Logout</button>
      </div>

      {/* MAIN CONTENT */}
      <div style={s.main}>

        {/* OVERVIEW */}
        {activeTab === 'overview' && (
          <div>
            <div style={s.pageNum}>DASH-01 // Overview</div>
            <div style={s.pageTitle}>
              Welcome back, <em style={{ fontStyle: 'italic', color: '#888' }}>{user?.name}.</em>
            </div>
            <div style={s.statGrid}>
              <div style={s.statCard}>
                <div style={s.statLabel}>Account Status</div>
                <div style={{ ...s.statVal, color: roleColor[user?.role] }}>{user?.role?.toUpperCase()}</div>
              </div>
              <div style={s.statCard}>
                <div style={s.statLabel}>Orders</div>
                <div style={s.statVal}>0</div>
              </div>
              <div style={s.statCard}>
                <div style={s.statLabel}>Build Log Updates</div>
                <div style={s.statVal}>4</div>
              </div>
              <div style={{ ...s.statCard, background: '#0047bb' }}>
                <div style={{ ...s.statLabel, color: 'rgba(255,255,255,0.6)' }}>Beta Slots Left</div>
                <div style={{ ...s.statVal, color: '#fff' }}>13</div>
              </div>
            </div>
            <div style={s.section}>
              <div style={s.sectionTitle}>Latest Build Log Entry</div>
              <div style={s.logCard}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
                  <span style={s.logDate}>March 11, 2026</span>
                  <span style={s.logTag}>Milestone</span>
                </div>
                <div style={s.logTitle}>Site Live + IK Demo Running</div>
                <div style={s.logBody}>47 waitlist signups in 48 hours. IK simulator deployed. Three direct investor enquiries received.</div>
              </div>
            </div>
          </div>
        )}

        {/* ORDERS */}
        {activeTab === 'orders' && (
          <div>
            <div style={s.pageNum}>DASH-02 // Orders</div>
            <div style={s.pageTitle}>My <em style={{ fontStyle: 'italic', color: '#888' }}>Orders</em></div>
            <div style={s.emptyState}>
              <div style={{ fontSize: '3rem' }}>📦</div>
              <div style={{ fontFamily: 'DM Serif Display, serif', fontSize: '1.4rem' }}>No orders yet.</div>
              <div style={{ color: '#888', fontSize: '0.88rem' }}>Reserve your unit to get started.</div>
              <a href="/preorder" style={s.emptyBtn}>Reserve a Unit →</a>
            </div>
          </div>
        )}

        {/* CRM — admin only */}
        {activeTab === 'leads' && user?.role === 'admin' && (
          <div>
            <div style={s.pageNum}>DASH-03 // CRM</div>
            <div style={s.pageTitle}>Leads <em style={{ fontStyle: 'italic', color: '#888' }}>&amp; Inquiries</em></div>
            {loading ? (
              <div style={{ fontFamily: 'Space Mono, monospace', fontSize: '0.7rem', color: '#888' }}>Loading leads...</div>
            ) : (
              <div style={s.tableWrap}>
                <table style={s.table}>
                  <thead>
                    <tr>
                      {['Name', 'Email', 'Type', 'Config', 'Status', 'Date', 'Action'].map((h) => (
                        <th key={h} style={s.th}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {leads.length === 0 ? (
                      <tr><td colSpan={7} style={{ ...s.td, textAlign: 'center', color: '#888' }}>No leads yet.</td></tr>
                    ) : leads.map((lead) => (
                      <tr key={lead._id}>
                        <td style={s.td}>{lead.name}</td>
                        <td style={{ ...s.td, fontFamily: 'Space Mono, monospace', fontSize: '0.72rem' }}>{lead.email}</td>
                        <td style={s.td}><span style={s.badge}>{lead.type}</span></td>
                        <td style={{ ...s.td, color: '#888' }}>{lead.config || '—'}</td>
                        <td style={s.td}>
                          <span style={{ ...s.badge, background: statusColor[lead.status] + '22', color: statusColor[lead.status] }}>
                            {lead.status}
                          </span>
                        </td>
                        <td style={{ ...s.td, fontFamily: 'Space Mono, monospace', fontSize: '0.65rem', color: '#888' }}>
                          {new Date(lead.createdAt).toLocaleDateString()}
                        </td>
                        <td style={s.td}>
                          <select value={lead.status} onChange={(e) => updateStatus(lead._id, e.target.value)} style={s.select}>
                            <option value="new">New</option>
                            <option value="contacted">Contacted</option>
                            <option value="qualified">Qualified</option>
                            <option value="closed">Closed</option>
                          </select>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* SETTINGS */}
        {activeTab === 'settings' && (
          <div>
            <div style={s.pageNum}>DASH-04 // Settings</div>
            <div style={s.pageTitle}>Account <em style={{ fontStyle: 'italic', color: '#888' }}>Settings</em></div>
            <div style={s.settingsCard}>
              {[
                ['Name',    user?.name],
                ['Email',   user?.email],
                ['Role',    user?.role],
                ['User ID', user?.id],
              ].map(([label, val]) => (
                <div key={label} style={s.settingsRow}>
                  <span style={s.settingsLabel}>{label}</span>
                  <span style={{ ...s.settingsVal, color: label === 'Role' ? roleColor[user?.role] : '#0e0e0e', fontFamily: label === 'User ID' ? 'Space Mono, monospace' : 'inherit', fontSize: label === 'User ID' ? '0.7rem' : 'inherit' }}>
                    {val}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

const s = {
  page:        { display: 'grid', gridTemplateColumns: '260px 1fr', minHeight: '100vh', paddingTop: 72 },
  sidebar:     { background: '#0a0f1e', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: '40px 0', borderRight: '1px solid #1a1a1a', position: 'sticky', top: 72, height: 'calc(100vh - 72px)', overflowY: 'auto' },
  sideTop:     { display: 'flex', flexDirection: 'column', gap: 32 },
  userCard:    { display: 'flex', alignItems: 'center', gap: 12, padding: '0 24px', paddingBottom: 24, borderBottom: '1px solid #1a1a1a' },
  avatar:      { width: 40, height: 40, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'DM Serif Display, serif', fontSize: '1.1rem', color: '#fff', flexShrink: 0 },
  userName:    { color: '#fff', fontSize: '0.9rem', fontWeight: 600 },
  userRole:    { fontFamily: 'Space Mono, monospace', fontSize: '0.58rem', textTransform: 'uppercase', letterSpacing: '0.1em', marginTop: 2 },
  sideNav:     { display: 'flex', flexDirection: 'column', padding: '0 12px', gap: 4 },
  nav:         { background: 'none', border: 'none', textAlign: 'left', padding: '10px 12px', fontFamily: 'Space Mono, monospace', fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#555', cursor: 'pointer', borderRadius: 4 },
  navActive:   { background: 'rgba(0,71,187,0.15)', border: 'none', textAlign: 'left', padding: '10px 12px', fontFamily: 'Space Mono, monospace', fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#00c8ff', cursor: 'pointer', borderRadius: 4 },
  logoutBtn:   { background: 'none', border: 'none', fontFamily: 'Space Mono, monospace', fontSize: '0.62rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#444', cursor: 'pointer', padding: '0 24px', textAlign: 'left' },
  main:        { padding: 56, background: '#faf9f7', overflowY: 'auto' },
  pageNum:     { fontFamily: 'Space Mono, monospace', fontSize: '0.62rem', textTransform: 'uppercase', letterSpacing: '0.15em', color: '#0047bb', marginBottom: '0.6rem' },
  pageTitle:   { fontFamily: 'DM Serif Display, serif', fontSize: '2.4rem', fontWeight: 400, marginBottom: '2.5rem' },
  statGrid:    { display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16, marginBottom: 40 },
  statCard:    { background: '#fff', border: '1px solid #e2e2e2', padding: '24px 20px' },
  statLabel:   { fontFamily: 'Space Mono, monospace', fontSize: '0.58rem', textTransform: 'uppercase', letterSpacing: '0.12em', color: '#888', marginBottom: 8 },
  statVal:     { fontFamily: 'DM Serif Display, serif', fontSize: '1.8rem', fontWeight: 400 },
  section:     { marginTop: 8 },
  sectionTitle:{ fontFamily: 'Space Mono, monospace', fontSize: '0.62rem', textTransform: 'uppercase', letterSpacing: '0.12em', color: '#888', marginBottom: 16 },
  logCard:     { background: '#fff', border: '1px solid #e2e2e2', padding: 28 },
  logDate:     { fontFamily: 'Space Mono, monospace', fontSize: '0.6rem', color: '#888' },
  logTag:      { background: '#0e0e0e', color: '#fff', fontFamily: 'Space Mono, monospace', fontSize: '0.55rem', padding: '3px 8px', borderRadius: 20 },
  logTitle:    { fontSize: '1.05rem', fontWeight: 600, marginBottom: 6 },
  logBody:     { color: '#888', fontSize: '0.88rem', lineHeight: 1.65 },
  emptyState:  { display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 320, gap: 12 },
  emptyBtn:    { marginTop: 8, padding: '12px 24px', background: '#0047bb', color: '#fff', fontFamily: 'Space Mono, monospace', fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.1em', textDecoration: 'none' },
  tableWrap:   { background: '#fff', border: '1px solid #e2e2e2', overflowX: 'auto' },
  table:       { width: '100%', borderCollapse: 'collapse' },
  th:          { fontFamily: 'Space Mono, monospace', fontSize: '0.58rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#888', padding: '12px 16px', borderBottom: '1px solid #e2e2e2', background: '#f5f4f1', textAlign: 'left', whiteSpace: 'nowrap' },
  td:          { padding: '14px 16px', fontSize: '0.88rem', borderBottom: '1px solid #f0f0f0' },
  badge:       { display: 'inline-block', padding: '3px 10px', borderRadius: 20, background: '#d6e4ff', color: '#0047bb', fontFamily: 'Space Mono, monospace', fontSize: '0.58rem', textTransform: 'uppercase', letterSpacing: '0.06em' },
  select:      { fontFamily: 'Space Mono, monospace', fontSize: '0.62rem', padding: '6px 10px', border: '1px solid #e2e2e2', background: '#fff', cursor: 'pointer', outline: 'none' },
  settingsCard:{ background: '#fff', border: '1px solid #e2e2e2', maxWidth: 480 },
  settingsRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '18px 24px', borderBottom: '1px solid #f0f0f0' },
  settingsLabel:{ fontFamily: 'Space Mono, monospace', fontSize: '0.6rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#888' },
  settingsVal: { fontSize: '0.9rem', fontWeight: 500 },
};

export default Dashboard;
