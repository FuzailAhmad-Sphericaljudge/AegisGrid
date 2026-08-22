import React,{useEffect,useState} from "react";
import {createRoot} from "react-dom/client";
import axios from "axios";
import {Shield,Activity,Network,Bot,LogOut,ChevronRight,AlertTriangle,CheckCircle2,Server,Database,Zap,Droplets,Siren,RefreshCw,Settings,Smartphone,FileText,Bell,Brain,CheckSquare} from "lucide-react";
import {AreaChart,Area,ResponsiveContainer,XAxis,YAxis,Tooltip} from "recharts";
import "./styles.css";

const api=axios.create({baseURL:import.meta.env.VITE_API_URL || "/api"});
api.interceptors.request.use(c=>{const t=localStorage.getItem("cascadia_token");c.headers = c.headers || {}; if(t){c.headers.Authorization=`Bearer ${t}`;} return c;});

function Stat({label,value,icon:Icon,tone}){return <div className="stat"><div className={"stat-icon "+tone}><Icon size={19}/></div><div><span>{label}</span><strong>{value}</strong></div></div>}

const positions={1:[8,52],2:[30,35],3:[52,25],4:[75,17],5:[50,78],6:[72,62],7:[89,70],8:[15,82]};
function Graph({data}){
 const [selected,setSelected]=useState(null);
 const color=s=>s.includes("Hospital")?"hospital":s.includes("Water")?"water":s.includes("Power")?"power":s.includes("Emergency")?"emergency":"shared";
 return <div className="graph"><svg viewBox="0 0 100 100" preserveAspectRatio="none">{data.edges.map(e=>{let a=positions[e.source],b=positions[e.target];return <line key={e.source+"-"+e.target} x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]}/>})}</svg>
 {data.nodes.map(n=>{let p=positions[n.id]||[50,50];return <button key={n.id} onClick={()=>setSelected(n)} className={"node "+color(n.sector)+" "+n.status} style={{left:p[0]+"%",top:p[1]+"%"}}><span>{n.asset_type}</span><b>{n.label}</b><em>{Math.round(n.risk)}</em></button>})}
 <div className="legend"><span>● Hospital</span><span>● Power</span><span>● Water</span><span>● Emergency</span></div>
 {selected&&<div className="pop"><b>{selected.label}</b><span>Risk {Math.round(selected.risk)}/100 · Criticality {selected.criticality}/100</span></div>}
 </div>
}

function ProfileCompletion({user,onComplete}){
 const [firstName,setFirstName]=useState(""),[lastName,setLastName]=useState(""),[bio,setBio]=useState(""),[phone,setPhone]=useState(""),[avatar,setAvatar]=useState(""),[loading,setLoading]=useState(false);
 async function handlePhotoUpload(e){const file=e.target.files[0];if(file){const reader=new FileReader();reader.onload=()=>setAvatar(reader.result);reader.readAsDataURL(file);}}
 async function submit(e){e.preventDefault();setLoading(true);try{await api.post("/profile/complete",{first_name:firstName,last_name:lastName,profile_bio:bio,profile_phone:phone,avatar});onComplete();}catch(err){alert("Error completing profile")}setLoading(false);}
 return <div className="profile-modal"><div className="profile-modal-content">
   <h2>Complete Your Profile</h2>
   <p>Let's get to know you better!</p>
   <form onSubmit={submit}>
     <div className="avatar-section">
       <div className="avatar-preview">{avatar?<img src={avatar} alt="avatar"/>:<div className="avatar-placeholder"><Shield size={40}/></div>}</div>
       <label className="file-input"><input type="file" accept="image/*" onChange={handlePhotoUpload}/><span>Upload Photo</span></label>
     </div>
     <label>First Name<input value={firstName} onChange={e=>setFirstName(e.target.value)} required/></label>
     <label>Last Name<input value={lastName} onChange={e=>setLastName(e.target.value)} required/></label>
     <label>Bio<textarea value={bio} onChange={e=>setBio(e.target.value)} rows={3} placeholder="Tell us about yourself..."/></label>
     <label>Phone<input value={phone} onChange={e=>setPhone(e.target.value)} type="tel" placeholder="+1 (555) 000-0000"/></label>
     <button type="submit" className="primary" disabled={loading}>{loading?"Saving...":"Complete Profile"}<ChevronRight size={18}/></button>
   </form>
 </div></div>
}

