import random
from datetime import datetime, UTC, date
from typing import List, Dict
from tortoise.transactions import atomic
from tortoise.exceptions import DoesNotExist
from core.extra_params import extra_params
from core.exceptions import UnAtomicError
from db.models import User, Card, UserCard, Order, Restaurant
from db.model_dependencies import OrderStatus, CardRarity, card_worth
from schemas.record_schemas import OrderParams
from schemas.card_schemas import UserCardParams


async def query_orders_service(user_id: int) -> List[OrderParams]:
    """
    查看待完成的订单，如果今日未创建过订单则创建
    
    :param user_id: 用户id
    
    :return:
    """
    # 1.查看所有今日创建的订单
    utc_today = datetime.now(UTC).date()
    local_today = date.today()
    orders = await Order.filter(
        user_id=user_id,
        created_at=utc_today,
    ).all()
    
    # 2.如果今日还未创建过订单，创建订单
    if not orders:
        epic_num = random.randint(2, extra_params.ORDER_PER_DAY)
        waiting_orders = await generate_order_service(
            user_id=user_id,
            number=epic_num,
            rarity=CardRarity.EPIC,
        )
        waiting_orders_legen = await generate_order_service(
            user_id=user_id,
            number=extra_params.ORDER_PER_DAY - epic_num,
            rarity=CardRarity.LEGENDARY
        )
        waiting_orders.extend(waiting_orders_legen)
    else:
        card_id_set = set()
        for order in orders:
            for card_id in order.require_cards.keys():
                card_id_set.add(int(card_id))
        cards = await Card.filter(id__in=card_id_set).values('id', 'name')
        card_name_map = {
            card['id']: card['name']
            for card in cards
        }
        waiting_orders: List[OrderParams] = [
            OrderParams(
                oder_id=order.id,
                require_cards={card_name_map[card_id]: num for card_id, num in order.require_cards.items()},
                byte=order.byte,
                exp=order.exp,
                expire_at=datetime(local_today.year, local_today.month, local_today.day+1, 8),
            )
            for order in orders if order.status == OrderStatus.WAITING
        ]

    return waiting_orders


async def query_history_order_service(
    user_id: int,
    trade_date: date
) -> List[OrderParams]:
    """
    查看指定日期的订单
    
    :param user_id: 用户id
    :param trade_date: 日期
    
    :return: 该日期的订单
    """
    orders = await Order.filter(
        user_id=user_id,
        created_at=trade_date,
    ).all()
    card_id_set = set()
    for order in orders:
        for card_id in order.require_cards.keys():
            card_id_set.add(int(card_id))
    cards = await Card.filter(id__in=card_id_set).values('id', 'name')
    card_name_map = {
        card['id']: card['name']
        for card in cards
    }
    return [
        OrderParams(
            order_id=order.id,
            require_cards={card_name_map[card_id]: num for card_id, num in order.require_cards.items()},
            byte=order.byte,
            exp=order.exp,
            status=order.status,
            expire_at=datetime(trade_date.year, trade_date.month, trade_date.day+1, 8),
        )
        for order in orders
    ]


async def generate_order_service(
    user_id: int,
    number: int,
    rarity: CardRarity,
) -> List[OrderParams]:
    """
    生成新订单

    :param user_id: 用户id
    :param number: 生成数量
    :param rarity: 订单的稀有度

    :return: 生成的新订单
    """
    today = date.today()
    user = await User.get(id=user_id)
    try:
        user_restaurant = await Restaurant.get(user_id=user_id)
    except DoesNotExist:
        raise ValueError('restaurant not open')
    
    main_cards = await Card.filter(
        rarity=rarity,
        package=user_restaurant.main_business.value,
        unlock_level__lte=user.level
    ).values('id', 'name')
    side_cards = await Card.filter(
        rarity__lte=rarity,
        package=user_restaurant.main_business.value,
        unlock_level__lt=user.level
    ).values('id', 'name', 'rarity')
    
    new_orders: List[OrderParams] = []
    for _ in range(number):
        total_worth = 0
        # 一道主菜
        main_card = random.choice(main_cards)
        require_cards = {str(main_card['id']): 1}
        card_map = {str(main_card['id']): main_card['name']}
        total_worth += card_worth[rarity]
        
        # 1-4道配菜
        side_card_count = random.randint(1, 4)
        selected_side_cards = random.sample(side_cards, side_card_count)
    
        for card in selected_side_cards:
            card_num = random.randint(1, 3)
            require_cards[str(card['id'])] = card_num
            total_worth += card_worth[card.get('rarity')] * card_num
        
        byte_percent = random.uniform(0.3, 0.6)
        order_byte = int(byte_percent * total_worth)
        order_exp = total_worth - order_byte
        
        new_order = await Order.create(
            user_id=user_id,
            require_card=require_cards,
            byte=order_byte,
            exp=order_exp,
            status=OrderStatus.WAITING,
        )
    
        new_orders.append(
            OrderParams(
                order_id=new_order.id,
                require_cards={card_map[card_id]: num for card_id, num in require_cards.items()},
                byte=order_byte,
                exp=order_exp,
                expire_at=datetime(today.year, today.month, today.day+1, 8),
            )
        )
    return new_orders
    

