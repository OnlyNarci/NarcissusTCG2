import random
from typing import List, Dict, Optional
from collections import defaultdict
from tortoise.queryset import Q
from tortoise.transactions import atomic
from tortoise.exceptions import DoesNotExist
from core.exceptions import UnAtomicError
from db.models import User, Card, UserCard
from db.model_dependencies import CardRarity, Package
from schemas.card_schemas import UserCardParams


async def get_box_service(
    user_id: int,
    name_in: Optional[str] = None,
    rarity: Optional[CardRarity] = None,
    package: Optional[Package] = None,
) -> List[UserCardParams]:
    """
    查看符合条件的个人持有卡牌
    
    :param user_id: 用户id，必须参数
    :param name_in: 卡牌名称包含的字符串，可选参数
    :param rarity: 卡牌稀有度，可选参数
    :param package: 卡牌包名称，可选参数
    
    :return: 符合条件的持有卡牌列表
    """
    query = Q(user_id=user_id)
    
    if name_in is not None:
        query &= Q(card__name__icontains=name_in)
    if rarity is not None:
        query &= Q(card__rarity=rarity)
    if package is not None:
        query &= Q(card__package=package)
        
    card_items = await UserCard.filter(query).select_related('card').all()
    
    if not card_items:
        return []
    
    cards = [
        UserCardParams(
            card_id=user_card.card.id,
            name=user_card.card.name,
            image=user_card.card.image,
            rarity=user_card.card.rarity,
            package=user_card.card.package,
            description=user_card.card.description,
            number=user_card.number,
        )
        for user_card in card_items
    ]
    cards = sorted(cards, key=lambda c: c.rarity.value, reverse=True)
    return cards


@atomic()
async def pull_card_service(
    user_id: int,
    package: Package,
    times: int
) -> List[UserCardParams]:
    """
    用户在指定扩展包抽指定次数的卡，扣除time*10的比特
    
    :param user_id: 用户id
    :param package: 玩家要抽的卡牌包
    :param times: 抽卡次数
    
    :return: 抽卡是否成功，失败 raise UnAtomicError，成功返回获取到的卡牌
    """
    def generate_random_number(n: int) -> List[int]:
        """
        生成n个随机数：75% 的概率返回 1, 20% 的概率返回 2, 4% 的概率返回 3, 1% 的概率返回 4
        """
        numbers = [1, 2, 3, 4]
        weights = [75, 20, 4, 1]

        result = random.choices(numbers, weights=weights, k=n)
        
        return result
    
    # 1.确认玩家比特充足并扣除相应比特
    need_byte = times * 10
    user = await User.filter(id=user_id).select_for_update().first()
    if user.byte < need_byte:
        raise UnAtomicError(message='byte not enough', required_byte=need_byte)
    
    user.byte -= need_byte
    await user.save()
    
    # 2.随机生成抽到的稀有度
    rarity_list = generate_random_number(times)
    rarity_set = set(rarity_list)
    
    # 3.查询所有符合稀有度的卡牌，并按照稀有度分组
    all_available_card = await Card.filter(
        package=package,
        rarity__in=rarity_set,
        unlock_level__gte=user.level
    ).all()
    cards_by_rarity: Dict[int, List[Card]] = defaultdict(list)
    for card in all_available_card:
        cards_by_rarity[card.rarity].append(card)
    
    # 4.遍历稀有度列表，为每次抽卡随机选择对应稀有度的卡牌，并记录每张卡牌抽到的次数
    drawn_cards: Dict[int, UserCardParams] = {}
    
    for rarity in rarity_list:
        available_cards = cards_by_rarity.get(rarity)
        selected_card: Card = random.choice(available_cards)
        if selected_card.id in drawn_cards:
            drawn_cards[selected_card.id].number += 1
        else:
            user_card = UserCardParams(
                card_id=selected_card.id,
                name=selected_card.name,
                image=selected_card.image,
                rarity=selected_card.rarity,
                package=selected_card.package,
                description=selected_card.description,
                number=1
            )
            drawn_cards[selected_card.id] = user_card
    
    # 5.根据本次抽到的卡牌id，查询用户已有的卡牌方便后续更新操作
    existing_user_cards = await UserCard.filter(
        user_id=user_id,
        card_id__in=list(drawn_cards.keys())
    ).select_for_update().select_related('card').all()
    if existing_user_cards:
        existing_card_dict = {uc.card.id: uc for uc in existing_user_cards}
    else:
        existing_card_dict = {}
    
    # 6.区分需要更新和创建的卡牌
    to_update = []
    to_create = []
    for card_id, drawn_card in drawn_cards.items():
        if card_id in existing_card_dict:
            # 如果已存在，则更新数量
            existing_card = existing_card_dict[card_id]
            existing_card.number += drawn_card.number
            to_update.append(existing_card)
        else:
            # 如果不存在，则准备创建新记录
            to_create.append(UserCard(
                user_id=user_id,
                card_id=card_id,
                number=drawn_card.number,
            ))
    
    # 7.执行数据库更新操作
    if to_update:
        await UserCard.bulk_update(to_update, fields=['number'])
    if to_create:
        await UserCard.bulk_create(to_create)

    return sorted(list(drawn_cards.values()), key=lambda c: c.rarity.value, reverse=True)


