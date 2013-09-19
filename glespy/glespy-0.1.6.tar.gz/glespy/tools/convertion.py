#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-


__author__ = 'yarnaid'

import os
import cStringIO as StringIO
import subprocess as sp

import numpy as np

import glespy.tools.tools as tools
import glespy.properties as properties
from glespy.ext.angles import Zone, Angle


rtypes = ('c', 'h', 'v', 'p', 'C', 'H', 'V', 'P')


def check_file(name):
    if not os.path.exists(name):
        raise IOError('Fail in proceeding file {}'.format(name))
    return name


def get_map_attrs(map_name):
    check_file(map_name)
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
    check_file(map_name)
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
    check_file(alm_name)
    return alm_name


def map_to_gif(map_name, gif_name=None, **kwargs):
    check_file(map_name)
    gif_name = tools.get_out_name(gif_name, suffix='map.gif')
    args = [tools.binaries['f2fig'], map_name, '-o', gif_name]
    args.extend(kwargs_to_glesp_args(**kwargs))
    tools.run_cmd(args, debug_msg='map to gif')
    check_file(gif_name)
    return gif_name


def show_map(map_name, **kwargs):
    check_file(map_name)
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
    check_file(alm_name)
    opt_args = kwargs_props_to_glesp_args(**kwargs)
    map_name = tools.get_out_name(map_name, suffix='alm_from_map.fit')
    args = [tools.binaries['cl2map'], '-falm', alm_name, '-o', map_name]
    args.extend(opt_args)
    tools.run_cmd(args, debug_msg='alm to map')
    check_file(map_name)
    return map_name


def map_to_hist(map_name, hn=20, **kwargs):
    check_file(map_name)
    tmp_hist = tools.get_out_name(suffix='hist_from_map.txt')
    args = [tools.binaries['difmap'], map_name,
            '-st', '-hn', hn, '-hf', tmp_hist]
    args.extend(kwargs_to_glesp_args(**kwargs))
    args = remove_nx_np(args)
    tools.run_cmd(args, debug_msg='map to hist')
    hist_data = np.loadtxt(tmp_hist)
    os.remove(tmp_hist)
    return hist_data


def remove_nx_np(bad_args):
    args = bad_args
    for k in ('-nx', '-np'):
        try:
            i = args.index(k)
            del args[i + 1], args[i]
        except:
            pass
    return args


def alm_to_cl(alm_name, **kwargs):
    if len(set(['lmax', 'l', 'lmin']).intersection(kwargs)) < 1:
        raise ValueError(
            '[%s]: lmax or l or lmin must be given' % (alm_to_cl.__name__))
    opt_args = kwargs_props_to_glesp_args(**kwargs)
    args = [tools.binaries['alm2dl'], '-cl', alm_name]
    args.extend(opt_args)
    args = remove_nx_np(args)
    with open(os.devnull) as stderr:
        args = map(str, args)
        raw_data = sp.check_output(args, stderr=stderr)
    cl_data = np.loadtxt(StringIO.StringIO(raw_data))
    return cl_data


def mask_map(map_name, mask_name, masked_map_name=None, **kwargs):
    check_file(map_name)
    check_file(mask_name)
    masked_map_name = tools.get_out_name(
        masked_map_name, suffix='masked_from_map.fit')
    opt_args = kwargs_props_to_glesp_args(**kwargs)
    args = [tools.binaries['difmap'], map_name,
            '-mf', mask_name, '-o', masked_map_name]
    args.extend(opt_args)
    args = remove_nx_np(args)
    tools.run_cmd(args, debug_msg='mask map')
    check_file(masked_map_name)
    return masked_map_name


def asci_to_map(asci_name, tp, map_name=None, **kwargs):
    if tp not in ['fm', 'fp']:
        raise ValueError('asci type must be fm or fp, {} got'.format(tp))
    if len(set(['nx', 'np', 'lmax', 'l', 'lmin']).intersection(kwargs)) < 1:
        raise ValueError(
            '[{}]: nx or np or lmax or l or lmin must be given'.format(
                alm_to_cl.__name__)
        )
    map_name = tools.get_out_name(map_name, suffix='map_from_points.fit')
    opt_args = kwargs_props_to_glesp_args(**kwargs)
    args = [tools.binaries['mappat'], '-'+tp, asci_name, '-o', map_name]
    args.extend(opt_args)
    tools.run_cmd(args, debug_msg='point to map')
    return check_file(map_name)


def points_to_map(points_name, map_name=None, **kwargs):
    return asci_to_map(points_name, 'fp', map_name, **kwargs)


def ascii_map_to_map(asci_map_name, map_name=None, **kwargs):
    return asci_to_map(asci_map_name, 'fm', map_name, **kwargs)


def smooth_alm(alm_name, smooth_window, smoothed_name=None, **kwargs):
    check_file(alm_name)
    smoothed_name = tools.get_out_name(
        smoothed_name, suffix='smoothed_alm.fit')
    opt_args = []
    try:
        opt_args = kwargs_props_to_glesp_args(**kwargs)
    except:
        pass
    args = [tools.binaries['rsalm'], alm_name,
            '-fw', smooth_window, '-o', smoothed_name]
    args.extend(opt_args)
    tools.run_cmd(args, debug_msg='smooth alm')
    return check_file(smoothed_name)


