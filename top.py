import pandas
import ConfigParser
import os
import sys
import numpy as np
from bitfusion.graph_plot.barchart import BarChart

import matplotlib

import warnings
warnings.filterwarnings('ignore')

import bitfusion.src.benchmarks.benchmarks as benchmarks
from bitfusion.src.simulator.stats import Stats
from bitfusion.src.simulator.simulator import Simulator
from bitfusion.src.sweep.sweep import SimulatorSweep, check_pandas_or_run
from bitfusion.src.utils.utils import *
from bitfusion.src.optimizer.optimizer import optimize_for_order, get_stats_fast

import dnnweaver2
batch_size = int(sys.argv[2])

results_dir = './results'
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

fig_dir = './fig'
if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)

# BitFusion configuration file
#config_file = 'bf_e_conf.ini'
config_file = sys.argv[1]
print("Using config file: {}".format(config_file))

# Create simulator object
verbose = False
bf_e_sim = Simulator(config_file, verbose)
bf_e_energy_costs = bf_e_sim.get_energy_cost()
print(bf_e_sim)

energy_tuple = bf_e_energy_costs
print('')
print('*'*50)
print(energy_tuple)

sim_sweep_columns = ['N', 'M',
        'Max Precision (bits)', 'Min Precision (bits)',
        'Network', 'Layer',
        'Cycles', 'Memory wait cycles',
        'WBUF Read', 'WBUF Write',
        'OBUF Read', 'OBUF Write',
        'IBUF Read', 'IBUF Write',
        'DRAM Read', 'DRAM Write',
        'Bandwidth (bits/cycle)',
        'WBUF Size (bits)', 'OBUF Size (bits)', 'IBUF Size (bits)',
        'Batch size']

filename = 'bitfusion-eyeriss-sim-sweep'+bf_e_sim.suffix+"_b"+str(batch_size)+'.csv'
bf_e_sim_sweep_csv = os.path.join(results_dir, filename)
if os.path.exists(bf_e_sim_sweep_csv):
    print("{} does not exist. Good".format(filename))
    bf_e_sim_sweep_df = pandas.read_csv(bf_e_sim_sweep_csv)
else:
    bf_e_sim_sweep_df = pandas.DataFrame(columns=sim_sweep_columns)
print('Got BitFusion Eyeriss, Numbers')

bf_e_results = check_pandas_or_run(bf_e_sim, bf_e_sim_sweep_df,
        bf_e_sim_sweep_csv, batch_size=batch_size, config_file=config_file)
bf_e_results = bf_e_results.groupby('Network',as_index=False).agg(np.sum)
area_stats = bf_e_sim.get_area()
print("Done")

def get_eyeriss_energy(df):
    eyeriss_energy_per_mac = 16 * 0.2 * 1.e-3 #energy in nJ
    eyeriss_energy_alu = float(df['ALU'])
    eyeriss_energy_dram = float(df['DRAM']) * 0.15 #Scaling due to technology
    eyeriss_energy_buffer = float(df['Buffer'])
    eyeriss_energy_array = float(df['Array'])
    eyeriss_energy_rf = float(df['RF'])
    eyeriss_energy = eyeriss_energy_alu + eyeriss_energy_dram + eyeriss_energy_buffer + eyeriss_energy_array + eyeriss_energy_rf
    eyeriss_energy *= eyeriss_energy_per_mac
    return eyeriss_energy

def get_eyeriss_energy_breakdown(df):
    eyeriss_energy_per_mac = 16 * 0.2 * 1.e-3 #energy in nJ
    eyeriss_energy_alu = float(df['ALU'])
    eyeriss_energy_dram = float(df['DRAM'])
    eyeriss_energy_buffer = float(df['Buffer'])
    eyeriss_energy_array = float(df['Array'])
    eyeriss_energy_rf = float(df['RF'])
    eyeriss_energy = [eyeriss_energy_alu+eyeriss_energy_array, eyeriss_energy_buffer, eyeriss_energy_rf, eyeriss_energy_dram]
    eyeriss_energy = [x * eyeriss_energy_per_mac for x in eyeriss_energy]
    return eyeriss_energy

