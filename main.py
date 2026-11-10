from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import shutil
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from travel_sppr.core import TravelSPPR
from travel_sppr.data import load_cities, save_cities
from travel_sppr.predictor import FlightPricePredictor

app = FastAPI(title="Travel SPPR")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

sppr = TravelSPPR()
os.makedirs("static", exist_ok=True)

class UserProfile(BaseModel):
    budget: int
    people: int
    season: str
    has_children: bool
    has_car: bool
    wants_beach: bool
    comfort_level: str
    month: int
    day_of_week: int

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

@app.post("/api/recommend")
async def recommend(profile: UserProfile):
    result = sppr.get_recommendations(profile.dict(), profile.month, profile.day_of_week)
    return result

@app.get("/api/cities")
async def get_cities():
    return load_cities()

@app.post("/api/cities")
async def add_city(city_name: str = Form(...), transport: str = Form(...), comfort: float = Form(...), price: int = Form(...), beach: bool = Form(False), child_ok: bool = Form(False), car_needed: bool = Form(False)):
    cities = load_cities()
    cities[city_name] = {
        "beach": beach, "child_ok": child_ok, "car_needed": car_needed,
        "comfort": comfort, "transport": transport, "base_price": price
    }
    save_cities(cities)
    return {"status": "success"}

@app.delete("/api/cities/{city_name}")
async def delete_city(city_name: str):
    cities = load_cities()
    if city_name in cities:
        del cities[city_name]
        save_cities(cities)
        return {"status": "success"}
    return {"status": "error", "message": "Not found"}

@app.post("/api/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
    file_location = f"custom_dataset.csv"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    sppr.predictor = FlightPricePredictor(data_path=file_location)
    sppr.predictor._train_model()
    return {"status": "success", "message": "Модель переобучена"}

@app.get("/api/charts/{chart_type}")
async def get_chart(chart_type: str):
    df = pd.read_csv(sppr.predictor.data_path)
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")
    
    if chart_type == "seasonality":
        pivot = df.pivot_table(index='month', columns='destination', values='price', aggfunc='mean')
        sns.lineplot(data=pivot, dashes=False, markers=True)
        plt.title('Сезонность цен')
        plt.xlabel('Месяц')
        plt.ylabel('Цена')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    elif chart_type == "distribution":
        sns.boxplot(data=df, x='destination', y='price')
        plt.title('Распределение цен')
        plt.xticks(rotation=45)
    
    plt.tight_layout()
    filepath = f"static/{chart_type}.png"
    plt.savefig(filepath, dpi=150)
    plt.close()
    return FileResponse(filepath)