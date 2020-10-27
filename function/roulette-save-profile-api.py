#!/usr/bin/env python3

import json
import logging
import boto3
from botocore.exceptions import ClientError

import traceback
import pprint
from collections import namedtuple
from pairme import PairMe, RouletteUser


## initialize logging
logger = logging.getLogger()
formatter = logging.Formatter(
    '[%(asctime)s)] %(filename)s:%(lineno)d} %(levelname)s - %(message)s')
logger.setLevel(logging.INFO)
logger.handlers[0].setFormatter(formatter)


## services
S3_CLIENT = boto3.client('s3')
S3_resource = boto3.resource('s3')
DB_CLIENT = boto3.resource('dynamodb')

table_name = 'roulette-user'

## initialize logging
logger = logging.getLogger()
formatter = logging.Formatter(
    '[%(asctime)s)] %(filename)s:%(lineno)d} %(levelname)s - %(message)s')
logger.setLevel(logging.INFO)
logger.handlers[0].setFormatter(formatter)


class User:
    pass


def handler(event, context):
    logging.info(json.dumps(event, default=str))

    if event != None:
        action = event['action']
        user = User()
        for key, value in event.items():
            setattr(user, key, value)

        user = RouletteUser(name=user.name, email=user.email, oid=user.oid, aboutYou=user.aboutyou if hasattr(user, 'aboutyou') else '',
                            careerPath=user.careerpath if hasattr(user, 'careerPath') else '', yearsExperience=user.yearofexperienceatlilly if hasattr(user, 'yearofexperienceatlilly') else '',
                            stayIn=user.stayIn if hasattr(user, 'stayIn') else '', pairedwith='')

        try:
            pairme = PairMe(user, logger)
            if action == 'create':
                status = pairme.create_profile()
                message = f'profile for {user.name} been been created successfully!'
                return {
                    'statusCode': 200,
                    'body': json.dumps(message)
                }

            elif action == 'get':
                status = pairme.get_profile()
                if not status:
                    return {
                        'statusCode': 200,
                        'body': json.dumps(f'profile for {user.name} was not found!')
                    }
                return {
                    'statusCode': 200,
                    'body': status
                }

            elif action == 'getpair':
                status = pairme.get_matched_pair()
                message = status
                return {
                    'statusCode': 200,
                    'body': json.dumps(status)
                }
        except Exception as ex:
            raise ex

        return {
            'statusCode': 200,
            'body': message
        }
