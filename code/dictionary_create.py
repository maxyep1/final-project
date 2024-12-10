import json
import pandas as pd

# 定义扩展的汽车部件数据
def get_auto_parts_data():
    return{
  "engine": [
    "engine", "motor", "engine block", "engine system",
    "cylinder", "piston", "crankshaft", "camshaft",
    "timing belt", "timing chain", "spark plug",
    "ignition coil", "valve", "oil pan", "flywheel",
    "intake manifold", "exhaust manifold", "fuel injector",
    "throttle body", "turbocharger", "supercharger",
    "engine mount", "cooling system", "radiator",
    "thermostat", "water pump"
  ],
  "transmission": [
    "transmission", "manual transmission", "automatic transmission",
    "transmission system", "clutch", "gearbox",
    "driveshaft", "differential", "axle", "cv joint",
    "torque converter", "shift linkage", "propeller shaft"
  ],
  "suspension": [
    "suspension", "shock absorber", "strut", "coil spring",
    "leaf spring", "control arm", "ball joint",
    "stabilizer bar", "sway bar", "tie rod", "wheel hub",
    "spindle"
  ],
  "steering": [
    "steering", "steering wheel", "rack and pinion",
    "power steering pump", "tie rod end", "pitman arm",
    "idler arm", "steering gearbox", "universal joint"
  ],
  "brakes": [
    "brake", "brake pedal", "brake pad", "brake rotor",
    "brake drum", "brake caliper", "master cylinder",
    "brake line", "abs system", "anti-lock braking system",
    "parking brake", "handbrake", "brake booster"
  ],
  "fuel_system": [
    "fuel system", "fuel tank", "fuel pump", "fuel injector",
    "fuel rail", "fuel filter", "fuel pressure regulator",
    "carburetor"
  ],
  "exhaust_system": [
    "exhaust system", "exhaust manifold", "catalytic converter",
    "muffler", "exhaust pipe", "oxygen sensor"
  ],
  "electrical_system": [
    "electrical system", "battery", "alternator", "starter motor",
    "wiring harness", "fuse box", "relay", "sensor",
    "ignition switch", "ecm", "engine control module",
    "tcm", "transmission control module"
  ],
  "climate_control": [
    "climate control", "ac compressor", "condenser", "evaporator",
    "heater core", "blower motor", "cabin air filter",
    "thermostat", "refrigerant line"
  ],
  "cooling_system": [
    "cooling system", "radiator", "radiator fan", "water pump",
    "coolant reservoir", "radiator hose", "heater core"
  ],
  "body_and_exterior": [
    "chassis", "frame", "hood", "trunk lid", "door", "fender",
    "bumper", "side mirror", "windshield", "window",
    "roof rack", "spoiler", "grille"
  ],
  "interior": [
    "seat", "seat belt", "dashboard", "center console",
    "gear lever", "pedal", "airbag", "glove compartment",
    "sun visor", "headliner", "floor mat"
  ],
  "lighting": [
    "light", "lighting system", "headlight", "taillight",
    "fog light", "brake light", "turn signal",
    "reverse light", "daytime running light", "interior dome light"
  ],
  "wheels_and_tires": [
    "wheel", "rim", "tire", "tire valve", "hubcap",
    "wheel bearing", "lug nut"
  ],
  "drivetrain": [
    "drivetrain", "driveshaft", "axle", "cv joint", "u-joint",
    "propeller shaft"
  ],
  "safety_systems": [
    "safety system", "airbag", "seat belt", "abs",
    "traction control", "electronic stability control",
    "lane departure warning", "blind spot detection"
  ],
  "adas": [
    "adas", "adas system", "adaptive cruise control",
    "lane keep assist", "parking sensor", "backup camera",
    "collision avoidance system", "autonomous emergency braking",
    "surround view camera"
  ],
  "miscellaneous": [
    "wiper blade", "windshield washer pump", "horn", "jack",
    "spare tire", "tool kit", "tow hook"
  ]
}



# Define a function to save data as a JSON file
def save_to_json(data, file_path):
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"JSON file saved to: {file_path}")

# Define a function to save data as a CSV file
def save_to_csv(data, file_path):
    # Convert data to a list format suitable for DataFrame
    csv_data = [{"Component": key, "Synonyms/Keywords": ", ".join(value)} for key, value in data.items()]
    df = pd.DataFrame(csv_data)
    df.to_csv(file_path, index=False)
    print(f"CSV file saved to: {file_path}")

# Main function
if __name__ == "__main__":
    # Retrieve data
    auto_parts_data = get_auto_parts_data()
    
    # Define save paths
    json_file_path = "data/auto_parts_synonyms.json"
    csv_file_path = "data/auto_parts_synonyms.csv"
    
    # Save data
    save_to_json(auto_parts_data, json_file_path)
    save_to_csv(auto_parts_data, csv_file_path)

