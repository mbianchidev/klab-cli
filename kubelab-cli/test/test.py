from gcp_nginx_test import TestGCPNginx

if __name__ == '__main__':
    test_instance = TestGCPNginx()
    test_instance.test_init()
    test_instance.test_create_gcp_cluster()
