#Delete existing csvs so that they are regenerated
rm -rf results/bitfusion-eyeriss-sim-sweep.*.csv bitfusion/sram/cacti_sweep.*.csv

#Delete existing logs
rm -rf results.*.log


#No need for these, coz now I have separate ini files
#Change a and c in bf_e_conf.ini
#a = N of systolic array
#c = M of systolic array
#Change precision 
#pmax = 8,2
#pmin = 2,2

##Run
#python2 top.py bf_e_conf.16_32_8_2.ini 16 |& tee results.16_32_8_2_b16.log
#python2 top.py bf_e_conf.16_16_8_2.ini 16 |& tee results.16_16_8_2_b16.log
#python2 top.py bf_e_conf.16_32_2_2.ini 16 |& tee results.16_32_2_2_b16.log
#python2 top.py bf_e_conf.16_16_2_2.ini 16 |& tee results.16_16_2_2_b16.log
#
#python2 top.py bf_e_conf.8_8_8_2.ini 16 |& tee results.8_8_8_2_b16.log
#python2 top.py bf_e_conf.8_8_2_2.ini 16 |& tee results.8_8_2_2_b16.log
#python2 top.py bf_e_conf.32_32_8_2.ini 16 |& tee results.32_32_8_2_b16.log
#python2 top.py bf_e_conf.32_32_2_2.ini 16 |& tee results.32_32_2_2_b16.log

#python2 top.py bf_e_conf.8_8_2_2.buf64_32_16.ini 16 |& tee results.8_8_2_2_b16.buf64_32_16.log
#python2 top.py bf_e_conf.16_16_2_2.buf64_32_16.ini 16 |& tee results.16_16_2_2_b16.buf64_32_16.log
#python2 top.py bf_e_conf.32_32_2_2.buf64_32_16.ini 16 |& tee results.32_32_2_2_b16.buf64_32_16.log

python2 top.py bf_e_conf.8_8_2_2.buf64_32_16.freq500m.ini 16 |& tee results.8_8_2_2_b16.buf64_32_16.freq500m.log
python2 top.py bf_e_conf.16_16_2_2.buf64_32_16.freq500m.ini 16 |& tee results.16_16_2_2_b16.buf64_32_16.freq500m.log
python2 top.py bf_e_conf.32_32_2_2.buf64_32_16.freq500m.ini 16 |& tee results.32_32_2_2_b16.buf64_32_16.freq500m.log

#  python2 top.py bf_e_conf.16_32_8_2.ini 1 |& tee results.16_32_8_2_b1.log
#  python2 top.py bf_e_conf.16_16_8_2.ini 1 |& tee results.16_16_8_2_b1.log
#  python2 top.py bf_e_conf.16_32_2_2.ini 1 |& tee results.16_32_2_2_b1.log
#  python2 top.py bf_e_conf.16_16_2_2.ini 1 |& tee results.16_16_2_2_b1.log

#  python2 top.py bf_e_conf.16_32_8_2.ini 32 |& tee results.16_32_8_2_b32.log
#  python2 top.py bf_e_conf.16_16_8_2.ini 32 |& tee results.16_16_8_2_b32.log
#  python2 top.py bf_e_conf.16_32_2_2.ini 32 |& tee results.16_32_2_2_b32.log
#  python2 top.py bf_e_conf.16_16_2_2.ini 32 |& tee results.16_16_2_2_b32.log

#Check the logs to ensure no bad messages
