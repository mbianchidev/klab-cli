from azure_nginx_test import TestAzureNginx

if __name__ == '__main__':
    test_instance = TestAzureNginx()
    test_instance.test_azure_init()
    test_instance.test_azure_create_cluster()
    test_instance.test_azure_use_cluster()
    test_instance.test_azure_install_nginx_deployment()
    test_instance.test_azure_update_nginx_deployment()
    test_instance.test_azure_switch_nginx_deployment()
    test_instance.test_azure_delete_operator()
    test_instance.test_azure_destroy_cluster()
