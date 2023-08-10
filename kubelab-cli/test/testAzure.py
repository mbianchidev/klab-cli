from azure_nginx_test import TestAzureNginx

if __name__ == '__main__':
    test_Azure = TestAzureNginx()
    test_Azure.testInit()
    test_Azure.test_create_azure_cluster()
    test_Azure.test_use_azure_cluster()
    test_Azure.install_NGINX_deployment_Azure() 
    test_Azure.update_NGINX_deployment()
    test_Azure.switch_NGINX_deployment_Azure()
    test_Azure.test_delete_operator()
    test_Azure.test_delete_cluster()
