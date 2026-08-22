import os
import httpx

SECURITY_PROMPT = (
    "You are AegisGrid Copilot, a defensive cyber-resilience assistant. "
    "The environment is a controlled simulation of critical infrastructure. "
    "Explain cybersecurity, application security, cloud security, identity, privacy, "
    "blockchain security, smart contracts, wallets, tokens, consensus and incident response. "
    "Explain risk, attack paths, incident context, response tradeoffs and recovery priorities. "
    "Never claim to have executed an action and never provide instructions for compromising real systems. "
    "Be concise and operationally useful."
)

GENERAL_PROMPT = (
    "You are an intelligent AI assistant with knowledge about the world. "
    "You can answer questions about science, history, technology, current events, geography, culture, and more. "
    "Provide accurate, helpful, and well-reasoned responses. Be conversational and friendly."
)

def is_security_question(message):
    """Detect if the question is about cybersecurity or infrastructure"""
    security_keywords = [
        "risk", "threat", "attack", "vulnerability", "cyber", "security", "incident",
        "contain", "response", "breach", "malware", "exploit", "path", "recover",
        "sector", "infrastructure", "critical infrastructure", "simulation", "defense",
        "aegis", "aegisgrid", "copilot", "project", "system status", "system health", "endpoint", "isolate", "segment", "monitor", "phishing", "ransomware", "firewall", "encryption", "cryptography",
        "authentication", "authorization", "iam", "zero trust", "soc", "siem", "edr",
        "cloud security", "application security", "owasp", "devsecops", "privacy",
        "blockchain", "bitcoin", "ethereum", "crypto", "cryptocurrency", "smart contract",
        "web3", "wallet", "token", "defi", "dao", "consensus", "51%", "bridge"
    ]
    return any(keyword in message.lower() for keyword in security_keywords)

