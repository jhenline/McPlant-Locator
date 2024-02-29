import json
import csv
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Path to cache file
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


# Initialize geolocator
geolocator = Nominatim(user_agent="zip_code_locator")


# Get the coordinates (latitude and longitude) and address
# for a given zip code. The country defaults to "USA" if not specified.
def get_coordinates(zip_code, country="USA", cache=None):
    # If no cache dictionary is provided, initialize an empty one.
    # This is used to store and retrieve results for zip codes that have already been queried.
    if cache is None:
        cache = {}

    # Check if the zip code is already in the cache.
    # If it is, return the cached result immediately without performing a new lookup.
    if zip_code in cache:
        return cache[zip_code]

    # Attempt to retrieve the location information for the given zip code and country.
    try:
        # Use the geolocator's geocode method to fetch the location data.
        # The addressdetails=True parameter requests additional address information.
        location = geolocator.geocode(f"{zip_code}, {country}", addressdetails=True)

        # Check if a location was successfully retrieved.
        if location:
            # If a location is found, store its latitude, longitude, and address
            # in the cache dictionary using the zip code as the key.
            cache[zip_code] = (location.latitude, location.longitude, location.address)
            # Return the location data.
            return cache[zip_code]
    # Catch specific exceptions related to geolocation service timeouts or errors.
    except (GeocoderTimedOut, GeocoderServiceError):
        # If an exception occurs, do nothing (pass) and proceed to return None values.
        pass

    # If the location could not be retrieved (either because of an exception or because
    # the location is not found), return None for latitude, longitude, and address.
    return None, None, None


def clean_zip_code(zip_code):
    return zip_code.split('-')[0]


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

