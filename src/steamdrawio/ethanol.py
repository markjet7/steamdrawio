# This tutorial models a corn grain dry mill ethanol process
# it is based on the following paper: https://www.sciencedirect.com/science/article/pii/S0926669005000944?ref=pdf_download&fr=RR-2&rr=7e1c247def331401 by (Kwiatkowski et al., 2006)

import biosteam as bst
import thermosteam as tmo
import pandas as pd
import matplotlib.pyplot as plt
import warnings

# Filter all warning messages
warnings.filterwarnings("ignore")
# Create chemical objects for the available chemicals
water = tmo.Chemical("Water")

ethanol = tmo.Chemical("Ethanol")
carbon_dioxide = tmo.Chemical("CO2")
lime = tmo.Chemical("CaO", phase="s", default=True)
ammonia = tmo.Chemical("NH3")
glucose = tmo.Chemical("Glucose", phase="l")

# Create chemical objects for the non-conventional compounds
starch = tmo.Chemical(
    "Starch",
    formula="C6H10O5",
    rho=1540,
    Cp=0.37656,
    default=True,
    search_db=False,
    phase="s",
    Hf=-1271100.0
)
protein = tmo.Chemical(
    "Protein",
    formula="C5H9NO2",
    rho=1540,
    Cp=0.37656,
    default=True,
    search_db=False,
    phase="s",
    Hf=-1271100.0
)
fiber = tmo.Chemical(
    "Fiber",
    formula="C6H10O5",
    rho=1540,
    Cp=0.37656,
    default=True,
    search_db=False,
    phase="s",
    Hf=-1271100.0
)
oil = tmo.Chemical(
    "Oil",
    formula="C57H104O6",
    rho=1540,
    Cp=0.37656,
    default=True,
    search_db=False,
    phase="s",
    Hf=-1271100.0
)
ash = tmo.Chemical(
    "Ash", rho=1540, Cp=0.37656, default=True, search_db=False, phase="s", MW=1.0,
    Hf=-1271100.0
)
enzymes = tmo.Chemical(
    "Enzymes", rho=1540, Cp=0.37656, default=True, search_db=False, phase="s", MW=1.0,
    Hf=-1271100.0
)
distillers_grains = tmo.Chemical(
    "DistillersGrains",
    rho=1540,
    Cp=0.37656,
    default=True,
    search_db=False,
    phase="s",
    MW=1.0,
    Hf=-1271100.0
)
yeast = tmo.Chemical(
    "Yeast", rho=1540, Cp=0.37656, default=True, search_db=False, phase="s", MW=1.0,
    Hf=-1271100.0
)

chemicals = tmo.Chemicals(
    [
        water,
        ethanol,
        carbon_dioxide,
        glucose,
        lime,
        enzymes,
        ammonia,
        yeast,
        starch,
        protein,
        fiber,
        oil,
        ash,
        distillers_grains,
    ]
)

for chemical in chemicals:
    if chemical.Psat.Tmax == None:
        chemical.Psat.add_model(0, Tmax=1000, Tmin=1)


bst.settings.set_thermo(chemicals)
bst.main_flowsheet.clear()

# %%
# Utilities
HeatUtility = bst.HeatUtility
Gas_utility = bst.UtilityAgent(
    "natural_gas",
    T=1200,
    P=101325,
    T_limit=1100,
    Water=1,
    heat_transfer_efficiency=0.85,
)
# bst.settings.heating_agents.append(Gas_utility)
# HeatUtility.heating_agents.append(Gas_utility)
HeatUtility.default_heating_agents()
HeatUtility.default_cooling_agents()

Cooling_utility = HeatUtility.get_agent("chilled_water")
Cooling_utility.regeneration_price = 0
Cooling_utility.heat_transfer_price = 0

Steam_utility = HeatUtility.get_agent("low_pressure_steam")
Steam_utility.regeneration_price = Steam_utility.regeneration_price * 0.1
HeatUtility.heating_agents.append(Gas_utility)

# %%
# Corn grain composition
starch_wt = 0.595  # Starch composition (%)
protein_wt = 0.084  # Protein composition (%)
fiber_wt = 0.107  # Fiber composition (%)
oil_wt = 0.043  # Oil composition (%)
ash_wt = 0.015  # Ash composition (%)
water_wt = 1-(starch_wt + protein_wt + fiber_wt + oil_wt + ash_wt)  # Water composition (%)

