import pytest
import threading
import time
from src.mock.soap_server import start_soap_server, stop_soap_server, reset_soap_state

SOAP_HOST = "127.0.0.1"
SOAP_PORT = 8002
SOAP_WSDL_URL = f"http://{SOAP_HOST}:{SOAP_PORT}/facturation?wsdl"


@pytest.fixture(scope="session")
def soap_server():
    start_soap_server(host=SOAP_HOST, port=SOAP_PORT)
    time.sleep(1)
    yield
    stop_soap_server()


@pytest.fixture(scope="session")
def soap_wsdl_url():
    return SOAP_WSDL_URL


@pytest.fixture(autouse=True)
def reset_state():
    reset_soap_state()
    yield