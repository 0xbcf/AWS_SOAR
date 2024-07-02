import unittest
from libraries.custom.python import custom_aws


class TestAWSOperations(unittest.TestCase):


    def test_get_aws_secret(self):
        """ Confirm that the library can get credentials from AWS """
        cred = custom_aws.get_aws_secret("slackbot", "test")
        self.assertEqual(list(cred.keys()), ['bot', 'verification', 'socket'])

    def test_a_put_dynamodb_functions(self):
        """ Tests that items can be added"""
        response = custom_aws.put_dynamodb_item("codebuild_test", {"test": "example", "data": "other data"})
        self.assertEqual(response.get('ResponseMetadata', {}).get('HTTPStatusCode', "NA"), 200)


    def test_b_get_dynamodb_functions(self):
        """ Tests that items can be retrieved"""
        response = custom_aws.get_dynamodb_item("codebuild_test", {"test": "example"})
        self.assertEqual(response.get('Item', {}).get('data', "NA"), "other data")


    def disabled_test_c_query_dynamodb_functions(self):
        response = custom_aws.put_dynamodb_item("codebuild_test", {"test": "example", "data": "more data"})
        response = custom_aws.query_dynamodb_item("codebuild_test", "test", "example")
        self.assertTrue(response)

    def test_d_delete_dynamodb_functions(self):
        """ Tests that items are deleted"""
        response = custom_aws.delete_dynamodb_item("codebuild_test", {"test": "example"})
        self.assertEqual(response.get('ResponseMetadata', {}).get('HTTPStatusCode', "NA"), 200)
