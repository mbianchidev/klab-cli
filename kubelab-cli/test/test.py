from aws_nginx_test import TestAWSNginx

if __name__ == '__main__':
    test_instance = TestAWSNginx()
    # test_instance.test_init()
    # test_instance.test_create_aws_cluster()
    # test_instance.test_use_aws_cluster()
    test_instance.install_nginx_deployment_aws()
    test_instance.update_nginx_deployment_aws()
    test_instance.switch_nginx_deployment_aws()
    test_instance.test_delete_operator()
    test_instance.test_destroy_aws_cluster()