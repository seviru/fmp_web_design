#!/usr/bin/env python3
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import sys
from django.core.management import call_command
sys.path.append("/home/sebas/physh_dev/src")
from src import main_class, feature_processing, utils, sphinxapi
from tree_analyzer import config
import json
from ete3 import TreeStyle
from sphinxapi import *

BASE_DATA_PATH = "/home/sebas/dummydata/data"


# Create your views here.

def index(request):
    context = "empty"
    template = loader.get_template("tree_analyzer/index.html")
    return HttpResponse(template.render({"context":context}, request))


def cluster_explorer(request):
    cluster_list = {}
    
    if request.method == "POST":
        query = dict(request.POST)["query"][0]
        client = SphinxClient()
        MAX_CLUSTERS_LIST = 1000
        client.SetLimits(0, MAX_CLUSTERS_LIST, max(MAX_CLUSTERS_LIST,1000))
        host = "localhost"
        port = 9306
        client.SetServer(host, port)
        index = "clusters_idx"
        res = client.Query(query, index)
        if not res:
            sys.stderr.write("res not found :(") 
        if client.GetLastWarning():
            sys.stderr.write('WARNING: %s\n' % client.GetLastWarning())
        if 'matches' in res:
            nmatch = 0
            for match in res["matches"]:
                cluster_list[nmatch] = match["attrs"]["clid"]
                nmatch += 1
        cluster_list = utils.sort_dict_byvalue(cluster_list)

    template = loader.get_template("tree_analyzer/cluster_explorer.html")
    return HttpResponse(template.render({"cluster_list":cluster_list}, request))


def design_tree(request, cluster_number):   
    cluster_list_file = f"{BASE_DATA_PATH}/cluster_list.txt"
    with open(cluster_list_file, "r") as cluster_list:
        for line in cluster_list:
            if cluster_number in line:
                partition = line.split("\t")[1].rstrip()

    if request.method == "GET":
        case_study = main_class.FeatureStudy(tree_path=f"{BASE_DATA_PATH}/partitions/{partition}/trees/{cluster_number}.tree",
                                             alignment_path=f"{BASE_DATA_PATH}/partitions/{partition}/alignments/{cluster_number}.fas.alg",
                                             table_path=f"{BASE_DATA_PATH}/partitions/{partition}/tables/{cluster_number}.tsv",
                                             uniprot_path=f"{BASE_DATA_PATH}/uniprot_2018_09.json",
                                             annotation_features="ALL", 
                                             min_evalue=1e-10, 
                                             node_score_algorithm="simple", 
                                             differentiate_gap_positions="Y",
                                             compute_logos="Y")
        case_study.all_features = list(case_study.all_features)
    else: # IF METHOD IS POST
        case_study = request.session["case_study"]
        update_params = dict(request.POST)
        case_study.update_features(update_params)

    case_study.design_tree()
    case_study.processed_tree = case_study.etetree_to_image()
    case_study.node_haplotype_logos = {node:logo for node, logo in case_study.node_haplotype_logos.items() if logo is not None}
    case_study.node_haplotype_logos = case_study.logo_to_image()

    request.session["case_study"] = case_study

    template = loader.get_template("tree_analyzer/design_tree.html")
    return HttpResponse(template.render({"case_study":case_study, "cluster":cluster_number, "calculus_algorithms":config.calculus_algorithms, "feature_info":config.feature_info}, request))


def select_custom_parameters(request):
    template = loader.get_template("tree_analyzer/select_custom_parameters.html")
    return HttpResponse(template.render({"calculus_algorithms":config.calculus_algorithms}, request))


def design_custom_tree(request):
    form_params = dict(request.POST)
    form_files = dict(request.FILES)
    calculus_algorithm = form_params["calculus_algorithm"][0]
    differentiate_gaps = form_params["differentiate_gaps"][0]
    annotation_positions = sorted([int(position) for position in list(set(form_params["annotation_positions"][0].split(",")))])
    tree_file = form_files["tree"][0]
    alignment_file = form_files["alignment"][0]
    
    
    custom_case_study = main_class.FeatureStudy(tree_path=tree_file,
                                                alignment_path=alignment_file,
                                                node_score_algorithm=calculus_algorithm, 
                                                differentiate_gap_positions=differentiate_gaps,
                                                position_matrix=annotation_positions,
                                                compute_logos="Y")
                                         
    
    custom_case_study.tree_in = utils.bytefile_to_stringfile(tree_file)
    custom_case_study.align_in = utils.bytefile_to_stringfile(alignment_file)
    custom_case_study.design_tree()
    custom_case_study.processed_tree = custom_case_study.etetree_to_image()
    custom_case_study.node_haplotype_logos = {node:logo for node, logo in custom_case_study.node_haplotype_logos.items() if logo is not None}
    custom_case_study.node_haplotype_logos = custom_case_study.logo_to_image()

    request.session["custom_case_study"] = custom_case_study

    template = loader.get_template("tree_analyzer/design_custom_tree.html")
    return HttpResponse(template.render({"custom_case_study":custom_case_study, "calculus_algorithms":config.calculus_algorithms}, request))


def update_custom_tree(request):
    custom_case_study = request.session["custom_case_study"]
    update_params = dict(request.POST)
    custom_case_study.update_features(update_params)
    custom_case_study.design_tree()
    custom_case_study.processed_tree = custom_case_study.etetree_to_image()
    custom_case_study.node_haplotype_logos = {node:logo for node, logo in custom_case_study.node_haplotype_logos.items() if logo is not None}
    custom_case_study.node_haplotype_logos = custom_case_study.logo_to_image()
    request.session["custom_case_study"] = custom_case_study

    template = loader.get_template("tree_analyzer/design_custom_tree.html")
    return HttpResponse(template.render({"custom_case_study":custom_case_study, "calculus_algorithms":config.calculus_algorithms}, request))