def correlate(map1, map2, correlation_window, correlated_map=None, **kwargs):
    check_file(map1)
    check_file(map2)
    correlated_map = tools.get_out_name(
        correlated_map, suffix='correlated_map.fit')
    try:
        opt_args = kwargs_props_to_glesp_args(**kwargs)
    except:
        opt_args = []
    args = [tools.binaries['difmap'], map1, map2,
            '-cw', correlation_window, '-o', correlated_map]
    args.extend(opt_args)
    args = remove_nx_np(args)
    tools.run_cmd(args, debug_msg='correlate maps')
    return check_file(correlated_map)


def sum_map(map1_name, map2_name, mult=[1.0, -1.0], summed_map=None, **kwargs):
    check_file(map1_name)
    check_file(map2_name)
    attrs1 = get_map_attrs(map1_name)
    attrs2 = get_map_attrs(map2_name)
    if attrs1 != attrs2:
        raise ValueError(
            '[{}]: maps has different resolution'.format(__name__))
    summed_map = tools.get_out_name(summed_map, suffix='summed.fit')
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
    args = remove_nx_np(args)
    tools.run_cmd(args, debug_msg='sum maps')
    return check_file(summed_map)


def rotate_alm(alm_name, rotated_name=None, angle=None, **kwargs):
    """
    phi and psi are angels in radians
    :param dphi
    :param dpsi
    :param dtheta
    :return: rotated_alm_name
    """
    if not isinstance(angle, (Angle, type(None))):
        raise TypeError(
            'Angle must be an instance of {} class, {}.got'.format(
                angle.Angle.__class__.__name__, type(angle),
            )
        )
    check_file(alm_name)
    rotated_name = tools.get_out_name(rotated_name, suffix='rotated_alm.fit')
    opt_args = kwargs.copy()
    if angle:
        for k in ['dphi', 'dtheta', 'dp', 'dt']:
            opt_args.pop(k, None)
        opt_args['dtheta'] = angle.theta_d()
        opt_args['dphi'] = angle.phi_d()

    opt_args = kwargs_to_glesp_args(**opt_args)
    args = [tools.binaries['difalm'], alm_name, '-o', rotated_name]
    args.extend(opt_args)
    tools.run_cmd(args, debug_msg='rotate alm')
    return check_file(rotated_name)


def cut_map_zone(map_name, zone, cutted_map=None, **kwargs):
    if not isinstance(zone, Zone):
        raise AssertionError('zone must be an instance of {}'.format(
            Zone.__class__.__name__
        ))
    check_file(map_name)
    cutted_map = tools.get_out_name(cutted_map, suffix='cutted_map.fit')
    opt_args = kwargs_to_glesp_args(**kwargs)
    args = [tools.binaries['difmap'], map_name, '-keep', zone(),
            '-o', cutted_map]
    args.extend(opt_args)
    args = remove_nx_np(args)
    tools.run_cmd(args, debug_msg='cut map zone')
    try:
        return check_file(cutted_map)
    except:
        tools.debug(args)
        raise IOError('Failed to calc file {}'.format(cutted_map))


def reflect_map(map_name, rtype, reflected_name=None, **kwargs):
    if rtype not in rtypes:
        raise ValueError(
            'Reflection type must be in {}, got {}'.format(rtypes, rtype)
        )
    reflected_name = tools.get_out_name(
        reflected_name, suffix='reflected_map.fit',
    )
    check_file(map_name)
    args = [tools.binaries['difmap'], map_name, '-o', reflected_name,
            '-mir{}'.format(rtype.upper()),
            ]
    opt_args = kwargs_to_glesp_args(**kwargs)
    args.extend(opt_args)
    args = remove_nx_np(args)
    tools.run_cmd(args, debug_msg='reflect map')
    return check_file(reflected_name)


def mult_map(map_name, mult, mult_name=None, **kwargs):
    check_file(map_name)
    mult_name = tools.get_out_name(
        mult_name,
        suffix='multed_{}_map_fit'.format(mult),
    )
    opt_args = kwargs_to_glesp_args(**kwargs)
    args = [tools.binaries['difmap'], map_name, '-cf', mult, '-o', mult_name]
    args.extend(opt_args)
    args = remove_nx_np(args)
    tools.run_cmd(args, debug_msg='multiplying map')
    return check_file(mult_name)


def alm_update_ls(alm_name, update_alm_name=None, **kwargs):
    check_file(alm_name)
    update_alm_name = tools.get_out_name(update_alm_name, 'update_alm.fit')
    args = [tools.binaries['difalm'], alm_name, '-o', update_alm_name]
    opt_args = kwargs_to_glesp_args(**kwargs)
    args.extend(opt_args)
    args = remove_nx_np(args)
    tools.run_cmd(args, debug_msg='update alm l')
    return check_file(update_alm_name)
