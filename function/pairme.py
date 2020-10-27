#!/usr/bin/env python3

import boto3

from botocore.exceptions import ClientError

import json
import time
import datetime
import os
import logging
from collections import namedtuple
import random
from boto3.dynamodb.conditions import Key, Attr
import uuid

RouletteUser = namedtuple('User', 'name email oid aboutYou careerPath yearsExperience stayIn pairedwith')


class PairMe(object):
    TABLE_NAME = 'roulette-user'
    
    def __init__(self, user, logger):
        self.user = user
        self.logger = logger 
        
        
    def create_profile(self):
        # initialie AWS
        db_resource= boto3.resource('dynamodb')
        db_client = boto3.client('dynamodb')
        
        table = db_resource.Table(self.TABLE_NAME)
        
        # scan for the user
        response = table.scan(FilterExpression=Attr('name').eq(self.user.name))
        
        try:
            if len(response['Items'])==0:
                # add user - oid aboutYou currentRole yearsExperience
                table.put_item(Item = {
                    'unique_id': self.make_id(),
                    'name':self.user.name,
                    'email':self.user.email,
                    'oid' : self.user.oid,
                    'aboutYou': self.user.aboutYou,
                    'careerPath': self.user.careerPath,
                    'yearsExperience': self.user.yearsExperience,
                    'stayIn':self.user.stayIn,
                    'pairedwith':''
                })
                
                self.logger.info(f"Inserted the user:{self.user.name}")
            else:
                item = response['Items'][0]
                response = table.update_item(
                Key={
                    'unique_id': str(item['unique_id'])
                },
                UpdateExpression="set  aboutYou =:aboutYou, currentPath= :currentPath, yearsExperience=:yearsExperience",
                ExpressionAttributeValues={
                    ':aboutYou': self.user.aboutYou,
                    ':currentPath': self.user.currentPath,
                    ':yearsExperience': self.user.yearsExperience
                })
                
                self.logger.info(f"Updated the user profile:{self.user.name}")
                
        except ClientError as error:
            # Put your error handling logic here
            raise error
        
        return True
        
        
    def set_user_preference(self, preference):
        # initialie AWS
        db_resource= boto3.resource('dynamodb')
        db_client = boto3.client('dynamodb')
        
        table = db_resource.Table(self.TABLE_NAME)
        
        # scan for the user
        response = table.scan(FilterExpression=Attr('name').eq(self.user.name))
        if len(response['Items']) == 0:
            ## create profile - 
            table.put_item({
                'unique_id': self.make_id(),
                'name':self.user.name,
                'email':self.user.email,
                'stayIn': self.user.stayIn
            })
        else:
            # update profile with preference
            item = response['Items'][0]
            
            if self.user.stayIn.lower() == 'yes':
                response = table.update_item(
                Key={
                    'unique_id': str(item['unique_id'])
                },
                UpdateExpression="set  stayIn=:stayIn",
                ExpressionAttributeValues={
                    ':stayIn': self.user.stayIn
                })
            else:
                response = table.update_item(
                Key={
                    'unique_id': str(item['unique_id'])
                },
                UpdateExpression="set  stayIn=:stayIn, pairedwith=:pairedwith",
                ExpressionAttributeValues={
                    ':stayIn': self.user.stayIn,
                    ':pairedwith' : ''
                })
                
        
    def get_matched_pair(self):
        # initialie AWS
        dynamodb_resource= boto3.resource('dynamodb')
        dynamodb_client = boto3.client('dynamodb')
        
        table = dynamodb_resource.Table(self.TABLE_NAME)
        
        # scan for the user
        response = table.scan(FilterExpression=Attr('name').eq(self.user.name))
        
        
        ## if user has matched pair - return - otherwise - pair user 
        if len(response['Items']) != 0:
            item = response['Items'][0]
            
            if item['pairedwith']!='':
                return item['pairedwith']
                
            else:
                
                ## list of user from table - randomly pick an assignment
                print(self.user.name)
                response_available = table.scan(FilterExpression=Attr('stayIn').eq("yes") & Attr('pairedwith').eq(''))

                print('available',response_available['Items'])
                if len(response_available['Items'])==0:
                    return ''
                
                random_user = random.choice(list(filter(lambda x: x['name']!=self.user.name,response_available['Items'])))
                
                ## save random user -
                selected_user = random_user['name']
                
                ## save both preferences
                item = response['Items'][0]
                response_update = table.update_item(
                Key={
                    'unique_id': str(item['unique_id'])
                },
                UpdateExpression="set  pairedwith=:pairedwith",
                ExpressionAttributeValues={
                    ':pairedwith' : selected_user
                })
                
                
                # updated paireduser
                response_paired = table.scan(FilterExpression=Attr('name').eq(selected_user))
                
                if len(response_paired['Items'])>0:
                    paired = response_paired['Items'][0]
                    response_paired_update = table.update_item(Key={'unique_id': str(paired['unique_id'])},UpdateExpression="set  pairedwith=:pairedwith",ExpressionAttributeValues={':pairedwith' : item['name']})
                    
                    
            return  selected_user
            
        return False
    
    def get_profile(self):
        # initialie AWS
        dynamodb_resource= boto3.resource('dynamodb')
        dynamodb_client = boto3.client('dynamodb')
        
        table = dynamodb_resource.Table(self.TABLE_NAME)
        
        # scan for the user
        
        response = table.scan(FilterExpression=Attr('name').eq(self.user.name))
        
        ## if user has matched pair - return - otherwise - pair user 
        if len(response['Items']) > 0:
            item = response['Items'][0]
            # name email oid aboutYou careerPath yearsExperience stayIn pairedwith
            return {'name':item['name'], 'email':item['email'], 'oid': item['oid'], 'aboutYou': item['aboutYou'], 'careerPath': item['careerPath'], 'yearsExperience': item['yearsExperience'], 'stayIn':item['stayIn'], 'pairedwith': item['pairedwith']}
                
        return False
        
    
    ## Helpers
    def make_id(self):
        id = uuid.uuid4()
        return str(id)