function Copilot({overview}){
 const [messages,setMessages]=useState([{role:"ai",text:"Hi! I can explain the AegisGrid project, report the simulated system status, answer cybersecurity and blockchain questions, or help with general knowledge."}]),[text,setText]=useState("");
 async function send(q=text){if(!q.trim())return;setMessages(m=>[...m,{role:"user",text:q}]);setText("");try{let r=await api.post("/chat",{message:q,context:{risk:overview.risk,threats:overview.threats,critical_assets:overview.critical_assets,sectors:overview.sectors.length}});setMessages(m=>[...m,{role:"ai",text:r.data.answer,mode:r.data.mode}])}catch{setMessages(m=>[...m,{role:"ai",text:"I'm temporarily unavailable. Please try again."}])}}
 return <div className="copilot"><div className="copilot-head"><div><Bot size={20}/> <b>AI Assistant</b></div><span>{messages[messages.length-1]?.mode||"ready"}</span></div><div className="chat">{messages.map((m,i)=><div key={i} className={"bubble "+m.role}>{m.text}</div>)}</div><div className="chips"><button onClick={()=>send("What is the AegisGrid project?")}>Project</button><button onClick={()=>send("What is the current system status?")}>System status</button><button onClick={()=>send("What if we isolate the endpoint?")}>What if?</button><button onClick={()=>send("What if we deploy this smart contract?")}>Blockchain what-if</button></div><div className="chat-input"><input value={text} onChange={e=>setText(e.target.value)} onKeyDown={e=>e.key==="Enter"&&send()} placeholder="Ask anything, including What if..."/><button onClick={()=>send()}>Send</button></div></div>
}

function Profile({user}){
 const [profile,setProfile]=useState(null),[firstName,setFirstName]=useState(""),[lastName,setLastName]=useState(""),[bio,setBio]=useState(""),[phone,setPhone]=useState(""),[avatar,setAvatar]=useState("");
 useEffect(()=>{api.get("/profile").then(r=>{setProfile(r.data);setFirstName(r.data.first_name);setLastName(r.data.last_name);setBio(r.data.profile_bio);setPhone(r.data.profile_phone);setAvatar(r.data.avatar);}).catch(()=>{});},[]);
 async function handlePhotoUpload(e){const file=e.target.files[0];if(file){const reader=new FileReader();reader.onload=()=>setAvatar(reader.result);reader.readAsDataURL(file);}}
 async function save(){await api.put("/profile",{first_name:firstName,last_name:lastName,profile_bio:bio,profile_phone:phone,avatar});alert("Profile updated!");}
 if(!profile)return <div className="loading"><Shield/>Loading profile…</div>;
 return <section><div className="panel full"><div className="panel-head"><div><span className="kicker">USER ACCOUNT</span><h2>Profile & Settings</h2></div></div>
   <div className="profile-grid">
     <div className="profile-card avatar-card">
       <span className="kicker">Avatar</span>
       <div className="avatar-preview">{avatar?<img src={avatar} alt="avatar"/>:<div className="avatar-placeholder"><Shield size={40}/></div>}</div>
       <label className="file-input"><input type="file" accept="image/*" onChange={handlePhotoUpload}/><span>Upload Photo</span></label>
     </div>
     <div className="profile-card"><span className="kicker">First Name</span><input value={firstName} onChange={e=>setFirstName(e.target.value)} placeholder="First name" type="text"/></div>
     <div className="profile-card"><span className="kicker">Last Name</span><input value={lastName} onChange={e=>setLastName(e.target.value)} placeholder="Last name" type="text"/></div>
     <div className="profile-card"><span className="kicker">Email</span><b>{profile.email}</b><span className="muted">Role: {profile.role}</span><span className="muted">Joined: {new Date(profile.created_at).toLocaleDateString()}</span></div>
     <div className="profile-card"><span className="kicker">Bio</span><textarea value={bio} onChange={e=>setBio(e.target.value)} placeholder="Enter your bio…" rows={3}/></div>
     <div className="profile-card"><span className="kicker">Phone</span><input value={phone} onChange={e=>setPhone(e.target.value)} placeholder="Phone number" type="tel"/></div>
   </div>
   <button className="action-btn" onClick={save}>Save Changes</button>
 </div></section>
}

