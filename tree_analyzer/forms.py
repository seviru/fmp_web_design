#!/usr/bin/env python3
from django import forms
from .models import Post

class ParameterForms(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("calc_alg", "diff_gaps", "features", "evalue")