@atomic()
async def compose_card_service(
    user_id: int,
    card_to_compose: str,
    number: int
) -> None:
    """
    合成卡牌
    :param user_id: 玩家id
    :param card_to_compose: 目标合成的卡牌（必须是全名）
    :param number: 合成数量
    """
    user = await User.get(id=user_id)
    # 1.检查目标卡牌是否存在且可合成
    try:
        card = await Card.get(name=card_to_compose)
    except DoesNotExist:
        raise UnAtomicError(message='card not found')

    if not card.compose_materials:
        raise UnAtomicError(message='not allow compose')
    elif card.unlock_level > user.level:
        raise UnAtomicError(message='level not enough', unlock_level=card.unlock_level)

    required_materials = {
        int(card_id): num * number
        for card_id, num in card.compose_materials.items()
    }
    required_card_ids = set(required_materials.keys())

    # 2.加行锁查询用户所有相关材料卡
    user_materials = await UserCard.filter(
        user_id=user_id,
        card_id__in=required_card_ids
    ).select_related('card').select_for_update().all()
    user_materials_map = {
        uc.card.id: uc
        for uc in user_materials
    }

    # 3.检查用户材料是否充足，并进行分组，后续直接使用前面查询到的模型操作，避免重复io
    lack_materials = []
    to_update = []
    to_delete = []
    
    for card_id, need_num in required_materials.items():
        user_card = user_materials_map.get(card_id)
        if not user_card:
            # 用户完全没有该材料卡
            lack_materials.append(UserCardParams(
                card_id=card_id,
                name=user_card.card.name,
                rarity=user_card.card.rarity,
                package=user_card.card.package,
                number=need_num,
            ))
        elif user_card.number < need_num:
            # 用户有该卡但数量不足
            lack_materials.append(UserCardParams(
                card_id=card_id,
                name=user_card.card.name,
                rarity=user_card.card.rarity,
                package=user_card.card.package,
                number=need_num,
            ))
        elif user_card.number == need_num:
            # 用户卡牌数量刚刚好，移除条目
            to_delete.append(user_card)
        else:
            # 用户卡牌数量有余，更新数量
            to_update.append(user_card)

    if lack_materials:
        raise UnAtomicError(message='materials not enough', lack_materials=lack_materials)

    # 4.扣减材料
    if to_update:
        await UserCard.bulk_update(to_update, fields=['number'])
    if to_delete:
        await UserCard.filter(id__in=[obj.id for obj in to_delete]).delete()

    # 5.添加目标卡牌
    user_compose_card, created = await UserCard.get_or_create(
        user_id=user_id,
        card_id=card.id,
        defaults={"number": 0}
    )
    user_compose_card.number += number
    await user_compose_card.save()

    return None


@atomic()
async def decompose_card_service(
    user_id: int,
    card_to_decompose: str,
    number: int
) -> List[UserCardParams]:
    """
    分解卡牌
    
    :param user_id: 发起请求的用户id
    :param card_to_decompose: 目标分解的卡牌名称（必须是全名）
    :param number: 分解数量

    :return: 分解获得的卡牌
    """
    # 1.确认卡牌存在且可分解
    try:
        card = await Card.get(name=card_to_decompose)
    except DoesNotExist:
        raise UnAtomicError(message='card not found')
    if not card.decompose_materials:
        raise UnAtomicError(message='not allow decompose')
    
    # 2.确认玩家持有目标分解的卡牌
    user_card = await UserCard.filter(
        user_id=user_id,
        card_id=card.id,
        number__gte=number
    ).select_for_update().select_related('card').first()
    if not user_card:
        raise UnAtomicError(message='require card')
        
    # 3.为玩家增加分解后获得的卡牌
    existing_user_cards = await UserCard.filter(
        user_id=user_id,
        card_id__in=list(user_card.card.decompose_materials.keys())
    ).select_for_update().select_related('card').all()
    existing_card_dict = {uc.card.id: uc for uc in existing_user_cards}
    
    to_update = []
    to_create = []
    for card_id, materials_number in user_card.card.decompose_materials.items():
        if card_id in existing_card_dict:
            # 如果已存在，则更新数量
            existing_card = existing_card_dict[card_id]
            existing_card.number += int(materials_number*number)
            to_update.append(existing_card)
        else:
            # 如果不存在，则准备创建新记录
            to_create.append(UserCard(
                user_id=user_id,
                card_id=card_id,
                number=int(materials_number*number),
            ))
    
    if to_update:
        await UserCard.bulk_update(to_update, fields=['number'])
    if to_create:
        await UserCard.bulk_create(to_create)
        
    # 4.拆线呢分解获得的卡牌信息
    decompose_materials_cards = await Card.filter(
        id__in=list(user_card.card.decompose_materials.keys())
    )
    
    # 5.扣减指定数量的目标分解卡牌，若扣减后数量为0则删除该条目
    user_card.number -= number
    if user_card.number == 0:
        await user_card.delete()
    else:
        await user_card.save()
        
    return [
        UserCardParams(
            card_id=card.id,
            name=card.name,
            image=card.image,
            rarity=card.rarity,
            package=card.package,
            description=card.description,
            number=user_card.card.decompose_materials[str(card.id)]*number
        )
        for card in decompose_materials_cards
    ]
