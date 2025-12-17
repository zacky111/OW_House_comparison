"""
Skrypt do:
- dodania kolumny 'Developer' do istniejącego house_data.csv (15 fikcyjnych firm o różnych udziałach)
- wygenerowania opinii lokatorów (różna liczba opinii na mieszkanie w zakresie 0-8)
Pliki wyjściowe:
- house_data_with_devs.csv
- house_reviews.csv
Uruchomienie: python data_creation.py
"""
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

def get_developers():
    # 15 firm o różnej popularności (wagi sumują się do 1)
    devs = [
        "Nova Estates", "Skyline Holdings", "GreenBrick", "Sunrise Group", "UrbanCore",
        "Horizon Builders", "BlueRiver Dev", "Pioneer Homes", "Oakfield Ltd", "MetroConstruct",
        "Stonegate", "EverHome", "Luna Developments", "Cedar & Co", "Atlas Properties"
    ]
    weights = np.array([0.20, 0.12, 0.10, 0.09, 0.08, 0.07, 0.06, 0.05, 0.05, 0.04, 0.04, 0.03, 0.03, 0.02, 0.02])
    weights = weights / weights.sum()
    return devs, weights

def assign_developers(houses_df):
    devs, weights = get_developers()
    houses_df = houses_df.copy()
    houses_df['Developer'] = np.random.choice(devs, size=len(houses_df), p=weights)
    return houses_df

def sample_reviews_for_house(row, review_id_start, min_rev=0, max_rev=8):
    """
    Generuje listę słowników (opinie) dla jednego wiersza domu (row).
    Zwraca (opinie_list, next_review_id)
    """
    n_reviews = np.random.randint(min_rev, max_rev+1)
    opinions = []
    # korelacja: Condition => średnie zadowolenia
    cond_mean = {'Excellent': 4.4, 'Good': 4.0, 'Fair': 3.2, 'Poor': 2.5}
    cond = row.get('Condition', 'Good')
    sat_mu = cond_mean.get(cond, 3.5)

    # lokalizacja => średni hałas
    noise_mu_map = {'Downtown': 3.6, 'Urban': 3.1, 'Suburban': 2.6, 'Rural': 1.8}
    noise_mu = noise_mu_map.get(row.get('Location', 'Urban'), 3.0)

    reviewer_types = ['Single', 'Couple', 'Family', 'Student', 'Retiree', 'Professional']
    reviewer_weights = [0.18, 0.22, 0.25, 0.10, 0.10, 0.15]

    comments_pos = [
        "Bardzo zadowolony/a, świetna lokalizacja.",
        "Czysto, wygodnie, polecam.",
        "Dobre zarządzanie, szybkie reakcje na zgłoszenia."
    ]
    comments_neu = [
        "Ogólnie ok, drobne uwagi.",
        "Przeciętnie, nic specjalnego.",
        "Są rzeczy do poprawy, ale da się mieszkać."
    ]
    comments_neg = [
        "Dużo hałasu, niepolecam.",
        "Problemy z utrzymaniem, długo czekano na naprawy.",
        "Sąsiedzi sprawiają problemy."
    ]

    for i in range(n_reviews):
        # Satisfaction 1-5 (gauss, sklejone do 1..5)
        sat = int(np.clip(np.round(np.random.normal(sat_mu, 0.7)), 1, 5))
        noise = int(np.clip(np.round(np.random.normal(noise_mu, 1.0)), 1, 5))
        neighbors = int(np.clip(np.round(np.random.normal(3.5, 1.0)), 1, 5))
        maintenance = int(np.clip(np.round(np.random.normal(3.5, 1.0)), 1, 5))
        reviewer = np.random.choice(reviewer_types, p=reviewer_weights)

        # zamiast tekstowego komentarza generujemy ocenę komentarza (1-5), skorelowaną z satysfakcją
        comment_score = int(np.clip(np.round(np.random.normal(sat, 0.6)), 1, 5))

        # losowa data w przeciągu ostatnich 8 lat
        end = datetime.now()
        start = end.replace(year=max(2015, end.year-8))
        rand_days = np.random.randint(0, (end - start).days + 1)
        review_date = (start + timedelta(days=int(rand_days))).date().isoformat()

        opinions.append({
            "ReviewId": review_id_start,
            "HouseId": int(row.get('Id')),
            "Developer": row.get('Developer'),
            "ReviewerType": reviewer,
            "Satisfaction": sat,
            "Noise": noise,
            "Neighbors": neighbors,
            "Maintenance": maintenance,
            "CommentScore": comment_score,
            "Date": review_date
        })
        review_id_start += 1

    return opinions, review_id_start

def generate_reviews(houses_df, min_rev=0, max_rev=8):
    reviews = []
    review_id = 1
    for _, row in houses_df.iterrows():
        revs, review_id = sample_reviews_for_house(row, review_id, min_rev=min_rev, max_rev=max_rev)
        reviews.extend(revs)
    reviews_df = pd.DataFrame(reviews)
    return reviews_df

def main():
    base = Path(__file__).resolve().parent
    in_path = base / "house_data.csv"
    if not in_path.exists():
        print(f"Nie znaleziono pliku źródłowego: {in_path}")
        return

    houses = pd.read_csv(in_path)
    print(f"Wczytano {len(houses)} wierszy z {in_path.name}")

    # 1) przypisz developerów i zapisz nowy CSV
    houses_with_devs = assign_developers(houses)
    out_houses = base / "house_data_with_devs.csv"
    houses_with_devs.to_csv(out_houses, index=False)
    print(f"Zapisano: {out_houses.name}")

    # 2) wygeneruj opinie (0-8 na mieszkanie) i zapisz CSV
    reviews = generate_reviews(houses_with_devs, min_rev=0, max_rev=8)
    out_reviews = base / "house_reviews.csv"
    if not reviews.empty:
        reviews.to_csv(out_reviews, index=False)
    else:
        # zapisz pusty plik z nagłówkami, jeśli brak opinii
        pd.DataFrame(columns=["ReviewId","HouseId","Developer","ReviewerType","Satisfaction","Noise","Neighbors","Maintenance","CommentScore","Date"]).to_csv(out_reviews, index=False)
    print(f"Zapisano: {out_reviews.name} (liczba opinii: {len(reviews)})")

if __name__ == "__main__":
    main()