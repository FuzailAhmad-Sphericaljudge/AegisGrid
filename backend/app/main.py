from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from datetime import datetime
from .database import init_db, get_db, SessionLocal
from .models import User, Asset, Threat, Recovery, Connection, Device, AuditLog, Notification
from .schemas import RegisterIn, LoginIn, ChatIn, SimulateIn, ThreatAnalysisIn, RecoveryUpdateIn, UpdateProfileIn, CompleteProfileIn, DeviceOut, AuditLogOut, NotificationOut
from .auth import hash_password, verify_password, create_token, current_user
from .seed import seed
from .risk import asset_risk, attack_path, network_score
from .ai import ask

app = FastAPI(title="AegisGrid API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()
    db = SessionLocal()
    seed(db)
    db.close()

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/demo-session")
def demo_session(db: Session = Depends(get_db)):
    """Create the built-in demo session used by the direct-entry dashboard."""
    user = db.query(User).filter(User.email == "demo@aegisgrid.local").first()
    if not user:
        raise HTTPException(503, "Demo user is not available")
    return {"access_token": create_token(user), "token_type": "bearer"}

@app.post("/api/auth/register")
def register(body: RegisterIn, db: Session = Depends(get_db)):
    email = body.email.strip().lower()
    if db.query(User).filter(func.lower(User.email) == email).first():
        raise HTTPException(409, "Email already registered")
    user = User(email=email, password_hash=hash_password(body.password), role="analyst")
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"access_token": create_token(user), "token_type": "bearer"}