function Devices(){
 const [devices,setDevices]=useState([]);
 useEffect(()=>{api.get("/devices").then(r=>setDevices(r.data)).catch(()=>{});},[]);
 async function removeDevice(id){if(confirm("Remove this device?")){await api.delete(`/devices/${id}`);setDevices(devices.filter(d=>d.id!==id));}}
 return <section><div className="panel full"><div className="panel-head"><div><span className="kicker">SECURITY</span><h2>Devices & Sessions</h2><p className="muted">Manage devices where you're logged in.</p></div></div>
   {devices.map(d=><div className="device-row" key={d.id}><div><Smartphone size={18}/><div><b>{d.device_name}</b><span>{d.device_type} · {d.ip_address}</span><small>Last active: {new Date(d.last_active).toLocaleString()}</small></div></div><button className="close-btn" onClick={()=>removeDevice(d.id)}>×</button></div>)}</div></section>
}

function AuditLogs(){
 const [logs,setLogs]=useState([]);
 useEffect(()=>{api.get("/audit-logs").then(r=>setLogs(r.data)).catch(()=>{});},[]);
 return <section><div className="panel full"><div className="panel-head"><div><span className="kicker">COMPLIANCE</span><h2>Audit Log</h2><p className="muted">All actions tracked for security and compliance.</p></div></div>
   <div className="audit-table"><div className="audit-header"><span>Action</span><span>Resource</span><span>Status</span><span>Timestamp</span></div>
   {logs.map(l=><div className="audit-row" key={l.id}><span>{l.action}</span><span>{l.resource_type}</span><span className={"status-"+l.status}>{l.status}</span><span>{new Date(l.created_at).toLocaleString()}</span></div>)}
   </div></div></section>
}

function AIAgents(){
 const [threat,setThreat]=useState(null),[compliance,setCompliance]=useState(null),[anomalies,setAnomalies]=useState(null),[loading,setLoading]=useState(false);
 async function runThreatAnalysis(){setLoading(true);try{let r=await api.post("/ai/threat-analysis",{threat_id:1});setThreat(r.data);}catch(e){alert("Error running analysis");}setLoading(false);}
 async function runComplianceCheck(){setLoading(true);try{let r=await api.post("/ai/compliance-check");setCompliance(r.data);}catch(e){alert("Error running check");}setLoading(false);}
 async function detectAnomalies(){setLoading(true);try{let r=await api.post("/ai/anomaly-detection");setAnomalies(r.data);}catch(e){alert("Error detecting anomalies");}setLoading(false);}
 return <section><div className="ai-grid">
   <div className="panel"><div className="panel-head"><div><span className="kicker">AI AGENT</span><h2>Threat Analysis</h2></div><Brain size={20}/></div><p className="muted">Deep learning-based threat prioritization and attack pattern recognition.</p><button className="action-btn" onClick={runThreatAnalysis} disabled={loading}>Analyze Threats</button>{threat&&<div className="result"><span>{threat.title}</span><b>Risk Level: {threat.severity.toUpperCase()}</b><p>{threat.ai_analysis}</p><span>Confidence: {(threat.confidence*100).toFixed(0)}%</span></div>}</div>
   <div className="panel"><div className="panel-head"><div><span className="kicker">AI AGENT</span><h2>Compliance Check</h2></div><CheckSquare size={20}/></div><p className="muted">Automated compliance verification against NIST, ISO, PCI-DSS, HIPAA standards.</p><button className="action-btn" onClick={runComplianceCheck} disabled={loading}>Run Compliance</button>{compliance&&<div className="result"><span>Overall Score: {compliance.overall_compliance_score}%</span><b>Standards Status</b><div className="standards-grid">{Object.entries(compliance.standards).filter(([,v])=>v).map(([k,v])=><div key={k} className="standard"><span>{k}</span><b>{v.score}%</b><span className="status">{v.status}</span></div>)}</div></div>}</div>
   <div className="panel"><div className="panel-head"><div><span className="kicker">AI AGENT</span><h2>Anomaly Detection</h2></div><AlertTriangle size={20}/></div><p className="muted">Machine learning-based network and behavioral anomaly detection in real-time.</p><button className="action-btn" onClick={detectAnomalies} disabled={loading}>Scan Anomalies</button>{anomalies&&<div className="result"><span>Anomalies Found: {anomalies.anomalies_detected}</span><b>Trend: {anomalies.trend.toUpperCase()}</b><p>{anomalies.ai_prediction}</p></div>}</div>
 </div></section>
}