@atomic()
async def complete_order_service(
    user_id: int,
    order_id: int,
) -> Dict[str, int]:
    """
    完成订单、交付卡牌、获取经验和比特
    
    :param user_id: 用户id
    :param order_id: 要交付的订单id
    
    :return: 无法完成订单返回缺少的卡牌
    """
    today = datetime.now(UTC).date()
    # 1.检查目标交付的订单存在
    order_to_complete = await Order.filter(
        id=order_id,
        user_id=user_id,
        status=OrderStatus.WAITING,
        created_at=today,
    ).select_for_update().first()
    if not order_to_complete:
        raise UnAtomicError(message='order not found')
    
    # 2.检查用户有足量卡牌可交付，没有则返回缺少的卡牌
    # 提前准备需要的卡牌参数
    cards = await Card.filter(
        card_id__in=list(order_to_complete.require_cards.keys())
    ).all()
    card_map = {
        card.id: card
        for card in cards
    }
    user_cards = await UserCard.filter(
        user_id=user_id,
        card_id__in=list(order_to_complete.require_cards.keys())
    ).select_for_update().select_related('card').all()
    user_card_map = {
        user_card.card.id: user_card
        for user_card in user_cards
    }
    
    lack_cards: List[UserCardParams] = []
    to_update_cards: List[UserCard] = []
    # 记录缺少的卡牌
    for require_card_id, require_number in order_to_complete.require_cards.items():
        require_card_id = int(require_card_id)
        if require_card_id not in user_card_map:
            lack_number = require_number
        elif user_card_map[require_card_id].number < require_number:
            lack_number = require_number - user_card_map[require_card_id].number
        elif user_card_map[require_card_id].number == require_number:
            lack_number = 0
            to_order_card = user_card_map[require_card_id]
            await to_order_card.delete()
        else:
            lack_number = 0
            to_order_card = user_card_map[require_card_id]
            to_order_card.number -= require_number
            to_update_cards.append(to_order_card)
            
        if lack_number != 0:
            lack_cards.append(UserCardParams(
                card_id=require_card_id,
                name=card_map[require_card_id].name,
                image=card_map[require_card_id].image,
                rarity=card_map[require_card_id].rarity,
                package=card_map[require_card_id].package,
                unlock_level=card_map[require_card_id].unlock_level,
                description=card_map[require_card_id].description,
                number=lack_number,
            ))
    if lack_cards:
        raise UnAtomicError(message='lack cards', lack_cards=lack_cards)
    
    # 3.扣除用户交付的卡牌
    await UserCard.bulk_update(to_update_cards, fields=['number'])
    
    # 4.修改订单状态为完成
    order_to_complete.status = OrderStatus.CONFIRM
    await order_to_complete.save()
    
    # 5.为用户增加经验和比特
    user = await User.get(id=user_id)
    user.exp += order_to_complete.exp
    user.byte += order_to_complete.byte
    await user.save()
    
    return {
        'exp': order_to_complete.exp,
        'byte': order_to_complete.byte
    }


@atomic()
async def generate_new_order_service(
    user_id: int,
    number: int,
    rarity: CardRarity,
) -> List[OrderParams]:
    """
    用户主动创建新订单服务
    
    :param user_id: 用户id
    :param number: 新订单数量
    :param rarity: 目标订单稀有度，创建史诗订单消耗10比特，创建传说订单消耗30比特
    
    :return: 新的订单
    """
    user = await User.get(id=user_id)
    if rarity == CardRarity.EPIC:
        user.byte -= number * 10
    elif rarity == CardRarity.LEGENDARY:
        user.byte -= number * 30
    else:
        raise ValueError(f'rarity {rarity} not supported')
    
    new_orders = await generate_order_service(
        user_id=user_id,
        number=number,
        rarity=rarity,
    )
    return new_orders
    