import asyncio
import json
from tortoise import Tortoise
from db.models import Card
from core.config import TORTOISE_ORM_CONFIG


async def init_db():
    await Tortoise.init(config=TORTOISE_ORM_CONFIG)
    
    
async def main():
    await init_db()
    with open('D:\\SFW\\python_learning\\NoneBotProject\\NarcissusTCG2\\static\\base_card_design.json', 'r', encoding='utf-8') as f:
        cards = json.load(f)
    for card in cards:
        await Card.create(
            id=card['id'],
            name=card['name'],
            rarity=card['rarity'],
            package=card['package'],
            unlock_level=1,
            description=card['description'],
            compose_materials=card['compose_materials'],
            decompose_materials=card['decompose_materials'],
        )
    await Tortoise.close_connections()


asyncio.run(main())
