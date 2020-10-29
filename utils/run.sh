#!/bin/bash

# secrets
source .secrets/funcapp.sh

# EduCrawler
ec handout list

# EduNotice
en "ec_output.csv"

rm ec_output.csv 