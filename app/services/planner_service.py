import json
from typing import Any
from .catalog import HOME_CATALOG, PARTY_CATALOG, JEWELRY_CATALOG, search_url
from .gemini_service import gemini_service
from ..schemas import HomeRequest, PartyRequest, JewelryRequest, RecommendationResponse


def _clean_items(raw: Any, budget: float, source: str) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("AI response must be an object.")
    raw["budget"] = budget
    raw["source"] = source
    return RecommendationResponse.model_validate(raw).model_dump()


def _fallback_home(req: HomeRequest) -> dict:
    per_item = max(1, int(req.budget / max(1, len(req.items))))
    rows = []
    total = 0.0
    for item in req.items:
        matches = sorted(HOME_CATALOG, key=lambda x: abs(x[2] - per_item))
        platform, name, price = matches[0]
        qty = item.quantity
        line = price * qty
        if total + line > req.budget:
            qty = max(1, int((req.budget - total) / price))
            line = price * qty
        if qty <= 0:
            continue
        rows.append({
            "name": name,
            "category": item.category,
            "platform": platform,
            "estimated_price": price,
            "quantity": qty,
            "reason": f"Budget-conscious {req.style} option for {item.category}.",
            "search_url": search_url(platform, name),
        })
        total += line
        if total >= req.budget:
            break

    return {
        "title": "Home Interior Budget Plan",
        "summary": f"A {req.style} setup for {', '.join(req.rooms)} with a controlled spend.",
        "total_estimated_cost": round(total, 2),
        "budget": req.budget,
        "budget_remaining": round(max(0, req.budget - total), 2),
        "allocations": [{"category": x.category, "amount": round(req.budget / len(req.items), 2)} for x in req.items],
        "recommendations": rows,
        "notes": ["Prices are estimates. Open a platform search link to check current listings."],
        "source": "fallback",
    }


def _fallback_party(req: PartyRequest) -> dict:
    food = round(req.budget * 0.50, 2)
    decor = round(req.budget * 0.20, 2)
    entertainment = round(req.budget * 0.15, 2)
    venue = round(req.budget - food - decor - entertainment, 2)
    meal_price = 250
    meal_qty = max(1, min(req.guests, int(food / meal_price)))
    rows = [
        {
            "name": "Party catering meal",
            "category": "catering",
            "platform": "Swiggy",
            "estimated_price": meal_price,
            "quantity": meal_qty,
            "reason": f"Simple catering estimate for {req.guests} guests.",
            "search_url": search_url("Swiggy", f"{req.event_type} catering {req.city}"),
        },
        {
            "name": "Party decoration kit",
            "category": "decoration",
            "platform": "Amazon",
            "estimated_price": 1200,
            "quantity": 1,
            "reason": "Basic decoration starter option.",
            "search_url": search_url("Amazon", f"{req.event_type} party decoration"),
        },
        {
            "name": "Event venue search",
            "category": "venue",
            "platform": "OYO",
            "estimated_price": venue,
            "quantity": 1,
            "reason": f"Search starting point for venues/accommodation in {req.city}.",
            "search_url": search_url("OYO", req.city),
        },
    ]
    total = meal_price * meal_qty + 1200
    return {
        "title": "Party Budget Plan",
        "summary": f"{req.event_type.title()} plan for {req.guests} guests.",
        "total_estimated_cost": round(total, 2),
        "budget": req.budget,
        "budget_remaining": round(max(0, req.budget - total), 2),
        "allocations": [
            {"category": "catering", "amount": food},
            {"category": "decoration", "amount": decor},
            {"category": "entertainment", "amount": entertainment},
            {"category": "venue", "amount": venue},
        ],
        "recommendations": rows,
        "notes": ["Allocation is a planning estimate, not a quote."],
        "source": "fallback",
    }


