import os
import httpx

SECURITY_PROMPT = (
    "You are AegisGrid Copilot, a defensive cyber-resilience assistant. "
    "The environment is a controlled simulation of critical infrastructure. "
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
        "aegis", "copilot"
    ]
    return any(keyword in message.lower() for keyword in security_keywords)

def local_security_answer(message, context=None):
    m = message.lower()
    if "risk" in m:
        return "Risk is contextual: combine asset criticality, vulnerability, exposure, behavioral signals and reachable attack paths. High-criticality assets reachable from compromised nodes should be prioritized."
    if "contain" in m or "response" in m:
        return "For the demo scenario, isolate the Nurse Station PC first. It offers high security benefit with low operational impact and breaks the simulated lateral-movement path."
    if "attack path" in m or "path" in m:
        return "The primary simulated path is Nurse Station PC → Admin Server → Patient Records DB → Monitoring System. Breaking the path at the endpoint reduces downstream exposure."
    if "recover" in m:
        return "Prioritize recovery by service criticality and dependency. Verify integrity, restore the least-disruptive critical service, then monitor before restoring dependent systems."
    if "sector" in m:
        return "AegisGrid's differentiator is shared context across Hospital, Power/SCADA, Water and Emergency Services instead of isolated alert streams."
    return "I can explain the current risk, summarize an attack path, compare containment options, prioritize recovery, or explain cross-sector impact."

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