# Corn grain flow rate
corn_grain_flow_rate = 2000  # Tonnes per day

# Create the corn stream
corn = bst.Stream(
    "CornIn",
    Starch=corn_grain_flow_rate * starch_wt,
    Protein=corn_grain_flow_rate * protein_wt,
    Fiber=corn_grain_flow_rate * fiber_wt,
    Oil=corn_grain_flow_rate * oil_wt,
    Ash=corn_grain_flow_rate * ash_wt,
    Water=corn_grain_flow_rate * water_wt,
    T=273.15 + 25,  # Temperature in Kelvin
    P=101325,  # Pressure in Pascal
    units="tonnes/day",
)
corn.price = 0.132  # USD/kg

waterIn = bst.Stream("WaterIn", T=273.15 + 25, P=101325, units="tonnes/day")

ammoniaIn = bst.Stream("AmmoniaIn", T=273.15 + 25, P=101325, units="tonnes/day")

limeIn = bst.Stream("LimeIn", CaO=53.07, T=273.15 + 25, P=101325, units="kg/hour")
limeIn.price = 0.01  # USD/kg

aamylase = bst.Stream("Aamylase", Enzymes=corn_grain_flow_rate*0.00082, T=273.15 + 25, P=101325, units="tonnes/day")
gamylase = bst.Stream("Gamylase", Enzymes=corn_grain_flow_rate*0.00082, T=273.15 + 25, P=101325, units="tonnes/day")

yeastIn = bst.Stream("YeastIn", Yeast=11.8, T=273.15 + 25, P=101325, units="kg/hour")
# %%
# Process units
grinding_mill = bst.units.HammerMill("grinding_mill", ins=corn)
mixing_tank = bst.units.MixTank(
    "mixing_tank", ins=(grinding_mill-0, limeIn, aamylase, ammoniaIn)
)
slurry_mix = bst.units.MixTank("slurry_mix", ins=mixing_tank-0)
liquefaction_hx = bst.units.HXutility("liquefaction_hx", ins=slurry_mix-0, T=35+273.15)
liquefaction_tank = bst.units.MixTank("liquefaction_tank", ins=liquefaction_hx-0)
cooling_tank = bst.units.StorageTank("cooling_tank", ins=liquefaction_tank-0)
saccharification_tank = bst.units.MixTank("saccharification_tank", ins=(cooling_tank-0, gamylase))
def saccharification_specification():
    saccharification_tank._run()
    saccharification_tank.outs[0].imass["Glucose"] = saccharification_tank.outs[0].imass["Starch"]*0.9
    saccharification_tank.outs[0].imass["Starch"] = saccharification_tank.outs[0].imass["Starch"]*0.1
    return
saccharification_tank.add_specification(saccharification_specification)

fermentation_tank = bst.units.MixTank(
    "fermentation_tank", ins=(saccharification_tank-0, yeastIn), tau=48
)

ethanol_yield = 0.51
def fermentation_specification():
    fermentation_tank._run()
    fermentation_tank.outs[0].imass["Ethanol"] = fermentation_tank.ins[0].imass["Glucose"]*ethanol_yield
    fermentation_tank.outs[0].imass["Glucose"] = fermentation_tank.ins[0].imass["Glucose"]*(1-ethanol_yield)
    fermentation_tank.outs[0].imass["CO2"] = fermentation_tank.ins[0].imass["Glucose"]*(1-ethanol_yield)
    return
fermentation_tank.add_specification(fermentation_specification)

fermentation_splitter = bst.units.Splitter(
    "fermentation_splitter", ins=fermentation_tank-0, split={
        "CO2": 0.99,
        "Ethanol": 0.10
    }
)

degasser_to_co2_scrubber = bst.Stream("degasser_to_co2_scrubber", units="tonnes/day")
co2_scrubber_mixer = bst.units.Mixer("co2_scrubber_mixer", ins=(fermentation_splitter-0, waterIn, degasser_to_co2_scrubber))