def local_security_answer(message, context=None):
    m = message.lower()
    if "what if" in m:
        if any(x in m for x in ["isolate", "endpoint", "nurse station"]):
            return "What-if result: isolating the Nurse Station PC has a high security benefit with low operational impact. It is estimated to block 92% of the simulated path and reduce risk by 28 points. Next: preserve evidence, rotate exposed credentials and verify the endpoint before reconnecting it."
        if any(x in m for x in ["database", "patient records", "shut down"]):
            return "What-if result: shutting down the Patient Records DB is estimated to block 99% of the simulated path and reduce risk by 38 points, but it has high operational impact. Next: validate backup integrity and confirm service owners before controlled restoration."
        if any(x in m for x in ["segment", "sector", "network"]):
            return "What-if result: segmenting the affected sector is estimated to block 86% of the simulated path and reduce risk by 24 points with medium operational impact. Next: verify essential service links and monitor denied traffic."
        if any(x in m for x in ["monitor", "watch"]):
            return "What-if result: increasing monitoring preserves availability with low operational impact, but blocks only an estimated 34% of the path and reduces risk by 8 points. Next: escalate to containment if suspicious activity increases."
        if any(x in m for x in ["smart contract", "blockchain", "wallet", "crypto"]):
            return "What-if result: deploying or connecting a blockchain system without independent review increases contract, key, oracle and bridge risk. Before proceeding, test access control and reentrancy defenses, use multisignature approvals, verify dependencies and prepare a pause or recovery plan."
        return "I can run a safe, simulation-only comparison. Ask a specific question such as: What if we isolate the endpoint, segment the sector, shut down the database, increase monitoring, or deploy this smart contract?"
    if any(x in m for x in ["what is this project", "what is aegisgrid", "about the project", "explain the project"]):
        return "AegisGrid is a proactive cyber-resilience control plane for connected critical infrastructure. It models Hospital, Power/SCADA, Water and Emergency Services, then helps teams understand exposure, detect threats, assess risk, simulate containment and track recovery. The current environment is a controlled demo, so simulations do not execute real infrastructure actions."
    if "status" in m or "system health" in m or "is the system" in m:
        if context:
            risk = round(context.get("risk", 0))
            threats = context.get("threats", 0)
            assets = context.get("critical_assets", "the tracked")
            sectors = context.get("sectors", "connected")
            return f"System status: the AegisGrid simulation is online and responding. Current network risk is {risk}/100 with {threats} active or monitored threats, {assets} critical assets and {sectors} connected sectors. Review the incident queue and recovery view for the next actions."
        return "System status: the AegisGrid simulation is online. I can report risk, active threats, critical assets, connected sectors, incidents and recovery priorities when dashboard context is available."
    if any(x in m for x in ["blockchain", "bitcoin", "ethereum", "crypto", "cryptocurrency", "web3", "smart contract", "wallet", "token", "defi", "dao", "consensus", "51%", "bridge"]):
        if "smart contract" in m:
            return "Smart-contract security depends on access control, input validation, reentrancy protection, safe arithmetic, oracle assumptions and upgrade governance. Use independent review, automated tests, fuzzing and a pause or recovery plan before deployment."
        if "wallet" in m or "private key" in m:
            return "Protect wallet keys with hardware-backed storage, least privilege, multisignature approval and transaction simulation. Never share seed phrases or sign requests whose destination, calldata or permissions you cannot verify."
        if "51%" in m or "consensus" in m:
            return "A 51% attack is control of enough consensus power to reorganize recent history or censor transactions. It does not automatically let an attacker spend from other users' wallets; confirmations, validator diversity and monitoring reduce the risk."
        if "bridge" in m:
            return "Bridges concentrate risk in validators, message verification, upgrade keys and liquidity accounting. Review trust assumptions, rate limits, pause controls, proof verification and independent monitoring before relying on one."
        if "defi" in m or "dao" in m or "token" in m:
            return "Assess a blockchain system across contract code, privileged roles, oracle and bridge dependencies, governance capture, key management, economic incentives and operational monitoring. On-chain transparency does not remove implementation risk."
        return "Blockchain is a replicated, tamper-evident ledger maintained through a consensus mechanism. For security, assess the protocol, smart contracts, keys, wallets, bridges, oracles, governance and the privacy impact of public data."
    if "risk" in m:
        return "Risk is contextual: combine asset criticality, vulnerability, exposure, behavioral signals and reachable attack paths. High-criticality assets reachable from compromised nodes should be prioritized."
    if "contain" in m or "response" in m:
        return "For the demo scenario, isolate the Nurse Station PC first. It offers high security benefit with low operational impact and breaks the simulated lateral-movement path."
    if "attack path" in m or "path" in m:
        return "The primary simulated path is Nurse Station PC → Admin Server → Patient Records DB → Monitoring System. Breaking the path at the endpoint reduces downstream exposure."
    if "recover" in m:
        return "Prioritize recovery by service criticality and dependency. Verify integrity, restore the least-disruptive critical service, then monitor before restoring dependent systems."
    if "phish" in m:
        return "Reduce phishing risk with phishing-resistant MFA, secure email controls, attachment and link isolation, user reporting, rapid token revocation and rehearsed response playbooks. Treat unusual login and mailbox-rule changes as high-value signals."
    if "ransom" in m or "malware" in m:
        return "For suspected ransomware or malware, isolate affected hosts without destroying evidence, disable compromised accounts, preserve logs, identify the initial access path, validate clean backups and restore in dependency order."
    if "encrypt" in m or "cryptograph" in m:
        return "Use well-reviewed modern cryptography, authenticated encryption, managed key rotation and strict key access controls. Encryption in transit and at rest does not replace identity, authorization, logging or endpoint protection."
    if "zero trust" in m or "iam" in m or "identity" in m or "authentication" in m:
        return "A strong identity program verifies every request, uses least privilege, phishing-resistant MFA, short-lived credentials, device and workload signals, segmentation and continuous audit. Start with privileged and service accounts."
    if "cloud" in m:
        return "Cloud security starts with clear shared-responsibility boundaries, least-privilege IAM, hardened images, network segmentation, secret management, centralized logs, secure backups and continuous configuration monitoring."
    if "owasp" in m or "application security" in m or "devsecops" in m:
        return "Application security should combine threat modeling, secure defaults, dependency and secret scanning, code review, dynamic testing, strong authorization checks, safe deployment gates and production monitoring."
    if "firewall" in m or "network" in m:
        return "Use deny-by-default segmentation, explicit business-justified flows, egress controls, protected management planes, monitored remote access and regular rule review. Network controls should support identity and telemetry rather than stand alone."
    if "sector" in m:
        return "AegisGrid's differentiator is shared context across Hospital, Power/SCADA, Water and Emergency Services instead of isolated alert streams."
    return "I can explain AegisGrid, report simulated system status, answer cybersecurity and blockchain questions, summarize attack paths, compare containment options, prioritize recovery, or explain cross-sector impact."

