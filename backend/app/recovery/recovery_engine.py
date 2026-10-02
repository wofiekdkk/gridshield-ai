"""
GridShield AI - Constraint-Aware Recovery Engine
WHY: Generates, validates, and optimizes recovery plans after faults.
WHAT: Creates candidate recovery configurations, checks constraints,
      optimizes for maximum load restoration with minimum risk.
HOW: Generates candidates from topology, validates with power flow,
     scores with multi-objective optimization.
INPUT: Fault info, grid state, topology, constraints.
OUTPUT: Ranked feasible recovery plans.
"""

import numpy as np
import pandapower as pp
import copy
import uuid
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class RecoveryActionItem:
    action_type: str  # OPEN_BREAKER, CLOSE_BREAKER, ISOLATE, REROUTE, SHED_LOAD, RESTORE_LOAD
    component_id: str
    previous_state: str
    new_state: str
    description: str


@dataclass
class RecoveryCandidate:
    plan_id: str
    fault_id: str
    actions: List[RecoveryActionItem]
    restored_load_mw: float = 0.0
    total_demand_mw: float = 0.0
    restored_load_pct: float = 0.0
    cascade_risk: float = 0.0
    max_line_loading: float = 0.0
    max_trafo_loading: float = 0.0
    min_voltage_pu: float = 1.0
    max_voltage_pu: float = 1.0
    switching_operations: int = 0
    constraint_violations: List[str] = field(default_factory=list)
    feasible: bool = False
    objective_score: float = 0.0
    status: str = "GENERATED"
    pf_converged: bool = False
    critical_loads_served: bool = True


class ConstraintChecker:
    """
    Validates recovery configurations against hard electrical constraints.
    """

    def __init__(self):
        self.constraints = {
            "voltage_min_pu": 0.90,
            "voltage_max_pu": 1.10,
            "line_loading_max_pct": 100.0,
            "trafo_loading_max_pct": 100.0,
            "frequency_min": 49.5,
            "frequency_max": 50.5
        }

    def check(self, net: pp.pandapowerNet) -> Tuple[bool, List[str], Dict]:
        """
        Check all hard constraints on a network.
        Returns: (feasible, violations, metrics)
        """
        violations = []
        metrics = {
            "max_line_loading": 0.0,
            "max_trafo_loading": 0.0,
            "min_voltage_pu": 1.0,
            "max_voltage_pu": 1.0,
            "total_load_mw": 0.0
        }

        # Run power flow
        try:
            pp.runpp(net, algorithm='nr', max_iteration=50)
        except:
            violations.append("POWER_FLOW_DIVERGED")
            return False, violations, metrics

        # Check line loadings
        for idx in net.res_line.index:
            if net.line.at[idx, 'in_service']:
                loading = net.res_line.at[idx, 'loading_percent']
                metrics["max_line_loading"] = max(metrics["max_line_loading"], loading)
                if loading > self.constraints["line_loading_max_pct"]:
                    name = net.line.at[idx, 'name']
                    violations.append(
                        f"LINE_OVERLOAD: {name} at {loading:.1f}%")

        # Check transformer loadings
        for idx in net.res_trafo.index:
            if net.trafo.at[idx, 'in_service']:
                loading = net.res_trafo.at[idx, 'loading_percent']
                metrics["max_trafo_loading"] = max(
                    metrics["max_trafo_loading"], loading)
                if loading > self.constraints["trafo_loading_max_pct"]:
                    name = net.trafo.at[idx, 'name']
                    violations.append(
                        f"TRAFO_OVERLOAD: {name} at {loading:.1f}%")

        # Check voltages
        for idx in net.res_bus.index:
            if net.bus.at[idx, 'in_service']:
                vm = net.res_bus.at[idx, 'vm_pu']
                metrics["min_voltage_pu"] = min(metrics["min_voltage_pu"], vm)
                metrics["max_voltage_pu"] = max(metrics["max_voltage_pu"], vm)
                if vm < self.constraints["voltage_min_pu"]:
                    violations.append(
                        f"UNDERVOLTAGE: BUS_{idx} at {vm:.3f} pu")
                if vm > self.constraints["voltage_max_pu"]:
                    violations.append(
                        f"OVERVOLTAGE: BUS_{idx} at {vm:.3f} pu")

        # Calculate total load
        for idx in net.res_load.index:
            if net.load.at[idx, 'in_service']:
                metrics["total_load_mw"] += net.res_load.at[idx, 'p_mw']

        feasible = len(violations) == 0
        return feasible, violations, metrics


