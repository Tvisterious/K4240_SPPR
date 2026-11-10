import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from .data import generate_synthetic_data

class FlightPricePredictor:
    def __init__(self, data_path='flight_prices.csv', model_path='rf_model.pkl', features_path='rf_features.pkl'):
        self.data_path = data_path
        self.model_path = model_path
        self.features_path = features_path
        self.model = None
        self.features = None
        self._init_model()

    def _init_model(self):
        generate_synthetic_data(self.data_path)
        try:
            self.model = joblib.load(self.model_path)
            self.features = joblib.load(self.features_path)
        except FileNotFoundError:
            self._train_model()

    def _train_model(self):
        df = pd.read_csv(self.data_path)
        df_encoded = pd.get_dummies(df, columns=['destination'], drop_first=False)
        
        X = df_encoded.drop(['price', 'date'], axis=1)
        y = df_encoded['price']
        
        self.features = X.columns.tolist()
        self.model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        self.model.fit(X, y)
        
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.features, self.features_path)

    def predict(self, destination, month, day_of_week):
        if destination not in [f.replace('destination_', '') for f in self.features if f.startswith('destination_')]:
            return 50000  # Заглушка, если города нет в модели (не должно срабатывать при правильной логике)

        is_weekend = 1 if day_of_week >= 5 else 0
        input_df = pd.DataFrame({
            'month': [month],
            'day_of_week': [day_of_week],
            'is_weekend': [is_weekend]
        })
        
        for col in self.features:
            if col.startswith('destination_'):
                city_name = col.replace('destination_', '')
                input_df[col] = 1 if city_name == destination else 0
                
        input_df = input_df[self.features]
        prediction = self.model.predict(input_df)[0]
        return int(prediction)