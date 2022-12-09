#imports

import random
from random import betavariate
from random import randint as randint

#  Generates random number from PERT-distribution

def pert(a, b, c):
  r = c - a
  alpha = 1 + 4 * (b - a) / r
  beta = 1 + 4 * (c - b) / r
  return a + betavariate(alpha, beta) * r



#parameters to set charging costs
#figures in NOK/kWh 
#NVE forecast skal endres til Statnett for 2023 - 2027
def get_electricity_parameters(surcharge_station = 1):

  #Sources el_price: 2023 - 2027 most likely: Statnett, 2028 - 2031 most likely: NVE 2030 forecast, 2023 - 2027 min og maks: Statnett, 2028 - 2031 min og maks: Statnett min og maks 2027
  el_prices =  {2023: [0.27, 0.60, 2.09], 2024: [0.16, 0.40, 1.81], 2025:[0.11, 0.45, 1.79], 2026:[0.10, 0.40, 1.34], 2027:[0.13, 0.50, 1.55], 2028:[0.13, 0.49, 1.55], 2029: [0.13, 0.49, 1.55], 2030: [0.13, 0.49, 1.55], 2031: [0.13, 0.49, 1.55]}
  
  # Set other costs parameters
  transmission_cost = {2023: 0.12, 2024: 0.12, 2025: 0.12, 2026: 0.12, 2027: 0.12, 2028: 0.12, 2029: 0.12, 2030: 0.12, 2031: 0.12} # nettleie, expense for charging station
  taxes_ex_mva = {2023: 0.15, 2024: 0.15, 2025: 0.15, 2026: 0.15, 2027: 0.15, 2028: 0.15, 2029: 0.15, 2030: 0.15, 2031: 0.15} # enova-avgift, forbruksavgift, expense for charging station
  surcharge_el = {2023: 0.05, 2024: 0.05, 2025: 0.05, 2026: 0.05, 2027: 0.05, 2028: 0.05, 2029: 0.05, 2030: 0.05, 2031: 0.05} # extra cost to electricity company
  other_el_costs = {}

  for key in transmission_cost.keys():
    other_el_costs[key] = transmission_cost[key] + taxes_ex_mva[key] + surcharge_el[key] + surcharge_station

  return el_prices, other_el_costs


def get_charging_cost(truck, el_prices, other_el_costs, start_year=2023, truck_delivery_year=2024):
  ''' Get charging prices for a year in real NOK (2022)
        Parameters
        ----------
        truck : Truck
          A battery electric truck
        el_price_ret: list
          list with relative changes in predicted prices for [min, most_likely, max]. First input is the real prices
        other_el_cost : list
          list of other costs for charging
        start_year: int
          year truck is ordered
        truck_delivery_year: int
          Year truck is delivered
  '''
  
  prices_d = {}
  charging_prices = [0]*truck.lifetime
  for i in range (start_year, truck_delivery_year+1):
     # Get energy prices from now until the truck is expected
    prices_d[i] = pert(el_prices[i][0], el_prices[i][1], el_prices[i][2])

  # Gets charging prices for the active years of the truck
  for j in range(truck_delivery_year, truck.lifetime + truck_delivery_year):
    if j == truck_delivery_year:
      start_price = prices_d[j]
      charging_prices[j-truck_delivery_year] = start_price
    else: 
      price  = pert(el_prices[j][0], el_prices[j][1], el_prices[j][2])
      charging_prices[j-truck_delivery_year] = price
  # Adds additional costs to the charging cost
  for j in range(truck_delivery_year, truck.lifetime + truck_delivery_year):
    charging_prices[j-truck_delivery_year] += other_el_costs[j]
    charging_prices[j-truck_delivery_year] = charging_prices[j-truck_delivery_year]/0.9

  return charging_prices


