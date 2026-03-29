import { useState, useEffect } from 'react';
import './App.css';

export default function App() {
  const [accounts, setAccounts] = useState([]);
  const [logs, setLogs] = useState([
    { time:'02:00:01', level:'info', msg:'Nightly CRM sweep initiated. 1,000 accounts queued for scoring.' },
    { time:'02:00:14', level:'ok', msg:'Random Forest scoring complete. 12 accounts flagged.' }
  ]);
  const [currentView, setCurrentView] = useState('accounts');
  const [currentTab, setCurrentTab] = useState('detail');
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [currentDraft, setCurrentDraft] = useState(null);
  const [isDrafting, setIsDrafting] = useState(false);
  const [hitlResult, setHitlResult] = useState(null);
  const [pipelineState, setPipelineState] = useState('paused');

  // Helper functions matching index.css utilities
  const getRiskColor = (r) => {
    if (r >= 0.75) return 'var(--danger)';
    if (r >= 0.50) return 'var(--warn)';
    return 'var(--accent)';
  };

  const getSignalTag = (s) => {
    const map = {
      usage_drop: <span className="tag orange">Usage Drop</span>,
      champion: <span className="tag blue">Champion Inactive</span>,
      competitor: <span className="tag red">Competitor</span>,
      payment: <span className="tag purple">DSO Spike</span>,
      normal: <span className="tag green">Healthy</span>
    };
    return map[s] || s;
  };

  const getToneTag = (t) => {
    const map = {
      'passive-aggressive': <span className="tag red">Passive-Aggressive</span>,
      'neutral': <span className="tag orange">Neutral</span>,
      'positive': <span className="tag green">Positive</span>
    };
    return map[t] || <span className="tag default">{t}</span>;
  };

  const addLog = (level, msg) => {
    const d = new Date();
    const time = `${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}:${d.getSeconds().toString().padStart(2,'0')}`;
    setLogs(prev => [{ time, level, msg }, ...prev]);
  };

  // Natively poll the backend for dynamic loading
  useEffect(() => {
    async function loadAccounts() {
      try {
        const res = await fetch('http://localhost:8000/api/accounts');
        if (res.ok) {
          const data = await res.json();
          setAccounts(data.accounts);
          addLog('ok', 'Telemetry dynamically loaded from FastAPI');
        } else throw new Error("Backend Offline");
      } catch (e) {
        addLog('warn', 'FastAPI backend offline. Loading React Safe-Mock state.');
        setAccounts([
          { id:1, name:"AcmeCorp", tier:"Enterprise", cmrr:4200, risk:0.87, signal:"usage_drop", tone:"passive-aggressive", days:18, tickets:4.2, adopt:32, cmrr_trend:-12, competitor:true, champion:false },
          { id:2, name:"Nexus Analytics", tier:"Mid-Market", cmrr:2800, risk:0.74, signal:"champion", tone:"neutral", days:22, tickets:1.1, adopt:45, cmrr_trend:-8, competitor:false, champion:true },
        ]);
      }
    }
    loadAccounts();
  }, []);

  const handleDraftClick = async (account) => {
    setSelectedAccount(account);
    setCurrentTab('draft');
    setIsDrafting(true);
    setCurrentDraft(null);
    setHitlResult(null);
    setPipelineState('paused');

    addLog('info', `Routing generation intent to FastAPI backend for ${account.name}`);
    try {
      const response = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ account_id: account.id, signal: account.signal, name: account.name })
      });
      if (!response.ok) throw new Error("Connections Failed");
      const result = await response.json();
      setCurrentDraft(result.draft);
      addLog('ok', `Draft safely received. HITL Gate paused for ${account.name}`);
    } catch(e) {
      addLog('warn', `Agent unreachable. Falling back to local mock framework for ${account.name}`);
      setTimeout(() => {
        let fallback = {
          subject: "Did we break something in the UI?",
          framework: "Usage Drop",
          color: "orange",
          body: "Hi " + account.name.split(' ')[0] + ",\n\nWe noticed a huge drop in your usage patterns. Since React took over the UI, let us know if we broke something.\n\n[AE Name]"
        };
        
        if (account.signal === "champion") {
          fallback = {
            subject: "Overwhelmed with the transition?",
            framework: "Champion Leaves",
            color: "blue",
            body: "Hi " + account.name.split(' ')[0] + ",\n\nIt seems like you are inheriting a massive amount of legacy systems right now. Does a quick zero-pressure briefing work for you to review compliance?\n\n[AE Name]"
          };
        } else if (account.signal === "competitor") {
          fallback = {
            subject: "Fair enough — they are a strong choice.",
            framework: "Competitor",
            color: "red",
            body: "Hi " + account.name.split(' ')[0] + ",\n\nHonestly? They've built a remarkably strong product over the last year. I would be evaluating them too. Are you entirely opposed to a brief 15-minute technical comparison?\n\n[AE Name]"
          };
        }

        setCurrentDraft(fallback);
        addLog('ok', `Local Mock Draft completed. HITL Paused.`);
      }, 1200);
    } finally {
      setIsDrafting(false);
    }
  };

  const handleHitlAction = (action) => {
    if (action === 'approve') {
       addLog('ok', `Draft approved for ${selectedAccount.name}. Dispatching to CRM.`);
       setHitlResult({ type: 'success', msg: `✓ Approved. Email queued in CRM for dispatch to ${selectedAccount.name}.` });
       setPipelineState('done');
    } else {
       addLog('err', `Draft rejected for ${selectedAccount.name}. RLHF log updated.`);
       setHitlResult({ type: 'danger', msg: `✗ Rejected. Draft discarded. Feedback logged to RLHF.` });
       setPipelineState('done');
    }
  };

  return (
    <>
      <header>
        <div className="logo">
          <div className="logo-dot"></div>
          REVOPS · INTELLIGENCE AGENT (REACT)
        </div>
        <div className="header-right">
          <div className="status-badge"><div className="dot"></div> AGENTS ONLINE · 2/2</div>
        </div>
      </header>

      <div className="app">
        <nav className="sidebar">
          <div className="nav-section">
            <div className="nav-label">Operations</div>
            <div className={`nav-item ${currentView==='accounts' ? 'active':''}`} onClick={()=>setCurrentView('accounts')}>
              <span className="icon">⬡</span> Account Monitor
            </div>
            <div className={`nav-item ${currentView==='pipeline' ? 'active':''}`} onClick={()=>setCurrentView('pipeline')}>
              <span className="icon">◎</span> Agent Pipeline
            </div>
            <div className={`nav-item ${currentView==='roi' ? 'active':''}`} onClick={()=>setCurrentView('roi')}>
              <span className="icon">◈</span> ROI Model
            </div>
          </div>
          <div className="nav-section">
            <div className="nav-label">System</div>
            <div className={`nav-item ${currentView==='logs' ? 'active':''}`} onClick={()=>setCurrentView('logs')}>
              <span className="icon">≡</span> System Logs
            </div>
          </div>
        </nav>

        <main className="main">
          {currentView === 'accounts' && (
            <div>
              <div className="metrics-row">
                <div className="metric-card red"><div className="metric-label">AT-RISK MRR</div><div className="metric-value red">$500K</div></div>
                <div className="metric-card orange"><div className="metric-label">CHURN PROB</div><div className="metric-value orange">28.4%</div></div>
                <div className="metric-card green"><div className="metric-label">RECOVERED MRR</div><div className="metric-value green">$75K</div></div>
                <div className="metric-card blue"><div className="metric-label">AGENT ACTIONS</div><div className="metric-value blue">47</div></div>
              </div>
              <div className="table-wrap" style={{marginTop: 20}}>
                <div className="table-header-row"><div className="section-title">At-Risk Accounts</div></div>
                <table>
                  <thead>
                    <tr><th>Account</th><th>CMRR</th><th>Risk</th><th>Signal</th><th>Action</th></tr>
                  </thead>
                  <tbody>
                    {accounts.map(a => (
                      <tr key={a.id} onClick={()=>setSelectedAccount(a)} className={selectedAccount?.id === a.id ? 'selected' : ''}>
                        <td><div style={{fontWeight:500}}>{a.name}</div><div style={{fontSize:11,color:'var(--muted)'}}>{a.tier}</div></td>
                        <td>${a.cmrr.toLocaleString()}</td>
                        <td>
                          <div className="risk-bar"><div className="risk-fill" style={{width: `${a.risk*100}%`, background: getRiskColor(a.risk)}}></div></div>
                          {a.risk.toFixed(2)}
                        </td>
                        <td>{getSignalTag(a.signal)}</td>
                        <td><button onClick={(e)=>{e.stopPropagation(); handleDraftClick(a)}} className="btn-sm primary">▶ Draft</button></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {currentView === 'pipeline' && (
            <div>
              <div className="section-title" style={{marginBottom:16}}>CrewAI Flow · Live Execution State</div>
              <div className="pipeline-viz" style={{marginBottom:16}}>
                <div className="pipe-node"><div className="pipe-circle done">⬢</div><div className="pipe-label">WEBHOOK<br/>TRIGGER</div></div>
                <div className="pipe-arrow done"></div>
                <div className="pipe-node"><div className="pipe-circle done">◬</div><div className="pipe-label">ANALYST<br/>AGENT</div></div>
                <div className="pipe-arrow done"></div>
                <div className="pipe-node"><div className="pipe-circle done">◭</div><div className="pipe-label">STRATEGIST<br/>AGENT</div></div>
                <div className={`pipe-arrow ${pipelineState === 'done' ? 'done' : ''}`}></div>
                <div className="pipe-node"><div className={`pipe-circle ${pipelineState === 'paused' ? 'active' : 'done'}`}>⏸</div><div className="pipe-label">HITL<br/>REVIEW</div></div>
                <div className={`pipe-arrow ${pipelineState === 'done' ? 'done' : ''}`}></div>
                <div className="pipe-node"><div className={`pipe-circle ${pipelineState === 'done' ? 'done' : 'idle'}`}>◈</div><div className="pipe-label">EXECUTE /<br/>ABORT</div></div>
              </div>

              <div className="table-wrap">
                <div className="table-header-row"><div className="section-title">Flow Step Detail</div></div>
                <div style={{padding:16, display:'flex', flexDirection:'column', gap:16}}>
                  <div className="flow-step">
                    <div className="flow-icon done">⬢</div>
                    <div className="flow-body">
                      <div className="flow-title">Webhook Event Received</div>
                      <div className="flow-desc">FastAPI endpoint received <strong>feature_usage_dropped</strong> event for {selectedAccount?.name || 'an account'}.</div>
                      <div className="flow-code">@start() · analyze_account_health()</div>
                    </div>
                  </div>
                  <div className="flow-step">
                    <div className="flow-icon done">◬</div>
                    <div className="flow-body">
                      <div className="flow-title">Intelligence Analyst Agent · Complete</div>
                      <div className="flow-desc">Random Forest churn score calculated. SHAP explanations generated. Zero-shot intent analyzed. NER applied.</div>
                      <div className="flow-code">Risk JSON emitted → Orchestrator</div>
                    </div>
                  </div>
                  <div className="flow-step">
                    <div className="flow-icon done">◭</div>
                    <div className="flow-body">
                      <div className="flow-title">Sales Strategist Agent · Draft Complete</div>
                      <div className="flow-desc">Framework selected based on telemetry. Chris Voss Labeling applied via Groq generation.</div>
                      <div className="flow-code">@listen("draft_recovery_play")</div>
                    </div>
                  </div>
                  <div className="flow-step">
                    <div className={`flow-icon ${pipelineState === 'paused' ? 'waiting' : 'done'}`}>⏸</div>
                    <div className="flow-body">
                      <div className="flow-title" style={{color: pipelineState === 'paused' ? 'var(--warn)' : 'var(--text)'}}>{pipelineState === 'paused' ? 'HITL Gate · Awaiting AE Approval' : 'HITL Gate · Cleared'}</div>
                      <div className="flow-desc">Execution paused. Draft + approval link dispatched to AE Slack channel. Router model standing by.</div>
                      <div className="flow-code">@human_feedback · emit: [approved | rejected | needs_revision]</div>
                    </div>
                  </div>
                  <div className="flow-step">
                    <div className={`flow-icon ${pipelineState === 'done' ? 'active' : 'pending'}`}>◈</div>
                    <div className="flow-body">
                      <div className="flow-title" style={{color: pipelineState === 'done' ? 'var(--accent)' : 'var(--muted)'}}>{pipelineState === 'done' ? 'Execute / Abort · Completed' : 'Execute / Abort · Pending'}</div>
                      <div className="flow-desc">Awaiting HITL gate resolution. Will route to execute_campaign() or abort_campaign().</div>
                      <div className="flow-code">@listen("approved") | @listen("rejected")</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {currentView === 'roi' && (() => {
            const atRiskMRR = accounts.reduce((s, a) => s + a.cmrr, 0);
            const highRisk = accounts.filter(a => a.risk >= 0.75);
            const highRiskMRR = highRisk.reduce((s, a) => s + a.cmrr, 0);
            const recoveredMRR = Math.round(highRiskMRR * 0.35);
            const annualRecovery = recoveredMRR * 12;
            const implCost = 30000;
            const agentOpsCost = 8400;
            const totalCost = implCost + agentOpsCost;
            const netROI = annualRecovery - totalCost;
            const roiPct = Math.round((netROI / totalCost) * 100);
            const signalGroups = [
              { label: 'Usage Drop', key: 'usage_drop', color: 'orange', cvrRate: '42%', avgRecovery: '$3,200', framework: 'Empathy Labeling' },
              { label: 'Champion Left', key: 'champion', color: 'blue', cvrRate: '28%', avgRecovery: '$5,800', framework: 'Continuity Bridge' },
              { label: 'Competitor Threat', key: 'competitor', color: 'red', cvrRate: '35%', avgRecovery: '$6,100', framework: 'Tactical Mirror' },
              { label: 'DSO / Payment', key: 'payment', color: 'purple', cvrRate: '61%', avgRecovery: '$1,900', framework: 'Calibrated Ask' },
            ];
            return (
              <div>
                <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:20}}>
                  <div className="section-title">Quantified Business Impact Model</div>
                  <span className="tag green">Live · Computed from {accounts.length} accounts</span>
                </div>

                {/* Top KPI Metrics */}
                <div className="metrics-row" style={{marginBottom:24}}>
                  <div className="metric-card red">
                    <div className="metric-label">AT-RISK ARR</div>
                    <div className="metric-value red">${(atRiskMRR * 12 / 1000).toFixed(0)}K</div>
                    <div style={{fontSize:11, color:'var(--muted)', marginTop:4}}>{accounts.length} accounts monitored</div>
                  </div>
                  <div className="metric-card green">
                    <div className="metric-label">PROJECTED RECOVERY</div>
                    <div className="metric-value green">${(annualRecovery / 1000).toFixed(0)}K</div>
                    <div style={{fontSize:11, color:'var(--muted)', marginTop:4}}>35% win-back rate · annual</div>
                  </div>
                  <div className="metric-card orange">
                    <div className="metric-label">TOTAL SYSTEM COST</div>
                    <div className="metric-value orange">${(totalCost / 1000).toFixed(0)}K</div>
                    <div style={{fontSize:11, color:'var(--muted)', marginTop:4}}>Impl + 12-mo. Ops</div>
                  </div>
                  <div className="metric-card blue">
                    <div className="metric-label">NET ROI</div>
                    <div className="metric-value blue">{roiPct}%</div>
                    <div style={{fontSize:11, color:'var(--muted)', marginTop:4}}>${(netROI / 1000).toFixed(0)}K net gain · Year 1</div>
                  </div>
                </div>

                {/* ROI Progress Visual */}
                <div className="table-wrap" style={{padding:'16px 20px', marginBottom:20}}>
                  <div style={{display:'flex', justifyContent:'space-between', marginBottom:8}}>
                    <div style={{fontSize:12, fontWeight:600, color:'var(--text)'}}>YEAR 1 ROI PROGRESSION</div>
                    <div style={{fontSize:12, color:'var(--accent)', fontWeight:700}}>{roiPct}% return</div>
                  </div>
                  <div style={{background:'var(--surface2)', borderRadius:8, height:14, overflow:'hidden'}}>
                    <div style={{
                      width: `${Math.min(roiPct / 4, 100)}%`,
                      height:'100%',
                      background: 'linear-gradient(90deg, var(--accent2), var(--accent))',
                      borderRadius:8,
                      transition:'width 1s ease'
                    }}></div>
                  </div>
                  <div style={{display:'flex', justifyContent:'space-between', marginTop:6, fontSize:11, color:'var(--muted)'}}>
                    <span>Q1: Break-even</span><span>Q2: +{Math.round(roiPct * 0.4)}%</span><span>Q3: +{Math.round(roiPct * 0.7)}%</span><span>Q4: +{roiPct}%</span>
                  </div>
                </div>

                {/* Signal Breakdown Table */}
                <div className="table-wrap" style={{marginBottom:20}}>
                  <div className="table-header-row"><div className="section-title">Recovery Playbook · Per Signal</div></div>
                  <table>
                    <thead>
                      <tr><th>Churn Signal</th><th>Accounts</th><th>At-Risk MRR</th><th>CVR</th><th>Avg. Recovery</th><th>Framework</th></tr>
                    </thead>
                    <tbody>
                      {signalGroups.map(sg => {
                        const accs = accounts.filter(a => a.signal === sg.key);
                        const mrr = accs.reduce((s, a) => s + a.cmrr, 0);
                        return (
                          <tr key={sg.key}>
                            <td><span className={`tag ${sg.color}`}>{sg.label}</span></td>
                            <td>{accs.length}</td>
                            <td>${mrr.toLocaleString()}</td>
                            <td style={{color:'var(--accent)', fontWeight:600}}>{sg.cvrRate}</td>
                            <td style={{fontWeight:500}}>{sg.avgRecovery}</td>
                            <td style={{fontSize:11, color:'var(--muted)'}}>{sg.framework}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                {/* Cost Model */}
                <div className="table-wrap">
                  <div className="table-header-row"><div className="section-title">Cost Model Breakdown</div></div>
                  <table>
                    <thead><tr><th>Line Item</th><th>Type</th><th>Annual Cost</th><th>Notes</th></tr></thead>
                    <tbody>
                      <tr><td>System Implementation</td><td><span className="tag orange">One-Time</span></td><td>$30,000</td><td style={{fontSize:11, color:'var(--muted)'}}>CrewAI + FastAPI + ML setup</td></tr>
                      <tr><td>Groq LLM API Usage</td><td><span className="tag blue">Recurring</span></td><td>$2,400</td><td style={{fontSize:11, color:'var(--muted)'}}>~$200/mo · 1,000 drafts/mo</td></tr>
                      <tr><td>Infrastructure (Cloud)</td><td><span className="tag blue">Recurring</span></td><td>$3,600</td><td style={{fontSize:11, color:'var(--muted)'}}>AWS EC2 + RDS</td></tr>
                      <tr><td>AE Time Savings</td><td><span className="tag green">Reduction</span></td><td style={{color:'var(--accent)'}}>-$35,000</td><td style={{fontSize:11, color:'var(--muted)'}}>~4 hrs/week × 52 weeks freed</td></tr>
                      <tr style={{fontWeight:700}}>
                        <td>Net Year-1 Cost</td><td>—</td>
                        <td style={{color: netROI > 0 ? 'var(--accent)' : 'var(--danger)'}}>${(totalCost / 1000).toFixed(0)}K</td>
                        <td style={{color:'var(--accent)', fontWeight:600}}>ROI: {roiPct}%</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            );
          })()}


          {currentView === 'logs' && (
            <div>
              <div className="section-title">System Execution Logs</div>
              <div className="table-wrap" style={{padding: 16}}>
                 {logs.map((l, i) => (
                   <div key={i} className="log-entry">
                     <span className="log-time">{l.time}</span>
                     <span className={`log-level ${l.level}`}>{l.level.toUpperCase()}</span>
                     <span className="log-msg">{l.msg}</span>
                   </div>
                 ))}
              </div>
            </div>
          )}
        </main>

        <aside className="right-panel">
          <div className="panel-tabs">
            <div className={`panel-tab ${currentTab==='detail'?'active':''}`} onClick={()=>setCurrentTab('detail')}>Account</div>
            <div className={`panel-tab ${currentTab==='draft'?'active':''}`} onClick={()=>setCurrentTab('draft')}>HITL Draft</div>
          </div>

          <div className="panel-content">
            {currentTab === 'detail' && selectedAccount && (
              <div>
                <div className="account-name">{selectedAccount.name}</div>
                <div className="account-meta">{selectedAccount.tier} | ${selectedAccount.cmrr.toLocaleString()}</div>
                <button className="btn btn-approve btn-full" onClick={()=>handleDraftClick(selectedAccount)}>🤖 Generate Draft</button>
              </div>
            )}

            {currentTab === 'draft' && selectedAccount && (
              <div>
                <div className="draft-box">
                  <div className="draft-header">
                    <div className="draft-subject">{isDrafting ? 'Thinking...' : currentDraft?.subject}</div>
                    <div className={`tag ${isDrafting ? 'orange' : currentDraft?.color || 'orange'}`}>{isDrafting ? 'Agent Analyzing' : currentDraft?.framework}</div>
                  </div>
                  <div className="draft-body" style={{whiteSpace:'pre-wrap'}}>{isDrafting ? '⟳ Routing to Orchestrator...' : currentDraft?.body}</div>
                </div>
                {!isDrafting && currentDraft && (
                  <div>
                    <div className="hitl-actions">
                      <button className="btn btn-approve" onClick={()=>handleHitlAction('approve')}>✓ Approve</button>
                      <button className="btn btn-reject" onClick={()=>handleHitlAction('reject')}>✗ Reject</button>
                    </div>
                    {hitlResult && (
                      <div style={{color: hitlResult.type === 'success' ? 'var(--accent)' : 'var(--danger)', padding:12, border:'1px solid', borderRadius:6, marginTop:12}}>
                        {hitlResult.msg}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </aside>
      </div>
    </>
  );
}
