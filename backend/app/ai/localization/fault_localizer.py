"""
GridShield AI - Topology-Aware Fault Localization
WHY: Determines WHERE in the grid a fault occurred, not just IF it occurred.
WHAT: Uses topology graph, sensor correlations, power flow analysis.
HOW: Analyzes neighboring sensor readings and graph structure.
INPUT: Anomalous readings, grid topology graph, grid state.
OUTPUT: Most probable fault location with confidence and affected region.
"""

import numpy as np
import networkx as nx
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
from collections import defaultdict


@dataclass
class LocalizationResult:
    component_id: str
    confidence: float
    affected_region: List[str]
    top_candidates: List[Dict]
    method: str
    evidence: Dict


class FaultLocalizer:
    """
    Topology-aware fault localization engine.

    Methods:
    1. Sensor anomaly propagation analysis
    2. Graph-based neighbor correlation
    3. Power flow deviation analysis
    4. Weighted evidence scoring
    """

    def __init__(self):
        self.topology: Optional[nx.Graph] = None
        self.component_sensors: Dict[str, str] = {}
        logger.info("FaultLocalizer initialized")

    def set_topology(self, graph: nx.Graph):
        """Set the grid topology graph."""
        self.topology = graph
        logger.info(f"Topology set: {graph.number_of_nodes()} nodes, "
                    f"{graph.number_of_edges()} edges")

    def localize(self, anomalous_readings: List[Dict],
                 all_readings: List[Dict],
                 grid_state: Dict) -> LocalizationResult:
        """
        Localize the fault source.

        Algorithm:
        1. For each anomalous sensor, score its component.
        2. Check neighbor sensors - if they're normal, fault is more local.
        3. If multiple anomalies, find the graph region that connects them.
        4. Use power flow data to narrow down.
        """
        if not anomalous_readings:
            return LocalizationResult(
                component_id="UNKNOWN",
                confidence=0.0,
                affected_region=[],
                top_candidates=[],
                method="none",
                evidence={"reason": "No anomalous readings provided"}
            )

        # Build sensor-to-anomaly-score mapping
        anomaly_map: Dict[str, float] = {}
        for reading in anomalous_readings:
            comp_id = reading.get("component_id", "")
            score = reading.get("_anomaly_score", 0.5)
            anomaly_map[comp_id] = max(anomaly_map.get(comp_id, 0), score)

        # Build normal sensor map
        normal_map: Dict[str, bool] = {}
        for reading in all_readings:
            comp_id = reading.get("component_id", "")
            if comp_id not in anomaly_map:
                normal_map[comp_id] = True

        # Score each component
        candidates = []
        for comp_id, anom_score in anomaly_map.items():
            neighbor_score = self._analyze_neighbors(comp_id, anomaly_map, normal_map)
            pf_score = self._analyze_power_flow(comp_id, grid_state)
            isolation_score = self._analyze_isolation(comp_id, anomaly_map)

            total_score = (
                0.4 * anom_score +
                0.25 * neighbor_score +
                0.2 * pf_score +
                0.15 * isolation_score
            )

            candidates.append({
                "component_id": comp_id,
                "total_score": round(total_score, 4),
                "anomaly_score": round(anom_score, 4),
                "neighbor_score": round(neighbor_score, 4),
                "pf_score": round(pf_score, 4),
                "isolation_score": round(isolation_score, 4)
            })

        # Sort by total score
        candidates.sort(key=lambda x: x["total_score"], reverse=True)

        if not candidates:
            return LocalizationResult(
                component_id="UNKNOWN", confidence=0.0,
                affected_region=[], top_candidates=[],
                method="none", evidence={}
            )

        best = candidates[0]
        affected_region = self._find_affected_region(
            best["component_id"], anomaly_map)

        return LocalizationResult(
            component_id=best["component_id"],
            confidence=min(1.0, best["total_score"]),
            affected_region=affected_region,
            top_candidates=candidates[:5],
            method="topology_aware_multi_evidence",
            evidence={
                "num_anomalous_sensors": len(anomaly_map),
                "num_normal_neighbors": len(normal_map),
                "scoring_breakdown": best
            }
        )

    def _analyze_neighbors(self, comp_id: str,
                            anomaly_map: Dict, normal_map: Dict) -> float:
        """
        If a component's neighbors are normal but it's anomalous,
        the fault is likely at this component.
        """
        if self.topology is None:
            return 0.5

        # Find the bus node for this component
        bus_node = self._comp_to_bus(comp_id)
        if bus_node is None or bus_node not in self.topology:
            return 0.5

        neighbors = list(self.topology.neighbors(bus_node))
        if not neighbors:
            return 0.5

        normal_neighbors = 0
        anomalous_neighbors = 0

        for neighbor in neighbors:
            neighbor_comp = neighbor  # BUS_X format
            if neighbor_comp in normal_map:
                normal_neighbors += 1
            if neighbor_comp in anomaly_map:
                anomalous_neighbors += 1

        total = normal_neighbors + anomalous_neighbors
        if total == 0:
            return 0.5

        # Higher score if this component is anomalous but neighbors are normal
        # (indicating a local fault)
        isolation_ratio = normal_neighbors / total
        return isolation_ratio * 0.8

    def _analyze_power_flow(self, comp_id: str, grid_state: Dict) -> float:
        """Check power flow data for the component."""
        score = 0.0

        # Check lines
        if comp_id.startswith("LINE_"):
            line_name = comp_id.replace("LINE_", "")
            line_data = grid_state.get("lines", {}).get(line_name, {})
            status = line_data.get("status", "NORMAL")
            loading = line_data.get("loading_percent", 0)

            if status == "FAULT":
                score = 0.95
            elif status == "OVERLOADED":
                score = 0.8
            elif loading > 90:
                score = 0.6
            elif loading > 80:
                score = 0.4

        # Check transformers
        elif "TRAFO" in comp_id:
            trafo_data = grid_state.get("transformers", {}).get(comp_id, {})
            status = trafo_data.get("status", "NORMAL")
            if status == "FAULT":
                score = 0.95
            elif status == "OVERLOADED":
                score = 0.8

        # Check buses
        elif comp_id.startswith("BUS_"):
            bus_data = grid_state.get("buses", {}).get(comp_id, {})
            vm_pu = bus_data.get("vm_pu", 1.0)
            if vm_pu < 0.90 or vm_pu > 1.10:
                score = 0.8
            elif vm_pu < 0.95 or vm_pu > 1.05:
                score = 0.4

        return score

    def _analyze_isolation(self, comp_id: str,
                            anomaly_map: Dict) -> float:
        """Higher score for components that are the most isolated anomaly."""
        if len(anomaly_map) == 1:
            return 0.9  # Only one anomaly = high confidence

        # Check if this component has the highest anomaly score
        max_score = max(anomaly_map.values())
        this_score = anomaly_map.get(comp_id, 0)

        if max_score > 0:
            return (this_score / max_score) * 0.8
        return 0.5

    def _comp_to_bus(self, comp_id: str) -> Optional[str]:
        """Convert component ID to its bus node in the topology graph."""
        if comp_id.startswith("BUS_"):
            return comp_id
        # For lines, use from_bus
        if comp_id.startswith("LINE_"):
            return None  # Lines are edges, not nodes
        return None

    def _find_affected_region(self, fault_comp: str,
                               anomaly_map: Dict) -> List[str]:
        """Find the region affected by the fault."""
        affected = list(anomaly_map.keys())

        if self.topology is not None:
            bus = self._comp_to_bus(fault_comp)
            if bus and bus in self.topology:
                for neighbor in self.topology.neighbors(bus):
                    if neighbor not in affected:
                        affected.append(neighbor)

        return affected[:10]  # Limit
