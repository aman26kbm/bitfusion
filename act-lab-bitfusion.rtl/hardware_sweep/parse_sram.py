def parse_stats(stats):
    words, bits, size_in_bits, mux, frequency,x,y,volt,ac_core_rd,ac_peri_rd,ac_core_wr,ac_peri_wr,standby_core_chipdisable,standby_peri_chipdisable,standby_core_ret1,standby_peri_ret1,standby_core_selective_precharge,standby_peri_selective_precharge,deselect_core,deselect_peri,peak_core,peak_peri,inrush_core,inrush_peri,_ = stats

    size_in_bytes = int(size_in_bits)/8
    area_in_um2 = float(x) * float(y)

    clock_period = 1 / (int(frequency) * 1.e6)
    rd_energy = (float(ac_core_rd) + float(ac_peri_rd)) * clock_period * float(volt) * 1.e9
    wr_energy = (float(ac_core_wr) + float(ac_peri_wr)) * clock_period * float(volt) * 1.e9
    static_power = 0

    aspect_ratio = float(x) / float(y)
    aspect_ratio = max(aspect_ratio, 1/aspect_ratio)

    return size_in_bytes, bits, area_in_um2, rd_energy, wr_energy, aspect_ratio

if __name__ == "__main__":
    with open('sram_results.csv', 'r') as f:
        lines = f.readlines()[1:]

    results = {}

    for line in lines:
        s, bits, a, rd, wr, ratio = parse_stats(line.rstrip('\n').split(','))
        key = '{}-bytes,{}-bitwidth'.format(s, bits)
        if key not in results or results[key][5] > ratio:
            results[key] = (s, bits, a, rd, wr, ratio)

    with open('sram_results_parsed.csv', 'w') as f:
        f.write('Size (Bytes), Width (bits), Area (um^2), Read Energy (nJ), Write Energy (nJ)\n')
        for key in sorted(results):
            s, bits, a, rd, wr, ratio = results[key]
            f.write('{},{},{},{},{},{}\n'.format(s, bits, a, rd, wr, ratio))
