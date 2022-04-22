import os
import ConfigParser
import subprocess

def generate_sram_data(override_params, instance_name='default', conf_file='./sram_16nm.conf', spec_dir='./spec', dat_dir='./data/'):
  config = ConfigParser.ConfigParser()
  config.optionxform=str
  config.read(conf_file)
  config.set('SRAM', 'instname', instance_name)

  if not os.path.exists(spec_dir):
    os.makedirs(spec_dir)

  if not os.path.exists(dat_dir):
    os.makedirs(dat_dir)

  spec_path = os.path.join(spec_dir, instance_name + '.spec')
  with open(spec_path, 'w') as f:
    for option in config.options('SRAM'):
      if option in override_params:
        config.set('SRAM', option, str(override_params[option]))
      f.write('{0} = {1}\n'.format(option, config.get('SRAM', option)))

  # bin_path = '/arm/ref/pipd/iprd/release/tsmc/cln28hp/sram_sp_hsd-TS33CA000/r3p1-00eac0/bin/sram_sp_hsd_svt_mvt'
  # bin_path = '/arm/ref/pipd/iprd/release/tsmc/cln28hpm/sram_sp_hde-TS44CA001/r4p0-00eac0/bin/sram_sp_hde'
  bin_path = '/arm/ref/pipd/iprd/release/tsmc/cln16fpll001/sram_sp_hde_svt_mvt-TS66CA000/r4p0-00eac0/bin/sram_sp_hde_svt_mvt'
  command = '{0} ascii -spec {1}'.format(bin_path, spec_path)
  bsub_command = 'bsub -R \"select[rhe6 && os64]\" -P RD016 -Jd misc-rd-universal -W 15000 -M 8000000 -o /dev/null {0}'.format(command)
  print bsub_command
  # subprocess.call(bsub_command, shell=True)

if __name__ == "__main__":
  params = {'corners': 'tt_0p85v_0p85v_25c'}
  generate_sram_data(params)
