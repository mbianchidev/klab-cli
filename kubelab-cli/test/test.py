from aws_nginx_test import TestAWSNginx
from azure_nginx_test import TestAzureNginx

if __name__ == '__main__':
    test_instance = TestAWSNginx()
    test_instance.test_init()
    test_instance.test_create_aws_cluster()
    test_instance.test_use_aws_cluster()
    test_instance.install_nginx_deployment_aws()
    test_instance.update_nginx_deployment_aws()
    test_instance.switch_nginx_deployment_aws()
    test_instance.test_delete_operator()
    test_instance.test_destroy_aws_cluster()
    
    test_instance = TestAzureNginx()
    test_instance.test_init()
    test_instance.test_create_azure_cluster()
    test_instance.test_use_azure_cluster()
    test_instance.install_NGINX_deployment_Azure()
    test_instance.update_NGINX_deployment()
    test_instance.switch_NGINX_deployment_Azure()
    test_instance.test_delete_operator()
    test_instance.test_delete_cluster()