def _fallback_jewelry(req: JewelryRequest, outfit_analysis: str = "") -> dict:
    target = req.budget / 3
    rows = []
    for platform, name, price in sorted(JEWELRY_CATALOG, key=lambda x: abs(x[2] - target))[:3]:
        rows.append({
            "name": name,
            "category": "jewelry",
            "platform": platform,
            "estimated_price": price,
            "quantity": 1,
            "reason": f"Suitable for a {req.occasion} occasion and {req.style} preference.",
            "search_url": search_url(platform, name),
        })
    total = sum(x["estimated_price"] for x in rows)
    note = "Image analysis was used." if outfit_analysis else "No outfit image was supplied."
    return {
        "title": "Jewelry Budget Plan",
        "summary": f"Jewelry suggestions for a {req.occasion} occasion.",
        "total_estimated_cost": total,
        "budget": req.budget,
        "budget_remaining": round(max(0, req.budget - total), 2),
        "allocations": [{"category": "jewelry", "amount": req.budget}],
        "recommendations": rows,
        "notes": [note, "Prices are estimates; verify current listing details before purchase."],
        "source": "fallback",
    }


async def generate_home(req: HomeRequest) -> dict:
    prompt = f"""
You are PocketSmart AI, a budget-aware home interior planning assistant.
Create a practical recommendation plan from this input:
{req.model_dump_json(indent=2)}

Return JSON only with exactly these top-level keys:
title, summary, total_estimated_cost, budget, budget_remaining, allocations, recommendations, notes

recommendations must be an array of objects with:
name, category, platform, estimated_price, quantity, reason, search_url

Allowed platforms: Amazon, IKEA, Flipkart.
Never invent a claim that a specific product is currently in stock.
Use platform search URLs when an exact product URL is unavailable.
Keep total_estimated_cost <= budget.
"""
    try:
        result = await gemini_service.generate_json(prompt)
        return _clean_items(result, req.budget, "gemini")
    except Exception:
        return _fallback_home(req)


async def generate_party(req: PartyRequest) -> dict:
    prompt = f"""
You are PocketSmart AI, a budget-aware party planning assistant.
Plan this event:
{req.model_dump_json(indent=2)}

Allocate the budget across catering, decoration, entertainment and venue.
Return JSON only with:
title, summary, total_estimated_cost, budget, budget_remaining, allocations, recommendations, notes

recommendations fields:
name, category, platform, estimated_price, quantity, reason, search_url

Allowed platforms: Swiggy, Zomato, Amazon, OYO.
Do not claim live availability or current prices. Use search URLs.
Keep total_estimated_cost <= budget.
"""
    try:
        result = await gemini_service.generate_json(prompt)
        return _clean_items(result, req.budget, "gemini")
    except Exception:
        return _fallback_party(req)


async def generate_jewelry(req: JewelryRequest, image_bytes: bytes | None = None, mime_type: str = "image/jpeg") -> dict:
    outfit_analysis = ""
    if image_bytes:
        try:
            outfit_analysis = await gemini_service.analyze_outfit(image_bytes, mime_type)
        except Exception:
            outfit_analysis = ""

    prompt = f"""
You are PocketSmart AI, a budget-aware jewelry recommendation assistant.
User request:
{req.model_dump_json(indent=2)}

Optional outfit analysis:
{outfit_analysis}

Return JSON only with:
title, summary, total_estimated_cost, budget, budget_remaining, allocations, recommendations, notes

recommendations fields:
name, category, platform, estimated_price, quantity, reason, search_url

Allowed platforms: Amazon, Flipkart.
Never identify the person in the image and never claim live inventory.
Use search URLs.
Keep total_estimated_cost <= budget.
"""
    try:
        result = await gemini_service.generate_json(prompt, image_bytes, mime_type) if gemini_service.enabled else {}
        return _clean_items(result, req.budget, "gemini") if result else _fallback_jewelry(req, outfit_analysis)
    except Exception:
        return _fallback_jewelry(req, outfit_analysis)


async def generate_recommendation(planner: str, request_data: Any, image_bytes: bytes | None = None, mime_type: str = "image/jpeg") -> dict:
    if planner == "home":
        return await generate_home(request_data)
    if planner == "party":
        return await generate_party(request_data)
    if planner == "jewelry":
        return await generate_jewelry(request_data, image_bytes, mime_type)
    raise ValueError("Unsupported planner.")
