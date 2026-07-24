import logging
import httpx
from telegram import Bot
from telegram.error import TelegramError
from typing import Dict, Any, Optional

from .config import Config
from .models import DecisionResult, ActionResult, WazuhAlert

logger = logging.getLogger(__name__)


class ActionExecutor:
    def __init__(self):
        self.wazuh_api_url = Config.WAZUH_API_URL
        self.wazuh_api_user = Config.WAZUH_API_USER
        self.wazuh_api_password = Config.WAZUH_API_PASSWORD
        self.telegram_bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        self.telegram_chat_id = Config.TELEGRAM_CHAT_ID

    async def _get_wazuh_api_token(self) -> Optional[str]:
        """Authenticate with Wazuh API and get JWT token."""
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.post(
                    f"{self.wazuh_api_url}/security/user/authenticate",
                    auth=(self.wazuh_api_user, self.wazuh_api_password)
                )
                response.raise_for_status()
                return response.json().get("data", {}).get("token")
        except httpx.HTTPStatusError as e:
            logger.error(f"Wazuh API authentication failed: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Wazuh API authentication request error: {e}")
        return None

    async def execute_action(self, decision: DecisionResult, alert: WazuhAlert) -> ActionResult:
        """Execute the decided action based on the decision engine output."""
        if decision.requires_approval:
            message = (
                f"🔔 ACTION REQUIRES APPROVAL\n"
                f"Alert: {alert.id}\n"
                f"Rule: {alert.rule_description}\n"
                f"Agent: {alert.agent_name}\n"
                f"Action: {decision.action_type}\n"
                f"Target: {decision.target}\n"
                f"Reason: {decision.reason}"
            )
            await self.send_telegram_notification(message)
            return ActionResult(success=False, message="Action requires approval, notification sent to admin.")

        if decision.action_type == "ALERT_ONLY":
            message = (
                f"ℹ️ ALERT NOTIFICATION\n"
                f"Alert: {alert.id}\n"
                f"Rule: {alert.rule_description}\n"
                f"Agent: {alert.agent_name}\n"
                f"Decision: Alert Only\n"
                f"Reason: {decision.reason}"
            )
            await self.send_telegram_notification(message)
            return ActionResult(success=True, message="Alert only, notification sent.")

        # Execute automated action via Wazuh API
        token = await self._get_wazuh_api_token()
        if not token:
            error_msg = "Failed to get Wazuh API token. Cannot execute action."
            await self.send_telegram_notification(f"❌ ERROR: {error_msg}")
            return ActionResult(success=False, message=error_msg)

        headers = {"Authorization": f"Bearer {token}"}
        action_details = {
            "action_type": decision.action_type,
            "target": decision.target,
            "parameters": decision.parameters
        }

        try:
            async with httpx.AsyncClient(verify=False) as client:
                if decision.action_type == "block_ip":
                    response = await client.put(
                        f"{self.wazuh_api_url}/active-response",
                        headers=headers,
                        json={
                            "command": "firewall-drop",
                            "arguments": [f"-srcip", decision.target],
                            "alert": {"data": {"srcip": decision.target}},
                            "agent_list": [alert.agent_id]
                        }
                    )
                    response.raise_for_status()
                    message = f"✅ BLOCKED IP {decision.target} on agent {alert.agent_name} (Alert: {alert.id})"

                elif decision.action_type == "isolate_host":
                    response = await client.put(
                        f"{self.wazuh_api_url}/active-response",
                        headers=headers,
                        json={
                            "command": "host-isolate",
                            "arguments": [],
                            "agent_list": [alert.agent_id]
                        }
                    )
                    response.raise_for_status()
                    message = f"✅ ISOLATED HOST {alert.agent_name} (Alert: {alert.id})"

                elif decision.action_type == "kill_process":
                    response = await client.put(
                        f"{self.wazuh_api_url}/active-response",
                        headers=headers,
                        json={
                            "command": "kill-process",
                            "arguments": ["-process", decision.target],
                            "agent_list": [alert.agent_id]
                        }
                    )
                    response.raise_for_status()
                    message = f"✅ KILLED PROCESS {decision.target} on {alert.agent_name} (Alert: {alert.id})"

                elif decision.action_type == "disable_user":
                    response = await client.put(
                        f"{self.wazuh_api_url}/active-response",
                        headers=headers,
                        json={
                            "command": "disable-user",
                            "arguments": ["-user", decision.target],
                            "agent_list": [alert.agent_id]
                        }
                    )
                    response.raise_for_status()
                    message = f"✅ DISABLED USER {decision.target} on {alert.agent_name} (Alert: {alert.id})"

                elif decision.action_type == "collect_forensics":
                    scope = decision.parameters.get("scope", "basic") if decision.parameters else "basic"
                    response = await client.put(
                        f"{self.wazuh_api_url}/active-response",
                        headers=headers,
                        json={
                            "command": "collect-forensics",
                            "arguments": ["-scope", scope],
                            "agent_list": [alert.agent_id]
                        }
                    )
                    response.raise_for_status()
                    message = f"✅ FORENSICS COLLECTION initiated on {alert.agent_name} (scope: {scope}, Alert: {alert.id})"

                else:
                    message = f"⚠️ Unknown action type: {decision.action_type}. No action taken for alert {alert.id}."
                    await self.send_telegram_notification(message)
                    return ActionResult(success=False, message=message, details=action_details)

                await self.send_telegram_notification(message)
                return ActionResult(success=True, message=message, details=action_details)

        except httpx.HTTPStatusError as e:
            error_message = f"❌ Wazuh API action '{decision.action_type}' failed: {e.response.status_code} - {e.response.text}"
            logger.error(error_message)
            await self.send_telegram_notification(error_message)
            return ActionResult(success=False, message=error_message, details=action_details)
        except httpx.RequestError as e:
            error_message = f"❌ Wazuh API connection error for '{decision.action_type}': {e}"
            logger.error(error_message)
            await self.send_telegram_notification(error_message)
            return ActionResult(success=False, message=error_message, details=action_details)
        except Exception as e:
            error_message = f"❌ Unexpected error during action '{decision.action_type}': {e}"
            logger.error(error_message)
            await self.send_telegram_notification(error_message)
            return ActionResult(success=False, message=error_message, details=action_details)

    async def send_telegram_notification(self, message: str):
        """Send notification to admin via Telegram bot."""
        try:
            # Truncate message if too long for Telegram (max 4096 chars)
            if len(message) > 4000:
                message = message[:4000] + "\n... (truncated)"
            await self.telegram_bot.send_message(
                chat_id=self.telegram_chat_id,
                text=message,
                parse_mode=None
            )
            logger.info(f"Telegram notification sent successfully.")
        except TelegramError as e:
            logger.error(f"Failed to send Telegram notification: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram notification: {e}")
