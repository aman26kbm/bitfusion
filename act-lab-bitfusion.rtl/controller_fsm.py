
class FSM(object):
    idle = 0
    count = 1
    seek = 2

if __name__ == "__main__":
    count_state = [0, 0, 0]
    max_count = [2, 1, 2]

    head_ptr = 0
    tail_ptr = len(count_state) - 1

    state = FSM.count

    count = 0
    base_count_max = max_count[0]
    head_ptr += 1
    ptr = head_ptr

    loop_iter = 1
    for i in max_count:
        loop_iter *= i+1
    total_iter = 0

    seek_window_size = 2


    while not state == FSM.idle:
        total_iter += 1
        print total_iter,
        if state == FSM.count:
            print count_state
        else:
            print '-', ptr

        if state == FSM.count and count == base_count_max:
            state = FSM.seek
            # ptr += 1
            count = 1
        elif state == FSM.seek:
            found = False
            for i in range(seek_window_size):
                if ptr+i < len(max_count) and not found:
                    if count_state[ptr+i] == max_count[ptr+i]:
                        count_state[ptr+i] = 0
                    else:
                        found = True
                        count_state[ptr+i] += 1
                        break

            if found:
                ptr = head_ptr
                state = FSM.count
            else:
                ptr += seek_window_size
        else:
            count += 1
            state = FSM.count

        if state == FSM.seek and ptr >= len(max_count):
            state = FSM.idle
            ptr = head_ptr

        assert ptr < len(max_count)

    print 'Actual Iterations: ', total_iter
    print '% Useful: ', float(loop_iter) / total_iter
