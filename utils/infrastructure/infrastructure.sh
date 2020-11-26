#!/bin/bash

# Script that sets up infrastructre for EduHub Notification Service on Azure in a 
#   given subscription (ENS_SUBSCRIPTION_ID).

# CONSTANTS
CONST_LOCATION='uksouth'
CONST_POSTGRES_V='11'
CONST_POSTGRES_SERVER='B_Gen5_1'

###################################################################################
# THE CODE BELOW SHOULD NOT BE MODIFIED
###################################################################################

# Azure resource group names
ENS_RG_NAME=""
ENS_RG_NAME_TEST="EduNoticeTest"
ENS_RG_NAME_PROD="EduNoticeProd"
ENS_STORAGE_ACCOUNT="edunoticestorage"

CONST_FUNCAPP_PLAN=$CROP_RG_NAME'funcappbasicplan'

if [ -z "$1" ]; then 
    echo "Unspecified positional argument for the environment. Options: PROD, TEST"; 
    exit 0 
fi

if [[ "$1" == "TEST" ]]; then
    ENS_RG_NAME=$ENS_RG_NAME_TEST
    ENS_STORAGE_ACCOUNT=$ENS_STORAGE_ACCOUNT"test"
else
    if [[ "$1" == "PROD" ]]; then
        ENS_RG_NAME=$ENS_RG_NAME_PROD
        ENS_STORAGE_ACCOUNT=$ENS_STORAGE_ACCOUNT"prod"
    else
        echo "Incorrect positional argument for the environment. Options: PROD, TEST"; 
        exit 0 
    fi
fi

if [ -z "$ENS_SUBSCRIPTION_ID" ]; then 
    echo "ENS_SUBSCRIPTION_ID is unset"; 
    exit 0 
fi

if [ -z "$ENS_SQL_WHITELISTED_IP" ]; then 
    echo "ENS_SQL_WHITELISTED_IP is unset"; 
    exit 0 
fi

# Setting the default subsciption
az account set -s $ENS_SUBSCRIPTION_ID || exit 0 
echo "EduNotice BUILD INFO: default subscription set to $ENS_SUBSCRIPTION_ID"

###################################################################################
# Resource group
###################################################################################

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
# Creates STORAGE ACCOUNT (required for the FunctionApp)
###################################################################################

# Checks if storage account does not exist
#   This is not a great implementation as it depends on Python to parse the json object.
#   Changes are wellcome.
available=`az storage account check-name --name $ENS_STORAGE_ACCOUNT | python -c 'import json,sys;obj=json.load(sys.stdin);print (obj["nameAvailable"])'`

if [ $available = "True" ]; then

    az storage account create --name $ENS_STORAGE_ACCOUNT \
        --location $CONST_LOCATION \
        --resource-group $ENS_RG_NAME \
        --sku Standard_LRS

    echo "EduNotice BUILD INFO: storage account $ENS_STORAGE_ACCOUNT has been created."
else
    echo "EduNotice BUILD INFO: storage account $ENS_STORAGE_ACCOUNT already exists. Skipping."
fi

# Getting the first storage account key
ACCESS_KEY=$(az storage account keys list --account-name $ENS_STORAGE_ACCOUNT --resource-group $ENS_RG_NAME --output tsv |head -1 | awk '{print $3}')
# Creating a connection string
CONNECTION_STRING="DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName=${ENS_STORAGE_ACCOUNT};AccountKey=${ACCESS_KEY}"

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
        -n azureservices \
        --start-ip-address 0.0.0.0 \
        --end-ip-address 0.0.0.0 \
        || exit 0

    echo "EduNotice BUILD INFO: PostgreSQL DB $ENS_SQL_SERVER firewall rule created: 0.0.0.0"

    az postgres server firewall-rule create \
        --resource-group $ENS_RG_NAME \
        --server-name $ENS_SQL_SERVER \
        -n whitelistedip \
        --start-ip-address $ENS_SQL_WHITELISTED_IP \
        --end-ip-address $ENS_SQL_WHITELISTED_IP \
        || exit 0

    echo "EduNotice BUILD INFO: PostgreSQL DB $ENS_SQL_SERVER firewall rule created: $ENS_SQL_WHITELISTED_IP"

    # Establishing database
    python -c 'from edunotice import db; db.create_db();' || exit 0

    echo "EduNotice BUILD INFO: PostgreSQL DB $ENS_SQL_SERVER database initialised."
