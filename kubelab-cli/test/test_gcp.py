from gcp_nginx_test import TestGCPNginx

if __name__ == '__main__':
    test_instance = TestGCPNginx()
    test_instance.test_gcp_init()
    test_instance.test_gcp_create_cluster()
    test_instance.test_gcp_use_cluster()
    test_instance.test_gcp_install_nginx_deployment()
    test_instance.test_gcp_update_nginx_deployment()
    test_instance.test_gcp_switch_nginx_deployment()
    test_instance.test_gcp_delete_operator()
    test_instance.test_gcp_destroy_cluster()
