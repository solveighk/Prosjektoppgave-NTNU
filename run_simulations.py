

from energy_costs import get_charging_cost, get_diesel_costs, get_diesel_returns, get_electricity_parameters
from simulation_input import monte_carlo_simulation
from truck import Truck
import matplotlib.pyplot as plt

from cost_functions import get_opex, get_pvf, get_tco, get_tco_penalty
from energy_costs import get_charging_cost, get_diesel_costs, get_diesel_returns, get_electricity_parameters
import numpy as np


# Monte Carlo simulation of total ownership costs with uncertainty 
def monte_carlo_simulation(truck_el, truck_diesel, simulation_type, no_simulations, diesel_returns, el_price_ret, other_el_costs, toll, interest_rate, penalty = True):
  ''' Run montecarlo simulations generate TCO distribution for trucks
      Parameters
      ----------
      truck_el : Truck
        A battery electric truck
      truck_diesel : Truck
        A diesel truck
      simulation_type : String
        "el" for electric and "diesel" for diesel
      el_price_ret : dict
        Dictionary with list of electricity prices in NOK, on format [min, most likely, max]. Year is key in dictionary. First input is real numbers, rest is the relative change. 
      other_el_costs : dict
        Dictionary with other charging costs for battery electric trucks in NOK/kWh for each year
      toll : int
        Yearly toll cost in NOK for a diesel truck
      other_opex_el : 
        Yearly other opex for el truck in NOK
      interest_rate : float
        Discount rate
      other_opex_diesel : int
        Yearly other opex for diesel truck in NOK
      penalty : boolean, optional
        If True, penalty cost is generated for years without infrastructure. If false, penalty cost is ignored.

  '''
  #print(truck_el.investment_cost)
  tco_list = []
  total_energy_list = []
  total_other_opex_list = []
  total_capex_list = []
  count = 0 #get number of simulations without infrastructure during truck's lifetime
  
  for i in range(no_simulations):
    if simulation_type == "el":
      # Generates relevant energy prices and opex for electric truck
      energy_prices_el = get_charging_cost(truck_el, el_price_ret, other_el_costs, 2023, 2024)
      energy_prices_diesel = get_diesel_costs(truck_diesel, 2023, 2024, diesel_returns)
      opex_list_el, energy_cost_list_el = get_opex(truck_el, toll, energy_prices_el)

      if penalty:
        days = np.random.geometric(p) # Number of days until infrastructure is in place - prblem med denne er at flere ganger blir tallet over 2192. Eller skal
        year = days / 365 

        if year > truck_el.lifetime: 
          year = truck_el.lifetime 
          count +=1 # increase count - no infrastructure during the truck's lifetime
        
        tco = get_tco_penalty(truck_el, truck_diesel, energy_prices_el, energy_prices_diesel, interest_rate, year,toll)
        tco_list.append(tco)

      else: # Not penalty case
        pvf = get_pvf(interest_rate, truck_el.lifetime)
        tco, other_opex, energy, capex = get_tco(truck_el, pvf, opex_list_el, energy_cost_list_el, interest_rate)
        tco_list.append(tco)
        total_energy_list.append(energy)
        total_other_opex_list.append(other_opex)
        total_capex_list.append(capex)
  

    else: # Simulation_type = "diesel"
      energy_prices_diesel = get_diesel_costs(truck_diesel, 2023, 2024, diesel_returns) # returns a list of diesel prices for the different years
      opex_list, energy_cost_list = get_opex(truck_diesel,toll,energy_prices_diesel) 
      pvf = get_pvf(interest_rate, truck_diesel.lifetime)
      tco, other_opex, energy, capex = get_tco(truck_diesel, pvf, opex_list, energy_cost_list, interest_rate)
      tco_list.append(tco)
      total_energy_list.append(energy)
      total_other_opex_list.append(other_opex)
      total_capex_list.append(capex)

  if simulation_type == "el":
    print("Simulations without infrastructure", count)
  
  return tco_list, total_energy_list, total_other_opex_list, total_capex_list



def histogram(mcs,title, x_low, x_high, y_high):
  plt.xlabel("TCO")
  plt.ylabel("Occurences")
  title = "Monte Carlo Simulation: " + title
  plt.title(title)
  plt.hist(mcs, bins = 100)
  plt.ylim(0,y_high)
  plt.xlim(x_low,x_high)
  plt.show()

