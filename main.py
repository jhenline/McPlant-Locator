import json
import csv
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Path to cache file where zip code and location data are stored to avoid redundant lookups.
cache_file_path = 'zip_code_cache.json'


# Load or initialize cache from a JSON file to improve performance by reducing the number of API calls.
def load_cache():
    try:
        with open(cache_file_path, 'r') as cache_file:
            return json.load(cache_file)
    except FileNotFoundError:
        # Return an empty dictionary if the cache file does not exist, indicating no cache is available.
        return {}


# Save cache to file by writing the current state of the cache dictionary to a JSON file.
def save_cache(cache):
    with open(cache_file_path, 'w') as cache_file:
        json.dump(cache, cache_file)


# Initialize geolocator with a specific user agent; required by Nominatim's usage policy.
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


# Remove any potential additional information from the zip code to ensure consistency.
def clean_zip_code(zip_code):
    return zip_code.split('-')[0]


# Read zip codes and their corresponding addresses from a CSV file.
def read_zip_codes_from_csv(file_path):
    locations = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            address = {
                "full_address": f"{row['Address']}, {row['City']}, {row['State']}",
                "zip_code": clean_zip_code(row['Zip'].strip())
            }
            locations.append(address)
    return locations


# Calculate the distance in miles between two sets of coordinates using the geodesic method.
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
        mcplant_locations = read_zip_codes_from_csv("mcplant_locations_feb_2024.csv")
        for location in mcplant_locations:
            zip_code = location["zip_code"]
            full_address = location["full_address"]
            coordinates = get_coordinates(zip_code, cache=zip_code_cache)
            if coordinates:
                distance = calculate_distance(home_coordinates, coordinates)
                if distance is not None:
                    distances.append((distance, full_address, coordinates[2]))

        distances.sort(key=lambda x: x[0])
        print(f"Top 3 closest McDonalds locations offering the McPlant to {home_zip_code}:")
        for i, (distance, full_address, _) in enumerate(distances[:3], 1):
            print(f"{i}. {full_address} - Distance: {distance:.2f} miles")

    save_cache(zip_code_cache)


if __name__ == "__main__":
    main()
