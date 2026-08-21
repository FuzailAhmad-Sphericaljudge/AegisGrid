import React,{useEffect,useState} from "react";
import {createRoot} from "react-dom/client";
import axios from "axios";
import {Shield,Activity,Network,Bot,LogOut,ChevronRight,AlertTriangle,CheckCircle2,Server,Database,Zap,Droplets,Siren,RefreshCw,Settings,Smartphone,FileText,Bell,Brain,CheckSquare} from "lucide-react";
import {AreaChart,Area,ResponsiveContainer,XAxis,YAxis,Tooltip} from "recharts";
import "./styles.css";

const api=axios.create({baseURL:import.meta.env.VITE_API_URL || "http://localhost:8000/api"});
api.interceptors.request.use(c=>{const t=localStorage.getItem("aegis_token");c.headers = c.headers || {}; if(t){c.headers.Authorization=`Bearer ${t}`;} return c;});

function Login({done}){
 const [mode,setMode]=useState("login"),[email,setEmail]=useState("demo@aegisgrid.local"),[password,setPassword]=useState("AegisGrid123!"),[error,setError]=useState("");
 async function submit(e){e.preventDefault();setError("");try{const r=await api.post("/auth/"+mode,{email,password});localStorage.setItem("aegis_token",r.data.access_token);done()}catch(x){setError(x.response?.data?.detail||"Authentication failed")}}
 return <div className="auth"><div className="orb"></div><div className="auth-card">
   <div className="brand"><div className="mark"><Shield/></div><div><b>AEGIS<span>GRID</span></b><small>CYBER-RESILIENCE CONTROL PLANE</small></div></div>
   <div className="auth-title"><h1>{mode==="login"?"Welcome back":"Create analyst account"}</h1><p>Understand risk before it becomes impact.</p></div>
   <form onSubmit={submit}><label>Email<input value={email} onChange={e=>setEmail(e.target.value)} type="email"/></label><label>Password<input value={password} onChange={e=>setPassword(e.target.value)} type="password"/></label>{error&&<div className="error">{error}</div>}<button className="primary">{mode==="login"?"Enter AegisGrid":"Create account"}<ChevronRight size={18}/></button></form>
   <button className="link" onClick={()=>setMode(mode==="login"?"register":"login")}>{mode==="login"?"Need an account? Register":"Already have an account? Sign in"}</button>
   <div className="demo">Demo credentials are prefilled for the hackathon prototype.</div>
 </div></div>
}

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
 const [messages,setMessages]=useState([{role:"ai",text:"Hi! I'm your AI assistant. I can help with cybersecurity questions or answer anything about the world. What would you like to know?"}]),[text,setText]=useState("");
 async function send(q=text){if(!q.trim())return;setMessages(m=>[...m,{role:"user",text:q}]);setText("");try{let r=await api.post("/chat",{message:q,context:{risk:overview.risk,threats:overview.top_threats}});setMessages(m=>[...m,{role:"ai",text:r.data.answer,mode:r.data.mode}])}catch{setMessages(m=>[...m,{role:"ai",text:"I'm temporarily unavailable. Please try again."}])}}
 return <div className="copilot"><div className="copilot-head"><div><Bot size={20}/> <b>AI Assistant</b></div><span>{messages[messages.length-1]?.mode||"ready"}</span></div><div className="chat">{messages.map((m,i)=><div key={i} className={"bubble "+m.role}>{m.text}</div>)}</div><div className="chips"><button onClick={()=>send("What is cybersecurity risk?")}>Security Q</button><button onClick={()=>send("What is the capital of France?")}>Geography</button><button onClick={()=>send("Explain artificial intelligence")}>Technology</button><button onClick={()=>send("Tell me about World War 2")}>History</button></div><div className="chat-input"><input value={text} onChange={e=>setText(e.target.value)} onKeyDown={e=>e.key==="Enter"&&send()} placeholder="Ask anything..."/><button onClick={()=>send()}>Send</button></div></div>
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

