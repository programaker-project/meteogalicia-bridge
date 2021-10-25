import meteogalicia

TEST_LOCATION = 36057
TEST_LOCATION_NAME = "Vigo"

print("Testing get_prediction for", TEST_LOCATION_NAME, "...")
print(meteogalicia.get_all_prediction(TEST_LOCATION, None))
print("")

print("Testing get_formatted_prediction for", TEST_LOCATION_NAME, "...")
print(meteogalicia.get_formatted_prediction(TEST_LOCATION, None))
print("")

print("Testing get_total_map")
print(meteogalicia.get_total_map(1, "1", None))
print("")
