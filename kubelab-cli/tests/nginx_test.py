import requests
import pytest

nginx_urls = {
    'deployment_aws': 'http://a14a4e2ed481642e185a141a30a66d09-1266868104.eu-west-1.elb.amazonaws.com/',
    'deployment_azure': 'http://20.242.223.73',
    'deployment_gcp': 'http://34.134.94.149',
    'operator_aws': 'http://<AWS_LOAD_BALANCER_DNS>',
    'operator_azure': 'http://<AZURE_LOAD_BALANCER_DNS>',
    'operator_gcp': 'http://<GCP_LOAD_BALANCER_DNS>'
}

@pytest.mark.parametrize('nginx_type', ['deployment_aws', 'deployment_azure', 'deployment_gcp',
                                        'operator_aws', 'operator_azure', 'operator_gcp'])
def test_nginx_page(nginx_type):
    url = nginx_urls.get(nginx_type)
    response = requests.get(url)
    assert response.status_code == 200