co2_scrubber = bst.units.Splitter(
    "co2_scrubber",
    ins=co2_scrubber_mixer-0,
    outs=("CO2_out", "ScrubberWaste"),
    split={
        "CO2": 0.99,
        "Water": 0.01
    }
)
co2_out = co2_scrubber-0

degasser = bst.units.Splitter(
    "degasser", ins=fermentation_splitter-1,
    outs=(degasser_to_co2_scrubber, ""),
    split={
        "CO2": 0.99,
        "Ethanol": 0.01,
        "Water": 0.01
    }
)

beer_column = bst.units.ShortcutColumn(
    "beer_column",
    ins=degasser-1,
    LHK=("Ethanol", "Water"),
    product_specification_format="Recovery",
    Lr=0.99,
    Hr=0.99,
    k=1.2
)

stripping_to_rectifier = bst.Stream("stripping_to_rectifier", units="tonnes/day")
rectifier_mixer = bst.units.Mixer("rectifier_mixer", ins=(beer_column-0, stripping_to_rectifier))

rectifier = bst.units.ShortcutColumn(
    "rectifier",
    ins=rectifier_mixer-0,
    outs=("Ethanol_out", ""),
    LHK=("Ethanol", "Water"),
    product_specification_format="Recovery",
    Lr=0.99,
    Hr=0.99,
    k=2,
)
ethanol_out = rectifier-0

stripping = bst.units.ShortcutColumn(
    "stripping",
    ins=rectifier-1,
    outs=(stripping_to_rectifier, "StrippingWaste"),
    LHK=("Ethanol", "Water"),
    product_specification_format="Recovery",
    Lr=0.99,
    Hr=0.99,
    k=1.2,
)

centrifuge = bst.units.SolidsCentrifuge(
    "centrifuge", ins=beer_column-1, split={
        "DistillersGrains": 0.99
    },
    moisture_content=0.4
)
dryer = bst.units.Splitter("dryer", ins=centrifuge-0,
                           outs=("", "DryerWaste"), split={
    "DistillersGrains": 0.99
})


thin_stillage = bst.units.MixTank("thin_stillage", ins=(centrifuge-1))
evaporator = bst.units.Splitter(
    "evaporator",
    ins=thin_stillage-0,
    outs=("evaporatorGas", "stillage"),
    split={
        "Ethanol": 0.99,
        "Water": 0.99
    }
)

ddgs_mixer = bst.units.Mixer("ddgs_mixer", ins=(dryer-0, evaporator-1), outs="DDGS")

ddgs_out = ddgs_mixer


system = bst.main_flowsheet.create_system("CornEthanol")
system.diagram()
# %%
system.simulate()
# # %%
# sys.show(flow="tonnes/day")
# # %%
# # Simple mass balance
# print("Inputs")
# input_streams = reversed(sorted(sys.ins, key=lambda s: s.F_mass))
# for i in input_streams:
#     print(i.ID, i.F_mass, "tonnes/day")

# print("\nOutputs")
# output_streams = reversed(sorted(sys.outs, key=lambda s: s.F_mass))
# for i in output_streams:
#     print(i.ID, i.F_mass, "tonnes/day")
# print("\n")
# # %%
# # Techno-economic analysis
# class TEA(bst.TEA):
#     labor_cost = 0

#     def _FOC(self, FCI):
#         return FCI *0.13 + self.labor_cost

# tea = TEA(system=sys,
#              IRR=0.1,
#              duration=(2018, 2038),
#              depreciation='MACRS7',
#              income_tax=0.21,
#              operating_days=333,
#              lang_factor=4.5, # ratio of total fixed capital cost to equipment cost
#              construction_schedule=(0.4, 0.6),
#              WC_over_FCI=0.05, #working capital / fixed capital investment
#             startup_months=3,
#             startup_FOCfrac=1,
#             startup_salesfrac=0,
#             startup_VOCfrac=0,
#              finance_fraction = 0.4,
#              finance_years=10,
#              finance_interest=0.07)
# tea.labor_cost = 1037000
# msp = tea.solve_price(ethanol_out)
# print("Fixed Capital Investment: ", tea.FCI/1e6, "million USD")
# rho_e = 2.96 # kg/gallon
# print("Ethanol Minimum Selling Price: $", msp*rho_e, "/gallon") # 1 gallon of ethanol weights 2.96 kg
# # %%
# # Equipment Costs
# equipment_costs = pd.DataFrame(dict((k.ID, k.installed_cost/1**6) for k in sys.units), index=[0]).T