function Notifications(){
 const [notifs,setNotifs]=useState([]);
 useEffect(()=>{api.get("/notifications").then(r=>setNotifs(r.data)).catch(()=>{});},[]);
 return <div className="notifications-panel">{notifs.slice(0,5).map(n=><div className="notif-item" key={n.id}><Bell size={14}/><div><b>{n.title}</b><span>{n.message}</span></div></div>)}</div>
}

function RecoveryBoard({items,onUpdate}){
 const [filter,setFilter]=useState("all"),[sort,setSort]=useState("priority"),[saving,setSaving]=useState(null);
 const filtered=items.filter(item=>filter==="all"||item.status===filter).sort((a,b)=>sort==="priority"?b.priority-a.priority:b.progress-a.progress);
 const completed=items.filter(item=>item.progress===100).length;
 const average=items.length?Math.round(items.reduce((sum,item)=>sum+item.progress,0)/items.length):0;
 async function update(item,progress){setSaving(item.id);try{await api.patch(`/recovery/${item.id}`,{progress});await onUpdate();}catch{alert("Unable to update recovery progress")}setSaving(null);}
 return <section><div className="recovery-summary"><div className="recovery-stat"><span>Overall readiness</span><strong>{average}%</strong><i><b style={{width:average+"%"}}/></i></div><div className="recovery-stat"><span>Services restored</span><strong>{completed}/{items.length}</strong><small>Fully healthy services</small></div><div className="recovery-stat"><span>Next priority</span><strong>{items[0]?.service||"None"}</strong><small>{items[0]?`Priority score ${items[0].priority}`:"All services stable"}</small></div></div>
   <div className="panel full"><div className="panel-head recovery-toolbar"><div><span className="kicker">RECOVER</span><h2>Service restoration plan</h2><p className="muted">Track integrity checks, restoration progress and operational readiness.</p></div><div className="recovery-controls"><select value={filter} onChange={e=>setFilter(e.target.value)}><option value="all">All statuses</option><option value="in_progress">In progress</option><option value="protected">Protected</option><option value="healthy">Healthy</option></select><select value={sort} onChange={e=>setSort(e.target.value)}><option value="priority">Sort by priority</option><option value="progress">Sort by progress</option></select></div></div>
   <div className="recovery-list">{filtered.map(item=><div className="recovery-card" key={item.id}><div className="recovery-card-head"><div><span className="recovery-sector">{item.sector}</span><h3>{item.service}</h3><p>{item.asset_status} asset · Criticality {item.criticality}/100</p></div><span className={`recovery-status ${item.status}`}>{item.status.replaceAll("_"," ")}</span></div><div className="recovery-progress"><div className="bar"><i style={{width:item.progress+"%"}}/></div><strong>{item.progress}%</strong><span>{item.eta_minutes?`${item.eta_minutes} min remaining`:"Ready"}</span></div><div className="recovery-actions"><label>Progress<input type="range" min="0" max="100" step="1" value={item.progress} disabled={saving===item.id} onChange={e=>update(item,Number(e.target.value))}/></label><button className="action-btn" disabled={saving===item.id||item.progress===100} onClick={()=>update(item,100)}>{saving===item.id?"Saving...":item.progress===100?"Restored":"Mark restored"}</button></div></div>)}{!filtered.length&&<div className="empty-state">No recovery services match this filter.</div>}</div></div></section>
 }

