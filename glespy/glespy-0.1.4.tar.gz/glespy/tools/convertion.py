__author__ = 'yarnaid'

import os
import io
import subprocess as sp

import numpy as np

try:
    import tools.tools as tools
    import properties
    import ext.angles as angles
except:
    import glespy.tools.tools as tools
    import glespy.properties as properties
    import glespy.ext.angles as angles


def get_map_attrs(map_name):
    if not os.path.exists(map_name):
        raise StandardError('[%s]: no such file "%s"' %
                            (get_map_attrs.__name__, map_name))
    output = tools.run_cmd(
        [tools.glesp['difmap'], '-st', map_name], debug_msg='getting attrs')
    output = output[0].split()
    output = list(map(lambda x: x.decode('utf-8'), output))
    try:
        res = {
            'nx': int(output[output.index('nx') + 2][0:-1]),
            'np': int(output[output.index('np') + 2]),
        }
    except:
        raise ValueError('Not a glesp file: "%s"' % (map_name))
    return res


def map_to_alm(map_name, alm_name=None, **kwargs):
    if not os.path.exists(map_name):
        raise StandardError('[%s]: no such file "%s"' %
                            (map_to_alm.__name__, map_name))
    attrs = get_map_attrs(map_name)
    tmp_tresh_map = tools.get_out_name(suffix='map_to_alm_trash.fit')
    lmax = (attrs['nx'] - 1) / 2
    alm_name = tools.get_out_name(alm_name, suffix='alm_from_map.fit')
    args = [tools.binaries['cl2map'], '-map', map_name,
            '-lmax', lmax, '-ao', alm_name, '-o', tmp_tresh_map]
    args.extend(kwargs_to_glesp_args(**kwargs))
    tools.run_cmd(args, debug_msg='map to alm')
    try:
        os.remove(tmp_tresh_map)
    except:
        pass
    return alm_name, lmax


def map_to_gif(map_name, gif_name=None, **kwargs):
    if not os.path.exists(map_name):
        raise StandardError('[%s]: no such file "%s"' %
                            (map_to_gif.__name__, map_name))
    gif_name = tools.get_out_name(gif_name, '.gif')
    args = [tools.binaries['f2fig'], map_name, '-o', gif_name]
    args.extend(kwargs_to_glesp_args(**kwargs))
    tools.run_cmd(args, debug_msg='map to gif')
    return gif_name


def show_map(map_name, **kwargs):
    if not os.path.exists(map_name):
        raise StandardError('[%s]: file "%s" does not exists' % (map_name))
    gif = map_to_gif(map_name, **kwargs)
    args = [tools.binaries['viewer'], gif]
    # args.extend(kwargs_to_glesp_args(**kwargs))
    tools.run_cmd(args, debug_msg='show map')


def kwargs_to_glesp_args(**kwargs):
    """
    convert dict of kwargs to format '-name' 'value'
    if value is None --- to '-name' only
    """
    res = []
    for k, v in kwargs.items():
        if v is not None:
            ext = ['-' + k, v]
        else:
            ext = ['-' + k]
        res.extend(ext)
    return res


def props_to_kwargs(prop):
    res = {}
    res.update(prop.__dict__)
    return res


def props_to_glesp_args(prop):
    """

    :param prop: GlesPy.properties.Rendered
    :return: list of args in format '-name' 'value'
    """
    kwargs = props_to_kwargs(prop)
    return kwargs_to_glesp_args(**kwargs)


def kwargs_props_to_glesp_args(**kwargs):
    """
    convert dict from kwargs to format '-name' 'value'
    WITH ADDING ALL PARAMS
    for using as arguments for glesp commands
    :param kwargs:
    :return:
    """
    prop = properties.Rendered(**kwargs)
    if 'l' in kwargs:  # todo: make it works!
        prop.lmin = kwargs['l']
        prop.lmax = kwargs['l']
        kwargs.pop('l')
    opt_args = props_to_glesp_args(prop)
    return opt_args


def alm_to_map(alm_name, map_name=None, **kwargs):
    if len({'nx', 'np', 'lmax', 'l', 'lmin'}.intersection(kwargs)) < 1:
        raise ValueError(
            '[%s]: l or lmax or nx or np must be given' % alm_to_map.__name__)
    opt_args = kwargs_props_to_glesp_args(**kwargs)
    map_name = tools.get_out_name(map_name, 'alm_from_map.fit')
    args = [tools.binaries['cl2map'], '-falm', alm_name, '-o', map_name]
    args.extend(opt_args)
    tools.run_cmd(args, debug_msg='alm to map')
    return map_name


def map_to_hist(map_name, hn=20, **kwargs):
    tmp_hist = tools.get_out_name(suffix='hist_from_map.txt')
    args = [tools.binaries['difmap'], map_name,
            '-st', '-hn', hn, '-hf', tmp_hist]
    args.extend(kwargs_to_glesp_args(**kwargs))
    tools.run_cmd(args, debug_msg='map to hist')
    hist_data = np.loadtxt(tmp_hist)
    os.remove(tmp_hist)
    return hist_data


