import streamlit as st
import numpy as np
import random
from geneticalgorithm import geneticalgorithm as ga

st.title("Stochastic Inventory Simulation")

# Define sidebar inputs
days = st.slider("For how many days do you want to run this Simulation", 1, 30, 5)
demand_mean = st.number_input("What is the Average daily Demand", value=50.0, step=0.1)
demand_sd = st.number_input("What is the Standard deviation of daily Demand", value=10.0, step=0.1)
lead_time_min, lead_time_max = st.slider("What is the Minimum and Maximum lead time in days", 1, 30, (1, 10))
asl = st.slider("What is the required service level (e.g. 95.0)", 0.0, 100.0, 95.0)

# Check service level input is between 0 to 100
while not 0 < asl < 100:
    st.error("required service level has to be between 0 to 100")
    asl = st.sidebar.slider("What is the required service level (e.g. 95.0)", 0.0, 100.0, 95.0)

days = days + 2*lead_time_max
days2 = days*2


# Define objective function
def stoch_inv_sim(X):
    obj = 0
    for k in range(10):
        tot_demand, tot_sales = 0, 0
        a = [max(0,np.random.normal(demand_mean,demand_sd,1)) for i in range(days)]
        inv, pip_inv, in_qty = [], [], [0 for i in range(days2)]
        order_qty, reorder_pt = X[0], X[1]
        for i in range(days):
            if i == 0:
                beg_inv = reorder_pt
                in_inv = 0
                stock_open = beg_inv + in_inv
            else:
                beg_inv = end_inv
                in_inv = in_qty[i]
                stock_open = beg_inv + in_inv
            demand = a[i]
            lead_time = random.randint(lead_time_min,lead_time_max)
            if demand < stock_open:
                end_inv = stock_open - demand
            else:
                end_inv = 0
            inv.append(0.5*stock_open+0.5*end_inv)
            if i==0:
                pipeline_inv = 0
            else:
                pipeline_inv = sum(in_qty[j] for j in (i+1,days2-1))
            if pipeline_inv + end_inv <= reorder_pt:
                if i+lead_time <days:
                    in_qty[i+lead_time] = in_qty[i+lead_time]+order_qty
            if i>=2*lead_time_max:
                tot_sales = tot_sales + stock_open - end_inv
                tot_demand = tot_demand + demand
        cycle_inv = sum(inv)/len(inv)
        if tot_sales*100/(tot_demand+0.000001) < asl:
            aa = cycle_inv+10000000*demand_mean*(tot_demand-tot_sales)
        else:
            aa = cycle_inv
        obj = obj + aa
    return obj/10


# Define GA algorithm parameters
varbound = np.array([[0, demand_mean*lead_time_max*5]]*2)
algorithm_param = {
    'max_num_iteration': 1000,
    'population_size': 15,
    'mutation_probability': 0.1,
    'elit_ratio': 0.01,
    'crossover_probability': 0.5,
    'parents_portion': 0.3,
    'crossover_type': 'uniform',
    'max_iteration_without_improv': 200
}

model = ga(function=stoch_inv_sim, dimension=2, variable_type='real', variable_boundaries=varbound, algorithm_parameters=algorithm_param)

if st.button("Run Optimization"):
    model.run()
    st.write("Optimization complete.")
    st.write('The best solution after optimization is:')
    st.write(' [Order Quantity, Reorder Point]: ', model.output_dict['variable'])
    st.write(' Estimated Cycle Inventory Level : ', model.output_dict['function'])
    st.write("End of simulation.")