from aws_nginx_test import TestAWSNginx


if __name__ == '__main__':
    test_instance = TestAWSNginx()
    test_instance.test_init()
    test_instance.test_create_aws_cluster()
