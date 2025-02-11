"""
03 - Create SHEMAT-Suite models
==========================
 
 With the MC ensemble of generated geological models stored in the respective lith-blocks, we can use them to create SHEMAT-Suite models for then doing 
 forward simulations of Heat- and Mass-transfer.
"""

#%%
# Libraries
import os,sys
sys.path.append('../../')
import OpenWF.shemat_preprocessing as shemsuite
import glob
import numpy as np
import itertools as it
import gempy as gp
import pandas as pd
import matplotlib.pyplot as plt

print(f"Run with GemPy version {gp.__version__}")

#%%
# load the base model
# -------------------
# For creating SHEMAT-Suite input files from the Monte Carlo Ensemble we created in :ref:`sphx_glr_examples_geo_modeling_02_POC_create-MC-ensemble.py` we load the base POC model, which was created
# in :ref:`sphx_glr_examples_geo_modeling_01_POC_generate-model.py`. As we want to have the topography also in the SHEMAT-Suite model later on, we will create a mask of the model topography, called
# `topo_mask`

model_path = '../../models/2021-06-04_POC_base_model'
geo_model = gp.load_model('POC_PCT_model',
                         path=model_path, recompile=False)
topo = geo_model._grid.topography.values.shape
topo_mask = geo_model._grid.regular_grid.mask_topo
dtm = np.load(model_path+'/POC_PCT_model_topography.npy')

#%%
# Load the MC-lithologies
# -----------------------
# Next, we load the lithology blocks created by the MC example and mask them by the topography

lith_blocks = np.load('../../data/outputs/MCexample_10realizations.npy')

lith_blocks_topo = np.array([])
for i in lith_blocks:
    lith_blocks_topo = np.append(lith_blocks_topo, shemsuite.topomask(geo_model, i))
lith_blocks_topo = lith_blocks_topo.reshape(len(lith_blocks), -1)

#%%
# The model topography is not only important for the geological model, i.e. cutting geology with topography to produce a geological map, but is also vital for later on heat transport simulations.
# Especially if a simulation should consider advective/convective heat transport, as these can be driven by the topography. Similarly, surface temperature correlates with altitute. 
# Hence, knowing topography is important, when we want to have a realistic top boundary condition for temperature in a model which includes topography. Usually, surface temperature is available from 
# meteorologic services. If, however, that is not the case, surface temperature as a function of altitude can be estimated from an average lapse rate $L$ (0.0065 K/m) and knowledge of temperature at 
# sea level. 

# calculate surface temperatures
sea_temp = 288 # in Kelvin
L = 0.0065 # in Kelvin per metre
surf_temp = (sea_temp - L * dtm[:,:,2]) - 273.15 # in Celsius

# create figure
fig, axs = plt.subplots(1,2, figsize=[15,4], sharey=True)

m = axs[0].contourf(dtm[:,:,0], dtm[:,:,1], dtm[:,:,2],20, cmap='gist_earth', zorder=0)
axs[0].contour(dtm[:,:,0], dtm[:,:,1], dtm[:,:,2],10, colors='gray', zorder=1)

s = axs[1].contourf(dtm[:,:,0], dtm[:,:,1], surf_temp,20, cmap='gist_heat', zorder=0)
axs[1].contour(dtm[:,:,0], dtm[:,:,1], dtm[:,:,2],10, colors='gray', zorder=1)
fig.colorbar(m, ax=axs[0], label='meter')
fig.colorbar(s, ax=axs[1], label='°C')
axs[0].set_title('Topography')
axs[1].set_title('Surface temperature')
axs[0].set_ylabel('Y [m]')
axs[0].set_xlabel('X [m]')
axs[1].set_xlabel('X [m]')

fig.tight_layout()

#%%
# Create Top Boundary Conditions for head and temperature
# -------------------------------------------------------
#
# First we load the lithology grid of the base model and make sure, the lithology IDs are all integers. 
# To know where we would have air cells, we mask the lithology grid with the model topology. Now, the air has its own unit, which is per default the maximum lithology ID + 1.

lith_grid = np.load('../../models/POC_base_model_lith_blocks.npy')

# make sure that lithologies are integer
lith_grid = np.round(lith_grid,0).astype('int')
lith_grid_topo = shemsuite.topomask(geo_model, lith_grid)

#%%
# Then, we reshape the lithologies in the model resolution to get a 3D array, representing the model grid.

res = geo_model._grid.regular_grid.resolution
liths3D = lith_grid_topo.reshape((res), order='C')

#%%
# Now, we know that the maximum lithology is 12 (or if now, we can call it with ``geo_model.surfaces``), so we can check where in the 3D array the lithology ID is 13 and save 
# these indices

ijk = np.where(liths3D[:,:,:]==13)

#%%
# Let's now reshape the array for SHEMAT-Suite, which needs X, Y, Z
ijk_shem = np.stack([ijk[0], ijk[1], ijk[2]], axis=1)

#%% and get the topography and temperature assigned to theses indices

head = np.zeros(len(ijk_shem))
temp = np.zeros(len(ijk_shem))

for i in range(len(ijk_shem)):
    indices = ijk_shem[i,:2]
    head[i] = dtm[:,:,2][indices[0], indices[1]]
    temp[i] = surf_temp[indices[0], indices[1]]

