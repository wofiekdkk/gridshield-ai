"""
Grid Service - Orchestrates power grid simulation
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path("D:/gridshield-ai")))

from typing import Dict, Any, List, Optional
from app.core.logger import logger

try:
    from simulation.grid.grid_builder import build_default_grid
    from simulation.grid.power_flow import run_power_flow
    SIMULATION_AVAILABLE = True
except Exception as e:
    logger.warning(f"Simulation modules not loaded: {e}")
    SIMULATION_AVAILABLE = False


class GridService:
    def __init__(self):
        self.net = None
        self.last_state: Dict[str, Any] = {}
        self.initialize()

    def initialize(self):
        if not SIMULATION_AVAILABLE:
            logger.warning("Running without pandapower simulation.")
            return
        try:
            self.net = build_default_grid()
            self.run_simulation()
            logger.info("Grid service initialized successfully")
        except Exception as e:
            logger.error(f"Grid init failed: {e}")

    def run_simulation(self) -> Dict[str, Any]:
        if not self.net:
            return self._mock_state()
        try:
            result = run_power_flow(self.net)
            self.last_state = result
            return result
        except Exception as e:
            logger.error(f"Power flow error: {e}")
            return self._mock_state()

    def get_state(self) -> Dict[str, Any]:
        return self.last_state or self._mock_state()

    def get_components(self) -> List[Dict[str, Any]]:
        if not self.net:
            return self._mock_components()
        components = []
        try:
            for idx, bus in self.net.bus.iterrows():
                components.append({
                    "component_id": f"BUS_{idx}",
                    "component_type": "bus",
                    "name": bus.get("name", f"Bus_{idx}"),
                    "status": "NORMAL",
                })
            for idx, line in self.net.line.iterrows():
                components.append({
                    "component_id": f"LINE_{idx}",
                    "component_type": "line",
                    "name": line.get("name", f"Line_{idx}"),
                    "status": "NORMAL",
                })
            for idx, trafo in self.net.trafo.iterrows():
                components.append({
                    "component_id": f"TRAFO_{idx}",
                    "component_type": "transformer",
                    "name": trafo.get("name", f"Trafo_{idx}"),
                    "status": "NORMAL",
                })
            for idx, load in self.net.load.iterrows():
                components.append({
                    "component_id": f"LOAD_{idx}",
                    "component_type": "load",
                    "name": load.get("name", f"Load_{idx}"),
                    "is_critical": bool(load.get("controllable", False)),
                    "status": "NORMAL",
                })
        except Exception as e:
            logger.error(f"Error extracting components: {e}")
        return components

    def _mock_state(self) -> Dict[str, Any]:
        return {
            "status": "NORMAL",
            "total_generation": 150.0,
            "total_load": 142.5,
            "max_line_loading": 72.3,
            "min_voltage": 0.98,
            "max_voltage": 1.02,
            "buses": [],
            "lines": [],
        }

    def _mock_components(self) -> List[Dict[str, Any]]:
        return [
            {"component_id": "BUS_0", "component_type": "bus", "name": "Main Bus", "status": "NORMAL"},
            {"component_id": "LINE_0", "component_type": "line", "name": "Line L1", "status": "NORMAL"},
            {"component_id": "LINE_7", "component_type": "line", "name": "Line L7", "status": "NORMAL"},
            {"component_id": "TRAFO_0", "component_type": "transformer", "name": "Trafo T1", "status": "NORMAL"},
            {"component_id": "LOAD_0", "component_type": "load", "name": "Hospital", "is_critical": True, "status": "NORMAL"},
        ]


grid_service = GridService()
