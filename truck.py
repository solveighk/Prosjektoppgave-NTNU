# Initializes a truck
class Truck():

  def __init__(self,  yearly_dist, fueltype, consumption_per_km, lifetime, truck_value, residual_rate,  maintenance_rate, other_cost_rate, comparable_truck_value = 0, name = ""):
    ''' Class to set parameters for a new truck
    
        Parameters
        ----------
        yearly_dist : int
            Yearly driving distance in km
        fueltype : str, "el" or "diesel
            If the truck is battery electric or diesel truck
        consumption_per_km : str
            Consumption in kWh/km for electric trucks, and l/km for diesel trucks
        lifetime : int
            Estimated lifetime of the vehicle in years
        truck_value: int
            Estimated value of the truck in NOK
        residual_rate : float
            Residual value of the truck after it has exeeced its lifetime, as decimal: eg. 40% = 0.4
        maintenance_rate : float
            Maintenance rate in NOK/km
        comparable_truck_value : int, optional
            Value of comparable truck diesl truck, used to calculate ENOVA support for el trucks (default is 0)
       
    '''
    self.yearly_dist = yearly_dist
    self.fueltype = fueltype
    self.consumption_per_km = consumption_per_km
    self.lifetime = lifetime
    self.truck_value = truck_value
    self.maintenance_rate = maintenance_rate
    self.other_cost_rate = other_cost_rate

    if comparable_truck_value <= truck_value and comparable_truck_value != 0 and fueltype == "el": 
      enova_support = 0.4 * (truck_value-comparable_truck_value)
    else:
      enova_support = 0

    self.enova_support = enova_support

    self.residual_rate = residual_rate
    self.residual_value = residual_rate*truck_value
    self.investment_cost = truck_value - enova_support 

    if name == "":
      self.name = fueltype + "-" + "truck"
    else: 
      self.name = name
    
  def __str__(self): 
    return self.name
