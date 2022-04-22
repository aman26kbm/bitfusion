import math
import logging

def get_swizzle(high_precision, low_precision):

    ii_max = int(high_precision/(low_precision*2))
    jj_max = int(high_precision/(low_precision*2))

    in_width = int(high_precision * high_precision / low_precision)
    num_data = int(high_precision * high_precision / (low_precision * low_precision))
    irange = int(high_precision/low_precision)
    jrange = int(high_precision/low_precision)

    a_num_modes = int(math.log(high_precision/low_precision) / math.log(2)) + 1
    b_num_modes = int(math.log(high_precision/low_precision) / math.log(2)) + 1
    num_modes = a_num_modes * b_num_modes
    logging.debug('Num Modes = {}'.format(num_modes))

    a_swizzle = {}
    b_swizzle = {}
    for a_mode in range(a_num_modes):

        a_prec = (2 ** a_mode) * low_precision
        for b_mode in range(b_num_modes):

            b_prec = (2 ** b_mode) * low_precision

            mode = '{}x{}'.format(a_prec, b_prec)
            a_swizzle[mode] = []
            b_swizzle[mode] = []

            logging.debug('{}-bit x {}-bit'.format(a_prec, b_prec))

            num_operands = int(high_precision / b_prec) * int(high_precision / a_prec)

            logging.debug('A: {}; B: {}'.format(num_operands, num_operands))

            a_divide = int(b_prec / low_precision)
            logging.debug('a_divide: {}'.format(a_divide))

            b_divide = int(a_prec / low_precision)
            logging.debug('b_divide: {}'.format(b_divide))

            for i in range(irange):
                for j in range(jrange):
                    op = 'a'
                    a_idx = (j + jrange * (i//a_divide))
                    a_op_num = int(a_idx // (a_prec / low_precision))
                    a_part = a_idx % int(a_prec/low_precision)

                    b_idx = (i + irange * (j//b_divide))
                    b_op_num = a_op_num
                    b_part = b_idx % int(b_prec/low_precision)

                    # logging.debug('a[{:>2}, {:>2}] * b[{:>2}, {:>2}]'.format(a_op_num, a_part, b_op_num, b_part), end='\t')
                    a = a_op_num * int(a_prec/low_precision) + j % int(a_prec/low_precision)
                    a_swizzle[mode].append(a)
                    for k in range(low_precision):
                        a_bit_idx = k + low_precision * a

            for j in range(jrange):
                logging.debug('  ')
                logging.debug('A: ', end = ' ')
                for i in range(irange):
                    op = 'a'
                    a_idx = (j + jrange * (i//a_divide))
                    a_op_num = int(a_idx // (a_prec / low_precision))
                    a_part = a_idx % int(a_prec/low_precision)

                    b_idx = (i + irange * (j//b_divide))
                    b_op_num = a_op_num
                    b_part = b_idx % int(b_prec/low_precision)

                    b = b_op_num * int(b_prec/low_precision) + i % int(b_prec/low_precision)
                    if i % (b_prec / low_precision) == 0:
                        b_swizzle[mode].append(b_op_num)
                    for k in range(low_precision):
                        b_bit_idx = k + low_precision * b


    for a_mode in range(a_num_modes):

        a_prec = (2 ** a_mode) * low_precision
        for b_mode in range(b_num_modes):

            b_prec = (2 ** b_mode) * low_precision
            mode = '{}x{}'.format(a_prec, b_prec)

            logging.debug('mode: {}'.format(mode))
            logging.debug('A: ', end='')
            for i in range(len(a_swizzle[mode])):
                logging.debug('{:>4}'.format(a_swizzle[mode][i]), end='')
            logging.debug('')
            logging.debug('B: ', end='')
            for i in range(len(b_swizzle[mode])):
                logging.debug('{:>4}'.format(b_swizzle[mode][i]), end='')
            logging.debug('')

    return b_swizzle

if __name__ == '__main__':
    b_swizzle = get_swizzle(4, 1)
    for mode in b_swizzle:
        print 'Mode: {}'.format(mode)
        print 'B: ',
        for i in b_swizzle[mode]:
            print '{:>4}'.format(i),
        print