else
    echo "EduNotice BUILD INFO: PostgreSQL DB $ENS_SQL_SERVER already exists. Skipping."
fi

###################################################################################
# (Re-)Creates Function App
###################################################################################

function_name=$ENS_RG_NAME"functionapp"
cwd=`pwd`

echo "EduNotice BUILD INFO: Function APP: cd ../../__app__"
cd ../../__app__

echo "EduNotice BUILD INFO: Function APP: az functionapp delete"
az functionapp delete \
    --name $function_name \
    --resource-group $ENS_RG_NAME \
    --subscription $ENS_SUBSCRIPTION_ID

echo "EduNotice BUILD INFO: Function APP: functionapp plan delete"
az functionapp plan delete \
    --resource-group $ENS_RG_NAME \
    --name $CONST_FUNCAPP_PLAN \
    --yes

echo "EduNotice BUILD INFO: Function APP: functionapp plan create"
az functionapp plan create \
    --resource-group $ENS_RG_NAME \
    --name $CONST_FUNCAPP_PLAN \
    --location $CONST_LOCATION \
    --number-of-workers 1 \
    --sku B1 \
    --is-linux

echo "EduNotice BUILD INFO: Function APP: az functionapp create"
az functionapp create \
    --subscription $ENS_SUBSCRIPTION_ID \
    --resource-group $ENS_RG_NAME \
    --storage-account $ENS_STORAGE_ACCOUNT \
    --name $function_name \
    --functions-version 3 \
    --plan $CONST_FUNCAPP_PLAN \
    --deployment-container-image-name $ENS_DOCKER_IMAGE \
    --docker-registry-server-user $ENS_DOCKER_USER \
    --docker-registry-server-password $ENS_DOCKER_PASS

echo "EduNotice BUILD INFO: Function APP: $function_name created."

echo "EduNotice BUILD INFO: Function APP: sleeping for 30 seconds"
sleep 30

echo "EduNotice BUILD INFO: Function APP: az functionapp config appsettings set"

az functionapp config appsettings set \
    --name $function_name \
    --resource-group $ENS_RG_NAME \
    --settings \
    "AzureWebJobsStorage=$CONNECTION_STRING" \
    "EC_EMAIL=$EC_EMAIL" \
    "EC_PASSWORD=$EC_PASSWORD" \
    "EC_MFA=$EC_MFA" \
    "ENS_SQL_HOST=$ENS_SQL_HOST" \
    "ENS_SQL_USER=$ENS_SQL_USER" \
    "ENS_SQL_PASS=$ENS_SQL_PASS" \
    "ENS_SQL_DBNAME=$ENS_SQL_DBNAME" \
    "ENS_SQL_PORT=$ENS_SQL_PORT" \
    "ENS_EMAIL_API=$ENS_EMAIL_API" \
    "ENS_FROM_EMAIL=$ENS_FROM_EMAIL" \
    "ENS_SUMMARY_RECIPIENTS=$ENS_SUMMARY_RECIPIENTS" \
    "ENS_EMAIL_EXCL=$ENS_EMAIL_EXCL" \
    "ENS_TEST_EMAIL_API=$ENS_TEST_EMAIL_API" \
    "ENS_TEST_EMAIL_API=$ENS_TEST_EMAIL_API" \
    "ENS_TEST_FROM_EMAIL=$ENS_TEST_FROM_EMAIL" \
    "ENS_TEST_TO_EMAIL=$ENS_TEST_TO_EMAIL" \
    > /dev/null

echo "EduNotice BUILD INFO: Function APP: $function_name configuration updated"

python $cwd/create_json.py $CONNECTION_STRING local.settings.json
echo "EduNotice BUILD INFO: Function APP: local.settings.json file updated."

echo "EduNotice BUILD INFO: Function APP: func azure functionapp publish"
func azure functionapp publish $function_name --build-native-deps --build remote

echo "EduNotice BUILD INFO: Function APP "$function" uploaded"

echo "EduNotice BUILD INFO: Function APP cd: "$cwd
cd $cwd

###################################################################################