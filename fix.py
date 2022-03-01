import json

with open("values.json", "r") as file:
  data = json.load(file)

for key in data:
  exotic_value = False
  if "Legendar" in str(data[key]["VALUE"]):
    exotic_value = int(data[key]["VALUE"][0])/6
  if "Common" in str(data[key]["VALUE"]):
    exotic_value = int(data[key]["VALUE"][0])/120
  if "Rare" in str(data[key]["VALUE"]):
    exotic_value = int(data[key]["VALUE"][0])/30
  if "Exotic" in str(data[key]["VALUE"]):
    exotic_value = int(data[key]["VALUE"][0])
  if isinstance(data[key]["VALUE"], int):
    exotic_value = int(data[key]["VALUE"])

  if not exotic_value:
    try:
      exotic_value = int(data[key]["VALUE"].replace(',', ''))
    except:
      exotic_value = "Unknown"
  data[key]["EXOTICVALUE"] = exotic_value

with open("values2.json", "w") as file:
  json.dump(data, file, indent=4)