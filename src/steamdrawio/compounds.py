# %%
import biosteam as bst

# %%
water = bst.Chemical("Water")
cellulose = bst.Chemical('Cellulose',
                  Cp=1.364, # Heat capacity [kJ/kg]
                  rho=1540, # Density [kg/m3]
                  default=True, # Default other chemicals properties like viscosity to that of water at 25 C
                  search_db=False, # Not in database, so do not search the database
                  phase='s',
                  formula="C6H10O5", # Glucose monomer minus water, molecular weight is computed based on formula
                Hf=-975708.8)
co2 = bst.Chemical("CO2")

chems = bst.Chemicals([water, cellulose, co2])
chems.compile()
# %%
bst.settings.set_thermo(chems)
s = bst.Stream('s', Water=1, Cellulose=1)
# %%
s.vle(T=298.15, P=101325)
# %%
s.HHV
# %%
try:
    s.Cp
except Exception as e:
    print(e)
# %%
