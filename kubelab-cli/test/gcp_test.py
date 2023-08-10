from gcp_nginx_test import TestGCPNginx

if __name__ == '__main__':
    test_instance = TestGCPNginx()
    test_instance.test_init()
    test_instance.test_create_gcp_cluster()
    test_instance.test_use_gcp_cluster()
    test_instance.install_nginx_deployment_gcp()
    test_instance.update_nginx_deployment_gcp()
    test_instance.switch_nginx_deployment_gcp()
    test_instance.test_delete_operator()
    test_instance.test_destroy_gcp_cluster()