function InfrastructureBoard({overview,graph,onAsk}){
 const [sector,setSector]=useState("All sectors"),[lens,setLens]=useState("risk");
 const sectors=["All sectors",...overview.sectors];
 const nodes=sector==="All sectors"?graph.nodes:graph.nodes.filter(node=>node.sector===sector);
 const nodeIds=new Set(nodes.map(node=>node.id));
 const edges=graph.edges.filter(edge=>nodeIds.has(edge.source)&&nodeIds.has(edge.target));
 const focus=[...nodes].sort((a,b)=>(lens==="risk"?b.risk-a.risk:b.criticality-a.criticality))[0];
 const exposed=nodes.filter(node=>node.status!=="healthy").length;
 const average=nodes.length?Math.round(nodes.reduce((sum,node)=>sum+(lens==="risk"?node.risk:node.criticality),0)/nodes.length):0;
 const insight=sector==="All sectors"?"Shared Services is the bridge between sectors. Watch Vendor VPN reachability because one weak trust link can widen the blast radius.":`${sector} has ${exposed} asset${exposed===1?"":"s"} needing attention. Prioritize ${focus?.label||"the highest-impact asset"} before restoring dependent links.`;
 return <section><div className="infra-hero"><div><span className="kicker">UNDERSTAND / INVESTIGATE</span><h2>Infrastructure command map</h2><p>Explore trust boundaries, exposure and criticality before choosing a response.</p></div><button className="action-btn" onClick={onAsk}>Ask What If?</button></div><div className="infra-lenses">{sectors.map(item=><button key={item} className={sector===item?"selected":""} onClick={()=>setSector(item)}>{item}</button>)}</div><div className="infra-metrics"><div><span>Assets in view</span><strong>{nodes.length}</strong><small>{sector}</small></div><div><span>{lens==="risk"?"Average risk":"Average criticality"}</span><strong>{average}<em>/100</em></strong><small>Network lens</small></div><div><span>Trust links</span><strong>{edges.length}</strong><small>{exposed} needing attention</small></div><div><span>Focus asset</span><strong className="metric-label">{focus?.label||"None"}</strong><small>{focus?`${Math.round(focus.risk)} risk score`:"No assets"}</small></div></div><div className="infra-layout"><div className="panel"><div className="panel-head"><div><span className="kicker">LIVE TOPOLOGY</span><h2>{sector} attack surface</h2></div><div className="lens-toggle"><button className={lens==="risk"?"active":""} onClick={()=>setLens("risk")}>Risk</button><button className={lens==="criticality"?"active":""} onClick={()=>setLens("criticality")}>Criticality</button></div></div><Graph data={{nodes,edges}}/></div><div className="panel infra-insight"><span className="kicker">GRID INTELLIGENCE</span><h2>What deserves attention?</h2><div className="signal"><span className="signal-dot"/><div><b>{focus?.label||"No focus asset"}</b><p>{focus?`Highest ${lens} signal in this view at ${Math.round(lens==="risk"?focus.risk:focus.criticality)}/100.`:"Select a sector to inspect its assets."}</p></div></div><p className="insight-copy">{insight}</p><div className="control-loop"><span>1. Map</span><span>2. Assess</span><span>3. Simulate</span></div><button className="action-btn" onClick={onAsk}>Run a scenario in AI Chat</button></div></div></section>
 }

