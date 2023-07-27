from azure_nginx_test import TestAzureNginx

if __name__ == '__main__':
    test_Azure = TestAzureNginx()
    # test_Azure.testInit()
    # test_Azure.test_create_azure_cluster()
    test_Azure.test_use_azure_cluster()