def df_to_stats(df):
    stats = Stats()
    stats.total_cycles = float(df['Cycles'])
    stats.mem_stall_cycles = float(df['Memory wait cycles'])
    stats.reads['act'] = float(df['IBUF Read'])
    stats.reads['out'] = float(df['OBUF Read'])
    stats.reads['wgt'] = float(df['WBUF Read'])
    stats.reads['dram'] = float(df['DRAM Read'])
    stats.writes['act'] = float(df['IBUF Write'])
    stats.writes['out'] = float(df['OBUF Write'])
    stats.writes['wgt'] = float(df['WBUF Write'])
    stats.writes['dram'] = float(df['DRAM Write'])
    return stats



# Eyeriss-Simulator
eyeriss_data = pandas.read_csv(os.path.join(results_dir, 'eyeriss_results.csv'))
eyeriss_data_bench = eyeriss_data.groupby('Benchmark', as_index=False).agg(np.sum)
eyeriss_data_bench['Platform'] = 'Eyeriss (16-bit)'

print('BitFusion-Eyeriss comparison')
eyeriss_area = 3.5*3.5*45*45/65./65.
print('Area budget = {}'.format(eyeriss_area))


print(area_stats)
if abs(sum(area_stats)-eyeriss_area)/eyeriss_area > 0.1:
    print('Warning: BitFusion Area is outside 10% of eyeriss')
print('total_area = {}, budget = {}'.format(sum(area_stats), eyeriss_area))
bf_e_area = sum(area_stats)

baseline_data = []
for bench in benchmarks.benchlist:
    lookup_dict = {'Benchmark': bench}

    eyeriss_cycles = float(lookup_pandas_dataframe(eyeriss_data_bench, lookup_dict)['time(ms)'])
    eyeriss_time = eyeriss_cycles / 500.e3 / 16
    eyeriss_energy = get_eyeriss_energy(lookup_pandas_dataframe(eyeriss_data_bench, lookup_dict))
    eyeriss_power = eyeriss_energy / eyeriss_time * 1.e-9

    eyeriss_speedup = eyeriss_time / eyeriss_time
    eyeriss_energy_efficiency = eyeriss_energy / eyeriss_energy

    eyeriss_ppa = eyeriss_speedup / eyeriss_area / (eyeriss_speedup / eyeriss_area)
    eyeriss_ppw = eyeriss_speedup / eyeriss_power / (eyeriss_speedup / eyeriss_power)
    
    bf_e_stats = df_to_stats(bf_e_results.loc[bf_e_results['Network'] == bench])
    bf_e_cycles = bf_e_stats.total_cycles * (batch_size / 16.)
    bf_e_time = bf_e_cycles / (bf_e_sim.accelerator.frequency / 1e3)
    bf_e_energy = bf_e_stats.get_energy(bf_e_sim.get_energy_cost()) * (batch_size / 16.)
    bf_e_power = (bf_e_energy / bf_e_time) * 1e-3

    bf_e_speedup = eyeriss_time / bf_e_time
    bf_e_energy_efficiency = eyeriss_energy / bf_e_energy

    bf_e_ppa = bf_e_speedup / bf_e_area / (eyeriss_speedup / eyeriss_area)
    bf_e_ppw = bf_e_speedup / bf_e_power / (eyeriss_speedup / eyeriss_power)

    baseline_data.append(['Performance', bench, bf_e_speedup])
    baseline_data.append(['Energy reduction', bench, bf_e_energy_efficiency])
    baseline_data.append(['Performance-per-Watt', bench, bf_e_ppw])
    baseline_data.append(['Performance-per-Area', bench, bf_e_ppa])
    
    print('*'*50)
    print('Benchmark: {}'.format(bench))
    #print('Eyeriss time: {} ms'.format(eyeriss_time))
    print('BitFusion time: {} ms'.format(bf_e_time))    
    #print('Eyeriss power: {} mWatt'.format(eyeriss_power*1.e3*16))
    print('BitFusion power: {} mWatt'.format(bf_e_power))
    print('BitFusion energy: {} nJ'.format(bf_e_energy))
    print('BitFusion total_cycles: {} '.format(bf_e_cycles))
    print('*'*50)
    
eyeriss_comparison_df = pandas.DataFrame(baseline_data, columns=['Metric', 'Network', 'Value'])