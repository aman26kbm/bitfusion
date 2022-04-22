import os
import subprocess

def run_synth(module_name, instance_name, param_list, file_list, tcl_dir, additional_commands=[], clock_delay=800):

  options = {
    'DESIGN': None,
    'DNAME': None,
    'parameter_list': None,
    'clkpin': 'clk',
    'delay': clock_delay,
    'source_dir': './',
    'hdl_path_list': '[ list ../rtl ]',
    'hdl_file_list': None
    }


  attributes = {
    'hdl_error_on_blackbox': 'true',
    'lib_search_path': './',
    'information_level': 6,
    #'library': '/projects/pipd/rad/resiliency/ML/hardware_benchmark/sc10p5mc_cln16fpll001_base_ulvt_c20_tt_typical_max_0p80v_25c.lib',
    'library': '/home/projects/ljohn/aarora1/FreePDK45/FreePDK45/osu_soc/lib/files/gscl45nm.lib',
    'hdl_search_path': '$hdl_path_list',
    'lp_insert_clock_gating': 'false /'
    }

  commands = [
    'read_hdl -sv ${hdl_file_list}',
    'set_attr hdl_array_naming_style %s_%d /',
    'puts "Start elaborate\"',
    'elaborate $DESIGN -parameters ${parameter_list}',
    'set clock [define_clock -period ${delay} -name ${clkpin} [clock_ports]]',
    'external_delay -input 0 -clock ${clkpin} [find / -port ports_in/*]',
    'external_delay -output 0 -clock ${clkpin} [find / -port ports_out/*]',
    'dc::set_clock_transition .05 ${clkpin}',
    'check_design -unresolved',
    'synthesize -to_mapped -effort high',
    #'insert_tiehilo_cells -hi "TIEHI_X1N_A10P5TUL_C20" -lo "TIELO_X1N_A10P5TUL_C20" -maxfanout 1 -skip_unused_hier_pins',
    'report timing > reports/${DNAME}_timing_synth.rep',
    'report gates  > reports/${DNAME}_cell_synth.rep',
    'report power  > reports/${DNAME}_power_synth.rep',
    'report area  > reports/${DNAME}_area.rep',
    # 'write_hdl -mapped > output/${DNAME}_synth.v',
    # 'ungroup -flatten -all',
    # 'write_hdl -mapped > output/${DNAME}_synth_flat.v',
    # 'write_sdc >  sdc/${DNAME}.sdc',
    'report timing -lint -verbose']

    # 'set mult_insts [ dbGet -u [ dbGet -p top.insts.cell.name signed_spatial_mult*] ]',
    # 'report gates -instance_hier LOOP_INPUT_FORWARD[0].LOOP_OUTPUT_FORWARD[0].mult_inst_mult_67_34  > reports/${DNAME}_cell_synth.rep',


  options['DESIGN'] = module_name
  options['DNAME'] = instance_name

  opt_param_list = '[ list '
  for p in param_list:
    opt_param_list += str(p) + ' '
  opt_param_list += ']'
  options['parameter_list'] = opt_param_list

  flist = []
  print file_list
  with open(file_list, 'r') as f:
    for l in f:
      flist.append(l.rstrip('\n'))

  opt_hdl_file_list = '[ list '
  for f in flist:
    opt_hdl_file_list += str(f) + ' '
  opt_hdl_file_list += ']'
  options['hdl_file_list'] = opt_hdl_file_list

  out_tcl_name = tcl_dir + '/' + instance_name + '.tcl'
  if not os.path.exists(tcl_dir):
    os.makedirs(tcl_dir)

  if not os.path.exists('./sdc'):
    os.makedirs('./sdc')

  with open(out_tcl_name, 'w') as f:
    for o in options:
      f.write('set {0} {1}\n'.format(o, options[o]))
    f.write('\n\n')
    for a in attributes:
      f.write('set_attribute {0} {1}\n'.format(a, attributes[a]))
    f.write('\n\n')
    for c in commands:
      f.write('{0}\n'.format(c))
    for c in additional_commands:
      f.write('{0}\n'.format(c))
    f.write('\n\nexit')

  # system("cat templates/syn_signed_spatial_mult.template >> ${tcl_name}");
  # system("
  #command = 'bsub -R \"select[rhe6 && os64]\" -P RD016 -Jd misc-rd-universal -W 15000 -M 8000000 -o /dev/null rc -f {0}'.format(out_tcl_name)
  command = 'rc -f {0}'.format(out_tcl_name)
  print command
  #subprocess.call(command, shell=True)
  os.system(command)


if __name__ == "__main__":
  module = 'signed_spatial_mult'
  param_dict = {'high_precision': 16, 'low_precison': 8}
  param_list = [16, 8]
  instance_name = module
  for p in sorted(param_dict):
    instance_name += '_{0}_{1}'.format(p, param_dict[p])

  run_synth(module, instance_name, param_list, 'file.list', './tcl')