# parameters for geometric probability distribution
dager = 2192 # days from start of 2023 to end of 2028. 
forventet = dager/2 # expected value halfway in the period
p = 1/forventet 

#fixed parameters
toll = 87500
discount_rate = 0.09

# Initializes trucks objects
el_truck = Truck(yearly_dist = 50000, fueltype = "el", consumption_per_km = 1.7, lifetime = 7, truck_value = 5000000, residual_rate = 0.2, maintenance_rate = 1, other_cost_rate = 1, comparable_truck_value = 2000000, name = "el")
diesel_truck = Truck(yearly_dist = 50000, fueltype = "diesel", consumption_per_km = 0.4, lifetime = 7, truck_value = 2000000, residual_rate = 0.2, maintenance_rate = 1.5, other_cost_rate = 1, comparable_truck_value = 5000000, name = "diesel")

# Number of Monte Carlo simulations
no_simulations = 20000

# Diesel returns
d_returns = get_diesel_returns()

# ELECTRICITY AND CHARGING PRICES, 3 CASES FOR SURCHARGE RATE
# Low surcharge on charging stations (2 NOK/kWh)
el_prices_NOK2, other_el_costs_NOK2 = get_electricity_parameters(2)
# Medium surcharge on charging stations (5 NOK/kWh)
el_prices_NOK5, other_el_costs_NOK5 = get_electricity_parameters(5)
# High surcharge on charging stations (8 NOK/kWh)
el_prices_NOK8, other_el_costs_NOK8 = get_electricity_parameters(8)



#simulations with infrastructure uncertainty
mcs_el_tillegg_NOK2, _, _, _ = monte_carlo_simulation(el_truck, diesel_truck, "el", no_simulations, d_returns, el_prices_NOK2, other_el_costs_NOK2, toll,  discount_rate,True)
mcs_el_tillegg_NOK5, _, _, _ = monte_carlo_simulation(el_truck, diesel_truck, "el", no_simulations, d_returns, el_prices_NOK5, other_el_costs_NOK5, toll, discount_rate, True)
mcs_el_tillegg_NOK8, _, _, _ = monte_carlo_simulation(el_truck, diesel_truck, "el", no_simulations, d_returns, el_prices_NOK8, other_el_costs_NOK8, toll, discount_rate, True)

# Histograms for infrastructure uncertainty
histogram( mcs_el_tillegg_NOK2, "2 NOK/kWh surcharge",5000000, 10000000, 1500)
histogram(mcs_el_tillegg_NOK5,"5 NOK/kWh surcharge", 5000000, 10000000, 1500)
histogram(mcs_el_tillegg_NOK8,"8 NOK/kWh surcharge", 5000000, 10000000, 1500)

#Simulations for no infrastructure uncertainty
mcs_NOK2_without_penalty_el, energy, otheropex, capex = monte_carlo_simulation(el_truck, diesel_truck, "el", no_simulations, d_returns, el_prices_NOK2, other_el_costs_NOK2, toll, discount_rate, False)
mcs_NOK5_without_penalty_el, energy, otheropex, capex = monte_carlo_simulation(el_truck, diesel_truck, "el", no_simulations, d_returns, el_prices_NOK5, other_el_costs_NOK5, toll, discount_rate, False)
mcs_NOK8_without_penalty_el, energy, otheropex, capex = monte_carlo_simulation(el_truck, diesel_truck, "el", no_simulations, d_returns, el_prices_NOK8, other_el_costs_NOK8, toll, discount_rate, False)
histogram(mcs_NOK2_without_penalty_el, "Surcharge NOK2, no penalty", 4000000, 7000000, 1000)
histogram(mcs_NOK5_without_penalty_el, "Surcharge NOK5, no penalty", 4500000, 8500000, 1000)
histogram(mcs_NOK8_without_penalty_el, "Surcharge NOK8, no penalty", 4000000, 10000000, 1000)

#Simulations for a diesel truck
tco_diesel, energy_diesel, otheropex_diesel, capex_diesel = monte_carlo_simulation(el_truck, diesel_truck, "diesel", no_simulations, d_returns, el_prices_NOK5, other_el_costs_NOK5, toll,  discount_rate, False)
histogram(tco_diesel, "mcs_diesel", 4000000, 7000000, 1000)

