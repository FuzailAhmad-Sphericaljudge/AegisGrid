from .models import User, Asset, Connection, Threat, Recovery
from .auth import hash_password, verify_password

def seed(db):
    demo_email = "demo@aegisgrid.local"
    demo_password = "AegisGrid123!"
    demo_user = db.query(User).filter(User.email == demo_email).first()

    if demo_user is None:
        db.add(User(email=demo_email, password_hash=hash_password(demo_password), role="admin", first_name="Demo", last_name="User", profile_complete=True))
    elif not verify_password(demo_password, demo_user.password_hash):
        demo_user.password_hash = hash_password(demo_password)
        demo_user.role = "admin"
        demo_user.first_name = "Demo"
        demo_user.last_name = "User"
        demo_user.profile_complete = True

    if db.query(User).count() == 0:
        db.add(User(email=demo_email, password_hash=hash_password(demo_password), role="admin", first_name="Demo", last_name="User", profile_complete=True))

    assets = [
        Asset(id=1,name="Nurse Station PC",sector="Hospital",asset_type="Endpoint",criticality=55,vulnerability=72,exposure=65,behavioral=80,status="compromised"),
        Asset(id=2,name="Admin Server",sector="Hospital",asset_type="Server",criticality=82,vulnerability=58,exposure=70,behavioral=61,status="at_risk"),
        Asset(id=3,name="Patient Records DB",sector="Hospital",asset_type="Database",criticality=98,vulnerability=42,exposure=45,behavioral=35,status="at_risk"),
        Asset(id=4,name="Monitoring System",sector="Hospital",asset_type="Critical Service",criticality=95,vulnerability=35,exposure=40,behavioral=25,status="healthy"),
        Asset(id=5,name="Water SCADA Gateway",sector="Water",asset_type="SCADA",criticality=94,vulnerability=64,exposure=55,behavioral=48,status="healthy"),
        Asset(id=6,name="Power Control Server",sector="Power & SCADA",asset_type="Control Server",criticality=97,vulnerability=52,exposure=60,behavioral=44,status="healthy"),
        Asset(id=7,name="Emergency Dispatch",sector="Emergency Services",asset_type="Service",criticality=96,vulnerability=46,exposure=58,behavioral=39,status="healthy"),
        Asset(id=8,name="Vendor VPN",sector="Shared Services",asset_type="Remote Access",criticality=76,vulnerability=78,exposure=82,behavioral=70,status="at_risk")
    ]
    db.add_all(assets)

    db.add_all([
        Connection(source_id=1,target_id=2,protocol="HTTPS",trust_level=72),
        Connection(source_id=2,target_id=3,protocol="SQL",trust_level=64),
        Connection(source_id=3,target_id=4,protocol="Internal API",trust_level=55),
        Connection(source_id=8,target_id=2,protocol="VPN",trust_level=48),
        Connection(source_id=8,target_id=5,protocol="VPN",trust_level=41),
        Connection(source_id=8,target_id=6,protocol="VPN",trust_level=38),
        Connection(source_id=6,target_id=7,protocol="Service Link",trust_level=52),
        Connection(source_id=5,target_id=7,protocol="Telemetry",trust_level=44)
    ])

    db.add_all([
        Threat(id=1,title="Lateral movement toward Patient DB",severity="critical",score=91,asset_id=1,status="active",details="Simulated credential reuse and suspicious internal traversal."),
        Threat(id=2,title="Abnormal Vendor VPN behavior",severity="high",score=78,asset_id=8,status="active",details="Simulated unusual access window and reachability expansion."),
        Threat(id=3,title="SCADA authentication anomaly",severity="medium",score=63,asset_id=6,status="monitoring",details="Simulated repeated failed authentication attempts.")
    ])

    db.add_all([
        Recovery(id=1,asset_id=1,service="Nurse Station PC",progress=72,status="in_progress",eta_minutes=12),
        Recovery(id=2,asset_id=3,service="Patient Records DB",progress=96,status="protected",eta_minutes=0),
        Recovery(id=3,asset_id=4,service="Monitoring System",progress=88,status="healthy",eta_minutes=0)
    ])
    db.commit()
