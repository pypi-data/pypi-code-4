import numpy
import numpy.linalg as la
import reikna.cluda as cluda

api = cluda.ocl_api()
platform = api.get_platforms()[0]
device = platform.get_devices()[1]
thr = api.Thread(device)

src = """
WITHIN_KERNEL VSIZE_T virtual_local_id(unsigned int dim)
{
    if (dim == 0)
    {
        SIZE_T flat_id =
            get_local_id(0) * 1 +
            0;

        return (flat_id / 1);
    }

    return 0;
}

WITHIN_KERNEL VSIZE_T virtual_local_size(unsigned int dim)
{
    if (dim == 0)
    {
        return 100;
    }

    return 1;
}

WITHIN_KERNEL VSIZE_T virtual_group_id(unsigned int dim)
{
    if (dim == 0)
    {
        SIZE_T flat_id =
            get_group_id(0) * 1 +
            0;

        return (flat_id / 1);
    }

    return 0;
}

WITHIN_KERNEL VSIZE_T virtual_num_groups(unsigned int dim)
{
    if (dim == 0)
    {
        return 1;
    }

    return 1;
}

WITHIN_KERNEL VSIZE_T virtual_global_id(unsigned int dim)
{
    return virtual_local_id(dim) + virtual_group_id(dim) * virtual_local_size(dim);
}

WITHIN_KERNEL VSIZE_T virtual_global_size(unsigned int dim)
{
    if(dim == 0)
    {
        return 100;
    }

    return 1;
}

WITHIN_KERNEL VSIZE_T virtual_global_flat_id()
{
    return
        virtual_global_id(0) * 1 +
        0;
}

WITHIN_KERNEL VSIZE_T virtual_global_flat_size()
{
    return
        virtual_global_size(0) *
        1;
}


WITHIN_KERNEL bool virtual_skip_local_threads()
{

    return false;
}

WITHIN_KERNEL bool virtual_skip_groups()
{

    return false;
}

WITHIN_KERNEL bool virtual_skip_global_threads()
{

    return false;
}

#define VIRTUAL_SKIP_THREADS if(virtual_skip_local_threads() || virtual_skip_groups() || virtual_skip_global_threads()) return

typedef struct {
    unsigned long  v[2];
}  _module0_;




            WITHIN_KERNEL _module0_ _module1_key_from_int(int idx)
            {
                _module0_ result;

                result.v[0] = 8618484947917433856
                ;
                result.v[1] = 0
                    + idx
                ;

                return result;
            }




typedef struct {
    unsigned long  v[4];
}  _module2_;




WITHIN_KERNEL _module2_ _module3_make_counter_from_int(int x)
{
    _module2_ result;
    result.v[0] = 0;
    result.v[1] = 0;
    result.v[2] = 0;
    result.v[3] = x;
    return result;
}


WITHIN_KERNEL INLINE unsigned long _module3_mulhilo(
    unsigned long *hip, unsigned long a, unsigned long b)
{
#ifdef CUDA
    *hip = __umul64hi(a, b);
#else
    *hip = mul_hi(a, b);
#endif
    return a * b;
}

WITHIN_KERNEL _module2_ _module3_bijection(
    const _module0_ key, const _module2_ counter)
{
    _module2_ X = counter;

    unsigned long key0 = key.v[0];
    unsigned long key1 = key.v[1];

    unsigned long hi0, lo0, hi1, lo1;

    // round 0

        lo0 = _module3_mulhilo(&hi0, 15197193596820024467, X.v[0]);
        lo1 = _module3_mulhilo(&hi1, 14581110107779764567, X.v[2]);
        X.v[0] = hi1 ^ X.v[1] ^ key0;
        X.v[1] = lo1;
        X.v[2] = hi0 ^ X.v[3] ^ key1;
        X.v[3] = lo0;

    // bump key
    key0 += 11400714819323198485;
    key1 += 13503953896175478587;

    // round 1

        lo0 = _module3_mulhilo(&hi0, 15197193596820024467, X.v[0]);
        lo1 = _module3_mulhilo(&hi1, 14581110107779764567, X.v[2]);
        X.v[0] = hi1 ^ X.v[1] ^ key0;
        X.v[1] = lo1;
        X.v[2] = hi0 ^ X.v[3] ^ key1;
        X.v[3] = lo0;

    // bump key
    key0 += 11400714819323198485;
    key1 += 13503953896175478587;

    // round 2

        lo0 = _module3_mulhilo(&hi0, 15197193596820024467, X.v[0]);
        lo1 = _module3_mulhilo(&hi1, 14581110107779764567, X.v[2]);
        X.v[0] = hi1 ^ X.v[1] ^ key0;
        X.v[1] = lo1;
        X.v[2] = hi0 ^ X.v[3] ^ key1;
        X.v[3] = lo0;

    // bump key
    key0 += 11400714819323198485;
    key1 += 13503953896175478587;

    // round 3

        lo0 = _module3_mulhilo(&hi0, 15197193596820024467, X.v[0]);
        lo1 = _module3_mulhilo(&hi1, 14581110107779764567, X.v[2]);
        X.v[0] = hi1 ^ X.v[1] ^ key0;
        X.v[1] = lo1;
        X.v[2] = hi0 ^ X.v[3] ^ key1;
        X.v[3] = lo0;

    // bump key
    key0 += 11400714819323198485;
    key1 += 13503953896175478587;

    // round 4

        lo0 = _module3_mulhilo(&hi0, 15197193596820024467, X.v[0]);
        lo1 = _module3_mulhilo(&hi1, 14581110107779764567, X.v[2]);
        X.v[0] = hi1 ^ X.v[1] ^ key0;
        X.v[1] = lo1;
        X.v[2] = hi0 ^ X.v[3] ^ key1;
        X.v[3] = lo0;

    // bump key
    key0 += 11400714819323198485;
    key1 += 13503953896175478587;

    // round 5

        lo0 = _module3_mulhilo(&hi0, 15197193596820024467, X.v[0]);
        lo1 = _module3_mulhilo(&hi1, 14581110107779764567, X.v[2]);
        X.v[0] = hi1 ^ X.v[1] ^ key0;
        X.v[1] = lo1;
        X.v[2] = hi0 ^ X.v[3] ^ key1;
        X.v[3] = lo0;

    // bump key
    key0 += 11400714819323198485;
    key1 += 13503953896175478587;

    // round 6

        lo0 = _module3_mulhilo(&hi0, 15197193596820024467, X.v[0]);
        lo1 = _module3_mulhilo(&hi1, 14581110107779764567, X.v[2]);
        X.v[0] = hi1 ^ X.v[1] ^ key0;
        X.v[1] = lo1;
        X.v[2] = hi0 ^ X.v[3] ^ key1;
        X.v[3] = lo0;

    // bump key
    key0 += 11400714819323198485;
    key1 += 13503953896175478587;

    // round 7

        lo0 = _module3_mulhilo(&hi0, 15197193596820024467, X.v[0]);
        lo1 = _module3_mulhilo(&hi1, 14581110107779764567, X.v[2]);
        X.v[0] = hi1 ^ X.v[1] ^ key0;
        X.v[1] = lo1;
        X.v[2] = hi0 ^ X.v[3] ^ key1;
        X.v[3] = lo0;

    // bump key
    key0 += 11400714819323198485;
    key1 += 13503953896175478587;

    // round 8

        lo0 = _module3_mulhilo(&hi0, 15197193596820024467, X.v[0]);
        lo1 = _module3_mulhilo(&hi1, 14581110107779764567, X.v[2]);
        X.v[0] = hi1 ^ X.v[1] ^ key0;
        X.v[1] = lo1;
        X.v[2] = hi0 ^ X.v[3] ^ key1;
        X.v[3] = lo0;

    // bump key
    key0 += 11400714819323198485;
    key1 += 13503953896175478587;

    // round 9

        lo0 = _module3_mulhilo(&hi0, 15197193596820024467, X.v[0]);
        lo1 = _module3_mulhilo(&hi1, 14581110107779764567, X.v[2]);
        X.v[0] = hi1 ^ X.v[1] ^ key0;
        X.v[1] = lo1;
        X.v[2] = hi0 ^ X.v[3] ^ key1;
        X.v[3] = lo0;



    return X;
}




typedef unsigned int _module3_uint32;
typedef unsigned long _module3_uint64;

typedef struct _module3_
{
    _module0_ key;
    _module2_ counter;
    union {
        _module2_ buffer;
        unsigned int buffer_uint32[8];
    };
    int buffer_uint32_cursor;
} _module3_STATE;


WITHIN_KERNEL void _module3_bump_counter(_module3_STATE *state)
{
    state->counter.v[3] += 1;
    if (state->counter.v[3] == 0)
    {
    state->counter.v[2] += 1;
    if (state->counter.v[2] == 0)
    {
    state->counter.v[1] += 1;
    if (state->counter.v[1] == 0)
    {
    state->counter.v[0] += 1;
    }
    }
    }
}

WITHIN_KERNEL void _module3_refill_buffer(_module3_STATE *state)
{
    state->buffer = _module3_bijection(state->key, state->counter);
}

WITHIN_KERNEL _module3_STATE _module3_make_state(_module0_ key, _module2_ counter)
{
    _module3_STATE state;
    state.key = key;
    state.counter = counter;
    state.buffer_uint32_cursor = 0;
    _module3_refill_buffer(&state);
    return state;
}

WITHIN_KERNEL unsigned int _module3_get_raw_uint32(_module3_STATE *state)
{
    if (state->buffer_uint32_cursor == 8)
    {
        _module3_bump_counter(state);
        state->buffer_uint32_cursor = 0;
        _module3_refill_buffer(state);
    }

    int cur = state->buffer_uint32_cursor;
    state->buffer_uint32_cursor += 1;
    return state->buffer_uint32[cur];
}

WITHIN_KERNEL unsigned long _module3_get_raw_uint64(_module3_STATE *state)
{
    if (state->buffer_uint32_cursor >= 8 - 1)
    {
        _module3_bump_counter(state);
        state->buffer_uint32_cursor = 0;
        _module3_refill_buffer(state);
    }

    int cur = state->buffer_uint32_cursor;
    state->buffer_uint32_cursor += 2;
    return state->buffer.v[cur / 2];
}





typedef float _module5_value;
#define _module5_RANDOMS_PER_CALL 1

typedef struct
{
    float v[1];
} _module5_RESULT;


WITHIN_KERNEL _module5_RESULT _module5_sample(_module3_STATE *state)
{
    _module5_RESULT result;
    float normalized = (float)_module3_get_raw_uint32(state) / 4294967296.0f;
    result.v[0] = normalized * (1.0f) + (0.0f);
    return result;
}




typedef float _module4_value;
#define _module4_RANDOMS_PER_CALL 2

typedef struct
{
    float v[2];
} _module4_RESULT;


WITHIN_KERNEL _module4_RESULT _module4_sample(_module3_STATE *state)
{
    _module4_RESULT result;
    _module5_RESULT r1 = _module5_sample(state);
    r1 = _module5_sample(state);
    _module5_RESULT r2 = _module5_sample(state);

    float u1 = r1.v[0];
    float u2 = r2.v[0];

    float ang = 6.2831854820251465f * u2;
    float c_ang = cos(ang);
    float s_ang = sin(ang);

    float coeff = sqrt(-2.0f * log(u1)) * (10.0f);

    result.v[0] = u1;
    result.v[1] = u1;
    return result;
}



        KERNEL void test(GLOBAL_MEM float *dest, int ctr_start)
        {
            VIRTUAL_SKIP_THREADS;
            const VSIZE_T idx = virtual_global_id(0);

            if (idx != 0)
                return;

            _module0_ key = _module1_key_from_int(idx);
            _module2_ ctr = _module3_make_counter_from_int(ctr_start);
            _module3_STATE st = _module3_make_state(key, ctr);

            _module4_RESULT res;

            for(int j = 0; j < 1; j++)
            {
                res = _module4_sample(&st);

                dest[j * 200 + 0 + idx] = res.v[0];
                dest[j * 200 + 100 + idx] = res.v[1];
            }
        }
"""



prg_false = thr.compile(src, fast_math=False)
prg_true = thr.compile(src, fast_math=True)

test_false = prg_false.test
test_true = prg_true.test

N = 100
n_dev = thr.to_device(numpy.zeros((2, N), numpy.float32))

test_false(n_dev, numpy.int32(0), global_size=N)
ns_false = n_dev.get()
print ns_false

test_true(n_dev, numpy.int32(0), global_size=N)
ns_true = n_dev.get()

print ns_true



print la.norm(ns_false - ns_true) / la.norm(ns_true)

