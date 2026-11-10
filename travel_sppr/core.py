from .predictor import FlightPricePredictor
from .knowledge_base import KnowledgeBase
from .recommender import Recommender
from .data import load_cities

class TravelSPPR:
    def __init__(self):
        self.predictor = FlightPricePredictor()
        self.kb = KnowledgeBase()
        self.recommender = Recommender()

    def _get_transport_costs(self, month, day_of_week, cities):
        costs = {}
        for city, traits in cities.items():
            if 'base_price' in traits and traits['base_price'] > 0:
                costs[city] = int(traits['base_price'])
            elif traits['transport'] == 'plane':
                costs[city] = self.predictor.predict(city, month, day_of_week)
            else:
                costs[city] = 5000
        return costs

    def get_recommendations(self, profile, month, day_of_week=5, top_n=3):
        cities = load_cities()
        costs = self._get_transport_costs(month, day_of_week, cities)

        valid_cities, rejected = self.kb.filter_cities(profile, costs, cities)

        if not valid_cities:
            return {
                'status': 'empty',
                'message': 'Нет подходящих направлений по заданным критериям.',
                'rejected': rejected
            }

        recommendations = self.recommender.recommend(valid_cities, profile, costs, cities, top_n)

        return {
            'status': 'success',
            'recommendations': recommendations,
            'rejected': rejected,
            'all_costs': costs
        }