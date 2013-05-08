import os
from chilin2.helpers import json_load, JinjaTemplateCommand, template_dump, underline_to_space, count_in_million, decimal_to_latex_percent

__author__ = 'ad9075'

def _items(json_path):
    return json_load(json_path)["stat"].items()


def _stat(json_path):
    return json_load(json_path)["stat"]


def _cons_summary_table(conf):

    table = []
    has_run = os.path.exists
    pre = conf.json_prefix



    _S = underline_to_space
    _M = count_in_million
    _P = decimal_to_latex_percent

    js = pre + "_fastqc.json"
    if has_run(js):
        for id, stat in _items(js):
            table.append(["FastQC",
                          _S(id), stat["median"], stat["cutoff"], stat["judge"]])

    js = pre + "_bowtie.json"
    if has_run(js):
        for id, stat in _items(js):
            table.append(["Unique mappable reads",
                          _S(os.path.basename(id)),
                          _M(stat["mappable_reads"]),
                          _M(stat["cutoff"]),
                          stat["judge"]])

    js = pre + "_macs2.json"
    if has_run(js):
        stat = _stat(js)
        table.append(
            ["High confident peaks",
             _S(conf.id),
             _M(stat["peaksge10"]),
             _M(stat["cutoff"]["high_conf_peaks"]),
             stat["judge"]["high_conf_peaks"]])

    js = pre + "_macs2_on_sample.json"
    if has_run(js):
        macs2s_stat = _stat(js)
        for id, stat in macs2s_stat.items():
            table.append(["Unique location rate",
                          _S(id),
                          _P(stat["unic_loc_rate"]),
                          _P(stat["cutoff"]["unic_loc_rate"]),
                          stat["judge"]["unic_loc_rate"]])
            table.append(["Unique location",
                          _S(id),
                          _M(stat["unic_loc"]),
                          _M(stat["cutoff"]["unic_loc"]),
                          stat["judge"]["unic_loc"]])

    js = pre + "_dhs.json"
    if has_run(js):
        stat = _stat(js)
        table.append(["DHS ratio",
                      _S(conf.id),
                      _P(stat["dhspercentage"]),
                      _P(stat["cutoff"]),
                      stat["judge"]])

    #    js = pre + "_cor.json"
    #    if has_run(js):
    #        stat = _S(js)
    #        table.append(["Replicates Correlation",
    #                      conf.id, stat["min_cor"], stat["cutoff"], stat["judge"]])

    js = pre + "_velcro.json"
    if has_run(js):
        stat = _stat(js)
        table.append(
            ["non Velro ratio",
             _S(conf.id),
             _P(stat["nonvelcropercentage"]),
             _P(stat["cutoff"]),
             stat["judge"]])

    js = pre + "_conserv.json"
    if has_run(js):
        stat = _stat(js)
        table.append(["Conservation QC",
                      _S(conf.id),
                      "",
                      "",
                      stat["judge"]])
    return table


def latex_summary_table(input, output, param):
    summary_table = _cons_summary_table(param["conf"])

    latex = JinjaTemplateCommand(
        template=input["template"],
        param={"SummaryQC": True,
               "summary_table": summary_table,
               "render_dump": output["latex"]})
    template_dump(latex)