from aws_nginx_test import TestAWSNginx

if __name__ == '__main__':
    test_instance = TestAWSNginx()
    test_instance.test_init()
    test_instance.test_create_aws_cluster()
    # test_instance.test_create_azure_cluster()
    # test_instance.test_create_gcp_cluster()
    # USE + ADD 
    # test_instance.test_nginx_deployment()

    # test_instance.test_catalog_yaml()
    # test_instance.test_update_nginx_version()
    # test_instance.test_switch_to_operator()
    # test_instance.test_remove_operator_installation()
    # test_instance.test_destroy_cluster()


