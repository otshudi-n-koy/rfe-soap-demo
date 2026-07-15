# =============================================================================
# PÉRIMÈTRE : Webservice SOAP legacy de facturation (RFE)
# Auteur    : N'Koy OTSHUDI — QA Senior
# =============================================================================

@soap
Feature: Facturation électronique via webservice SOAP legacy

  En tant que système d'intégration,
  Je veux soumettre et consulter des factures via le webservice SOAP legacy,
  Afin d'assurer l'interopérabilité avec les fournisseurs legacy d'Intermarché.

  Background:
    Given le webservice SOAP de facturation est disponible

  @smoke @soap
  Scenario: Soumission d'une facture B2B valide via SOAP
    When je soumets une facture SOAP 'FAC-SOAP-001' avec SIREN '123456789' destinataire '987654321' montant 1000.00 TVA 20 TTC 1200.00
    Then la réponse SOAP est un succès
    And l'identifiant de facture SOAP est renseigné
    And le statut SOAP retourné est "SUBMITTED"

  @soap
  Scenario: Rejet SOAP d'une facture avec SIREN invalide
    When je soumets une facture SOAP 'FAC-SOAP-002' avec SIREN '000000000' destinataire '987654321' montant 500.00 TVA 20 TTC 600.00
    Then la réponse SOAP est un échec
    And le code Fault SOAP est "INVALID_SIREN"

  @soap
  Scenario: Rejet SOAP d'une facture avec TVA incohérente
    When je soumets une facture SOAP 'FAC-SOAP-003' avec SIREN '123456789' destinataire '987654321' montant 100.00 TVA 20 TTC 150.00
    Then la réponse SOAP est un échec
    And le code Fault SOAP est "TVA_MISMATCH"

  @soap
  Scenario: Consultation du statut d'une facture existante
    Given une facture SOAP 'FAC-SOAP-004' a été soumise avec succès
    When je consulte le statut SOAP de la facture 'FAC-SOAP-004'
    Then la réponse SOAP est un succès
    And le statut SOAP retourné est "SUBMITTED"

  @soap
  Scenario: Consultation d'une facture SOAP introuvable
    When je consulte le statut SOAP de la facture 'INEXISTANT-999'
    Then la réponse SOAP est un échec
    And le code Fault SOAP est "INVOICE_NOT_FOUND"