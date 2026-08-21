import networkx as nx
from sqlalchemy.orm import Session
from .models import Asset, Connection

def asset_risk(a):
    value = (
        0.35 * a.criticality +
        0.25 * a.vulnerability +
        0.15 * a.exposure +
        0.25 * a.behavioral
    )
    return round(min(100, value), 1)

def make_graph(db: Session):
    g = nx.DiGraph()
    for a in db.query(Asset).all():
        g.add_node(a.id, name=a.name, sector=a.sector, risk=asset_risk(a))
    for e in db.query(Connection).all():
        g.add_edge(e.source_id, e.target_id, trust=e.trust_level, protocol=e.protocol)
    return g

def attack_path(db, source_id, target_id):
    g = make_graph(db)
    try:
        ids = nx.shortest_path(g, source_id, target_id)
    except nx.NetworkXNoPath:
        return []
    return [{"id": i, "name": g.nodes[i]["name"], "risk": g.nodes[i]["risk"]} for i in ids]

def network_score(db):
    assets = db.query(Asset).all()
    return round(sum(asset_risk(a) for a in assets) / len(assets), 1) if assets else 0
