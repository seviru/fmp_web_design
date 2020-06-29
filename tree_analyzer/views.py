from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import sys
from django.core.management import call_command
sys.path.append("/home/biopeqqer/Desktop/fmp_core_functionality/scripts")
from src import main_class
from tree_analyzer import config

BASE_DATA_PATH = "/home/biopeqqer/Desktop/fmp_web_design/tree_analyzer/data"


# Create your views here.

def index(request):
    cluster_list_file = f"{BASE_DATA_PATH}/cluster_list.txt"
    cluster_dict = {}
    with open(cluster_list_file, "r") as cluster_list:
        for line in cluster_list:
            (cluster, partition) = line.split("\t")
            cluster_dict[cluster] = partition.rstrip()
    template = loader.get_template("tree_analyzer/cluster_list.html")
    return HttpResponse(template.render({"cluster_list":cluster_dict}, request))

def design_tree(request, cluster_number, features="ALL", min_evalue=1e-100, calc_algorithm="simple", differentiate_gaps="Y"):
    cluster_list_file = f"{BASE_DATA_PATH}/cluster_list.txt"
    with open(cluster_list_file, "r") as cluster_list:
        for line in cluster_list:
            if cluster_number in line:
                partition = line.split("\t")[1].rstrip()
    print(features, min_evalue, calc_algorithm, differentiate_gaps)
    case_study = main_class.FeatureStudy(f"{BASE_DATA_PATH}/partitions/{partition}/trees/{cluster_number}.tree",
                                   f"{BASE_DATA_PATH}/partitions/{partition}/alignments/{cluster_number}.fas.alg",
                                   f"{BASE_DATA_PATH}/partitions/{partition}/tables/{cluster_number}.tsv",
                                   f"{BASE_DATA_PATH}/uniprot_2018_09.json",
                                   features, min_evalue, calc_algorithm, differentiate_gaps)
                             
    template = loader.get_template("tree_analyzer/design_tree.html")
    case_study.design_tree()
    return HttpResponse(template.render({"case_study":case_study, "calculus_algorithms":config.calculus_algorithms}, request))