def alm_to_cl(alm_name, **kwargs):
    if len({'lmax', 'l', 'lmin'}.intersection(kwargs)) < 1:
        raise ValueError(
            '[%s]: lmax or l or lmin must be given' % (alm_to_cl.__name__))
    opt_args = kwargs_props_to_glesp_args(**kwargs)
    args = [tools.binaries['alm2dl'], '-cl']
    args.extend(opt_args)
    with open(os.devnull) as stderr:
        raw_data = sp.check_output(args, stderr=stderr)
    cl_data = np.loadtxt(io.StringIO(raw_data))
    return cl_data


def mask_map(map_name, mask_name, masked_map_name=None, **kwargs):
    masked_map_name = tools.get_out_name(
        masked_map_name, 'masked_from_map.fit')
    opt_args = kwargs_props_to_glesp_args(**kwargs)
    args = [tools.binaries['difmap'], map_name,
            '-mf', mask_name, '-o', masked_map_name]
    args.extend(opt_args)
    tools.run_cmd(args, debug_msg='mask map')
    return masked_map_name


def points_to_map(points_name, map_name=None, **kwargs):
    if len({'nx', 'np', 'lmax', 'l', 'lmin'}.intersection(kwargs)) < 1:
        raise ValueError(
            '[{}]: nx or np or lmax or l or lmin must be given'.format(
                alm_to_cl.__name__)
        )
    map_name = tools.get_out_name(map_name, 'map_from_points.fit')
    opt_args = kwargs_props_to_glesp_args(**kwargs)
    args = [tools.binaries['mappat'], '-fp', points_name, '-o', map_name]
    args.extend(opt_args)
    tools.run_cmd(args, debug_msg='point to map')
    return map_name


def smooth_alm(alm_name, smooth_window, smoothed_name=None, **kwargs):
    smoothed_name = tools.get_out_name(smoothed_name, 'smoothed_alm.fit')
    opt_args = []
    try:
        opt_args = kwargs_props_to_glesp_args(**kwargs)
    except:
        pass
    args = [tools.binaries['rsalm'], alm_name,
            '-fw', smooth_window, '-o', smoothed_name]
    args.extend(opt_args)
    tools.run_cmd(args, debug_msg='smooth alm')
    return smoothed_name


def correlate(map1, map2, correlation_window, correlated_map=None, **kwargs):
    correlated_map = tools.get_out_name(correlated_map, 'correlated_map.fit')
    try:
        opt_args = kwargs_props_to_glesp_args(**kwargs)
    except:
        opt_args = []
    args = [tools.binaries['difmap'], map1, map2,
            '-cw', correlation_window, '-o', correlated_map]
    args.extend(opt_args)
    tools.run_cmd(args, debug_msg='correlate maps')
    return correlated_map


def sum_map(map1_name, map2_name, mult=[1.0, -1.0], summed_map=None, **kwargs):
    attrs1 = get_map_attrs(map1_name)
    attrs2 = get_map_attrs(map2_name)
    if attrs1 != attrs2:
        raise ValueError(
            '[{}]: maps has different resolution'.format(__name__))
    summed_map = tools.get_out_name(summed_map, 'summed.fit')
    for i in range(1, 2, 1):
        k = 'c{}'.format(i)
        if k in kwargs.keys():
            mult[i] = kwargs[k]
            del kwargs[k]
    try:
        targs = kwargs.copy()
        targs.update(attrs1)
        opt_args = kwargs_props_to_glesp_args(**targs)
    except:
        opt_args = []
    args = [tools.binaries['difmap'], '-c1', mult[0],
            '-c2', mult[1], map1_name, map2_name, '-o', summed_map]
    args.extend(opt_args)
    tools.run_cmd(args, debug_msg='sum maps')
    return summed_map


def rotate_alm(alm_name, rotated_name=None, **kwargs):
    """
    phi and psi are angels in radians
    :param dphi
    :param dpsi
    :param dtheta
    :return: rotated_alm_name
    """
    rotated_named = tools.get_out_name(rotated_name, 'rotated_alm.fit')
    opt_args = kwargs_to_glesp_args(**kwargs)
    args = [tools.binaries['difalm'], alm_name, '-o', rotated_named]
    args.extend(opt_args)
    tools.run_cmd(args, debug_msg='rotate alm')
    return rotated_named


def cut_map_zone(map_name, zone, cutted_map=None, **kwargs):
    if not isinstance(zone, angles.Zone):
        raise AssertionError('zone must be an instance of {}'.format(
            angles.Zone.__class__.__name__
        ))
    cutted_map = tools.get_out_name(cutted_map, 'cutted_map.fit')
    opt_args = kwargs_to_glesp_args(**kwargs)
    args = [tools.binaries['difmap'], map_name, '-keep', zone(),
            '-o', cutted_map]
    args.extend(opt_args)
    tools.run_cmd(args, debug_msg='cut map zone')
    return cutted_map
