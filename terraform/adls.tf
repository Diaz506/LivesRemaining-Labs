# ADLS Gen2 storage account + container for the Bronze/Silver/Gold data lake,
# plus the Databricks Access Connector (managed identity) Unity Catalog uses to
# reach the storage account.

resource "azurerm_storage_account" "datalake" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.this.name
  location                 = azurerm_resource_group.this.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true # Hierarchical namespace = ADLS Gen2
  min_tls_version          = "TLS1_2"
  tags                     = var.tags
}

resource "azurerm_storage_container" "datalake" {
  name                  = var.storage_container_name
  storage_account_name  = azurerm_storage_account.datalake.name
  container_access_type = "private"
}

# Managed identity used by Unity Catalog storage credentials.
resource "azurerm_databricks_access_connector" "this" {
  name                = "${var.workspace_name}-ac"
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Let the access connector read/write the data lake container.
resource "azurerm_role_assignment" "ac_storage" {
  scope                = azurerm_storage_account.datalake.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_databricks_access_connector.this.identity[0].principal_id
}
