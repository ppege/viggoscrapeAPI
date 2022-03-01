import json

with open("values.json", "r") as file:
  data = json.load(file)

def sum_of_list(l):
  total = 0
  for val in l:
    total = total + val
  return total

for key in data:
  demand = data[key]["DEMAND"]
  demand = demand.replace(u"\u2605", "1").replace(u"\u2606", "0").replace("NOT TRADABLE", "0").replace("???", "0")
  demand = list(demand)
  demand = [int(i) for i in demand]
  data[key]["DEMANDNUMBER"] = sum_of_list(demand)

with open("values.json", "w") as file:
  json.dump(data, file, indent=4)