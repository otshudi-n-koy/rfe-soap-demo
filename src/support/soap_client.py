"""
Client SOAP — Webservice legacy de facturation RFE
Utilise zeep pour consommer le WSDL et appeler les opérations SOAP
"""
from zeep import Client
from zeep.exceptions import Fault
from zeep.transports import Transport
from requests import Session
import os


class SoapFacturationClient:
    def __init__(self, wsdl_url: str = None):
        self.wsdl_url = wsdl_url or os.getenv(
            "SOAP_WSDL_URL",
            "http://127.0.0.1:8002/facturation?wsdl"
        )
        session = Session()
        transport = Transport(session=session, timeout=10)
        self.client = Client(wsdl=self.wsdl_url, transport=transport)
        print(f"  [SOAP] Client connecté sur {self.wsdl_url}")

    def soumettre_facture(
        self,
        numero_facture: str,
        siren_emetteur: str,
        siren_destinataire: str,
        date_emission: str,
        montant_ht: float,
        taux_tva: float,
        montant_ttc: float,
        devise: str = "EUR"
    ) -> dict:
        """Appelle l'opération SoumettreFacture"""
        try:
            response = self.client.service.SoumettreFacture(
                numeroFacture=numero_facture,
                sirenEmetteur=siren_emetteur,
                sirenDestinataire=siren_destinataire,
                dateEmission=date_emission,
                montantHT=montant_ht,
                tauxTVA=taux_tva,
                montantTTC=montant_ttc,
                devise=devise
            )
            return {
                "success": True,
                "idFacture": response.idFacture,
                "statut": response.statut,
                "message": response.message,
                "dateReception": response.dateReception,
                "fault": None
            }
        except Fault as f:
            print(f"  [SOAP] Fault reçu : {f.code} — {f.message}")
            return {
                "success": False,
                "idFacture": None,
                "statut": None,
                "message": f.message,
                "fault": f.code
            }

    def consulter_statut(self, id_facture: str) -> dict:
        """Appelle l'opération ConsulterStatut"""
        try:
            response = self.client.service.ConsulterStatut(
                idFacture=id_facture
            )
            return {
                "success": True,
                "idFacture": response.idFacture,
                "statut": response.statut,
                "dateModification": response.dateModification,
                "fault": None
            }
        except Fault as f:
            print(f"  [SOAP] Fault reçu : {f.code} — {f.message}")
            return {
                "success": False,
                "idFacture": id_facture,
                "statut": None,
                "dateModification": None,
                "fault": f.code
            }