function App(){
 const [overview,setOverview]=useState(null),[graph,setGraph]=useState(null),[recovery,setRecovery]=useState([]),[tab,setTab]=useState("overview"),[selectedThreat,setSelectedThreat]=useState(1),[simulation,setSimulation]=useState(null),[user,setUser]=useState(null),[showProfileCompletion,setShowProfileCompletion]=useState(false);
 async function load(){try{let [o,g,r]=await Promise.all([api.get("/overview"),api.get("/graph"),api.get("/recovery")]);setOverview(o.data);setGraph(g.data);setRecovery(r.data);try{let u=await api.get("/profile");setUser(u.data);if(!u.data.profile_complete){setShowProfileCompletion(true);}}catch(e){setUser({email:"User",role:"analyst",created_at:new Date().toISOString(),last_login:null});}}catch(x){console.error("Load failed:",x);localStorage.removeItem("cascadia_token");location.reload();}}
 useEffect(()=>{load().catch(()=>{localStorage.removeItem("cascadia_token");location.reload()})},[]);
 if(!overview)return <div className="loading"><Shield/>Loading resilience model…</div>;
 if(showProfileCompletion)return <ProfileCompletion user={user} onComplete={()=>{setShowProfileCompletion(false);load();}}/>;
 const simulate=async action=>setSimulation((await api.post("/simulate",{threat_id:selectedThreat,action})).data);
 return <div className="app"><aside><div className="side-brand"><div className="mark"><Shield/></div><div><b>CASCADIA</b><small>RESILIENCE OS</small></div></div><nav>{[["overview","Overview",Activity],["infrastructure","Infrastructure",Network],["incidents","Incidents",AlertTriangle],["recovery","Recovery",RefreshCw],["ai-agents","AI Agents",Brain],["copilot","AI Chat",Bot],["profile","Profile",Settings],["devices","Devices",Smartphone],["audit","Audit Log",FileText]].map(([id,label,I])=><button className={tab===id?"active":""} onClick={()=>setTab(id)} key={id}><I size={18}/>{label}</button>)}</nav><div className="side-bottom"><Notifications/><span className="online">● Simulation environment online</span></div></aside>
 <main><header><div><span className="eyebrow">CRITICAL INFRASTRUCTURE / CONTROL ROOM</span><h1>{tab==="overview"?"Resilience Overview":tab==="ai-agents"?"AI Security Agents":tab==="profile"?"User Profile":tab==="devices"?"Devices & Sessions":tab==="audit"?"Audit Log":tab==="copilot"?"AI Assistant":tab[0].toUpperCase()+tab.slice(1)}</h1></div><div className="header-actions"><span className="live">● LIVE SIMULATION</span><button className="action-btn what-if-link" onClick={()=>setTab("copilot")}>What If?</button><button className="icon" onClick={load}><RefreshCw size={16}/></button></div></header>
 {tab==="overview"&&<section><div className="stats"><Stat label="Network risk" value={Math.round(overview.risk)+"/100"} icon={Shield} tone="red"/><Stat label="Active threats" value={overview.threats} icon={AlertTriangle} tone="orange"/><Stat label="Critical assets" value={overview.critical_assets} icon={Database} tone="purple"/><Stat label="Sectors connected" value={overview.sectors.length} icon={Network} tone="blue"/></div>
 <div className="cols"><div className="panel"><div className="panel-head"><div><span className="kicker">LIVE INFRASTRUCTURE MODEL</span><h2>Cross-sector attack surface</h2></div><span className="risk">RISK {Math.round(overview.risk)}</span></div><Graph data={graph}/></div>
 <div className="panel"><div className="panel-head"><div><span className="kicker">THREAT PRESSURE</span><h2>Risk trend</h2></div></div><div className="chart"><ResponsiveContainer width="100%" height="100%"><AreaChart data={[{t:"08:00",v:48},{t:"09:00",v:54},{t:"10:00",v:62},{t:"11:00",v:78},{t:"12:00",v:overview.risk}]}><XAxis dataKey="t"/><YAxis domain={[0,100]}/><Tooltip/><Area type="monotone" dataKey="v" fillOpacity=".16"/></AreaChart></ResponsiveContainer></div><p className="muted">Threat pressure increased after simulated lateral movement.</p></div></div>
 <div className="cols lower"><div className="panel"><div className="panel-head"><div><span className="kicker">PRIORITY INCIDENT</span><h2>Phishing → lateral movement</h2></div><span className="severity critical">CRITICAL</span></div><div className="path">Nurse Station PC <ChevronRight/> Admin Server <ChevronRight/> Patient DB <ChevronRight/> Monitoring</div><div className="recommend"><CheckCircle2/><div><span>RECOMMENDED CONTAINMENT</span><b>Isolate Nurse Station PC</b><p>High security benefit · Low operational impact · Breaks the path before patient data is reached.</p></div><button onClick={()=>setTab("incidents")}>Simulate</button></div></div>
 <div className="panel"><div className="panel-head"><div><span className="kicker">RECOVERY</span><h2>Critical service readiness</h2></div></div>{recovery.map(r=><div className="recovery-row" key={r.id}><div><b>{r.service}</b><span>{r.status}</span></div><div className="bar"><i style={{width:r.progress+"%"}}/></div><strong>{r.progress}%</strong></div>)}</div></div></section>}
 {tab==="infrastructure"&&<InfrastructureBoard overview={overview} graph={graph} onAsk={()=>setTab("copilot")}/>}
 {tab==="incidents"&&<section><div className="cols"><div className="panel"><div className="panel-head"><div><span className="kicker">DETECT + ASSESS</span><h2>Incident queue</h2></div></div>{overview.top_threats.map(t=><button className={"incident "+(selectedThreat===t.id?"selected":"")} key={t.id} onClick={()=>setSelectedThreat(t.id)}><div><span className={"severity "+t.severity}>{t.severity.toUpperCase()}</span><b>{t.title}</b><small>Asset ID {t.asset_id} · {t.status}</small></div><strong>{Math.round(t.score)}</strong></button>)}</div>
 <div className="panel"><div className="panel-head"><div><span className="kicker">WHAT IF?</span><h2>Response simulation</h2></div><span className="simulation-badge">NO REAL ACTIONS</span></div><p className="muted">Compare containment choices against the selected simulated threat.</p>{[["isolate_endpoint","Isolate endpoint","High","Low"],["restrict_admin","Restrict admin access","Medium","Medium"],["shutdown_database","Shut down database","High","High"],["segment_sector","Segment affected sector","High","Medium"],["increase_monitoring","Increase monitoring","Low","Low"]].map(a=><button className="action" key={a[0]} onClick={()=>simulate(a[0])}><div><b>{a[1]}</b><span>Security benefit: {a[2]} · Operational impact: {a[3]}</span></div><ChevronRight/></button>)}{simulation&&<div className="result"><span>SIMULATION RESULT</span><h3>{simulation.action.replaceAll("_"," ")}</h3><p>{simulation.result.summary}</p><div className="simulation-metrics"><b>{simulation.result.blocked_probability}%<small>Path blocked</small></b><b>{simulation.result.risk_reduction}<small>Risk reduction</small></b><b>{simulation.result.operational_impact}<small>Operational impact</small></b></div><p className="next-step"><strong>Next step:</strong> {simulation.result.next_step}</p></div>}</div></div></section>}
 {tab==="recovery"&&<RecoveryBoard items={recovery} onUpdate={async()=>{const r=await api.get("/recovery");setRecovery(r.data);}}/>}
 {tab==="ai-agents"&&<AIAgents/>}
 {tab==="copilot"&&<section><Copilot overview={overview}/></section>}
 {tab==="profile"&&<Profile user={user}/>}
 {tab==="devices"&&<Devices/>}
 {tab==="audit"&&<AuditLogs/>}
 </main></div>
}
function DirectEntry(){
 const [ready,setReady]=useState(false),[error,setError]=useState("");
 useEffect(()=>{api.post("/demo-session").then(r=>{localStorage.setItem("cascadia_token",r.data.access_token);setReady(true);}).catch(()=>setError("Unable to start the demo session. Check that the API is running."));},[]);
 if(error)return <div className="loading"><Shield/>{error}</div>;
 return ready?<App/>:<div className="loading"><Shield/>Starting resilience model…</div>;
}
createRoot(document.getElementById("root")).render(<DirectEntry/>);
