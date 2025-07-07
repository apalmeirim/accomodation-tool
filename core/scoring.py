def default_score(distance_km:float,
                  price:float,
                  n_count:int) -> float:
    
    return (5 - distance_km) + (n_count * 2) - (price / 10000)