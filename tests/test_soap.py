import pytest
from pytest_bdd import scenario

@pytest.mark.usefixtures("soap_server")
@scenario(
    "../features/soap/facturation_soap.feature",
    "Soumission d'une facture B2B valide via SOAP"
)
def test_soumission_valide():
    pass


@pytest.mark.usefixtures("soap_server")
@scenario(
    "../features/soap/facturation_soap.feature",
    "Rejet SOAP d'une facture avec SIREN invalide"
)
def test_rejet_siren_invalide():
    pass


@pytest.mark.usefixtures("soap_server")
@scenario(
    "../features/soap/facturation_soap.feature",
    "Rejet SOAP d'une facture avec TVA incohérente"
)
def test_rejet_tva_incoherente():
    pass


@pytest.mark.usefixtures("soap_server")
@scenario(
    "../features/soap/facturation_soap.feature",
    "Consultation du statut d'une facture existante"
)
def test_consultation_statut():
    pass


@pytest.mark.usefixtures("soap_server")
@scenario(
    "../features/soap/facturation_soap.feature",
    "Consultation d'une facture SOAP introuvable"
)
def test_consultation_introuvable():
    pass


from src.steps.soap_steps import *