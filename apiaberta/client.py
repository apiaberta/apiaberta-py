"""
apiaberta-py — Python SDK for API Aberta
https://apiaberta.pt | https://github.com/apiaberta/apiaberta-py
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional
from urllib.parse import urlencode

__version__ = "1.0.0"
DEFAULT_BASE_URL = "https://api.apiaberta.pt/v1"


class ApiAbertaError(Exception):
    """Raised when the API returns an error response."""

    def __init__(self, message: str, status_code: int = 0, body: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class ApiAberta:
    """
    Python client for the API Aberta platform.

    Parameters
    ----------
    api_key : str, optional
        Your API key. Falls back to the ``APIABERTA_KEY`` environment variable.
    base_url : str, optional
        Override the API base URL (default: https://api.apiaberta.pt/v1).
    timeout : float, optional
        Request timeout in seconds (default: 10).
    session : requests.Session, optional
        Provide a custom ``requests.Session`` (useful for testing / proxies).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 10.0,
        session=None,
    ):
        self.api_key = api_key or os.environ.get("APIABERTA_KEY")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = session

    # ── Internal ──────────────────────────────────────────────────────────────

    def _get_session(self):
        if self._session is not None:
            return self._session
        try:
            import requests
            s = requests.Session()
            s.headers.update({
                "User-Agent": f"apiaberta-py/{__version__}",
                "Accept": "application/json",
            })
            if self.api_key:
                s.headers["X-API-Key"] = self.api_key
            return s
        except ImportError:
            raise ImportError(
                "The 'requests' package is required. Install it with: pip install requests"
            )

    def _fetch(self, path: str, params: Optional[Dict] = None) -> Any:
        url = f"{self.base_url}{path}"
        if params:
            clean = {k: v for k, v in params.items() if v is not None}
            if clean:
                url = f"{url}?{urlencode(clean)}"

        session = self._get_session()
        try:
            res = session.get(url, timeout=self.timeout)
        except Exception as e:
            raise ApiAbertaError(f"Network error: {e}", 0)

        try:
            body = res.json()
        except Exception:
            body = {"message": "Invalid JSON response"}

        if not res.ok:
            msg = body.get("message") or body.get("error") or "Unknown error"
            raise ApiAbertaError(msg, res.status_code, body)

        return body

    # ── Fuel ──────────────────────────────────────────────────────────────────

    def fuel(
        self,
        district: Optional[str] = None,
        fuel: Optional[str] = None,
        date: Optional[str] = None,
    ) -> Dict:
        """
        Get fuel prices in Portugal.

        Parameters
        ----------
        district : str, optional
            Filter by district name (e.g. "Lisboa").
        fuel : str, optional
            Filter by fuel slug (e.g. "diesel", "gasolina_95").
        date : str, optional
            Date in YYYY-MM-DD format (defaults to today).

        Returns
        -------
        dict
            ``{"data": [...]}``
        """
        return self._fetch("/fuel/prices", {"district": district, "fuel": fuel, "date": date})

    def fuel_stations(
        self,
        district: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Dict:
        """Get fuel stations."""
        return self._fetch("/fuel/stations", {"district": district, "page": page, "limit": limit})

    # ── Weather (IPMA) ────────────────────────────────────────────────────────

    def weather(self, days: int = 5) -> Dict:
        """
        Get weather forecasts for all Portuguese cities.

        Parameters
        ----------
        days : int
            Number of days ahead (1–10, default 5).
        """
        return self._fetch("/ipma/forecasts", {"days": days})

    def weather_city(self, city_id: int) -> Dict:
        """
        Get weather forecast for a specific city.

        Parameters
        ----------
        city_id : int
            IPMA city ID (e.g. 1110600 for Lisboa).
        """
        if not city_id:
            raise ApiAbertaError("city_id is required", 400)
        return self._fetch(f"/ipma/forecasts/{city_id}")

    def weather_warnings(
        self,
        level: Optional[str] = None,
        region: Optional[str] = None,
    ) -> Dict:
        """
        Get active meteorological warnings.

        Parameters
        ----------
        level : str, optional
            Filter by level: yellow, orange, red.
        region : str, optional
            Filter by region code.
        """
        return self._fetch("/ipma/warnings", {"level": level, "region": region})

    # ── Civil Protection (ANPC) ───────────────────────────────────────────────

    def incidents(
        self,
        active: Optional[bool] = None,
        district: Optional[str] = None,
        natureza: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Dict:
        """
        Get civil protection incidents (wildfires, floods, etc.).

        Parameters
        ----------
        active : bool, optional
            Filter by active status (default: True = active only).
        district : str, optional
            Filter by district name.
        natureza : str, optional
            Filter by incident type (e.g. "Mato", "Florestal").
        from_date : str, optional
            ISO date filter (from).
        to_date : str, optional
            ISO date filter (to).
        """
        return self._fetch("/anpc/incidents", {
            "active": active,
            "district": district,
            "natureza": natureza,
            "from": from_date,
            "to": to_date,
            "page": page,
            "limit": limit,
        })

    def active_incidents(self) -> Dict:
        """Get currently active civil protection incidents."""
        return self._fetch("/anpc/incidents/active")

    # ── Statistics (INE/Eurostat) ─────────────────────────────────────────────

    def stats(self, indicator: Optional[str] = None) -> Dict:
        """
        Get Portuguese national statistics.

        Parameters
        ----------
        indicator : str, optional
            Indicator slug: population, gdp, unemployment, inflation,
            fertility, life_expectancy, etc.
        """
        return self._fetch("/ine/stats", {"indicator": indicator})

    # ── EV Tariffs ────────────────────────────────────────────────────────────

    def ev(self) -> Dict:
        """Get EV charging tariffs from OMIE/ERSE."""
        return self._fetch("/ev/tariffs")

    # ── Public Contracts (BASE) ───────────────────────────────────────────────

    def contracts(
        self,
        query: Optional[str] = None,
        contract_type: Optional[str] = None,
        procedure_type: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Dict:
        """
        Get public contracts from BASE.gov.pt.

        Parameters
        ----------
        query : str, optional
            Full-text search query.
        """
        return self._fetch("/base/contracts", {
            "query": query,
            "contractType": contract_type,
            "procedureType": procedure_type,
            "from": from_date,
            "to": to_date,
            "page": page,
            "limit": limit,
        })

    # ── Platform ──────────────────────────────────────────────────────────────

    def status(self) -> Dict:
        """Get platform status (all services)."""
        return self._fetch("/status")

    def usage(self) -> Dict:
        """
        Get API usage stats for the authenticated developer.
        Requires api_key.
        """
        if not self.api_key:
            raise ApiAbertaError("api_key is required for usage()", 401)
        return self._fetch("/auth/usage")
