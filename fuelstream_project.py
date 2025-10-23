import fastf1
from matplotlib import pyplot as plt
from fastf1 import plotting

print("Welcome to fuelstream.")


session = fastf1.get_session(2021, "Silverstone", 'Q')
session.load()
print(session.results)
