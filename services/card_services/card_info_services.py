from typing import List, Dict, Optional
from tortoise.exceptions import DoesNotExist
from schemas.card_schemas import UserCardParams, CardParams
from db.models import Card, UserCard
from db.model_dependencies import Package


async def query_card_info_service(card_name: str) -> Optional[CardParams]:
    """
    查看指定卡牌的信息
    
    :param card_name: 卡牌名称(全名)
    
    :return:卡牌信息模型
    """
    try:
        card = await Card.get(name=card_name)
    except DoesNotExist:
        return None
    
    compose_materials = await Card.filter(id__in=[int(key) for key in card.compose_materials.keys()]).values('name')
    decompose_materials = await Card.filter(id__in=[int(key) for key in card.decompose_materials.keys()]).values('name')
    
    return CardParams(
        card_id=card.id,
        name=card.name,
        image=card.image,
        rarity=card.rarity,
        package=card.package,
        unlock_level=card.unlock_level,
        description=card.description,
        compose_materials={materials['name']: num for materials, num in zip(compose_materials, card.compose_materials.values())},
        decompose_materials={materials['name']: num for materials, num in zip(decompose_materials, card.decompose_materials.values())},
    )


async def query_package_catalog_service(
    user_id: int,
    package: Package
) -> Optional[Dict[str, int]]:
    """
    查看指定拓展包的全部可收集卡牌
    
    :param user_id: 用户id
    :param package: 扩展包名称
    """
    cards = await Card.filter(package=package).values('id', 'name')
    if not cards:
        return None
    user_cards = await UserCard.filter(
        user_id=user_id,
        card_id__in=[card['id'] for card in cards]
    ).values('card_id', 'number')
    user_card_dict = {card['card_id']: card['number'] for card in user_cards}
    
    cards.sort(key=lambda x: int(x['rarity']), reverse=True)
    catalog = {}
    for card in cards:
        catalog[card['name']] = user_card_dict.get(card['id'], 0)
    
    return catalog
    
    
async def query_card_compose_materials_service(card_id: int) -> List[UserCardParams] | str:
    """
    查看合成一张指定卡牌所需的材料

    :param card_id: 卡牌id

    :return: 合成所需材料
    """
    # 1.确认卡牌存在
    try:
        card = await Card.get(id=card_id)
    except DoesNotExist:
        return 'card not found'
    
    # 2.查询合成所需材料
    materials = await Card.filter(id__in=list(card.compose_materials.keys())).all()
    
    # 3.组织为UserCardParams返回
    compose_materials = []
    for material in materials:
        compose_materials.append(
            UserCardParams(
                card_id=material.id,
                name=material.name,
                image=material.image,
                rarity=material.rarity,
                package=material.package,
                unlock_level=material.unlock_level,
                description=material.description,
                number=card.compose_materials[material.id],
            )
        )
    return compose_materials
    

async def query_card_decompose_materials_service(card_id: int) -> List[UserCardParams] | str:
    """
    查看一张指定卡牌分解产物
    
    :param card_id: 卡牌id
    
    :return: 分解产物
    """
    try:
        card = await Card.get(id=card_id)
    except DoesNotExist:
        return 'card not found'
        
    # 2.查询分解获得材料
    products = await Card.filter(id__in=list(card.decompose_materials.keys())).all()
    
    # 3.组织为UserCardParams返回
    decompose_materials = []
    for product in products:
        decompose_materials.append(
            UserCardParams(
                card_id=product.id,
                name=product.name,
                image=product.image,
                rarity=product.rarity,
                package=product.package,
                unlock_level=product.unlock_level,
                description=product.description,
                number=card.compose_materials[product.id],
            )
        )
    return decompose_materials
