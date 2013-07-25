pins = {
    'adc': {
        9: {
            35:{'name': 'ain7'},
            36:{'name': 'ain6'},
            33:{'name': 'ain5'},
            37:{'name': 'ain3'},
            38:{'name': 'ain4'},
            39:{'name': 'ain1'},
            40:{'name': 'ain2'},
        },
    },
    'pwm': {
        8: {
            13:{
                'directory': 'ehrpwm.2:1',#ehrpwm2B
                'mode':4
                },
            19: {
                'directory': 'ehrpwm.2:0',#ehrpwm2A
                'mode':4
                },
            },
        9: {
            14: {
                'directory': 'ehrpwm.1:0', #ehrpwm1A_mux1
                'mode': 6
            },
            16:{
                'directory': 'ehrpwm.1:1',
                'mode': 6
            },
            21:{
                'directory': 'ehrpwm.0:1',
                'mode': 3
            },
            22:{
                'directory': 'ehrpwm.0:0',
                'mode': 3
            },
        },
    },
    'gpio': {
        8: {
            10: {
                'export':68
            },
            26:  {
                'export':61
            },
        },
        9: {
            12: {
                'export':60
            },
            14: {
                'export':50
            },
            15: {
                'export':48
            },
            16: {
                'export':51
            },
        }
    },
}
