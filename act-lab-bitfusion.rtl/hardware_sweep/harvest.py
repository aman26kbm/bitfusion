import numpy as np
import math
import os
import csv

import hw_sweep

def get_cell_area(filename):
    with open(filename) as f:
      for line in f:
        if 'total' in line:
          result = line.split()
          return result[1], result[2]

def get_power(filename):
    with open(filename) as f:
      lines = f.readlines()
      for i in range(len(lines)):
        line = lines[i]
        if 'Instance' in line:
          return lines[i+2].split()[2:]

def get_slack(filename):
  with open(filename) as f:
    lines = f.readlines()
    for i in range(len(lines)):
      line = lines[i]
      if 'Timing slack' in line:
        return line.split()[3][:-2]


def parse(reports_dir, module_name, instance_name, param_list, file_list='./file.list', tcl_dir='./tcl', clock_delay=800):
    cell_area_file_name = reports_dir + instance_name + '_cell_synth.rep'
    power_file_name = reports_dir + instance_name + '_power_synth.rep'
    timing_file_name = reports_dir + instance_name + '_timing_synth.rep'

    if not (os.path.isfile(cell_area_file_name) and os.path.isfile(power_file_name)):
      hw_sweep.run_synth(module_name, instance_name, param_list, file_list, tcl_dir, clock_delay=clock_delay)
      None
    else:
      cell, area = get_cell_area(cell_area_file_name)
      pow_leak, pow_dyn, pow_total = get_power(power_file_name)
      slack = get_slack(timing_file_name)
      return cell, area, pow_leak, pow_dyn, pow_total, slack

if __name__ == "__main__":

  results_file = 'results.csv'
  reports_dir = './reports/'

  #clock_delay = [200, 300, 400, 500, 550, 600, 650, 700, 750, 800]
  clock_delay = [2000]
  # clock_delay = [600, 650, 700, 750, 800]

