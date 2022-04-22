max_precision = 16
min_precision = 2

imax = int(max_precision // (min_precision * 2))
jmax = int(max_precision // (min_precision * 2))

a_split = [2, 2, 2, 2, 3, 2, 2, -1]
a = a_split * 8
print(a)

a_0 = a_split * 2
a_1 = a_split * 2
a_2 = a_split * 2
a_3 = a_split * 2
for i in reversed(range(imax)):
    for j in reversed(range(jmax)):
        idx = j + i * jmax
        swizzled_idx_0 = j + i * jmax * 2
        swizzled_idx_1 = (j+jmax) + i * jmax * 2
        swizzled_idx_2 = j + (i + imax) * jmax * 2
        swizzled_idx_3 = (j+jmax) + (i+imax) * jmax * 2
        a_0[idx] = a[swizzled_idx_0]
        a_0[idx] = a[swizzled_idx_0]
        a_2[idx] = a[swizzled_idx_2]
        a_3[idx] = a[swizzled_idx_3]

print a_0
print a_1
print a_2
print a_3
