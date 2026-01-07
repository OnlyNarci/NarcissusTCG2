from enum import StrEnum


class RouteType(StrEnum):
    TOURIST = 'tourist'
    CARD = 'card'
    GROUP = 'group'
    RESTAURANT = 'restaurant'
    STORE = 'store'
    USER = 'user'


class NarcissusRoute:
    def __init__(self, routes: str, route_type: RouteType):
        self.routes = routes
        self.route_type = route_type
    
    def __str__(self):
        return "/" + self.routes


tourist_routes = {'help', 'ping', 'echo', '注册', '开始营业', '小姚闭嘴'}
    