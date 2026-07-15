"""
Step definitions pytest-bdd — Webservice SOAP legacy de facturation RFE
"""
import pytest
from pytest_bdd import given, when, then, parsers
from src.support.soap_client import SoapFacturationClient


# ── Background ─────────────────────────────────────────────────────────────

@given("le webservice SOAP de facturation est disponible", target_fixture="context")
def soap_available(soap_server, soap_wsdl_url):
    client = SoapFacturationClient(wsdl_url=soap_wsdl_url)
    return {"client": client, "response": None}


# ── When ───────────────────────────────────────────────────────────────────

@when(parsers.re(
    r"je soumets une facture SOAP '(?P<numero>[^']+)' avec SIREN '(?P<siren>[^']+)' "
    r"destinataire '(?P<destinataire>[^']+)' montant (?P<montant>[0-9.]+) "
    r"TVA (?P<tva>[0-9.]+) TTC (?P<ttc>[0-9.]+)"
))
def submit_soap_invoice(numero, siren, destinataire, montant, tva, ttc, context):
    response = context["client"].soumettre_facture(
        numero_facture=numero,
        siren_emetteur=siren,
        siren_destinataire=destinataire,
        date_emission="2024-06-01",
        montant_ht=float(montant),
        taux_tva=float(tva),
        montant_ttc=float(ttc),
        devise="EUR"
    )
    context["response"] = response


@when(parsers.parse("je consulte le statut SOAP de la facture '{id_facture}'"))
def consult_soap_status(id_facture, context):
    response = context["client"].consulter_statut(id_facture)
    context["response"] = response


# ── Given ──────────────────────────────────────────────────────────────────

@given(parsers.parse("une facture SOAP '{numero}' a été soumise avec succès"))
def facture_soap_submitted(numero, context):
    response = context["client"].soumettre_facture(
        numero_facture=numero,
        siren_emetteur="123456789",
        siren_destinataire="987654321",
        date_emission="2024-06-01",
        montant_ht=1000.00,
        taux_tva=20.0,
        montant_ttc=1200.00,
        devise="EUR"
    )
    assert response["success"], f"Prérequis échoué : {response['fault']}"
    context["last_id"] = response["idFacture"]


# ── Then ───────────────────────────────────────────────────────────────────

@then("la réponse SOAP est un succès")
def soap_response_success(context):
    response = context["response"]
    assert response is not None, "Aucune réponse reçue"
    assert response["success"], \
        f"Réponse SOAP en échec — Fault : {response.get('fault')} — {response.get('message')}"


@then("la réponse SOAP est un échec")
def soap_response_failure(context):
    response = context["response"]
    assert response is not None, "Aucune réponse reçue"
    assert not response["success"], \
        f"Réponse SOAP attendue en échec mais succès reçu"


@then("l'identifiant de facture SOAP est renseigné")
def soap_id_present(context):
    response = context["response"]
    assert response.get("idFacture"), "Identifiant de facture absent"
    print(f"\n  [SOAP] ID Facture : {response['idFacture']}")


@then(parsers.parse('le statut SOAP retourné est "{statut}"'))
def soap_status_check(statut, context):
    response = context["response"]
    assert response.get("statut") == statut, \
        f"Statut attendu {statut}, reçu {response.get('statut')}"


@then(parsers.parse('le code Fault SOAP est "{fault_code}"'))
def soap_fault_check(fault_code, context):
    response = context["response"]
    assert response.get("fault") == fault_code, \
        f"Fault attendu {fault_code}, reçu {response.get('fault')}"