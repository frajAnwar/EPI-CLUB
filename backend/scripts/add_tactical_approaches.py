
import json
from dungeons.models import TacticalApproach

tactical_approaches = [
    {
        "name": "Calculated Risk",
        "category": "High-Risk",
        "description": "Slightly increase rewards for this floor, but also slightly increase encounter power.",
        "effects": [
            {"type": "LOOT_MODIFIER", "stat": "GameCoinReward", "operation": "MULTIPLY", "target": "ALL_ENCOUNTERS_ON_FLOOR", "value": 1.2},
            {"type": "ENCOUNTER_MODIFIER", "stat": "EncounterPower", "operation": "MULTIPLY", "target": "ALL_ENCOUNTERS_ON_FLOOR", "value": 1.1}
        ]
    },
    {
        "name": "Resourceful Scavenging",
        "category": "Economic",
        "description": "Significantly increases the chance to find crafting materials on this floor.",
        "effects": [
            {"type": "LOOT_MODIFIER", "stat": "CraftingMaterialDropRate", "operation": "ADD", "target": "ALL_ENCOUNTERS_ON_FLOOR", "value": 0.25}
        ]
    },
    {
        "name": "Head-On Assault",
        "category": "Brute Force",
        "description": "A straightforward power boost for the next encounter.",
        "effects": [
            {"type": "PLAYER_MODIFIER", "stat": "PlayerPower", "operation": "ADD", "target": "NEXT_ENCOUNTER_ONLY", "value": 20}
        ]
    },
    {
        "name": "Swift and Silent",
        "category": "Stealth & Speed",
        "description": "A small chance to bypass the next encounter entirely.",
        "effects": [
            {"type": "RULE_MODIFIER", "condition": "BYPASS_ENCOUNTER_CHANCE", "target": "ALL_ENCOUNTERS_ON_FLOOR", "value": 0.1}
        ]
    },
    {
        "name": "Guardian's Bane",
        "category": "Strategic",
        "description": "Significantly weaken the Floor Guardian.",
        "effects": [
            {"type": "ENCOUNTER_MODIFIER", "stat": "EncounterPower", "operation": "MULTIPLY", "target": "FLOOR_GUARDIAN_ONLY", "value": 0.8}
        ]
    },
    {
        "name": "Treasure Hunter's Instinct",
        "category": "Economic",
        "description": "A small chance for a massive GameCoin bonus from the next encounter.",
        "effects": [
            {"type": "LOOT_MODIFIER", "stat": "GameCoinReward", "operation": "MULTIPLY", "target": "NEXT_ENCOUNTER_ONLY", "value": 5.0},
            {"type": "LOOT_MODIFIER", "stat": "GameCoinReward", "operation": "ADD", "target": "NEXT_ENCOUNTER_ONLY", "value": 1000}
        ]
    },
    {
        "name": "Defensive Stance",
        "category": "Strategic",
        "description": "Greatly reduces the power of the next encounter, but also reduces your power.",
        "effects": [
            {"type": "ENCOUNTER_MODIFIER", "stat": "EncounterPower", "operation": "MULTIPLY", "target": "NEXT_ENCOUNTER_ONLY", "value": 0.5},
            {"type": "PLAYER_MODIFIER", "stat": "PlayerPower", "operation": "MULTIPLY", "target": "NEXT_ENCOUNTER_ONLY", "value": 0.8}
        ]
    },
    {
        "name": "Berserker's Rage",
        "category": "High-Risk",
        "description": "Massive power boost for the entire floor, but you lose 1 Anima.",
        "effects": [
            {"type": "PLAYER_MODIFIER", "stat": "PlayerPower", "operation": "ADD", "target": "ALL_ENCOUNTERS_ON_FLOOR", "value": 75},
            {"type": "PLAYER_MODIFIER", "stat": "Anima", "operation": "ADD", "target": "IMMEDIATE", "value": -1}
        ]
    },
    {
        "name": "Master Scout",
        "category": "Stealth & Speed",
        "description": "Reveal all information about the next floor's encounters.",
        "effects": [
            {"type": "RULE_MODIFIER", "condition": "REVEAL_FLOOR_INFO", "target": "NEXT_FLOOR", "value": 1}
        ]
    },
    {
        "name": "Floor Clearer",
        "category": "Brute Force",
        "description": "A moderate power boost that lasts for the entire floor.",
        "effects": [
            {"type": "PLAYER_MODIFIER", "stat": "PlayerPower", "operation": "ADD", "target": "ALL_ENCOUNTERS_ON_FLOOR", "value": 35}
        ]
    }
]

for approach_data in tactical_approaches:
    TacticalApproach.objects.update_or_create(
        name=approach_data["name"],
        defaults={
            "category": approach_data["category"],
            "description": approach_data["description"],
            "effects": json.dumps(approach_data["effects"])
        }
    )
    print(f"Added/Updated: {approach_data['name']}")

print("--- Tactical approaches script finished ---")