#%%
# Next, we reshape the temperature and head boundary conditions back to a 1D vector and append them
# to the ijk vector for SHEMAT-Suite

head_reshaped = head.reshape(-1,1)
temp_reshaped = temp.reshape(-1,1)

ijkh = np.append(ijk_shem, head_reshaped, axis=1)
ijkt = np.append(ijk_shem, temp_reshaped, axis=1)

#%%
# It is important to remember, that indices between Python and Fortran (language of SHEMAt-Suite) are different.
# Whil Python starts with 0, Fortran starts with 1. Hence, we have to add 1 to the first three columns of the ijk arrays
# To make them Fortran compatible

ijkh[:,:3] = ijkh[:,:3] + 1
ijkt[:,:3] = ijkt[:,:3] + 1

# finally add the model height below sea-level to the head boundary condition
ijkh[:,3] = ijkh[:,3] + 6500

# SHEMAT requires an direction column for the boundary conditions 
direction = np.zeros_like(head_reshaped)

ijkh_d = np.append(ijkh, direction, axis=1)
ijkt_d = np.append(ijkt, direction, axis=1)

#%%
# Now, that we have the two arrays with conditions assigned to single cells, we can save them as txt files for later usage

np.savetxt('../../data/SHEMAT-Suite/POC_head_bcd.txt', ijkh_d, fmt='%d, %d, %d, %.3f, %d')
np.savetxt('../../data/SHEMAT-Suite/POC_temp_bcd.txt', ijkt_d, fmt='%d, %d, %d, %.3f, %d')

#%%
# Now we prepared the lithologies, which are necessary for the `# uindex` field in a SHEMA-Suite input file, we can prepare the other parameters. Of which some are necessary, like the model
# dimensions, and some are optional, like an array for the hydraulic head boundary condition, or observed data.

xmin, xmax, ymin, ymax, zmin, zmax = geo_model.grid.regular_grid.extent
temp_data = '../../data/SHEMAT-Suite/all_boreholes_as_shemat_data.csv'


#%% 
# Set up the units for the SHEMAT-Suite model
# -------------------------------------------
# One core element of a SHEMAT-Suite Input file is the `# units` table. This table comprises the petrophysical parameters of the lithological units whose geometry is stored in the `# uindex` field.
# The following code shows an example of how set up the `# units` table as a dataframe to be then stored in a SHEMAT-Suite input file. 

# Load existing units of the geological model:
units = geo_model.surfaces.df[['surface', 'id']]
units

#%%
# Now we create a dictionary with values for important parameters of each of the 12 units:
# And join it with the existing units dataframe.

params = {'por': np.array([1e-10, 1e-10, 1e-10, 1e-10, 1e-10, 0.1, 0.05, 0.05, 0.01, 0.1, 0.05, 0.01]).T,
         'perm': np.array([1e-16, 1e-16, 1e-16, 1e-16, 1e-16, 1.0e-14, 1.0e-14, 1.0e-15, 1.0e-17, 1.0e-14, 1.0e-15, 1.0e-16]),
         'lz':   np.array([2.5, 2.5, 2.5, 2.5, 2.5, 2.3, 1.93, 2.9, 4.64, 2.03, 3.21, 3.1])}

units = units.join(pd.DataFrame(params, index=units.index))

#%%
# So now, the `units` table looks like this:
units

#%%
# It is still missing the air component though. We have to add this, because the cells above the topography are
# assigned to a unit representing the air. For mimicking the long-wavelength radiation outward from the ground, we assign
# a high thermal conductivity to the air. If we were to assign a realistic low thermal conductivity, it would work as an insulator.
air = {'surface': 'air',
       'id': units.shape[0]+1,
      'por': 1e-10,
      'perm': 1e-22,
      'lz': 100}
units = units.append(air, ignore_index=True)

#%%
# Export to SHEMAT-Suite
# ----------------------
# We are now all set for combining the lithology arrays, the `# units` table, temperature data from boreholes
# into a SHEMAT-Suite input file. For this, we use the method `export_shemat_suite_input_file` in 
# OpenWF.shemat_preprocessing.

shemade = ""
for c in range(len(lith_blocks_topo)):
    model = lith_blocks_topo[c,:]
    model_name = f"POC_MC_{c}"
    shemsuite.export_shemat_suite_input_file(geo_model, lithology_block=model, units=units,  
                                   data_file=temp_data, head_bcs_file='../../data/SHEMAT-Suite/POC_head_bcd.txt',
                                   top_temp_bcs_file='../../data/SHEMAT-Suite/POC_temp_bcd.txt', lateral_boundaries='closed',
                                   path='../../models/SHEMAT-Suite_input/',
                                  filename=model_name)
    shemade += model_name + " \n"
shemade += "POC_base_model"
with open("../../models/SHEMAT-Suite_input/shemade.job", 'w') as jobfile:
    jobfile.write(shemade)

shemsuite.export_shemat_suite_input_file(geo_model, lithology_block=lith_grid_topo, units=units,  
                                   data_file=temp_data, head_bcs_file='../../data/SHEMAT-Suite/POC_head_bcd.txt',
                                   top_temp_bcs_file='../../data/SHEMAT-Suite/POC_temp_bcd.txt', lateral_boundaries='closed',
                                   path='../../models/SHEMAT-Suite_input/',
                                  filename='POC_base_model')