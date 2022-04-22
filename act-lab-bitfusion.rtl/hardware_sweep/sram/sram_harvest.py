import os
import numpy as np
import re

import sram_sweep

def sram_dat_parser(name, dat_file, params):
  if not (os.path.isfile(dat_file)):
    print 'Running {0}'.format(name)
    sram_sweep.generate_sram_data(params, instance_name=name)
  else:
    with open(dat_file, 'r') as f:
      lines = f.readlines()

    regex = {
        'x': re.compile('^geomx\s*(\d*\.\d*)'),
        'y': re.compile('^geomy\s*(\d*\.\d*)'),
        'volt':re.compile('^volt\s*(\d*\.\d*)'),
        'ac_core_rd': re.compile('^icc_c_rd3\s*(\d*\.\d*)'),
        'ac_peri_rd': re.compile('^icc_p_rd3\s*(\d*\.\d*)'),
        'ac_core_wr': re.compile('^icc_c_wr3\s*(\d*\.\d*)'),
        'ac_peri_wr': re.compile('^icc_p_wr3\s*(\d*\.\d*)'),
        'standby_core_chipdisable': re.compile('^icc_standby_c_chipdisable\s*(\d*\.\d*)'),
        'standby_peri_chipdisable': re.compile('^icc_standby_p_chipdisable\s*(\d*\.\d*)'),
        'standby_core_ret1': re.compile('^icc_standby_c_ret1\s*(\d*\.\d*)'),
        'standby_peri_ret1': re.compile('^icc_standby_p_ret1\s*(\d*\.\d*)'),
        'standby_core_selective_precharge': re.compile('^icc_standby_c_selective_precharge\s*(\d*\.\d*)'),
        'standby_peri_selective_precharge': re.compile('^icc_standby_p_selective_precharge\s*(\d*\.\d*)'),
        'deselect_core': re.compile('^icc_c_desel\s*(\d*\.\d*)'),
        'deselect_peri': re.compile('^icc_p_desel\s*(\d*\.\d*)'),
        'peak_core': re.compile('^icc_c_peak\s*(\d*\.\d*)'),
        'peak_peri': re.compile('^icc_p_peak\s*(\d*\.\d*)'),
        'inrush_core': re.compile('^icc_c_inrush\s*(\d*\.\d*)'),
        'inrush_peri': re.compile('^icc_p_inrush\s*(\d*\.\d*)')
    }

    value= {}
    for val in regex:
      value[val] = -1

    for line in lines:
      for v in regex:
        r = regex[v]
        match = r.match(line)

        if match:
          value[v] = match.group(1)


    return value

if __name__ == "__main__":
  corners = ['tt_0p85v_0p85v_25c']
  w_min = 10
  b_min = 4
  s_min = w_min+b_min # 1KB
  s_max = 20 # 1MB

  i = 0
  data_points = [
      'x',
      'y',
      'volt',
      'ac_core_rd',
      'ac_peri_rd',
      'ac_core_wr',
      'ac_peri_wr',
      'standby_core_chipdisable',
      'standby_peri_chipdisable',
      'standby_core_ret1',
      'standby_peri_ret1',
      'standby_core_selective_precharge',
      'standby_peri_selective_precharge',
      'deselect_core',
      'deselect_peri',
      'peak_core',
      'peak_peri',
      'inrush_core',
      'inrush_peri'
      ]
  with open('results.csv', 'w') as f:
    row = 'words, bits, size, mux, frequency'
    for d in data_points:
      row += str(d) + ','
    f.write(row + '\n')

    for _s in np.linspace(s_min, s_max, s_max-s_min+1):
      size = 1 << int(_s)
      for _w in np.linspace(w_min, _s, _s-w_min+1):
        words = 1 << int(_w)
        _b = _s - _w
        bits = 1<<int(_b)
        for mux in [8, 16, 32]:
          #MHz
          for freq in [1000, 500, 200]:
            for corner in corners:
              name = 'W{0}_B{1}_M{2}_{3}MHz'.format(words, bits, mux, freq)
              params = {'mux':mux, 'words':words, 'bits':bits, 'corners':corner, 'frequency': freq}
              dat_file = name + '_' + corner + '.dat'
              try:
                values = sram_dat_parser(name, dat_file, params)
                row = '{0}, {1}, {2}, {3}, {4},'.format(words, bits, size, mux, freq)
                for d in data_points:
                  row += str(values[d]) + ','
                f.write(row + '\n')

              except TypeError:
                None