@app.post("/api/auth/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    email = body.email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    
    # Update last login
    user.last_login = datetime.utcnow()
    
    # Log device
    device = Device(
        user_id=user.id,
        device_name="Web Browser",
        device_type="web",
        ip_address="127.0.0.1",
        user_agent="Mozilla",
        last_active=datetime.utcnow()
    )
    db.add(device)
    
    # Log audit
    audit_log = AuditLog(
        user_id=user.id,
        action="login",
        resource_type="User",
        resource_id=user.id,
        status="success",
        ip_address="127.0.0.1"
    )
    db.add(audit_log)
    
    # Create notification
    notification = Notification(
        user_id=user.id,
        notification_type="login",
        title="New login detected",
        message=f"You logged in from Web Browser at 127.0.0.1",
        priority="info"
    )
    db.add(notification)
    
    db.commit()
    db.refresh(user)
    return {"access_token": create_token(user), "token_type": "bearer"}

@app.get("/api/me")
def me(user=Depends(current_user)):
    return {"id": user.id, "email": user.email, "role": user.role}

@app.get("/api/overview")
def overview(db: Session = Depends(get_db), user=Depends(current_user)):
    assets = db.query(Asset).all()
    threats = db.query(Threat).filter(Threat.status.in_(["active","monitoring"])).all()
    return {
        "risk": network_score(db),
        "threats": len(threats),
        "critical_assets": sum(a.criticality >= 90 for a in assets),
        "sectors": sorted({a.sector for a in assets}),
        "assets": [
            {"id":a.id,"name":a.name,"sector":a.sector,"type":a.asset_type,
             "criticality":a.criticality,"risk":asset_risk(a),"status":a.status}
            for a in assets
        ],
        "top_threats": [
            {"id":t.id,"title":t.title,"severity":t.severity,"score":t.score,
             "status":t.status,"asset_id":t.asset_id}
            for t in threats
        ]
    }

@app.get("/api/graph")
def graph(db: Session = Depends(get_db), user=Depends(current_user)):
    return {
        "nodes": [
            {"id":a.id,"label":a.name,"sector":a.sector,"risk":asset_risk(a),
             "criticality":a.criticality,"status":a.status,"asset_type":a.asset_type}
            for a in db.query(Asset).all()
        ],
        "edges": [
            {"source":e.source_id,"target":e.target_id,"protocol":e.protocol,"trust":e.trust_level}
            for e in db.query(Connection).all()
        ]
    }

@app.get("/api/attack-path")
def get_attack_path(source_id: int, target_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    return {"path": attack_path(db, source_id, target_id)}

@app.get("/api/recovery")
def recovery(db: Session = Depends(get_db), user=Depends(current_user)):
    records = []
    for item in db.query(Recovery).all():
        asset = db.get(Asset, item.asset_id)
        records.append({
            "id": item.id, "asset_id": item.asset_id, "service": item.service,
            "progress": item.progress, "status": item.status,
            "eta_minutes": item.eta_minutes,
            "sector": asset.sector if asset else "Unknown",
            "criticality": asset.criticality if asset else 0,
            "asset_status": asset.status if asset else "unknown",
            "priority": round((asset.criticality if asset else 0) * (1 - item.progress / 100), 1)
        })
    return sorted(records, key=lambda item: item["priority"], reverse=True)


@app.patch("/api/recovery/{recovery_id}")
def update_recovery(recovery_id: int, body: RecoveryUpdateIn, user=Depends(current_user), db: Session = Depends(get_db)):
    item = db.get(Recovery, recovery_id)
    if not item:
        raise HTTPException(404, "Recovery item not found")
    item.progress = body.progress
    item.status = body.status or ("healthy" if body.progress == 100 else "in_progress")
    item.eta_minutes = 0 if item.progress == 100 else max(5, round((100 - item.progress) / 2))
    db.commit()
    log_audit(db, user.id, "recovery_progress_updated", "Recovery", recovery_id)
    return {"id": item.id, "progress": item.progress, "status": item.status, "eta_minutes": item.eta_minutes}

@app.post("/api/simulate")
def simulate(body: SimulateIn, db: Session = Depends(get_db), user=Depends(current_user)):
    threat = db.get(Threat, body.threat_id)
    if not threat:
        raise HTTPException(404, "Threat not found")
    choices = {
        "isolate_endpoint": {
            "security_benefit":"High","operational_impact":"Low",
            "blocked_probability":92,
            "risk_reduction":28,
            "next_step":"Collect endpoint evidence and rotate exposed credentials.",
            "summary":"Breaks the simulated lateral-movement path at the entry endpoint."
        },
        "restrict_admin": {
            "security_benefit":"Medium","operational_impact":"Medium",
            "blocked_probability":68,
            "risk_reduction":16,
            "next_step":"Review privileged access logs and confirm an approved administrator.",
            "summary":"Slows the path while preserving most endpoint availability."
        },
        "shutdown_database": {
            "security_benefit":"High","operational_impact":"High",
            "blocked_probability":99,
            "risk_reduction":38,
            "next_step":"Validate backup integrity before beginning controlled restoration.",
            "summary":"Stops downstream access but disrupts critical records availability."
        },
        "segment_sector": {
            "security_benefit":"High","operational_impact":"Medium",
            "blocked_probability":86,
            "risk_reduction":24,
            "next_step":"Verify required service links and monitor denied traffic.",
            "summary":"Contains the incident to the affected sector while preserving essential services."
        },
        "increase_monitoring": {
            "security_benefit":"Low","operational_impact":"Low",
            "blocked_probability":34,
            "risk_reduction":8,
            "next_step":"Escalate to containment if suspicious activity increases.",
            "summary":"Adds visibility and evidence collection without interrupting service availability."
        }
    }
    if body.action not in choices:
        raise HTTPException(400, "Unknown simulation action")
    return {"threat":threat.title,"action":body.action,"result":choices[body.action],"simulation_only":True}

@app.post("/api/chat")
async def chat(body: ChatIn, user=Depends(current_user)):
    return await ask(body.message, body.context)

@app.get("/api/profile")
def get_profile(user=Depends(current_user), db: Session = Depends(get_db)):
    user_obj = db.get(User, user.id)
    return {
        "id": user_obj.id,
        "email": user_obj.email,
        "role": user_obj.role,
        "first_name": user_obj.first_name,
        "last_name": user_obj.last_name,
        "profile_bio": user_obj.profile_bio,
        "profile_phone": user_obj.profile_phone,
        "avatar": user_obj.avatar,
        "profile_complete": user_obj.profile_complete,
        "two_factor_enabled": user_obj.two_factor_enabled,
        "created_at": user_obj.created_at.isoformat(),
        "last_login": user_obj.last_login.isoformat() if user_obj.last_login else None
    }

@app.put("/api/profile")
def update_profile(body: UpdateProfileIn, user=Depends(current_user), db: Session = Depends(get_db)):
    user_obj = db.get(User, user.id)
    if body.first_name is not None:
        user_obj.first_name = body.first_name
    if body.last_name is not None:
        user_obj.last_name = body.last_name
    if body.profile_bio is not None:
        user_obj.profile_bio = body.profile_bio
    if body.profile_phone is not None:
        user_obj.profile_phone = body.profile_phone
    if body.avatar is not None:
        user_obj.avatar = body.avatar
    if body.two_factor_enabled is not None:
        user_obj.two_factor_enabled = body.two_factor_enabled
    db.commit()
    db.refresh(user_obj)
    log_audit(db, user.id, "profile_updated", "User", user_obj.id)
    return {"message": "Profile updated successfully"}

@app.post("/api/profile/complete")
def complete_profile(body: CompleteProfileIn, user=Depends(current_user), db: Session = Depends(get_db)):
    user_obj = db.get(User, user.id)
    user_obj.first_name = body.first_name
    user_obj.last_name = body.last_name
    user_obj.profile_bio = body.profile_bio
    user_obj.profile_phone = body.profile_phone
    user_obj.avatar = body.avatar
    user_obj.profile_complete = True
    db.commit()
    db.refresh(user_obj)
    log_audit(db, user.id, "profile_completed", "User", user_obj.id)
    notification = Notification(
        user_id=user.id,
        notification_type="profile",
        title="Profile completed",
        message="Your profile has been successfully completed!",
        priority="info"
    )
    db.add(notification)
    db.commit()
    return {"message": "Profile completed successfully", "profile": {
        "first_name": user_obj.first_name,
        "last_name": user_obj.last_name,
        "email": user_obj.email,
        "avatar": user_obj.avatar
    }}


@app.get("/api/devices")
def list_devices(user=Depends(current_user), db: Session = Depends(get_db)):
    devices = db.query(Device).filter(Device.user_id == user.id).order_by(desc(Device.last_active)).all()
    return [
        {
            "id": d.id,
            "device_name": d.device_name,
            "device_type": d.device_type,
            "ip_address": d.ip_address,
            "last_active": d.last_active.isoformat(),
            "is_trusted": d.is_trusted,
            "created_at": d.created_at.isoformat()
        }
        for d in devices
    ]

@app.put("/api/devices/{device_id}/trust")
def trust_device(device_id: int, trust: bool, user=Depends(current_user), db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id, Device.user_id == user.id).first()
    if not device:
        raise HTTPException(404, "Device not found")
    device.is_trusted = trust
    db.commit()
    log_audit(db, user.id, "device_trust_changed", "Device", device_id)
    return {"message": f"Device {'trusted' if trust else 'untrusted'} successfully"}

@app.delete("/api/devices/{device_id}")
def remove_device(device_id: int, user=Depends(current_user), db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id, Device.user_id == user.id).first()
    if not device:
        raise HTTPException(404, "Device not found")
    db.delete(device)
    db.commit()
    log_audit(db, user.id, "device_removed", "Device", device_id)
    return {"message": "Device removed successfully"}

@app.get("/api/audit-logs")
def get_audit_logs(skip: int = 0, limit: int = 50, user=Depends(current_user), db: Session = Depends(get_db)):
    logs = db.query(AuditLog).filter(AuditLog.user_id == user.id).order_by(desc(AuditLog.created_at)).offset(skip).limit(limit).all()
    return [
        {
            "id": l.id,
            "action": l.action,
            "resource_type": l.resource_type,
            "resource_id": l.resource_id,
            "status": l.status,
            "ip_address": l.ip_address,
            "details": l.details,
            "created_at": l.created_at.isoformat()
        }
        for l in logs
    ]

@app.get("/api/notifications")
def get_notifications(user=Depends(current_user), db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(Notification.user_id == user.id).order_by(desc(Notification.created_at)).limit(20).all()
    return [
        {
            "id": n.id,
            "notification_type": n.notification_type,
            "title": n.title,
            "message": n.message,
            "is_read": n.is_read,
            "priority": n.priority,
            "created_at": n.created_at.isoformat()
        }
        for n in notifications
    ]

@app.put("/api/notifications/{notification_id}/read")
def mark_notification_read(notification_id: int, user=Depends(current_user), db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user.id).first()
    if not notif:
        raise HTTPException(404, "Notification not found")
    notif.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}

@app.post("/api/ai/threat-analysis")
def threat_analysis(body: ThreatAnalysisIn, db: Session = Depends(get_db), user=Depends(current_user)):
    threat = db.get(Threat, body.threat_id)
    if not threat:
        raise HTTPException(404, "Threat not found")
    asset = db.get(Asset, threat.asset_id)
    analysis = {
        "threat_id": threat.id,
        "title": threat.title,
        "severity": threat.severity,
        "score": threat.score,
        "asset_affected": asset.name if asset else "Unknown",
        "ai_analysis": f"Based on threat patterns, this {threat.severity} severity threat targets {asset.sector if asset else 'critical'} infrastructure. "
                      f"Attack vector: {threat.source}. Recommended containment: Isolate affected endpoint immediately.",
        "confidence": 0.92,
        "similar_threats": [t.title for t in db.query(Threat).filter(Threat.severity == threat.severity).limit(3).all()],
        "recommended_actions": [
            "Isolate the affected system",
            "Review authentication logs",
            "Scan for lateral movement indicators"
        ]
    }
    log_audit(db, user.id, "threat_analysis_requested", "Threat", body.threat_id)
    return analysis

@app.post("/api/ai/compliance-check")
def compliance_check(asset_id: int = None, db: Session = Depends(get_db), user=Depends(current_user)):
    assets = db.query(Asset).all() if not asset_id else [db.get(Asset, asset_id)]
    if not assets or assets[0] is None:
        raise HTTPException(404, "Asset not found")
    
    compliance_report = {
        "assets_checked": len(assets),
        "overall_compliance_score": 78,
        "standards": {
            "NIST": {"status": "partial", "score": 75, "gaps": ["Access Control", "Incident Response"]},
            "ISO27001": {"status": "compliant", "score": 88, "gaps": []},
            "PCI-DSS": {"status": "partial", "score": 72, "gaps": ["Data Protection", "Monitoring"]},
            "HIPAA": {"status": "compliant", "score": 85, "gaps": []} if any(a.sector == "Hospital" for a in assets) else None
        },
        "recommendations": [
            "Implement multi-factor authentication across all systems",
            "Enhance monitoring and logging capabilities",
            "Conduct regular security awareness training"
        ],
        "ai_insights": "AI analysis suggests prioritizing access control improvements for NIST compliance within 60 days."
    }
    log_audit(db, user.id, "compliance_check_run", "Compliance", asset_id or 0)
    return compliance_report

@app.post("/api/ai/anomaly-detection")
def anomaly_detection(db: Session = Depends(get_db), user=Depends(current_user)):
    threats = db.query(Threat).filter(Threat.status == "active").all()
    anomalies = []
    for t in threats:
        if t.score > 80:
            anomalies.append({
                "type": "High-Risk Threat",
                "threat_id": t.id,
                "description": f"Anomaly detected: {t.title}",
                "risk_level": "critical" if t.score > 90 else "high",
                "detected_at": t.source
            })
    
    return {
        "anomalies_detected": len(anomalies),
        "anomalies": anomalies,
        "trend": "increasing" if len(anomalies) > 2 else "stable",
        "ai_prediction": "Pattern analysis indicates 70% probability of escalation within 24 hours if left unaddressed."
    }

def log_audit(db: Session, user_id: int, action: str, resource_type: str, resource_id: int):
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        status="success",
        ip_address="127.0.0.1"
    )
    db.add(audit_log)
    db.commit()

