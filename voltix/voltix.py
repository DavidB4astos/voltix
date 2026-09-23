"""Voltix Reflex application."""

import asyncio
import json
import os
import urllib.error
import urllib.request

import reflex as rx

from rxconfig import config


XANO_HEALTH_URL_ENV = "XANO_HEALTH_URL"


def _request_xano_health(url: str) -> dict[str, str]:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        if response.status < 200 or response.status >= 300:
            raise ValueError(f"Xano returned unexpected HTTP status {response.status}.")
        payload = json.loads(response.read().decode("utf-8"))

    if not isinstance(payload, dict):
        raise ValueError("Xano health response must be a JSON object.")

    expected_payload = {
        "status": "ok",
        "service": "voltix-xano",
        "integration": "available",
    }
    if payload != expected_payload:
        raise ValueError("Xano health response does not match the expected contract.")
    return expected_payload


class State(rx.State):
    integration_loading: bool = False
    integration_status: str = "idle"
    integration_message: str = "Integration check has not run."
    integration_payload: str = ""

    @rx.event
    async def check_integration(self):
        self.integration_loading = True
        self.integration_status = "loading"
        self.integration_message = "Checking the Reflex-Xano integration..."
        self.integration_payload = ""

        health_url = os.getenv(XANO_HEALTH_URL_ENV, "").strip()
        if not health_url:
            self.integration_loading = False
            self.integration_status = "error"
            self.integration_message = (
                f"Missing required environment variable: {XANO_HEALTH_URL_ENV}."
            )
            return

        try:
            payload = await asyncio.to_thread(_request_xano_health, health_url)
        except urllib.error.HTTPError as error:
            self.integration_loading = False
            self.integration_status = "error"
            self.integration_message = (
                f"Xano health check failed with HTTP status {error.code}."
            )
            return
        except urllib.error.URLError as error:
            self.integration_loading = False
            self.integration_status = "error"
            self.integration_message = f"Xano health check could not reach the backend: {error.reason}."
            return
        except (TimeoutError, ValueError, json.JSONDecodeError) as error:
            self.integration_loading = False
            self.integration_status = "error"
            self.integration_message = f"Xano health check failed: {error}"
            return

        self.integration_loading = False
        self.integration_status = "success"
        self.integration_message = "Reflex-Xano integration is available."
        self.integration_payload = json.dumps(payload, sort_keys=True)


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Voltix integration check", size="9"),
            rx.text(
                "Validate the server-side connection from Reflex State to Xano.",
            ),
            rx.button(
                rx.cond(
                    State.integration_loading,
                    "Checking...",
                    "Check Xano connection",
                ),
                on_click=State.check_integration,
                disabled=State.integration_loading,
            ),
            rx.text(State.integration_message),
            rx.cond(
                State.integration_payload != "",
                rx.code(State.integration_payload),
                rx.fragment(),
            ),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
    )


app = rx.App()
app.add_page(index)
