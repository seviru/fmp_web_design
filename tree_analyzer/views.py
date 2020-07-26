#!/usr/bin/env python3
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import sys
from django.core.management import call_command
sys.path.append("/home/biopeqqer/Desktop/fmp_core_functionality/scripts")
from src import main_class, feature_processing
from tree_analyzer import config
import json
from ete3 import TreeStyle

BASE_DATA_PATH = "/home/biopeqqer/Desktop/fmp_web_design/tree_analyzer/data"


# Create your views here.

def index(request):
    context = "empty"
    template = loader.get_template("tree_analyzer/index.html")
    return HttpResponse(template.render({"context":context}, request))

def cluster_explorer(request):
    cluster_list_file = f"{BASE_DATA_PATH}/cluster_list.txt"
    cluster_dict = {}
    with open(cluster_list_file, "r") as cluster_list:
        for line in cluster_list:
            (cluster, partition) = line.split("\t")
            cluster_dict[cluster] = partition.rstrip()
    template = loader.get_template("tree_analyzer/cluster_explorer.html")
    return HttpResponse(template.render({"cluster_list":cluster_dict}, request))

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
                                    annotation_features="ALL", min_evalue=1e-10, 
                                    node_score_algorithm="simple", differentiate_gap_positions="Y")
        case_study.all_features = list(case_study.all_features)

        request.session["case_study"] = case_study
    else: # IF METHOD IS POST
        case_study = request.session["case_study"]
        form_params = dict(request.POST)
        if form_params["calc_alg"][0] is not "": # IF PARAMETER HAS BEEN MODIFIED
            case_study.calc_alg = form_params["calc_alg"][0]
        if "features" in form_params:
            case_study.study_features = set(form_params["features"])
        if form_params["evalue"][0] is not "":
            case_study.min_eval = float(form_params["evalue"][0])
        if (config.calculus_algorithms[case_study.calc_alg]["differentiate_gaps"]) == "N": # TO ENSURE THEY DONT CHANGE GAP PARAMETER IN A NOT ALLOWED ALGOORITHM
            case_study.differentiate_gaps = "N"
        else:
            if "diff_gaps" in form_params and form_params["diff_gaps"][0] is not "":
                case_study.differentiate_gaps = form_params["diff_gaps"][0]
        request.session["case_study"] = case_study

    case_study.design_tree()
    ts = TreeStyle()
    ts.layout_fn = lambda x: True
    base64_img, img_map = case_study.processed_tree.render("%%return.PNG", 
                                                            tree_style=ts,
                                                            h=2000, w=800)
    case_study.processed_tree = base64_img.data().decode("utf-8")

    template = loader.get_template("tree_analyzer/design_tree.html")
    return HttpResponse(template.render({"case_study":case_study, "cluster":cluster_number, "calculus_algorithms":config.calculus_algorithms, "feature_info":config.feature_info}, request))

def design_custom_tree(request):
    if request.method == "GET":
        pass
        # Cargar la pagina para que salgan las pijdadas de los archivos:
    else: # SI EL METODO ES POST PORQUE YA SUBIO LOS ARCHIVOS
        form_params = dict(request.POST)
        print(form_params)
        case_study = main_class.FeatureStudy(tree_path=form_params["tree"][0],
                                alignment_path=form_params["alignment"][0],
                                node_score_algorithm=form_params["calc_alg"][0], differentiate_gap_positions=form_params["diff_gaps"][0],
                                position_matrix=[177,180,185])

        # case_study = main_class.FeatureStudy(tree_path=f"{BASE_DATA_PATH}/partitions/{partition}/trees/{cluster_number}.tree",
        #                         alignment_path=f"{BASE_DATA_PATH}/partitions/{partition}/alignments/{cluster_number}.fas.alg",
        #                         node_score_algorithm="simple", differentiate_gap_positions="Y",
        #                         position_matrix=[177,180,185])
        with open(case_study.tree_in, "r") as tree:
            for line in tree:
                print(line)
        print(case_study.tree_in)

    context = "potato"
    template = loader.get_template("tree_analyzer/design_custom_tree.html")
    return HttpResponse(template.render({"calculus_algorithms":config.calculus_algorithms}, request))