class RecoveryOptimizer:
    """
    Scores and ranks recovery candidates.

    Objective:
    maximize: Restored_Load - alpha*Cascade_Risk - beta*Switching_Cost
              - gamma*Overload_Penalty

    Subject to: All hard constraints satisfied.
    """

    def __init__(self):
        self.alpha = 0.3   # Cascade risk weight
        self.beta = 0.05   # Switching cost weight
        self.gamma = 0.2   # Overload penalty weight
        self.critical_load_bonus = 0.15

    def score(self, candidate: RecoveryCandidate) -> float:
        """Calculate objective score for a candidate."""
        if not candidate.feasible:
            return -1.0

        # Normalized restored load (0-1)
        load_score = candidate.restored_load_pct / 100.0

        # Cascade risk penalty
        cascade_penalty = self.alpha * candidate.cascade_risk

        # Switching cost (normalized)
        switch_penalty = self.beta * min(1.0, candidate.switching_operations / 10)

        # Overload proximity penalty
        overload_penalty = self.gamma * max(0, (candidate.max_line_loading - 70) / 30)

        # Critical load bonus
        critical_bonus = self.critical_load_bonus if candidate.critical_loads_served else 0

        score = load_score - cascade_penalty - switch_penalty - overload_penalty + critical_bonus
        return round(max(0, min(1.0, score)), 4)


