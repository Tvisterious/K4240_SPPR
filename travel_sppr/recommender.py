import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class Recommender:
    def __init__(self):
        self.comfort_map = {'Эконом': 0.2, 'Средний': 0.5, 'Премиум': 1.0}

    def _get_user_vector(self, profile):
        budget_norm = min((profile['budget'] / profile['people']) / 100000.0, 1.0)
        comfort = self.comfort_map.get(profile.get('comfort_level', 'Средний'), 0.5)
        
        return np.array([
            1.0 if profile.get('wants_beach') else 0.0,
            1.0 if profile.get('has_children') else 0.0,
            budget_norm,
            comfort
        ]).reshape(1, -1)

    def _get_city_vector(self, city, price, cities):
        price_norm = min(price / 100000.0, 1.0)
        t = cities[city]
        
        return np.array([
            1.0 if t['beach'] else 0.0,
            1.0 if t['child_ok'] else 0.0,
            price_norm,
            t['comfort']
        ]).reshape(1, -1)

    def recommend(self, valid_cities, profile, costs, cities, top_n=3):
        user_vec = self._get_user_vector(profile)
        results = []

        for city in valid_cities:
            price = costs.get(city, 50000)
            city_vec = self._get_city_vector(city, price, cities)
            
            score = cosine_similarity(user_vec, city_vec)[0][0]
            
            if profile.get('comfort_level') == 'Премиум' and profile['budget'] > 150000:
                if city in ['Дубай', 'Анталья']:
                    score = min(score + 0.1, 1.0)

            reasons = []
            if profile.get('wants_beach') and cities[city]['beach']:
                reasons.append("есть пляж")
            if profile.get('has_children') and cities[city]['child_ok']:
                reasons.append("подходит для детей")
            if price * profile['people'] <= profile['budget']:
                reasons.append("укладывается в бюджет")
                
            explanation = f"Совпадение {int(score*100)}%. " + (", ".join(reasons) if reasons else "Базовые критерии")
            
            results.append({
                'city': city,
                'score': round(float(score), 3),
                'price': price,
                'total_cost': price * profile['people'],
                'explanation': explanation
            })

        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_n]