#  with open('register.csv', 'w') as f:
#    csvwriter = csv.writer(f, delimiter=',')
#    csvwriter.writerow(['Synchronous Register'])
#    header = ['name', 'Synchronous/Asynchronous', 'Width (bits)', 'Clock Delay (ps)', 'Slack (ps)', 'Cell count', 'Area (um^2)', 'Leakage Power (nW)', 'Dynamic Power (nW)', 'Total Power (nW)']
#    csvwriter.writerow(header)
#    type = 'Synchronous'
#    for i in [8, 16, 24, 32, 40, 48, 56, 64]:
#      for clk in clock_delay:
#        width = i
#        module_name = 'register_sync'
#        instance_name = 'register_sync_width_{0}_clk_{1}'.format(width, clk)
#        parameters = [width]
#        try:
#          cell, area, pow_leak, pow_dyn, pow_total, slack = parse(reports_dir, module_name, instance_name, parameters, clock_delay=clk)
#          csvwriter.writerow([instance_name, type, width, clk, slack, cell, area, pow_leak, pow_dyn, pow_total])
#        except:
#          None
#
#    csvwriter.writerow(['Asynchronous Register'])
#    header = ['name', 'Synchronous/Asynchronous', 'Width (bits)', 'Clock Delay (ps)', 'Slack (ps)', 'Cell count', 'Area (um^2)', 'Leakage Power (nW)', 'Dynamic Power (nW)', 'Total Power (nW)']
#    csvwriter.writerow(header)
#    type = 'Asynchronous'
#    for i in [8, 16, 24, 32, 40, 48, 56, 64]:
#      for clk in clock_delay:
#        width = i
#        module_name = 'register_async'
#        instance_name = 'register_async_width_{0}_clk_{1}'.format(width, clk)
#        parameters = [width]
#        try:
#          cell, area, pow_leak, pow_dyn, pow_total, slack = parse(reports_dir, module_name, instance_name, parameters, clock_delay=clk)
#          csvwriter.writerow([instance_name, type, width, clk, slack, cell, area, pow_leak, pow_dyn, pow_total])
#        except:
#          None
#
#  with open('accumulator.csv', 'w') as f:
#    csvwriter = csv.writer(f, delimiter=',')
#    csvwriter.writerow(['Accumulator'])
#    header = ['name', 'Input Width (bits)', 'Output Width (bits)', 'Clock Delay (ps)', 'Slack (ps)', 'Cell count', 'Area (um^2)', 'Leakage Power (nW)', 'Dynamic Power (nW)', 'Total Power (nW)']
#    csvwriter.writerow(header)
#    for i in range(8):
#      out_width = 8 * (i+1)
#      for j in range(i+1):
#        in_width = 8 * (j+1)
#        for clk in clock_delay:
#          module_name = 'accumulator'
#          instance_name = 'accumulator_IN_{0}_OUT_{1}_clk_{2}'.format(in_width, out_width, clk)
#          parameters = [in_width, out_width]
#          try:
#            cell, area, pow_leak, pow_dyn, pow_total, slack = parse(reports_dir, module_name, instance_name, parameters, clock_delay=clk)
#            csvwriter.writerow([instance_name, in_width, out_width, clk, slack, cell, area, pow_leak, pow_dyn, pow_total])
#          except:
#            None
#
#  with open('mux.csv', 'w') as f:
#    csvwriter = csv.writer(f, delimiter=',')
#    csvwriter.writerow(['Mux'])
#    header = ['name', 'Output Width (bits)', 'N (Input Width = N * Output Width)', 'Clock Delay (ps)', 'Slack (ps)', 'Cell count', 'Area (um^2)', 'Leakage Power (nW)', 'Dynamic Power (nW)', 'Total Power (nW)']
#    csvwriter.writerow(header)
#    module_name = 'mux_n_1'
#    for log2i in range(7):
#      data_width = (1 << log2i)
#      for log2n in range(8):
#        N = (1 << log2n)
#        for clk in clock_delay:
#          instance_name = 'mux_n_1_data_{0}_N_{1}_clk_{2}'.format(data_width, N, clk)
#          parameters = [data_width, log2n]
#          try:
#            cell, area, pow_leak, pow_dyn, pow_total, slack = parse(reports_dir, module_name, instance_name, parameters, clock_delay=clk)
#            csvwriter.writerow([instance_name, data_width, N, clk, slack, cell, area, pow_leak, pow_dyn, pow_total])
#          except:
#            None
#
#  with open('shifter.csv', 'w') as f:
#    csvwriter = csv.writer(f, delimiter=',')
#    csvwriter.writerow(['Shifter'])
#    header = ['name', 'Input Width (bits)', 'Output Width (bits)', 'Clock Delay (ps)', 'Slack (ps)', 'Cell count', 'Area (um^2)', 'Leakage Power (nW)', 'Dynamic Power (nW)', 'Total Power (nW)']
#    csvwriter.writerow(header)
#    module_name = 'shifter'
#    for log2o in range(7):
#      out_width = (1 << log2o)
#      for log2i in range(log2o):
#        in_width = (1 << log2i)
#        for clk in clock_delay:
#          instance_name = 'shifter_IN_{0}_OUT_{1}_clk_{2}'.format(in_width, out_width, clk)
#          parameters = [in_width, out_width]
#          try:
#            cell, area, pow_leak, pow_dyn, pow_total, slack = parse(reports_dir, module_name, instance_name, parameters, clock_delay=clk)
#            csvwriter.writerow([instance_name, in_width, out_width, clk, slack, cell, area, pow_leak, pow_dyn, pow_total])
#          except:
#            None
#
#  with open('signed_adder.csv', 'w') as f:
#    csvwriter = csv.writer(f, delimiter=',')
#    csvwriter.writerow(['Adder'])
#    header = ['name', 'Input 0 Width (bits)', 'Input 1 Width (bits)', 'Output Width (bits)', 'Clock Delay (ps)', 'Slack (ps)', 'Cell count', 'Area (um^2)', 'Leakage Power (nW)', 'Dynamic Power (nW)', 'Total Power (nW)']
#    csvwriter.writerow(header)
#    module_name = 'signed_adder'
#    for log2out in range(6):
#      out_width = (1 << log2out)
#      for log2in0 in range(log2out+1):
#        in0_width = (1 << log2in0)
#        for log2in1 in range(log2in0+1):
#          in1_width = (1 << log2in1)
#          for clk in clock_delay:
#            instance_name = 'adder_IN0_{0}_IN1_{1}_OUT_{2}_clk_{3}'.format(in0_width, in1_width, out_width, clk)
#            parameters = [in0_width, in1_width, out_width]
#            try:
#              cell, area, pow_leak, pow_dyn, pow_total, slack = parse(reports_dir, module_name, instance_name, parameters, clock_delay=clk)
#              csvwriter.writerow([instance_name, in0_width, in1_width, out_width, clk, slack, cell, area, pow_leak, pow_dyn, pow_total])
#            except:
#              None
#
#  with open('signed_max_comparator.csv', 'w') as f:
#    csvwriter = csv.writer(f, delimiter=',')
#    csvwriter.writerow(['Signed Max Comparator'])
#    header = ['name', 'Input Width (bits)', 'Output Width (bits)', 'Clock Delay (ps)', 'Slack (ps)', 'Cell count', 'Area (um^2)', 'Leakage Power (nW)', 'Dynamic Power (nW)', 'Total Power (nW)']
#    csvwriter.writerow(header)
#    module_name = 'signed_max_comparator'
#    for log2out in range(7):
#      out_width = (1 << log2out)
#      for log2in in range(log2out+1):
#        in_width = (1 << log2in)
#        for clk in clock_delay:
#          instance_name = 'signed_max_comparator_IN_{0}_OUT_{1}_clk_{2}'.format(in_width, out_width, clk)
#          parameters = [in_width, out_width]
#          try:
#            cell, area, pow_leak, pow_dyn, pow_total, slack = parse(reports_dir, module_name, instance_name, parameters, clock_delay=clk)
#            csvwriter.writerow([instance_name, in0_width, in1_width, out_width, clk, slack, cell, area, pow_leak, pow_dyn, pow_total])
#          except:
#            None
#
#  with open('signed_mult.csv', 'w') as f:
#    csvwriter = csv.writer(f, delimiter=',')
#    csvwriter.writerow(['Signed Multiplier'])
#    header = ['name', 'Input 0 Width (bits)', 'Input 1 Width (bits)', 'Output Width (bits)', 'Clock Delay (ps)', 'Slack (ps)', 'Cell count', 'Area (um^2)', 'Leakage Power (nW)', 'Dynamic Power (nW)', 'Total Power (nW)']
#    csvwriter.writerow(header)
#    module_name = 'signed_mult'
#    for log2in0 in range(7):
#      in0_width = (1 << log2in0)
#      for log2in1 in range(log2in0+1):
#        in1_width = (1 << log2in1)
#        out_width = in0_width + in1_width
#        for clk in clock_delay:
#          instance_name = 'signed_mult_IN0_{0}_IN1_{1}_OUT_{2}_clk_{3}'.format(in0_width, in1_width, out_width, clk)
#          parameters = [in0_width, in1_width]
#          try:
#            cell, area, pow_leak, pow_dyn, pow_total, slack = parse(reports_dir, module_name, instance_name, parameters, clock_delay=clk)
#            csvwriter.writerow([instance_name, in0_width, in1_width, out_width, clk, slack, cell, area, pow_leak, pow_dyn, pow_total])
#          except:
#            None
#
#
#  # Register File
#  with open('register_file_sp.csv', 'w') as f:
#    csvwriter = csv.writer(f, delimiter=',')
#    csvwriter.writerow(['Register File'])
#    header = ['name', 'Data Width (bits)', 'Addr Width (bits)', 'Clock Delay (ps)', 'Slack (ps)', 'Cell count', 'Area (um^2)', 'Leakage Power (nW)', 'Dynamic Power (nW)', 'Total Power (nW)']
#    csvwriter.writerow(header)
#    module_name = 'register_file_sp'
#    for log2d in range(11):
#      data_width = (1 << log2d)
#      for log2a in range(15):
#        addr_width = log2a
#        for clk in clock_delay:
#          instance_name = 'register_file_sp_DATA_{0}_ADDR_{1}_clk_{2}'.format(data_width, addr_width, clk)
#          parameters = [data_width, addr_width]
#          try:
#            cell, area, pow_leak, pow_dyn, pow_total, slack = parse(reports_dir, module_name, instance_name, parameters, clock_delay=clk)
#            csvwriter.writerow([instance_name, data_width, addr_width, clk, slack, cell, area, pow_leak, pow_dyn, pow_total])
#          except:
#            None
#
#
#  with open('spatial_mult.csv', 'w') as f:
#    csvwriter = csv.writer(f, delimiter=',')
#    module_name = 'spatial_mult'
#    header = ['Mult Type', 'Signed/Unsigned', 'Max Precision (bits)', 'Min Precision (bits)', 'Clock delay (ps)', 'Slack (ps)', 'Cell usage', 'Area', 'Leakage Power (nW)', 'Dynamic Power (nW)', 'Total Power (nW)']
#    csvwriter.writerow(header)
#    type = 'unsigned'
#    for hp in np.linspace(4, 0, 5):
#      for lp in np.linspace(hp, 0, hp+1):
#        high_p = 2**int(hp)
#        low_p = 2**int(lp)
#        for clk in clock_delay:
#          mult_name = '{0}:{1} mult'.format(high_p, low_p)
#          instance_name = module_name + "_{0}_{1}_clk_{2}".format(high_p, low_p, clk)
#          try:
#            cell, area, pow_leak, pow_dyn, pow_total, slack = parse(reports_dir, module_name, instance_name, [high_p, low_p], clock_delay=clk)
#            csvwriter.writerow([mult_name, type, high_p, low_p, clk, slack, cell, area, pow_leak, pow_dyn, pow_total])
#          except TypeError:
#            None
#
#  with open('signed_spatial_mult.csv', 'w') as f:
#    csvwriter = csv.writer(f, delimiter=',')
#    header = ['Mult Type', 'Signed/Unsigned', 'Max Precision (bits)', 'Min Precision (bits)', 'Clock delay (ps)', 'Slack (ps)', 'Cell usage', 'Area', 'Leakage Power (nW)', 'Dynamic Power (nW)', 'Total Power (nW)']
#    csvwriter.writerow(header)
#    module_name = 'signed_spatial_mult'
#    type = 'signed'
#    for hp in [8]:
#      for lp in [2]:
#        high_p = hp
#        low_p = lp
#        for clk in clock_delay:
#          mult_name = '{0}:{1} mult'.format(high_p, low_p)
#          instance_name = module_name + "_{0}_{1}_clk_{2}".format(high_p, low_p, clk)
#          try:
#            cell, area, pow_leak, pow_dyn, pow_total, slack = parse(reports_dir, module_name, instance_name, [high_p, low_p], clock_delay=clk)
#            csvwriter.writerow([mult_name, type, high_p, low_p, clk, slack, cell, area, pow_leak, pow_dyn, pow_total])
#          except TypeError:
#            None
#
#  with open('signed_temporal_mult.csv', 'w') as f:
#    csvwriter = csv.writer(f, delimiter=',')
#    header = ['Mult Type', 'Signed/Unsigned', 'Max supported precision (bits)', 'Accumulator width (bits)', 'Activation Precision (bits)', 'Weight Precision', 'Clock delay (ps)', 'Slack (ps)', 'Cell usage', 'Area', 'Leakage Power (nW)', 'Dynamic Power (nW)', 'Total Power (nW)']
#    csvwriter.writerow(header)
#    type = 'signed'
#    module_name = 'signed_temporal_mult'
#    for log_max_p in np.linspace(4, 1, 4):
#      max_p = 2**int(log_max_p)
#      acc_w = 2*max_p + 8
#      for _acc_w in range(8):
#        acc_w = 2*max_p + _acc_w
#        for log_a in np.linspace(log_max_p, 1, log_max_p):
#          a_prec = 2**int(log_a)
#          for log_b in np.linspace(log_a, 1, log_a):
#            b_prec = 2**int(log_b)
#
#            for clk in clock_delay:
#
#              mult_name = '{0}x{1}-bit temporal mult'.format(a_prec, b_prec)
#              instance_name = '{0}_max_prec_{1}_a_{2}_b_{3}_acc_{4}_clk_{5}'.format(module_name, max_p, a_prec, b_prec, acc_w, clk)
#              param_list = [a_prec, b_prec, acc_w, max_p]
#
#              try:
#                cell, area, pow_leak, pow_dyn, pow_total, slack = parse(reports_dir, module_name, instance_name, param_list, clock_delay=clk)
#                csvwriter.writerow([mult_name, type, max_p, acc_w, a_prec, b_prec, clk, slack, cell, area, pow_leak, pow_dyn, pow_total])
#              except TypeError:
#                None

  with open('signed_systolic_array.csv', 'w') as f:
    module_name = 'systolic_array'
    type = 'signed'
    csvwriter = csv.writer(f, delimiter=',')
    csvwriter.writerow(['Signed Systolic Array'])
    header = ['name', 'Array_N', 'Array_M', 'Signed/Unsigned', 'Max Precision (bits)', 'Min Precision (bits)', 'Clock delay (ps)', 'slack (ps)', 'Cell usage', 'Area (um^2)', 'Leakage Power (nW)', 'Dynamic Power (nW)', 'Total Power (nW)']
    csvwriter.writerow(header)
    #max_N = 16
    #_max_N = int(math.log(max_N) / math.log(2))
    for _arr_n in [8,32]:
      arr_n = int(_arr_n)
      #arr_m = arr_n
      #arr_m = 32
      for _arr_m in [8,32]:
        arr_m = int(_arr_m)
        if arr_n != arr_m:
          continue
        for _pmax in [8,2]:
          pmax = _pmax
          #pmax = 2 ** int(_pmax)
          for _pmin in [2]:
            pmin = _pmin
            #pmin = 2 ** int(_pmin)
            for clk in clock_delay:
              instance_name = module_name + '_n_{0}_m_{1}_pmax_{2}_pmin_{3}_clk_{4}'.format(arr_n, arr_m, pmax, pmin, clk)
              param_list = [arr_n, arr_m, pmax, pmin]
              try:
                cell, area, pow_leak, pow_dyn, pow_total, slack = parse(reports_dir, module_name, instance_name, param_list, clock_delay=clk)
                csvwriter.writerow([instance_name, arr_n, arr_m, type, pmax, pmin, clk, slack, cell, area, pow_leak, pow_dyn, pow_total])
              except TypeError:
                None
