CODEC_PERMUTATION = {
    'libx264': {
        'profiles': ['baseline', 'main', 'high', 'high10', 'high422', 'high444'],
        'pixelFormats': {
            'baseline': ['yuv420p'],
            'main': ['yuv420p'],
            'high': ['yuv420p'],
            'high10': ['yuv422p10le', 'yuv420p10le'],
            'high422': ['yuv422p'],
            'high444': ['yuv444p']
        },
        'presets': {
            'baseline': ['ultrafast', 'superfast', 'veryfast', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
            'main': ['ultrafast', 'superfast', 'veryfast', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
            'high': ['ultrafast', 'superfast', 'veryfast', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
            'high10': ['ultrafast', 'superfast', 'veryfast', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
            'high422': ['ultrafast', 'superfast', 'veryfast', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
            'high444': ['ultrafast', 'superfast', 'veryfast', 'fast', 'medium', 'slow', 'slower', 'veryslow']
        }
    },
    'h264_nvenc': {
        'profiles': ['baseline', 'main', 'high', 'high444p'],
        'pixelFormats': {
            'baseline': ['yuv420p', 'nv12', 'cuda'],
            'main': ['yuv420p', 'nv12', 'p010le', 'cuda'],
            'high': ['yuv420p', 'nv12', 'p010le', 'cuda'],
            'high444p': ['yuv444p', 'yuv444p16le', 'gbrp', 'gbrp16le']
        },
        'presets': {
            'default': ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7'],
            'hq': ['slow', 'medium', 'fast', 'll', 'llhq', 'llhp', 'lossless'],
            'll': ['ll', 'llhq', 'llhp'],
            'lossless': ['lossless', 'losslesshp']
        },
        'levels': ['1', '1.0', '1b', '1.1', '1.2', '1.3', '2', '2.0', '2.1', '2.2', '3', '3.0',
                   '3.1', '3.2', '4', '4.0', '4.1', '4.2', '5', '5.0', '5.1', '5.2', '6', '6.0', '6.1', '6.2'],
        'tunes': ['hq', 'll', 'ull', 'lossless'],
        'rc_modes': ['constqp', 'vbr', 'cbr', 'vbr_minqp', 'll_2pass_quality', 'll_2pass_size']
    },

    'libx265': {
        'profiles': ['main', 'main10', 'main422-10', 'main444-10'],
        'pixelFormats': {
            'main': ['yuv420p'],
            'main10': ['yuv420p10le', 'yuv422p10le'],
            'main422-10': ['yuv422p10le'],
            'main444-10': ['yuv444p10le']
        },
        'presets': {
            'main': ['ultrafast', 'superfast', 'veryfast', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
            'main10': ['ultrafast', 'superfast', 'veryfast', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
            'main422-10': ['ultrafast', 'superfast', 'veryfast', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
            'main444-10': ['ultrafast', 'superfast', 'veryfast', 'fast', 'medium', 'slow', 'slower', 'veryslow']
        }
    }
}
