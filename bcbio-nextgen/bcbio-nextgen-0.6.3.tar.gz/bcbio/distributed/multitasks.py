"""Multiprocessing ready entry points for sample analysis.
"""
from bcbio import utils
from bcbio.bam import callable
from bcbio.pipeline import lane, qcsummary, sample, shared, variation
from bcbio.variation import bamprep, realign, genotype, ensemble, multi, recalibrate

@utils.map_wrap
def process_lane(*args):
    return lane.process_lane(*args)

@utils.map_wrap
def trim_lane(*args):
    return lane.trim_lane(*args)

@utils.map_wrap
def process_alignment(*args):
    return lane.process_alignment(*args)
process_alignment.metadata = {"resources": ["novoalign", "bwa"]}

@utils.map_wrap
def align_prep_full(*args):
    return lane.align_prep_full(*args)
align_prep_full.metadata = {"resources": ["novoalign", "bwa", "gatk"]}

@utils.map_wrap
def merge_sample(*args):
    return sample.merge_sample(*args)

@utils.map_wrap
def delayed_bam_merge(*args):
    return sample.delayed_bam_merge(*args)

@utils.map_wrap
def piped_bamprep(*args):
    return bamprep.piped_bamprep(*args)

@utils.map_wrap
def prep_recal(*args):
    return recalibrate.prep_recal(*args)
prep_recal.metadata = {"resources": ["gatk"]}

@utils.map_wrap
def write_recal_bam(*args):
    return recalibrate.write_recal_bam(*args)

@utils.map_wrap
def realign_sample(*args):
    return realign.realign_sample(*args)

@utils.map_wrap
def split_variants_by_sample(*args):
    return multi.split_variants_by_sample(*args)

@utils.map_wrap
def postprocess_variants(*args):
    return variation.postprocess_variants(*args)

@utils.map_wrap
def pipeline_summary(*args):
    return qcsummary.pipeline_summary(*args)

@utils.map_wrap
def generate_transcript_counts(*args):
    return sample.generate_transcript_counts(*args)

@utils.map_wrap
def generate_bigwig(*args):
    return sample.generate_bigwig(*args)

@utils.map_wrap
def combine_bam(*args):
    return shared.combine_bam(*args)

@utils.map_wrap
def variantcall_sample(*args):
    return genotype.variantcall_sample(*args)

@utils.map_wrap
def combine_variant_files(*args):
    return genotype.combine_variant_files(*args)

@utils.map_wrap
def detect_sv(*args):
    return variation.detect_sv(*args)

@utils.map_wrap
def combine_calls(*args):
    return ensemble.combine_calls(*args)

@utils.map_wrap
def combine_bed(*args):
    return callable.combine_bed(*args)

@utils.map_wrap
def calc_callable_loci(*args):
    return callable.calc_callable_loci(*args)