# Funksjon som returner en liste over diesel returns
def get_diesel_returns():
  #Disse er tatt fra eia.gov sin forecast for crude oil, enhet er dollars per barrel
  crude_oil_forecast = {2023: [32, 61, 123], 2024: [34, 66, 130], 2025:[35, 67, 133], 2026: [36, 69, 137], 2027: [36, 70, 140], 2028: [37, 72, 142], 2029: [38, 73, 144], 2030: [38, 74, 145], 2031: [39, 75, 146]}

  # Konstanter brukt i konvertering til NOK/liter
  dollar_to_nok = 10
  barrel_to_liter = 158.987294928

  # Konstanter for å regne ut internasjonal dieselpris
  sept_crude_oil_2022 = (89.76 * dollar_to_nok) / barrel_to_liter # Gj.snittlig crude oil pris september 2022 omgjort fra dollars/barrel til NOK/liter
  refinery = (sept_crude_oil_2022 / 0.42) * 0.27 # I september 2022 var raffinering 27 % og crude oil 42 % av oljpris

  # Initialiserer tomme dictionaries 
  international_diesel_forecast = {2023: [0,0,0], 2024: [0,0,0], 2025: [0,0,0], 2026: [0,0,0], 2027: [0,0,0], 2028: [0,0,0], 2029: [0,0,0], 2030: [0,0,0], 2031: [0,0,0]}
 # us_diesel_price = {2023: [0,0,0], 2024: [0,0,0], 2025: [0,0,0], 2026: [0,0,0], 2027: [0,0,0], 2028: [0,0,0], 2029: [0,0,0], 2030: [0,0,0], 2031: [0,0,0]}

  #Funksjon som returner en liste over diesel returns

  #Regner ut tilnærmet internasjonal dieselpris for årene våre
  for year in crude_oil_forecast.keys():
    for i in range(3):
      # Konvererterer forecastene fra dollars per barrel til NOK/liter
      crude_oil_forecast[year][i] = crude_oil_forecast[year][i]*dollar_to_nok / barrel_to_liter

      # Regner ut forventede USA dieselpriser der man antar at crude oil står for 42% av pumpeprisen der (kilde eia)
    #  us_diesel_price[year][i] = crude_oil_forecast[year][i] / 0.42
      
      # Trekker fra taxes og distribution fra USA-dieselprisen for å finne tilnærmet internasjonal dieselpris. Taxes står får 12% og distribution står for 20% av dieselpris. 
      international_diesel_forecast[year][i] = crude_oil_forecast[year][i] + refinery #- us_taxes - us_dist_mark #*(1-0.32) #

  # Regner ut diesel price returns baser på internasjonal dieselpris
  international_diesel_ret = {}
  for key in international_diesel_forecast.keys():
  # Hvis vi er i 2023 legger vi ikke til returns, bare verdien direkte
    if key == 2023: 
      international_diesel_ret[key] = international_diesel_forecast[key]

    else:
      international_diesel_ret[key] = [0,0,0]
      international_diesel_ret[key][1] = international_diesel_forecast[key][1] / international_diesel_forecast[key-1][1]
      international_diesel_ret[key][0] = international_diesel_forecast[key][0] / international_diesel_forecast[key-1][1]
      international_diesel_ret[key][2] = international_diesel_forecast[key][2] / international_diesel_forecast[key-1][1]

  return international_diesel_ret

def get_diesel_costs(truck, start_year, delivery_year, international_diesel_ret):
  ''' Get diesel costs for lifetime of the truck
      Parameters
      ----------
      truck : Truck
        A diesel truck
      start_year
        Year truck arrives (??) (assumed to be 2023)

  '''
  # Konstanter til å regne på dieselpris
  veibruksavgift = 3.52
  co2_avgift_21 = 1.58 # Dette er 2021 nivå
  co2_avgift_22 = 2.05 
  økning_co2_avgift = 1.15 # Skal økes med 15 prosent årlig fra 2021 nivå og til 2030

  diesel_cost_list = [0]*truck.lifetime # Initializes empty list for dieselcost
  d_price = {}

  # Calculates the diesel price for 2024 based on 2023 price and returns
  for i in range (start_year, delivery_year+1):
    if i == start_year:
      price = pert(international_diesel_ret[i][0], international_diesel_ret[i][1], international_diesel_ret[i][2])
      d_price[i] = price
    else:
      dist_parameter =  pert(international_diesel_ret[i][0], international_diesel_ret[i][1], international_diesel_ret[i][2])
      d_price[i] = dist_parameter * d_price[i-1]

  # Starts collecting relevant diesel prices from delivery year and onwards 
  for j in range(delivery_year, truck.lifetime + delivery_year):
    if j == delivery_year:
      start_price = d_price[j]
      diesel_cost_list[j-delivery_year] = start_price
    else: 
      dist_parameter = pert(international_diesel_ret[j][0], international_diesel_ret[j][1], international_diesel_ret[j][2])
      price  = diesel_cost_list[j-delivery_year-1] * dist_parameter
      diesel_cost_list[j-delivery_year] = price

  co2_avgift_dict = {2021: co2_avgift_21, 2022: co2_avgift_22, 2023: co2_avgift_21*økning_co2_avgift*økning_co2_avgift, 2024: 0, 2025: 0, 2026: 0, 2027: 0, 2028: 0, 2029: 0, 2030: 0, 2031: 0}
  # Adds additional taxes to get the Norwegian diesel price 
  for k in range(delivery_year, truck.lifetime + delivery_year):
    co2_avgift_dict[k] = co2_avgift_dict[k-1]*1.15

    # Etter 2030 vet vi ikke om den skal økes mer, så setter den bare lik 2030 nivå så den ikke øker uendelig 
    if k >= 2030: 
       co2_avgift_dict[k] = 5.558245 # Øker med 15 årlig prosent fra 2021 til 2030

    pumpepris = (diesel_cost_list[k-delivery_year] + veibruksavgift + co2_avgift_dict[k])/0.9 # Her legges til bensinstasjontillegg 10% for å få pumpeprisen 
    diesel_cost_list[k-delivery_year] = pumpepris #*0.75 # Her trekkes momsen fra fordi man ikke betaler denne som yrkessjåfør

  return diesel_cost_list