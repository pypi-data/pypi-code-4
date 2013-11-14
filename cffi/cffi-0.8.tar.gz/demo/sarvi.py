import cffi

ffi = cffi.FFI()

ffi.cdef("""
typedef ... *tdl_handle_t;

typedef tdl_handle_t my_local_handle;
typedef tdl_handle_t my_remote_handle;

typedef struct my_error_code_ {
    int error;
    my_remote_handle *rh;
} my_error_code_t;

typedef int (*my_app_error_member_handler_t)(
            my_local_handle,
            my_remote_handle,
            my_remote_handle,
            int,
            void *);

my_local_handle make_handle(void);

// Just a dummy function that prints "Hello World and all the parameters"
int my_iterate_error_code(my_local_handle lh,
                           my_remote_handle rh,
                           my_error_code_t *context,
                           my_app_error_member_handler_t app_callback,
                           void *app_context);
""")






lib = ffi.verify('''

typedef struct tdlhandle_s *tdl_handle_t;
struct tdlhandle_s {
      int hello;
      char world[255];
      void *ctx;
};
typedef tdl_handle_t my_local_handle;
typedef tdl_handle_t my_remote_handle;

typedef struct my_error_code_ {
    int error;
    my_remote_handle *rh;
} my_error_code_t;

typedef int (*my_app_error_member_handler_t)(
            my_local_handle,
            my_remote_handle,
            my_remote_handle,
            int,
            void *);

my_local_handle make_handle(void)
{
   return (my_local_handle)malloc(sizeof(struct tdlhandle_s));
}

// Just a dummy function that prints "Hello World and all the parameters"
int my_iterate_error_code(my_local_handle lh,
                           my_remote_handle rh,
                           my_error_code_t *context,
                           my_app_error_member_handler_t app_callback,
                           void *app_context)
{
   return 42;
}

''')


p1 = lib.make_handle()
p2 = lib.make_handle()

print p1

print lib.my_iterate_error_code(p1, p2, ffi.NULL, ffi.NULL, ffi.NULL)
