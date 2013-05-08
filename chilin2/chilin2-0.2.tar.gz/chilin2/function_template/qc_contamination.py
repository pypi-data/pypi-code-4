import json
import random
from chilin2.function_template.qc_bowtie import _bowtie_summary_parse
from chilin2.helpers import JinjaTemplateCommand, template_dump, json_load, underline_to_space, decimal_to_latex_percent

__author__ = 'qinqianhappy'

def fastq_sampling(input = {"fastq": ""}, output = {"fastq_sample": ""}, param = {"random_number": ""}):
    """ get N random headers from a fastq file without reading the
    whole thing into memory"""
    num_lines = sum(1 for _ in open(input["fastq"])) / 4

    rand_nums = sorted([random.randint(0, num_lines - 1) for _ in range(param["random_number"])])

    fastq = open(input["fastq"],"rU")
    fastq_sample = open(output["fastq_sample"], "w")

    cur_num = - 1
    for rand_num in rand_nums:
        while cur_num < rand_num:
            for i in range(4):
                fastq.readline()
            cur_num += 1

        for i in range(4):
            fastq_sample.write(fastq.readline())
        cur_num += 1

    fastq_sample.close()
    fastq.close()

    print("wrote to %s" % (output["fastq_sample"]))

## summary of library contamination
def stat_contamination(input = {"bowtie_summaries": [[]]},
                    output = {"json": ""}, param = {"samples": "", "species": "", "id": ""}):

    library_contamination = {}
    library_contamination["meta"] = {"sample": param["id"], "species": param["species"]}
    library_contamination["value"] = {}
    for a_summary, s in zip(input["bowtie_summaries"], map(underline_to_space, param["samples"])):
        ## each bowtie_summary has several species information
        library_contamination["value"][s] = {}
        for i, j in zip(a_summary, param["species"]):
            ## species 1, species2, species3
            parsed_summary = _bowtie_summary_parse(i)
            library_contamination["value"][s][j] = parsed_summary["mappable_rate"]

    json_dict = {"stat": {}, "input": input, "output": output, "param": param}
    json_dict["stat"] = library_contamination
    with open(output["json"], "w") as f:
        json.dump(json_dict, f, indent=4)

def latex_contamination(input, output, param):
    json_dict = json_load(input["json"])

    if len(json_dict["stat"]["meta"]["species"]) < 1:
        section_name = ""
    else:
        section_name = "library_contamination"

    contam_values = json_dict["stat"]["value"]
    for sample in contam_values:
        for species in contam_values[sample]:
            contam_values[sample][species] = decimal_to_latex_percent(contam_values[sample][species])

    library_quality_latex = JinjaTemplateCommand(
        name="library contamination",
        template=input["template"],
        param={"section_name": section_name,
               "library_contamination": json_dict["stat"],
               'prefix_dataset_id': json_dict["param"]['id'],
               "render_dump": output["latex"]
        })
    template_dump(library_quality_latex)
