class KnowledgeBase:
    def filter_cities(self, user_profile, costs, cities):
        valid = []
        rejected = {}

        for city, traits in cities.items():
            reason = None
            cost = costs.get(city, 50000)
            total_cost = cost * user_profile['people']

            if user_profile['season'] == 'Зима' and traits['beach']:
                reason = "Зимой пляжный отдых недоступен"
            elif not user_profile['has_car'] and traits['car_needed']:
                reason = "Требуется автомобиль для передвижения"
            elif user_profile['has_children'] and not traits['child_ok']:
                reason = "Не подходит для поездок с детьми"
            elif total_cost > user_profile['budget']:
                reason = f"Превышен бюджет (требуется {total_cost} руб.)"
            
            if reason:
                rejected[city] = reason
            else:
                valid.append(city)

        return valid, rejected