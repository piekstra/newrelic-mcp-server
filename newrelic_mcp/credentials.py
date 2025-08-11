#!/usr/bin/env python3
"""
Secure credential management for New Relic MCP Server using macOS Keychain
"""

import logging
import os
from typing import Optional

import keyring

logger = logging.getLogger(__name__)

SERVICE_NAME = "newrelic-mcp-server"


class SecureCredentials:
    """Secure credential storage using macOS Keychain"""

    @staticmethod
    def store_api_key(api_key: str) -> None:
        """Store New Relic API key securely in keychain"""
        try:
            keyring.set_password(SERVICE_NAME, "api_key", api_key)
            logger.info("API key stored securely in keychain")
        except Exception as e:
            logger.error(f"Failed to store API key in keychain: {e}")
            raise

    @staticmethod
    def get_api_key() -> Optional[str]:
        """Retrieve New Relic API key from keychain or environment"""
        # First try keychain
        try:
            api_key = keyring.get_password(SERVICE_NAME, "api_key")
            if api_key:
                logger.info("Retrieved API key from keychain")
                return api_key
        except Exception as e:
            logger.warning(f"Failed to retrieve API key from keychain: {e}")

        # Fallback to environment variables for backwards compatibility
        api_key = os.getenv("NEWRELIC_API_KEY") or os.getenv("NEW_RELIC_API_KEY")
        if api_key:
            logger.warning(
                "Using API key from environment variable "
                "(consider migrating to keychain)"
            )

        return api_key

    @staticmethod
    def store_account_id(account_id: str) -> None:
        """Store New Relic account ID securely in keychain"""
        try:
            keyring.set_password(SERVICE_NAME, "account_id", account_id)
            logger.info("Account ID stored securely in keychain")
        except Exception as e:
            logger.error(f"Failed to store account ID in keychain: {e}")
            raise

    @staticmethod
    def get_account_id() -> Optional[str]:
        """Retrieve New Relic account ID from keychain or environment"""
        # First try keychain
        try:
            account_id = keyring.get_password(SERVICE_NAME, "account_id")
            if account_id:
                logger.info("Retrieved account ID from keychain")
                return account_id
        except Exception as e:
            logger.warning(f"Failed to retrieve account ID from keychain: {e}")

        # Fallback to environment variable for backwards compatibility
        account_id = os.getenv("NEWRELIC_ACCOUNT_ID")
        if account_id:
            logger.warning(
                "Using account ID from environment variable "
                "(consider migrating to keychain)"
            )

        return account_id

    @staticmethod
    def get_region() -> str:
        """Get New Relic region (stored as env var as it's not sensitive)"""
        return os.getenv("NEWRELIC_REGION", "US")

    @staticmethod
    def delete_credentials() -> None:
        """Remove all stored credentials from keychain"""
        try:
            keyring.delete_password(SERVICE_NAME, "api_key")
            logger.info("API key removed from keychain")
        except keyring.errors.PasswordDeleteError:
            logger.info("No API key found in keychain to delete")
        except Exception as e:
            logger.error(f"Failed to delete API key from keychain: {e}")

        try:
            keyring.delete_password(SERVICE_NAME, "account_id")
            logger.info("Account ID removed from keychain")
        except keyring.errors.PasswordDeleteError:
            logger.info("No account ID found in keychain to delete")
        except Exception as e:
            logger.error(f"Failed to delete account ID from keychain: {e}")

    @staticmethod
    def list_stored_credentials() -> dict:
        """List what credentials are stored (True/False, not actual values)"""
        credentials = {}

        try:
            api_key = keyring.get_password(SERVICE_NAME, "api_key")
            credentials["api_key_in_keychain"] = api_key is not None
        except Exception:
            credentials["api_key_in_keychain"] = False

        try:
            account_id = keyring.get_password(SERVICE_NAME, "account_id")
            credentials["account_id_in_keychain"] = account_id is not None
        except Exception:
            credentials["account_id_in_keychain"] = False

        credentials["api_key_in_env"] = bool(
            os.getenv("NEWRELIC_API_KEY") or os.getenv("NEW_RELIC_API_KEY")
        )
        credentials["account_id_in_env"] = bool(os.getenv("NEWRELIC_ACCOUNT_ID"))
        credentials["region"] = os.getenv("NEWRELIC_REGION", "US")

        return credentials


def setup_credentials_cli():
    """Interactive CLI for setting up secure credentials"""
    import getpass

    print("=== New Relic MCP Server - Secure Credential Setup ===\n")

    # Show current status
    status = SecureCredentials.list_stored_credentials()
    print("Current credential status:")
    print(f"  API Key in keychain: {'✓' if status['api_key_in_keychain'] else '✗'}")
    print(f"  API Key in environment: {'✓' if status['api_key_in_env'] else '✗'}")
    print(
        f"  Account ID in keychain: "
        f"{'✓' if status['account_id_in_keychain'] else '✗'}"
    )
    print(f"  Account ID in environment: {'✓' if status['account_id_in_env'] else '✗'}")
    print(f"  Region: {status['region']}\n")

    # API Key setup
    if not status["api_key_in_keychain"]:
        while True:
            api_key = getpass.getpass(
                "Enter your New Relic API Key (starts with NRAK-): "
            ).strip()
            if api_key.startswith("NRAK-"):
                try:
                    SecureCredentials.store_api_key(api_key)
                    print("✓ API key stored securely in keychain\n")
                    break
                except Exception as e:
                    print(f"✗ Failed to store API key: {e}")
                    break
            else:
                print(
                    "✗ Invalid API key format. " "New Relic API keys start with 'NRAK-'"
                )
    else:
        print("✓ API key already stored in keychain\n")

    # Account ID setup
    if not status["account_id_in_keychain"]:
        account_id = input(
            "Enter your New Relic Account ID " "(optional, press Enter to skip): "
        ).strip()
        if account_id:
            try:
                SecureCredentials.store_account_id(account_id)
                print("✓ Account ID stored securely in keychain\n")
            except Exception as e:
                print(f"✗ Failed to store account ID: {e}")
    else:
        print("✓ Account ID already stored in keychain\n")

    print(
        "Setup complete! You can now remove the API key from your "
        "environment variables and Claude Desktop config."
    )
    print("The server will automatically use the secure keychain storage.")


if __name__ == "__main__":
    setup_credentials_cli()
