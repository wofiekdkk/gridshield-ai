"""
GridShield AI - Cascading Failure Predictor
WHY: Predicts whether a fault will propagate to neighboring components.
WHAT: Simulates removal of failed component and checks resulting loads.
HOW: Runs contingency power flow analysis using pandapower.
INPUT: Current grid state, failed component, topology.
OUTPUT: Cascade risk score, affected components, propagation path.
"""

import numpy as np
import pandapower as pp
import copy
from typing import Dict, List, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class CascadeResult:
    risk_score: float
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    affected_components: List[Dict]
    propagation_path: List[str]
    overloaded_lines: List[Dict]
    voltage_violations: List[Dict]
    time_to_cascade: Optional[float]
    recommendations: List[str]


class CascadePredictor:
    """
    Cascading failure prediction using contingency analysis.

    For each failed component:
    1. Create a copy of the network
    2. Remove the failed component
    3. Run power flow on the modified network
    4. Check if any remaining component exceeds limits
    5. Score the cascade risk
    """

    def __init__(self):
        self.thresholds = {
            "line_overload_warning": 80.0,
            "line_overload_critical": 95.0,
            "line_overload_max": 100.0,
            "voltage_min_pu": 0.90,
            "voltage_max_pu": 1.10,
            "trafo_loading_max": 100.0
        }
        logger.info("CascadePredictor initialized")

    def predict(self, net: pp.pandapowerNet,
                failed_component: str,
                current_state: Dict) -> CascadeResult:
        """
        Predict cascade risk for a given failure scenario.
        """
        # Create contingency network (component already failed)
        contingency_net = copy.deepcopy(net)

        # Run power flow on contingency network
        try:
            pp.runpp(contingency_net, algorithm='nr',
                    max_iteration=50, tolerance_mva=1e-8)
            converged = True
        except:
            converged = False

        if not converged:
            return CascadeResult(
                risk_score=0.95,
                risk_level="CRITICAL",
                affected_components=[{"component": "NETWORK", "issue": "Power flow diverged"}],
                propagation_path=[failed_component, "NETWORK_COLLAPSE"],
                overloaded_lines=[],
                voltage_violations=[],
                time_to_cascade=0.0,
                recommendations=["IMMEDIATE ACTION REQUIRED", "Network may collapse"]
            )

        # Analyze contingency results
        overloaded_lines = []
        voltage_violations = []
        affected_components = []
        propagation_path = [failed_component]
        risk_factors = []

        # Check line loadings
        for idx in contingency_net.line.index:
            if not contingency_net.line.at[idx, 'in_service']:
                continue
            if idx in contingency_net.res_line.index:
                loading = contingency_net.res_line.at[idx, 'loading_percent']
                name = contingency_net.line.at[idx, 'name']

                # Compare with original loading
                orig_loading = 0.0
                orig_line_data = current_state.get("lines", {}).get(name, {})
                orig_loading = orig_line_data.get("loading_percent", 0.0)

                if loading > self.thresholds["line_overload_max"]:
                    overloaded_lines.append({
                        "component": f"LINE_{name}",
                        "loading": round(float(loading), 1),
                        "original_loading": round(orig_loading, 1),
                        "increase": round(float(loading - orig_loading), 1),
                        "severity": "CRITICAL"
                    })
                    risk_factors.append(min(1.0, loading / 100))
                    propagation_path.append(f"LINE_{name}")
                    affected_components.append({
                        "component": f"LINE_{name}",
                        "issue": f"Overloaded to {loading:.1f}%",
                        "severity": "CRITICAL"
                    })
                elif loading > self.thresholds["line_overload_critical"]:
                    overloaded_lines.append({
                        "component": f"LINE_{name}",
                        "loading": round(float(loading), 1),
                        "original_loading": round(orig_loading, 1),
                        "increase": round(float(loading - orig_loading), 1),
                        "severity": "HIGH"
                    })
                    risk_factors.append(loading / 120)
                    affected_components.append({
                        "component": f"LINE_{name}",
                        "issue": f"Near overload at {loading:.1f}%",
                        "severity": "HIGH"
                    })
                elif loading > self.thresholds["line_overload_warning"]:
                    risk_factors.append(loading / 150)

        # Check bus voltages
        for idx in contingency_net.bus.index:
            if idx in contingency_net.res_bus.index:
                vm_pu = contingency_net.res_bus.at[idx, 'vm_pu']
                if vm_pu < self.thresholds["voltage_min_pu"] or \
                   vm_pu > self.thresholds["voltage_max_pu"]:
                    voltage_violations.append({
                        "component": f"BUS_{idx}",
                        "voltage_pu": round(float(vm_pu), 4),
                        "severity": "HIGH"
                    })
                    risk_factors.append(0.6)
                    affected_components.append({
                        "component": f"BUS_{idx}",
                        "issue": f"Voltage violation: {vm_pu:.3f} pu",
                        "severity": "HIGH"
                    })

        # Check transformer loadings
        for idx in contingency_net.trafo.index:
            if not contingency_net.trafo.at[idx, 'in_service']:
                continue
            if idx in contingency_net.res_trafo.index:
                loading = contingency_net.res_trafo.at[idx, 'loading_percent']
                if loading > self.thresholds["trafo_loading_max"]:
                    name = contingency_net.trafo.at[idx, 'name']
                    affected_components.append({
                        "component": name,
                        "issue": f"Transformer overloaded: {loading:.1f}%",
                        "severity": "CRITICAL"
                    })
                    risk_factors.append(min(1.0, loading / 100))

        # Calculate overall risk score
        if not risk_factors:
            risk_score = 0.05
        else:
            risk_score = min(1.0, np.mean(risk_factors) + 0.1 * len(risk_factors))

        # Determine risk level
        if risk_score > 0.8:
            risk_level = "CRITICAL"
        elif risk_score > 0.6:
            risk_level = "HIGH"
        elif risk_score > 0.3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # Generate recommendations
        recommendations = self._generate_recommendations(
            risk_level, overloaded_lines, voltage_violations, affected_components
        )

        return CascadeResult(
            risk_score=round(risk_score, 4),
            risk_level=risk_level,
            affected_components=affected_components,
            propagation_path=propagation_path,
            overloaded_lines=overloaded_lines,
            voltage_violations=voltage_violations,
            time_to_cascade=self._estimate_time_to_cascade(risk_score),
            recommendations=recommendations
        )

    def _estimate_time_to_cascade(self, risk_score: float) -> Optional[float]:
        if risk_score < 0.3:
            return None
        return max(1.0, (1.0 - risk_score) * 60)  # seconds

    def _generate_recommendations(self, risk_level, overloaded_lines,
                                   voltage_violations, affected) -> List[str]:
        recs = []
        if risk_level == "CRITICAL":
            recs.append("IMMEDIATE: Isolate fault and activate alternate paths")
            recs.append("IMMEDIATE: Shed non-critical loads if needed")
        elif risk_level == "HIGH":
            recs.append("URGENT: Prepare alternate routing")
            recs.append("MONITOR: Watch affected components closely")
        elif risk_level == "MEDIUM":
            recs.append("PREPARE: Have recovery plans ready")
        else:
            recs.append("MONITOR: Continue normal monitoring")

        for ol in overloaded_lines[:3]:
            recs.append(f"LOAD: Reduce loading on {ol['component']} "
                       f"(currently {ol['loading']}%)")

        for vv in voltage_violations[:3]:
            recs.append(f"VOLTAGE: Address violation at {vv['component']} "
                       f"({vv['voltage_pu']} pu)")

        return recs
