import json
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from predefined_zip_codes import predefined_zip_codes

# Path to cache file used for faster performance after initial run
cache_file_path = 'zip_code_cache.json'


# Load or initialize cache
def load_cache():
    try:
        with open(cache_file_path, 'r') as cache_file:
            return json.load(cache_file)
    except FileNotFoundError:
        return {}


# Save cache to file
def save_cache(cache):
    with open(cache_file_path, 'w') as cache_file:
        json.dump(cache, cache_file)


# Initialize geolocator once
geolocator = Nominatim(user_agent="zip_code_locator")


def get_coordinates(zip_code, country="USA", cache=None):
    if cache is None:
        cache = {}
    if zip_code in cache:
        return cache[zip_code]
    try:
        location = geolocator.geocode(f"{zip_code}, {country}", addressdetails=True)
        if location:
            cache[zip_code] = (location.latitude, location.longitude, location.address)
            return cache[zip_code]
    except (GeocoderTimedOut, GeocoderServiceError):
        pass
    return None, None, None


def clean_zip_code(zip_code):
    return zip_code.split('-')[0]


def calculate_distance(coords1, coords2):
    try:
        return geodesic((coords1[0], coords1[1]), (coords2[0], coords2[1])).miles
    except TypeError:
        return None


def main():
    zip_code_cache = load_cache()

    home_zip_code = input("Enter your home zip code: ").strip()
    home_zip_code_cleaned = clean_zip_code(home_zip_code)
    home_coordinates = get_coordinates(home_zip_code_cleaned, cache=zip_code_cache)

    if home_coordinates:
        distances = []
        for zip_code in predefined_zip_codes:
            zip_code_cleaned = clean_zip_code(zip_code)
            coordinates = get_coordinates(zip_code_cleaned, cache=zip_code_cache)
            if coordinates:
                distance = calculate_distance(home_coordinates, coordinates)
                if distance is not None:
                    distances.append((distance, zip_code, coordinates[2]))

        distances.sort(key=lambda x: x[0])
        print(f"Top 3 closest locations to {home_zip_code}:")
        for i, (distance, zip_code, location) in enumerate(distances[:3], 1):
            print(f"{i}. {zip_code} ({location}) - Distance: {distance:.2f} miles")

    save_cache(zip_code_cache)


if __name__ == "__main__":
    main()

