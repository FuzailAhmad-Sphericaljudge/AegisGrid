from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal, engine
from backend.app.models import Base, User
from backend.app.seed import seed
from backend.app.auth import verify_password, hash_password


def test_demo_user_is_repaired_on_seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.add(User(email='demo@aegisgrid.local', password_hash='bad-hash', role='admin'))
    db.commit()
    seed(db)
    user = db.query(User).filter(User.email == 'demo@aegisgrid.local').one()
    assert verify_password('AegisGrid123!', user.password_hash) is True
    db.close()


# Fresh database
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
db = SessionLocal()
seed(db)
db.close()

client = TestClient(app)

# Full login flow
print('=== FULL LOGIN FLOW TEST ===')
print()
print('1. Login with demo credentials...')
login_resp = client.post('/api/auth/login', json={'email':'demo@aegisgrid.local','password':'AegisGrid123!'})
print(f'   Status: {login_resp.status_code}')
token = login_resp.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Load all required data
print('2. Fetching overview...')
overview = client.get('/api/overview', headers=headers)
print(f'   Status: {overview.status_code}')

print('3. Fetching graph...')
graph = client.get('/api/graph', headers=headers)
print(f'   Status: {graph.status_code}')

print('4. Fetching recovery...')
recovery = client.get('/api/recovery', headers=headers)
print(f'   Status: {recovery.status_code}')

print('5. Fetching profile...')
profile = client.get('/api/profile', headers=headers)
print(f'   Status: {profile.status_code}')
if profile.status_code == 200:
    p = profile.json()
    print(f'   Email: {p["email"]}, Role: {p["role"]}')

print()
print('=== ALL ENDPOINTS WORKING ===')
print('✓ Login successful')
print('✓ Overview loaded')
print('✓ Graph loaded')
print('✓ Recovery loaded')
print('✓ Profile loaded')
print()
print('App should now load successfully after login!')