function App(){
 const [overview,setOverview]=useState(null),[graph,setGraph]=useState(null),[recovery,setRecovery]=useState([]),[tab,setTab]=useState("overview"),[selectedThreat,setSelectedThreat]=useState(1),[simulation,setSimulation]=useState(null),[user,setUser]=useState(null),[showProfileCompletion,setShowProfileCompletion]=useState(false);
 async function load(){try{let [o,g,r]=await Promise.all([api.get("/overview"),api.get("/graph"),api.get("/recovery")]);setOverview(o.data);setGraph(g.data);setRecovery(r.data);try{let u=await api.get("/profile");setUser(u.data);if(!u.data.profile_complete){setShowProfileCompletion(true);}}catch(e){setUser({email:"User",role:"analyst",created_at:new Date().toISOString(),last_login:null});}}catch(x){console.error("Load failed:",x);localStorage.removeItem("aegis_token");location.reload();}}
 useEffect(()=>{load().catch(()=>{localStorage.removeItem("aegis_token");location.reload()})},[]);
 if(!overview)return <div className="loading"><Shield/>Loading resilience model…</div>;
 if(showProfileCompletion)return <ProfileCompletion user={user} onComplete={()=>{setShowProfileCompletion(false);load();}}/>;
 const simulate=async action=>setSimulation((await api.post("/simulate",{threat_id:selectedThreat,action})).data);
 const logout=()=>{localStorage.removeItem("aegis_token");location.reload()};
 return <div className="app"><aside><div className="side-brand"><div className="mark"><Shield/></div><div><b>AEGIS<span>GRID</span></b><small>RESILIENCE OS</small></div></div><nav>{[["overview","Overview",Activity],["infrastructure","Infrastructure",Network],["incidents","Incidents",AlertTriangle],["recovery","Recovery",RefreshCw],["ai-agents","AI Agents",Brain],["copilot","AI Chat",Bot],["profile","Profile",Settings],["devices","Devices",Smartphone],["audit","Audit Log",FileText]].map(([id,label,I])=><button className={tab===id?"active":""} onClick={()=>setTab(id)} key={id}><I size={18}/>{label}</button>)}</nav><div className="side-bottom"><Notifications/><span className="online">● Simulation environment online</span><button onClick={logout}><LogOut size={16}/>Sign out</button></div></aside>
 <main><header><div><span className="eyebrow">CRITICAL INFRASTRUCTURE / CONTROL ROOM</span><h1>{tab==="overview"?"Resilience Overview":tab==="ai-agents"?"AI Security Agents":tab==="profile"?"User Profile":tab==="devices"?"Devices & Sessions":tab==="audit"?"Audit Log":tab==="copilot"?"AI Assistant":tab[0].toUpperCase()+tab.slice(1)}</h1></div><div className="header-actions"><span className="live">● LIVE SIMULATION</span><button className="icon" onClick={load}><RefreshCw size={16}/></button></div></header>
 {tab==="overview"&&<section><div className="stats"><Stat label="Network risk" value={Math.round(overview.risk)+"/100"} icon={Shield} tone="red"/><Stat label="Active threats" value={overview.threats} icon={AlertTriangle} tone="orange"/><Stat label="Critical assets" value={overview.critical_assets} icon={Database} tone="purple"/><Stat label="Sectors connected" value={overview.sectors.length} icon={Network} tone="blue"/></div>
 <div className="cols"><div className="panel"><div className="panel-head"><div><span className="kicker">LIVE INFRASTRUCTURE MODEL</span><h2>Cross-sector attack surface</h2></div><span className="risk">RISK {Math.round(overview.risk)}</span></div><Graph data={graph}/></div>
 <div className="panel"><div className="panel-head"><div><span className="kicker">THREAT PRESSURE</span><h2>Risk trend</h2></div></div><div className="chart"><ResponsiveContainer width="100%" height="100%"><AreaChart data={[{t:"08:00",v:48},{t:"09:00",v:54},{t:"10:00",v:62},{t:"11:00",v:78},{t:"12:00",v:overview.risk}]}><XAxis dataKey="t"/><YAxis domain={[0,100]}/><Tooltip/><Area type="monotone" dataKey="v" fillOpacity=".16"/></AreaChart></ResponsiveContainer></div><p className="muted">Threat pressure increased after simulated lateral movement.</p></div></div>
 <div className="cols lower"><div className="panel"><div className="panel-head"><div><span className="kicker">PRIORITY INCIDENT</span><h2>Phishing → lateral movement</h2></div><span className="severity critical">CRITICAL</span></div><div className="path">Nurse Station PC <ChevronRight/> Admin Server <ChevronRight/> Patient DB <ChevronRight/> Monitoring</div><div className="recommend"><CheckCircle2/><div><span>RECOMMENDED CONTAINMENT</span><b>Isolate Nurse Station PC</b><p>High security benefit · Low operational impact · Breaks the path before patient data is reached.</p></div><button onClick={()=>setTab("incidents")}>Simulate</button></div></div>
 <div className="panel"><div className="panel-head"><div><span className="kicker">RECOVERY</span><h2>Critical service readiness</h2></div></div>{recovery.map(r=><div className="recovery-row" key={r.id}><div><b>{r.service}</b><span>{r.status}</span></div><div className="bar"><i style={{width:r.progress+"%"}}/></div><strong>{r.progress}%</strong></div>)}</div></div></section>}
 {tab==="infrastructure"&&<section><div className="panel full"><div className="panel-head"><div><span className="kicker">UNDERSTAND</span><h2>Infrastructure & attack-path graph</h2><p className="muted">Every alert gains meaning through criticality, reachability, vulnerability and behavior.</p></div></div><Graph data={graph}/></div><div className="sector-grid">{overview.sectors.map(s=><div className="sector" key={s}><div>{s.includes("Hospital")?<Server/>:s.includes("Power")?<Zap/>:s.includes("Water")?<Droplets/>:<Siren/>}</div><b>{s}</b><span>{overview.assets.filter(a=>a.sector===s).length} connected assets</span></div>)}</div></section>}
 {tab==="incidents"&&<section><div className="cols"><div className="panel"><div className="panel-head"><div><span className="kicker">DETECT + ASSESS</span><h2>Incident queue</h2></div></div>{overview.top_threats.map(t=><button className={"incident "+(selectedThreat===t.id?"selected":"")} key={t.id} onClick={()=>setSelectedThreat(t.id)}><div><span className={"severity "+t.severity}>{t.severity.toUpperCase()}</span><b>{t.title}</b><small>Asset ID {t.asset_id} · {t.status}</small></div><strong>{Math.round(t.score)}</strong></button>)}</div>
 <div className="panel"><div className="panel-head"><div><span className="kicker">WHAT IF?</span><h2>Response simulation</h2></div><span className="simulation-badge">NO REAL ACTIONS</span></div><p className="muted">Compare containment choices against the selected simulated threat.</p>{[["isolate_endpoint","Isolate endpoint","High","Low"],["restrict_admin","Restrict admin access","Medium","Medium"],["shutdown_database","Shut down database","High","High"]].map(a=><button className="action" key={a[0]} onClick={()=>simulate(a[0])}><div><b>{a[1]}</b><span>Security benefit: {a[2]} · Operational impact: {a[3]}</span></div><ChevronRight/></button>)}{simulation&&<div className="result"><span>SIMULATION RESULT</span><h3>{simulation.action.replaceAll("_"," ")}</h3><p>{simulation.result.summary}</p><b>{simulation.result.blocked_probability}% estimated path-block probability</b></div>}</div></div></section>}
 {tab==="recovery"&&<section><div className="panel full"><div className="panel-head"><div><span className="kicker">RECOVER</span><h2>Service restoration</h2></div></div>{recovery.map(r=><div className="recovery-big" key={r.id}><div><b>{r.service}</b><span>{r.status} · ETA {r.eta_minutes} min</span></div><div className="bar"><i style={{width:r.progress+"%"}}/></div></div>)}</div></section>}
 {tab==="ai-agents"&&<AIAgents/>}
 {tab==="copilot"&&<section><Copilot overview={overview}/></section>}
 {tab==="profile"&&<Profile user={user}/>}
 {tab==="devices"&&<Devices/>}
 {tab==="audit"&&<AuditLogs/>}
 </main></div>
}
createRoot(document.getElementById("root")).render(localStorage.getItem("aegis_token")?<App/>:<Login done={()=>location.reload()}/>);
