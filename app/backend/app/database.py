import boto3
from app.config import settings
from typing import Optional
from datetime import datetime
import uuid


class DynamoDBService:
    """
    DynamoDB Service for managing advertisements.

    Table Schema Requirements:
    - Primary Table: advertisements
      - Partition Key: user_id (string)
      - Sort Key: run_id (string)

    - Global Secondary Index: user_id-status-index
      - Partition Key: user_id (same as main table)
      - Sort Key: status (string)
      - Projection: ALL

    This GSI enables efficient queries for "all ads of user X with status Y".
    """
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.users_table = self.dynamodb.Table(settings.USERS_TABLE)
        self.advertisements_table = self.dynamodb.Table(settings.ADVERTISEMENTS_TABLE)

    # User operations
    def create_user(self, user_data: dict) -> dict:
        # Email is now the partition key, no need for separate user_id
        now = datetime.utcnow()

        user_item = {
            'email': user_data['email'],  # Partition key
            'full_name': user_data['full_name'],
            'role': user_data.get('role', 'creator'),
            'password_hash': user_data['password_hash'],
            'created_at': now.isoformat(),
            'updated_at': now.isoformat()
        }

        self.users_table.put_item(Item=user_item)
        return user_item

    def get_user_by_email(self, email: str) -> Optional[dict]:
        # Direct partition key lookup - much more efficient!
        response = self.users_table.get_item(Key={'email': email})
        return response.get('Item')

    # Advertisement operations
    def create_advertisement(self, user_id: str, ad_data: dict) -> dict:
        run_id = ad_data.get('run_id') or str(uuid.uuid4())
        now = datetime.utcnow()

        ad_item = {
            'user_id': user_id,  # Partition key
            'run_id': run_id,  # Sort key and primary identifier
            'name': ad_data['name'],
            'desc': ad_data['desc'],
            'status': ad_data.get('status', 'draft'),
            'final_video_uri': ad_data.get('final_video_uri'),
            'created_at': now.isoformat(),
            'updated_at': now.isoformat()
        }

        self.advertisements_table.put_item(Item=ad_item)
        return ad_item

    def get_advertisement(self, user_id: str, run_id: str) -> Optional[dict]:
        response = self.advertisements_table.get_item(
            Key={'user_id': user_id, 'run_id': run_id}
        )
        return response.get('Item')

    def get_user_advertisements(self, user_id: str) -> list:
        response = self.advertisements_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id)
        )
        return response.get('Items', [])

    def get_user_advertisements_by_status(self, user_id: str, status: str) -> list:
        """Query advertisements by user and status using GSI"""
        response = self.advertisements_table.query(
            IndexName='user_id-status-index',  # GSI name
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id) & 
                                   boto3.dynamodb.conditions.Key('status').eq(status)
        )
        return response.get('Items', [])

    def update_advertisement(self, user_id: str, run_id: str, updates: dict) -> bool:
        update_expression = "SET "
        expression_attribute_values = {}
        expression_attribute_names = {}

        for key, value in updates.items():
            if key == 'updated_at':
                value = datetime.utcnow().isoformat()
            update_expression += f"#{key} = :{key}, "
            expression_attribute_values[f":{key}"] = value
            expression_attribute_names[f"#{key}"] = key

        update_expression = update_expression.rstrip(", ")

        try:
            self.advertisements_table.update_item(
                Key={'user_id': user_id, 'run_id': run_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ExpressionAttributeNames=expression_attribute_names
            )
            return True
        except Exception:
            return False


# Global instance
dynamodb_service = DynamoDBService()
