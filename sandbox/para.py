import multiprocessing
import timeit
import operator

def do_something(x):
    v = pow(x, 2)
    return v


# multiprocessing.freeze_support()

if __name__ == "__main__":

    a = []
    start = timeit.default_timer()
    for i in range(1, 1000000000):
        a.append(do_something(i))

    end = timeit.default_timer()
    print('single processing time:', str(end-start), 's')
    print(a[1:10])

    # revise to parallel
    items = [x for x in range(1, 1000000000)]
    p = multiprocessing.Pool(4)
    start = timeit.default_timer()
    b = p.map(do_something, items)
    p.close()
    p.join()
    end = timeit.default_timer()
    print('multi processing time:', str(end-start),'s')
    print(b[1:10])
    print('Return values are all equal ?:', operator.eq(a, b))
