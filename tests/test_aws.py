from aws_nginx_test import TestAWSNginx

if __name__ == '__main__':
    test_instance = TestAWSNginx()
    test_instance.test_aws_init()
    test_instance.test_aws_create_cluster()
    test_instance.test_aws_use_cluster()
    test_instance.test_aws_install_nginx_deployment()
    test_instance.test_aws_update_nginx_deployment()
    test_instance.test_aws_switch_nginx_deployment()
    test_instance.test_aws_delete_deployment()
    test_instance.test_aws_delete_operator()
    test_instance.test_aws_destroy_cluster()