# equipment_costs[equipment_costs[0]>250000].T.plot.bar( stacked=True, figsize=(7, 12))

# plt.style.use("ggplot")
# plt.xlabel("Equipment")
# plt.xticks([])
# plt.ylabel("Installed Cost (MM$)")
# plt.legend(loc="upper right", bbox_to_anchor=(1.5, 1))
# plt.grid("major", axis="y")
# # %%
# # Operating Costs
# operating_costs = pd.DataFrame({
#     "Labor": tea.labor_cost/1e6,
#     "Corn": corn.price*corn.F_mass*tea.operating_hours/1e6,
#     "Lime": limeIn.price*limeIn.F_mass*tea.operating_hours/1e6,
#     "Ammonia": ammoniaIn.price*ammoniaIn.F_mass*tea.operating_hours/1e6,
#     "Utilities": tea.utility_cost/1e6,
#     "Depreciation": tea.annual_depreciation/1e6,
#     "Capital": tea.FCI*0.13/1e6
# }, index=[0])

# operating_costs.plot.bar(stacked=True, figsize=(7, 12))
# plt.xlabel("Operating Cost")
# plt.ylabel("Annual Cost (MM$)")
# plt.xticks([])
# plt.grid("major", axis="y")
# # %%
# # Sensitivity Analysis
# sensitivity_results = []

# # For each sensitivity parameter, we will calculate the minimum and maximum ethanol selling price by changing the parameter by 20%, then, we will return the value to its original (baseline) value
# baseline = corn.price
# corn.price = baseline*1.2
# high = tea.solve_price(ethanol_out)
# corn.price = baseline*0.8
# low = tea.solve_price(ethanol_out)
# corn.price = baseline
# sensitivity_results.append(["Corn Price", low*rho_e, high*rho_e])

# baseline = limeIn.price
# limeIn.price = baseline*1.2
# high = tea.solve_price(ethanol_out)
# limeIn.price = baseline*0.8
# low = tea.solve_price(ethanol_out)
# limeIn.price = baseline
# sensitivity_results.append(["Lime Price", low*rho_e, high*rho_e])

# # we have to resimulate the system because we changed a process variable (ethanol yield)
# baseline = ethanol_yield
# ethanol_yield = baseline*1.2
# tea.system.simulate()
# high = tea.solve_price(ethanol_out)
# ethanol_yield = baseline*0.8
# tea.system.simulate()
# low = tea.solve_price(ethanol_out)
# ethanol_yield = baseline
# tea.system.simulate()
# sensitivity_results.append(["Ethanol Yield", low*rho_e, high*rho_e])

# baseline = 0.1
# tea.IRR = baseline*1.2
# high = tea.solve_price(ethanol_out)
# tea.IRR = baseline*0.8
# low = tea.solve_price(ethanol_out)
# tea.IRR = baseline
# sensitivity_results.append(["IRR", low*rho_e, high*rho_e])

# # %%
# shifted_sensitivity_results = []
# for i in sensitivity_results:
#     shifted_sensitivity_results.append([i[0], i[1]-msp*rho_e, i[2]-msp*rho_e])

# sorted_sensitivity_results = sorted(shifted_sensitivity_results, key=lambda x: abs(x[1]))

# plt.figure(figsize=(10, 8))
# plt.barh(range(len(shifted_sensitivity_results)), [i[1] for i in sorted_sensitivity_results])

# plt.barh(range(len(shifted_sensitivity_results)), [i[2] for i in sorted_sensitivity_results])
# plt.yticks(range(len(shifted_sensitivity_results)), [i[0] for i in sorted_sensitivity_results])
# plt.xlabel("Corn Ethanol Selling Price Sensitivity (USD/gallon)")
# plt.xticks([i/100 for i in range(0, 100, 25)], [("%.2f" % (msp*rho_e+i/100)) for i in range(0, 100, 25)])

# # %%
# # %%
# # problem statement