class RecoveryEngine:
    """
    Main recovery engine that generates, validates, and selects recovery plans.
    """

    def __init__(self, grid_simulator):
        self.grid = grid_simulator
        self.constraint_checker = ConstraintChecker()
        self.optimizer = RecoveryOptimizer()
        self.recovery_history: List[RecoveryCandidate] = []
        logger.info("RecoveryEngine initialized")

    def generate_recovery_plans(self, fault_id: str,
                                 failed_component: str,
                                 fault_type: str,
                                 grid_state: Dict) -> List[RecoveryCandidate]:
        """
        Generate candidate recovery plans for a fault.

        Strategy:
        1. Isolate the faulty component
        2. Try alternate paths
        3. Try load shedding
        4. Try combination of above
        """
        candidates = []

        # Strategy 1: Alternate path routing
        alternate_plans = self._generate_alternate_path_plans(
            fault_id, failed_component, fault_type)
        candidates.extend(alternate_plans)

        # Strategy 2: Load shedding + alternate path
        shedding_plans = self._generate_load_shedding_plans(
            fault_id, failed_component, fault_type)
        candidates.extend(shedding_plans)

        # Strategy 3: Tie breaker activation
        tie_plans = self._generate_tie_breaker_plans(
            fault_id, failed_component, fault_type)
        candidates.extend(tie_plans)

        # Evaluate all candidates
        evaluated = []
        for candidate in candidates:
            evaluated_candidate = self._evaluate_candidate(candidate)
            evaluated.append(evaluated_candidate)

        # Sort by feasibility first, then objective score
        evaluated.sort(key=lambda c: (c.feasible, c.objective_score), reverse=True)

        logger.info(f"Generated {len(evaluated)} recovery plans for fault {fault_id}, "
                    f"{sum(1 for c in evaluated if c.feasible)} feasible")

        return evaluated

    def _generate_alternate_path_plans(self, fault_id: str,
                                        failed_component: str,
                                        fault_type: str) -> List[RecoveryCandidate]:
        plans = []
        alt_paths = self.grid.get_alternate_paths()

        for alt_line in alt_paths:
            plan_id = f"RP-{uuid.uuid4().hex[:8].upper()}"
            actions = [
                RecoveryActionItem(
                    action_type="ISOLATE",
                    component_id=failed_component,
                    previous_state="FAULT",
                    new_state="ISOLATED",
                    description=f"Isolate faulty {failed_component}"
                ),
                RecoveryActionItem(
                    action_type="CLOSE_LINE",
                    component_id=f"LINE_{alt_line}",
                    previous_state="OPEN",
                    new_state="CLOSED",
                    description=f"Activate alternate path {alt_line}"
                )
            ]

            candidate = RecoveryCandidate(
                plan_id=plan_id,
                fault_id=fault_id,
                actions=actions,
                switching_operations=2
            )
            plans.append(candidate)

        return plans

    def _generate_load_shedding_plans(self, fault_id: str,
                                       failed_component: str,
                                       fault_type: str) -> List[RecoveryCandidate]:
        plans = []
        loads_by_priority = self.grid.get_loads_by_priority()
        alt_paths = self.grid.get_alternate_paths()

        # Shed non-critical loads + activate alt path
        non_critical = loads_by_priority.get("NON_CRITICAL", [])
        if non_critical and alt_paths:
            plan_id = f"RP-{uuid.uuid4().hex[:8].upper()}"
            actions = [
                RecoveryActionItem(
                    action_type="ISOLATE",
                    component_id=failed_component,
                    previous_state="FAULT",
                    new_state="ISOLATED",
                    description=f"Isolate faulty {failed_component}"
                )
            ]

            for load in non_critical:
                actions.append(RecoveryActionItem(
                    action_type="SHED_LOAD",
                    component_id=load,
                    previous_state="ACTIVE",
                    new_state="SHED",
                    description=f"Shed non-critical load {load}"
                ))

            if alt_paths:
                actions.append(RecoveryActionItem(
                    action_type="CLOSE_LINE",
                    component_id=f"LINE_{alt_paths[0]}",
                    previous_state="OPEN",
                    new_state="CLOSED",
                    description=f"Activate alternate path {alt_paths[0]}"
                ))

            candidate = RecoveryCandidate(
                plan_id=plan_id,
                fault_id=fault_id,
                actions=actions,
                switching_operations=len(actions)
            )
            plans.append(candidate)

        return plans

    def _generate_tie_breaker_plans(self, fault_id: str,
                                     failed_component: str,
                                     fault_type: str) -> List[RecoveryCandidate]:
        plans = []

        # Close tie breaker between substations
        plan_id = f"RP-{uuid.uuid4().hex[:8].upper()}"
        actions = [
            RecoveryActionItem(
                action_type="ISOLATE",
                component_id=failed_component,
                previous_state="FAULT",
                new_state="ISOLATED",
                description=f"Isolate faulty {failed_component}"
            ),
            RecoveryActionItem(
                action_type="CLOSE_SWITCH",
                component_id="CB_L14_TIE",
                previous_state="OPEN",
                new_state="CLOSED",
                description="Close tie breaker between Sub A and Sub B"
            ),
            RecoveryActionItem(
                action_type="CLOSE_LINE",
                component_id="LINE_L14",
                previous_state="OPEN",
                new_state="CLOSED",
                description="Activate tie line L14"
            )
        ]

        candidate = RecoveryCandidate(
            plan_id=plan_id,
            fault_id=fault_id,
            actions=actions,
            switching_operations=3
        )
        plans.append(candidate)

        return plans

    def _evaluate_candidate(self, candidate: RecoveryCandidate) -> RecoveryCandidate:
        """
        Evaluate a recovery candidate by:
        1. Applying actions to a copy of the network
        2. Running power flow
        3. Checking constraints
        4. Calculating objective score
        """
        test_net = copy.deepcopy(self.grid.net)

        # Apply recovery actions
        for action in candidate.actions:
            self._apply_action_to_net(test_net, action)

        # Check constraints
        feasible, violations, metrics = self.constraint_checker.check(test_net)

        candidate.feasible = feasible
        candidate.constraint_violations = violations
        candidate.max_line_loading = metrics["max_line_loading"]
        candidate.max_trafo_loading = metrics["max_trafo_loading"]
        candidate.min_voltage_pu = metrics["min_voltage_pu"]
        candidate.max_voltage_pu = metrics["max_voltage_pu"]
        candidate.pf_converged = len(violations) == 0 or \
                                  "POWER_FLOW_DIVERGED" not in violations

        # Calculate restored load
        total_demand = sum(
            float(self.grid.base_net.load.at[idx, 'p_mw'])
            for idx in self.grid.base_net.load.index
        )
        candidate.total_demand_mw = total_demand
        candidate.restored_load_mw = metrics["total_load_mw"]
        candidate.restored_load_pct = round(
            (metrics["total_load_mw"] / total_demand * 100)
            if total_demand > 0 else 0, 1
        )

        # Check critical loads
        critical_loads = self.grid.get_loads_by_priority().get("CRITICAL", [])
        for load_name in critical_loads:
            for idx in test_net.load.index:
                if test_net.load.at[idx, 'name'] == load_name:
                    if not test_net.load.at[idx, 'in_service']:
                        candidate.critical_loads_served = False

        # Calculate objective score
        candidate.objective_score = self.optimizer.score(candidate)

        return candidate

    def _apply_action_to_net(self, net: pp.pandapowerNet,
                              action: RecoveryActionItem):
        """Apply a single recovery action to a pandapower network."""
        if action.action_type == "ISOLATE":
            # Already handled by fault - line out of service
            pass
        elif action.action_type == "CLOSE_LINE":
            line_name = action.component_id.replace("LINE_", "")
            for idx in net.line.index:
                if net.line.at[idx, 'name'] == line_name:
                    net.line.at[idx, 'in_service'] = True
        elif action.action_type == "OPEN_LINE":
            line_name = action.component_id.replace("LINE_", "")
            for idx in net.line.index:
                if net.line.at[idx, 'name'] == line_name:
                    net.line.at[idx, 'in_service'] = False
        elif action.action_type == "CLOSE_SWITCH":
            for idx in net.switch.index:
                if net.switch.at[idx, 'name'] == action.component_id:
                    net.switch.at[idx, 'closed'] = True
        elif action.action_type == "OPEN_SWITCH":
            for idx in net.switch.index:
                if net.switch.at[idx, 'name'] == action.component_id:
                    net.switch.at[idx, 'closed'] = False
        elif action.action_type == "SHED_LOAD":
            for idx in net.load.index:
                if net.load.at[idx, 'name'] == action.component_id:
                    net.load.at[idx, 'in_service'] = False
        elif action.action_type == "RESTORE_LOAD":
            for idx in net.load.index:
                if net.load.at[idx, 'name'] == action.component_id:
                    net.load.at[idx, 'in_service'] = True

    def execute_plan(self, plan: RecoveryCandidate) -> Dict:
        """
        Execute a recovery plan on the actual grid simulation.
        Returns result with post-recovery state.
        """
        if not plan.feasible:
            return {
                "success": False,
                "message": "Cannot execute infeasible plan",
                "violations": plan.constraint_violations
            }

        logger.info(f"Executing recovery plan {plan.plan_id}")

        # Apply each action to the actual grid
        for action in plan.actions:
            logger.info(f"  Action: {action.action_type} on {action.component_id}")
            if action.action_type == "CLOSE_LINE":
                line_name = action.component_id.replace("LINE_", "")
                self.grid.close_line(line_name)
            elif action.action_type == "CLOSE_SWITCH":
                self.grid.close_switch(action.component_id)
            elif action.action_type == "SHED_LOAD":
                self.grid.shed_load(action.component_id)
            elif action.action_type == "RESTORE_LOAD":
                self.grid.restore_load(action.component_id)

        # Verify by running power flow
        pf_success = self.grid.run_power_flow()

        if pf_success:
            # Recheck constraints on actual grid
            feasible, violations, metrics = self.constraint_checker.check(self.grid.net)

            result = {
                "success": feasible,
                "plan_id": plan.plan_id,
                "pf_converged": True,
                "violations": violations,
                "metrics": metrics,
                "restored_load_pct": round(
                    metrics["total_load_mw"] / plan.total_demand_mw * 100
                    if plan.total_demand_mw > 0 else 0, 1
                ),
                "message": "Recovery successful" if feasible else
                          f"Recovery applied but {len(violations)} violations remain"
            }
        else:
            result = {
                "success": False,
                "plan_id": plan.plan_id,
                "pf_converged": False,
                "message": "Power flow did not converge after recovery"
            }

        self.recovery_history.append(plan)
        return result

    def select_best_plan(self, candidates: List[RecoveryCandidate]) -> Optional[RecoveryCandidate]:
        """Select the best feasible recovery plan."""
        feasible = [c for c in candidates if c.feasible]
        if not feasible:
            logger.warning("No feasible recovery plan found")
            return None

        best = max(feasible, key=lambda c: c.objective_score)
        best.status = "SELECTED"
        logger.info(f"Selected plan {best.plan_id} with score {best.objective_score:.3f}, "
                   f"restored load: {best.restored_load_pct:.1f}%")
        return best
