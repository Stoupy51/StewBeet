"""
Handles text component formatting and updates for the manual
"""
from typing import Literal

from beet.core.utils import TextComponent


def create_hover_event(action: Literal["show_text", "show_item"], value: TextComponent) -> dict:
	"""Creates a hover event with the new format"""
	if action == "show_text":
		return {
			"action": "show_text",
			"value": value
		}
	elif action == "show_item" and isinstance(value, dict):
		return {
			"action": "show_item",
			"id": value.get("id", ""),
			"components": value.get("components", {})
		}
	return {}

def create_click_event(action: Literal["change_page", "run_command", "suggest_command", "open_url"], value: str | int) -> dict:
	"""Creates a click event with the new format"""
	if action == "change_page":
		return {
			"action": "change_page",
			"page": int(value) if isinstance(value, str) else value
		}
	elif action == "run_command":
		return {
			"action": "run_command",
			"command": value
		}
	elif action == "suggest_command":
		return {
			"action": "suggest_command",
			"command": value
		}
	elif action == "open_url":
		return {
			"action": "open_url",
			"url": value
		}
	return {}

