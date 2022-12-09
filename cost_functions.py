#imports
import truck
import random
#import numpy as np
from random import betavariate
from random import randint as randint
from statistics import mean, median, stdev
#import matplotlib.mlab as mlab



#present value factor
def get_pvf(i, N):
  return 1 / (1+i)**N


# Returns a list of the operational costs for the active years of the truck
def get_opex(truck, toll, energy_prices):
  ''' Method to get opex for a truck
        Parameters
        ----------
        truck : Truck
          Target truck
        toll: int
          Yearly toll costs in NOK
        other_cost : int
          Yearly others costs in NOK
        energy_prices: list
          List of filling/charging prices, NOK/kWh for el and NOK/l for diesel. In real NOK
  '''
  if truck.fueltype == "el":
    toll_cost = toll*0.2
  else: 
    toll_cost = toll
  opex = []
  energy = []
  maintenance = truck.yearly_dist * truck.maintenance_rate
  other_cost = truck.yearly_dist * truck.other_cost_rate
  for i in range (len(energy_prices)):
    energy_price = truck.consumption_per_km*truck.yearly_dist*energy_prices[i]
    opex_yearly = maintenance + toll_cost + other_cost
    energy.append(energy_price)
    opex.append(opex_yearly)
  return opex, energy

# Returns the total cost of ownership per year 
# Formula from Wu et al
def get_tco(truck, pvf, opex_list, energy_cost_list, i):
  ''' Get tco for a year
        Parameters
        ----------
        truck : Truck
          The truck
        pvf : float
          present value factor
        crf : float
          capital recovery factor
        opex_list: list
          list of opex for each year (nominal values)
        energy_cost_list: lis
          list of energy cost for each year (real 2022 values)
        i: float
          discount rate
  '''
  other_opex = 0
  energy = 0
  for n in range (len(opex_list)): 
    other_opex += opex_list[n] / ((1+i)**n) # diskontering 
    energy += energy_cost_list[n] / ((1+i)**n)
  capex = (truck.investment_cost - truck.residual_value * pvf)
  tco = capex + other_opex + energy
  return tco, other_opex, energy, capex 

def get_tco_penalty(truck_el, truck_diesel, energy_prices_el, energy_prices_diesel, i, year, toll):
  pvf_el = get_pvf(i, truck_el.lifetime)
  pvf_diesel = get_pvf(i, truck_diesel.lifetime)
  capex_el = (truck_el.investment_cost - truck_el.residual_value * pvf_el)
  capex_diesel = (truck_diesel.investment_cost - truck_diesel.residual_value * pvf_diesel)
  final_costs = [0]* truck_el.lifetime

  opex_el, energy_el = get_opex(truck_el,toll,energy_prices_el)

  for j in range (len(opex_el)): #legge til energy i opex
    opex_el[j] += energy_el[j]
  opex_diesel, energy_diesel = get_opex(truck_diesel,toll,energy_prices_diesel)

  for j in range (len(opex_diesel)): #legge til energy i opex
    opex_diesel[j] += energy_diesel[j]

  for j in range(1,truck_el.lifetime+1):
    if j < year: #year without infrastructure
      final_costs[j-1] = opex_diesel[j-1] + capex_diesel/truck_diesel.lifetime 
    elif j < (year + 1): #year when infrastructure is built out, you pay for an electric truck one part of the year and a diesel truck the other part
        diesel_part = year - (j-1)
        el_part = 1 - diesel_part
        final_costs[j-1] = opex_diesel[j-1] * diesel_part + opex_el[j-1] * el_part + (capex_diesel/truck_el.lifetime) *diesel_part
    else: 
      final_costs[j-1] = opex_el[j-1] 
  tco = 0
  for n in range (len(final_costs)): 
    tco += final_costs[n] / ((1+i)**n) # diskontering 
  tco += capex_el

  return tco