def local_general_answer(message):
    """Provide general knowledge responses about the world"""
    m = message.lower()
    
    # Geography and capitals
    if "capital" in m:
        capitals = {
            "france": "Paris",
            "japan": "Tokyo",
            "brazil": "Brasília",
            "india": "New Delhi",
            "china": "Beijing",
            "australia": "Canberra",
            "canada": "Ottawa",
            "germany": "Berlin",
            "spain": "Madrid",
            "italy": "Rome"
        }
        for country, capital in capitals.items():
            if country in m:
                return f"The capital of {country.capitalize()} is {capital}."
        return "I can tell you the capitals of many countries. Which country are you interested in?"
    
    # Science questions
    if any(x in m for x in ["gravity", "planet", "star", "universe", "physics"]):
        if "earth" in m and "orbit" in m:
            return "Earth orbits the Sun once every 365.25 days, which defines our year. It rotates on its axis once every 24 hours, creating day and night."
        if "gravity" in m:
            return "Gravity is a fundamental force that attracts objects with mass. Earth's gravity pulls objects toward its center, giving us weight."
        return "I can answer questions about physics, astronomy, and the universe. What would you like to know?"
    
    # History questions
    if any(x in m for x in ["history", "war", "ancient", "century", "historical"]):
        if "renaissance" in m:
            return "The Renaissance was a period of cultural and intellectual revival in Europe from the 14th to 17th centuries, marking the transition from Medieval to Modern times."
        if "world war" in m or "ww" in m:
            if "2" in m or "ii" in m:
                return "World War II (1939-1945) was a global conflict between Allied and Axis powers, resulting in approximately 70-85 million deaths."
            return "World War I (1914-1918) involved major European powers and resulted in about 17 million deaths."
        return "I'm well-versed in historical events. What period or event interests you?"
    
    # Technology and culture
    if any(x in m for x in ["technology", "internet", "computer", "artificial intelligence", "ai", "programming"]):
        if "ai" in m or "artificial intelligence" in m:
            return "Artificial Intelligence refers to computer systems designed to perform tasks that typically require human intelligence, such as learning, reasoning, and problem-solving."
        if "internet" in m:
            return "The Internet is a global system of interconnected networks that enables communication and data sharing worldwide, founded in the late 1960s."
        return "I can discuss technology, programming, AI, and digital innovations. What's your question?"
    
    # Current events and general knowledge
    if "about" in m or "tell me" in m or "what is" in m or "explain" in m:
        return "I'm an AI assistant with knowledge across many domains including history, science, geography, technology, culture, and current events. Feel free to ask me anything!"
    
    return "I'm here to help with any questions you have about the world. Ask me about history, science, geography, technology, culture, or anything else you're curious about!"

async def ask(message, context=None):
    # Determine if this is a security or general question
    is_security = is_security_question(message)
    
    key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")
    
    # If we have API credentials, use the LLM
    if key and model:
        try:
            prompt = message
            system_prompt = SECURITY_PROMPT if is_security else GENERAL_PROMPT
            
            async with httpx.AsyncClient(timeout=25) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.2 if is_security else 0.7,
                        "max_tokens": 500
                    }
                )
                response.raise_for_status()
                data = response.json()
                return {"answer": data["choices"][0]["message"]["content"], "mode": "llm"}
        except Exception as e:
            # Fall back to local answers if LLM fails
            pass
    
    # Use local responses when no API key or as fallback
    if is_security:
        return {"answer": local_security_answer(message, context), "mode": "local_security"}
    else:
        return {"answer": local_general_answer(message), "mode": "local_general"}

