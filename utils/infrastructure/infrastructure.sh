#!/bin/bash

# Script that sets up infrastructre for EduHub Notification Service on Azure in a 
#   given subscription (ENS_SUBSCRIPTION_ID).

# CONSTANTS
CONST_LOCATION='uksouth'
CONST_POSTGRES_V='11'
CONST_POSTGRES_SERVER='B_Gen5_1'

# Azure resource group names
ENS_RG_NAME_TEST="EduNoticeTest"
ENS_RG_NAME_PROD="EduNoticeProduction"

###################################################################################
# THE CODE BELOW SHOULD NOT BE MODIFIED
###################################################################################

ENS_RG_NAME=""

if [ -z "$1" ]; then 
    echo "Unspecified positional argument for the environment. Options: PROD, TEST"; 
    exit 0 
fi

if [[ "$1" == "TEST" ]]; then
    ENS_RG_NAME=$ENS_RG_NAME_TEST
else
    if [[ "$1" == "PROD" ]]; then
        ENS_RG_NAME=$ENS_RG_NAME_PROD
    else
        echo "Incorrect positional argument for the environment. Options: PROD, TEST"; 
        exit 0 
    fi
fi

if [ -z "$ENS_SUBSCRIPTION_ID" ]; then 
    echo "ENS_SUBSCRIPTION_ID is unset"; 
    exit 0 
fi

# Setting the default subsciption
az account set -s $ENS_SUBSCRIPTION_ID || exit 0 
echo "EduNotice BUILD INFO: default subscription set to $ENS_SUBSCRIPTION_ID"

# -----------------------------------------------------------------------------
# Resource group
# -----------------------------------------------------------------------------

# If resource group does not exist - create
if ! `az group exists -n $ENS_RG_NAME`; then

    az group create --name $ENS_RG_NAME \
        --location $CONST_LOCATION \
    || exit 0

    echo "EduNotice BUILD INFO: resource group $ENS_RG_NAME has been created."
else
    echo "EduNotice BUILD INFO: resource group $ENS_RG_NAME already exists. Skipping."
fi

###################################################################################
# Creates PostgreSQL DB
###################################################################################

# Checks for postgres databases
#   This is not a great implementation as it depends on Python to parse the json object.
#   Suggestions are welcome.

exists=`az postgres server list -g $ENS_RG_NAME`

# Checks the lenght of the query result. 2 means there were no results.
if [ ${#exists} = 2 ]; then
    az postgres server create \
        --resource-group $ENS_RG_NAME \
        --name $ENS_SQL_SERVER \
        --location $CONST_LOCATION \
        --admin-user $ENS_SQL_USERNAME \
        --admin-password $ENS_SQL_PASS \
        --sku-name $CONST_POSTGRES_SERVER \
        --version $CONST_POSTGRES_V \
        --ssl-enforcement Disabled \
        || exit 0

    echo "EduNotice BUILD INFO: PostgreSQL DB $ENS_SQL_SERVER has been created."

    # Adding rules of allowed ip addresses
    #   0.0.0.0 - Azure services
    az postgres server firewall-rule create \
        --resource-group $ENS_RG_NAME \
        --server-name $ENS_SQL_SERVER \
        -n whitelistedip \
        --start-ip-address 0.0.0.0 \
        --end-ip-address 0.0.0.0 \
        || exit 0


    echo "EduNotice BUILD INFO: PostgreSQL DB $ENS_SQL_SERVER firewall rules created."
else
    echo "EduNotice BUILD INFO: PostgreSQL DB $ENS_SQL_SERVER already exists. Skipping."
fi