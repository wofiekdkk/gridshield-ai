"""
GridShield AI - Power Grid Simulation Engine
WHY: Creates a realistic virtual electrical grid using pandapower.
WHAT: Defines buses, generators, lines, transformers, loads, switches.
HOW: Uses pandapower for actual power-flow calculations.
INPUT: Grid topology parameters.
OUTPUT: pandapower network with power-flow results.
TESTED: Via pytest in tests/test_grid.py.
"""

import pandapower as pp
import pandapower.networks as pn
import numpy as np
import networkx as nx
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from loguru import logger
import json
import copy


@dataclass
class GridComponentInfo:
    component_id: str
    component_type: str
    name: str
    substation: str = ""
    bus_id: Optional[int] = None
    from_bus: Optional[int] = None
    to_bus: Optional[int] = None
    rated_capacity: float = 0.0
    voltage_level: float = 0.0
    load_priority: str = "NORMAL"
    pp_index: Optional[int] = None
    pp_table: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class PowerGridSimulator:
    """
    Core power grid simulator using pandapower.

    Creates a medium-sized grid with:
    - 1 power plant (external grid + generator)
    - 4 substations
    - 12 buses
    - 15 transmission/distribution lines
    - 3 transformers
    - 10 loads (including 2 critical)
    - 4 switches/breakers
    - Alternate paths for self-healing
    """

    def __init__(self):
        self.net = None
        self.components: Dict[str, GridComponentInfo] = {}
        self.topology_graph: Optional[nx.Graph] = None
        self.base_net = None  # Store clean copy for reset
        self._fault_states: Dict[str, dict] = {}
        self._original_values: Dict[str, dict] = {}
        logger.info("PowerGridSimulator initialized")

    def create_grid(self) -> pp.pandapowerNet:
        """
        Build the complete virtual power grid.

        Topology:
                        POWER_PLANT (Bus 0, 110kV)
                              |
                         Trafo T1 (110/20kV)
                              |
                         Bus 1 (20kV) - MAIN_BUS
                        /            \
                   Line L1           Line L2
                      /                \
              Bus 2 (SUB_A)       Bus 3 (SUB_B)
              /    |    \          /   |    \
           L3   L4   L5        L6   L7    L8
            /    |     \        /    |      \
         Bus4  Bus5  Bus6   Bus7  Bus8   Bus9
          |     |     |      |     |      |
        Load1 Load2 Load3  Load4 Load5  Load6
                                   |
                               Trafo T2 (20/0.4kV)
                                   |
                                Bus 10 (0.4kV)
                                /        \
                             L9          L10
                              /            \
                          Bus 11         Bus 12
                            |              |
                         Load7(CRIT)    Load8(CRIT)

        Alternate paths:
        - L11: Bus4 <-> Bus7 (cross-substation)
        - L12: Bus5 <-> Bus8 (cross-substation)
        - L13: Bus6 <-> Bus9 (cross-substation)
        - L14: Bus2 <-> Bus3 (substation tie)

        All alternate paths start as open switches.
        """
        self.net = pp.create_empty_network(name="GridShield_AI_Network")
        net = self.net

        logger.info("Creating virtual power grid topology...")

        # ---- BUSES ----
        # Bus 0: Power Plant HV (110 kV)
        pp.create_bus(net, vn_kv=110, name="POWER_PLANT_HV", index=0)
        self._add_component("BUS_0", "BUS", "Power Plant HV Bus",
                          "POWER_PLANT", bus_id=0, voltage_level=110.0)

        # Bus 1: Main Bus MV (20 kV)
        pp.create_bus(net, vn_kv=20, name="MAIN_BUS_MV", index=1)
        self._add_component("BUS_1", "BUS", "Main Distribution Bus",
                          "MAIN", bus_id=1, voltage_level=20.0)

        # Bus 2: Substation A (20 kV)
        pp.create_bus(net, vn_kv=20, name="SUB_A_BUS", index=2)
        self._add_component("BUS_2", "BUS", "Substation A Bus",
                          "SUB_A", bus_id=2, voltage_level=20.0)

        # Bus 3: Substation B (20 kV)
        pp.create_bus(net, vn_kv=20, name="SUB_B_BUS", index=3)
        self._add_component("BUS_3", "BUS", "Substation B Bus",
                          "SUB_B", bus_id=3, voltage_level=20.0)

        # Buses 4-6: Substation A feeders
        for i, name in enumerate(["SUB_A_FEEDER_1", "SUB_A_FEEDER_2", "SUB_A_FEEDER_3"], start=4):
            pp.create_bus(net, vn_kv=20, name=name, index=i)
            self._add_component(f"BUS_{i}", "BUS", name, "SUB_A",
                              bus_id=i, voltage_level=20.0)

        # Buses 7-9: Substation B feeders
        for i, name in enumerate(["SUB_B_FEEDER_1", "SUB_B_FEEDER_2", "SUB_B_FEEDER_3"], start=7):
            pp.create_bus(net, vn_kv=20, name=name, index=i)
            self._add_component(f"BUS_{i}", "BUS", name, "SUB_B",
                              bus_id=i, voltage_level=20.0)

        # Bus 10: Substation C MV/LV (0.4 kV)
        pp.create_bus(net, vn_kv=0.4, name="SUB_C_LV", index=10)
        self._add_component("BUS_10", "BUS", "Substation C LV Bus",
                          "SUB_C", bus_id=10, voltage_level=0.4)

        # Bus 11-12: Critical load buses
        pp.create_bus(net, vn_kv=0.4, name="CRITICAL_BUS_1", index=11)
        self._add_component("BUS_11", "BUS", "Critical Load Bus 1 (Hospital)",
                          "SUB_C", bus_id=11, voltage_level=0.4)

        pp.create_bus(net, vn_kv=0.4, name="CRITICAL_BUS_2", index=12)
        self._add_component("BUS_12", "BUS", "Critical Load Bus 2 (Emergency)",
                          "SUB_C", bus_id=12, voltage_level=0.4)

        # ---- EXTERNAL GRID (Slack) ----
        pp.create_ext_grid(net, bus=0, vm_pu=1.02, name="UTILITY_GRID", index=0)
        self._add_component("EXT_GRID_0", "EXTERNAL_GRID", "Utility Grid Connection",
                          "POWER_PLANT", bus_id=0, rated_capacity=200.0)

        # ---- GENERATOR ----
        pp.create_gen(net, bus=0, p_mw=80, vm_pu=1.02, name="GEN_1",
                     min_p_mw=10, max_p_mw=100, index=0)
        self._add_component("GEN_1", "GENERATOR", "Main Power Plant Generator",
                          "POWER_PLANT", bus_id=0, rated_capacity=100.0)

        # ---- TRANSFORMERS ----
        # T1: 110/20 kV (Power Plant to Distribution)
        pp.create_transformer(net, hv_bus=0, lv_bus=1,
                            std_type="25 MVA 110/20 kV", name="TRAFO_T1", index=0)
        self._add_component("TRAFO_T1", "TRANSFORMER",
                          "Main Power Transformer 110/20kV", "MAIN",
                          from_bus=0, to_bus=1, rated_capacity=25.0)

        # T2: 20/0.4 kV (Distribution to Critical Loads)
        pp.create_transformer(net, hv_bus=8, lv_bus=10,
                            std_type="0.4 MVA 20/0.4 kV", name="TRAFO_T2", index=1)
        self._add_component("TRAFO_T2", "TRANSFORMER",
                          "Critical Load Transformer 20/0.4kV", "SUB_C",
                          from_bus=8, to_bus=10, rated_capacity=0.4)

        # T3: Additional transformer for redundancy
        pp.create_transformer(net, hv_bus=9, lv_bus=10,
                            std_type="0.4 MVA 20/0.4 kV", name="TRAFO_T3", index=2)
        self._add_component("TRAFO_T3", "TRANSFORMER",
                          "Backup Critical Load Transformer", "SUB_C",
                          from_bus=9, to_bus=10, rated_capacity=0.4)

        # ---- TRANSMISSION LINES ----
        line_configs = [
            # Main distribution lines
            ("L1", 1, 2, 5.0, "SUB_A", "Main to Sub A"),
            ("L2", 1, 3, 6.0, "SUB_B", "Main to Sub B"),
            # Substation A feeders
            ("L3", 2, 4, 3.0, "SUB_A", "Sub A to Feeder 1"),
            ("L4", 2, 5, 3.5, "SUB_A", "Sub A to Feeder 2"),
            ("L5", 2, 6, 4.0, "SUB_A", "Sub A to Feeder 3"),
            # Substation B feeders
            ("L6", 3, 7, 3.0, "SUB_B", "Sub B to Feeder 1"),
            ("L7", 3, 8, 4.0, "SUB_B", "Sub B to Feeder 2"),
            ("L8", 3, 9, 3.5, "SUB_B", "Sub B to Feeder 3"),
            # Critical load distribution
            ("L9", 10, 11, 0.5, "SUB_C", "To Hospital"),
            ("L10", 10, 12, 0.5, "SUB_C", "To Emergency Services"),
        ]

        for idx, (name, fb, tb, length, sub, desc) in enumerate(line_configs):
            std_type = "NAYY 4x50 SE" if length < 1 else "149-AL1/24-ST1A 20.0"
            pp.create_line(net, from_bus=fb, to_bus=tb,
                         length_km=length, std_type=std_type,
                         name=name, index=idx)
            self._add_component(f"LINE_{name}", "LINE", desc, sub,
                              from_bus=fb, to_bus=tb,
                              rated_capacity=self._get_line_capacity(std_type))

        # ---- ALTERNATE PATH LINES (normally open) ----
        alt_lines = [
            ("L11", 4, 7, 6.0, "ALT", "Alt Path: A-F1 to B-F1"),
            ("L12", 5, 8, 5.5, "ALT", "Alt Path: A-F2 to B-F2"),
            ("L13", 6, 9, 5.0, "ALT", "Alt Path: A-F3 to B-F3"),
            ("L14", 2, 3, 4.0, "ALT", "Substation Tie: A to B"),
        ]

        for idx_offset, (name, fb, tb, length, sub, desc) in enumerate(alt_lines):
            idx = len(line_configs) + idx_offset
            pp.create_line(net, from_bus=fb, to_bus=tb,
                         length_km=length, std_type="149-AL1/24-ST1A 20.0",
                         name=name, index=idx, in_service=False)
            self._add_component(f"LINE_{name}", "LINE", desc, sub,
                              from_bus=fb, to_bus=tb,
                              metadata={"alternate_path": True, "normally_open": True})

        # ---- SWITCHES/BREAKERS ----
        pp.create_switch(net, bus=1, element=0, et="l", closed=True,
                        type="CB", name="CB_L1", index=0)
        self._add_component("CB_L1", "BREAKER", "Circuit Breaker L1",
                          "MAIN", bus_id=1)

        pp.create_switch(net, bus=1, element=1, et="l", closed=True,
                        type="CB", name="CB_L2", index=1)
        self._add_component("CB_L2", "BREAKER", "Circuit Breaker L2",
                          "MAIN", bus_id=1)

        pp.create_switch(net, bus=3, element=6, et="l", closed=True,
                        type="CB", name="CB_L7", index=2)
        self._add_component("CB_L7", "BREAKER", "Circuit Breaker L7",
                          "SUB_B", bus_id=3)

        pp.create_switch(net, bus=2, element=13, et="l", closed=False,
                        type="CB", name="CB_L14_TIE", index=3)
        self._add_component("CB_L14_TIE", "BREAKER", "Tie Breaker A-B",
                          "ALT", bus_id=2, metadata={"tie_breaker": True})

        # ---- LOADS ----
        load_configs = [
            ("LOAD_1", 4, 3.0, 0.9, "NORMAL", "SUB_A", "Residential Area 1"),
            ("LOAD_2", 5, 4.0, 1.2, "NORMAL", "SUB_A", "Commercial District"),
            ("LOAD_3", 6, 2.5, 0.7, "NON_CRITICAL", "SUB_A", "Industrial Park"),
            ("LOAD_4", 7, 3.5, 1.0, "NORMAL", "SUB_B", "Residential Area 2"),
            ("LOAD_5", 8, 2.0, 0.6, "NORMAL", "SUB_B", "Office Complex"),
            ("LOAD_6", 9, 3.0, 0.8, "NON_CRITICAL", "SUB_B", "Shopping Center"),
            ("LOAD_7", 11, 0.08, 0.03, "CRITICAL", "SUB_C", "Hospital"),
            ("LOAD_8", 12, 0.06, 0.02, "CRITICAL", "SUB_C", "Emergency Services"),
            ("LOAD_9", 4, 1.5, 0.4, "NORMAL", "SUB_A", "School District"),
            ("LOAD_10", 7, 2.0, 0.5, "NORMAL", "SUB_B", "Water Treatment"),
        ]

        for idx, (name, bus, p_mw, q_mvar, priority, sub, desc) in enumerate(load_configs):
            pp.create_load(net, bus=bus, p_mw=p_mw, q_mvar=q_mvar,
                         name=name, index=idx)
            self._add_component(name, "LOAD", desc, sub, bus_id=bus,
                              rated_capacity=p_mw,
                              metadata={"load_priority": priority})

        # Save base state
        self.base_net = copy.deepcopy(net)

        logger.info(f"Grid created: {len(net.bus)} buses, {len(net.line)} lines, "
                   f"{len(net.trafo)} trafos, {len(net.load)} loads, "
                   f"{len(net.gen)} generators")

        return net

    def _add_component(self, comp_id: str, comp_type: str, name: str,
                      substation: str, bus_id: int = None,
                      from_bus: int = None, to_bus: int = None,
                      rated_capacity: float = 0.0, voltage_level: float = 0.0,
                      metadata: Dict = None):
        self.components[comp_id] = GridComponentInfo(
            component_id=comp_id,
            component_type=comp_type,
            name=name,
            substation=substation,
            bus_id=bus_id,
            from_bus=from_bus,
            to_bus=to_bus,
            rated_capacity=rated_capacity,
            voltage_level=voltage_level,
            metadata=metadata or {}
        )

    def _get_line_capacity(self, std_type: str) -> float:
        if "NAYY" in std_type:
            return 0.15  # MVA
        return 10.0  # MVA approx

    def run_power_flow(self) -> bool:
        """Run AC power flow calculation."""
        try:
            pp.runpp(self.net, algorithm='nr', calculate_voltage_angles=True,
                    init='auto', max_iteration=50, tolerance_mva=1e-8)
            logger.debug("Power flow converged successfully")
            return True
        except pp.LoadflowNotConverged:
            logger.warning("Power flow did not converge")
            return False
        except Exception as e:
            logger.error(f"Power flow error: {e}")
            return False

    def get_grid_state(self) -> Dict:
        """Get complete grid state after power flow."""
        if not self.run_power_flow():
            return {"status": "DIVERGED", "error": "Power flow did not converge"}

        net = self.net
        state = {
            "status": "NORMAL",
            "buses": {},
            "lines": {},
            "transformers": {},
            "loads": {},
            "generators": {},
            "switches": {},
            "total_generation": 0.0,
            "total_load": 0.0,
            "total_loss": 0.0,
            "frequency": 50.0 + np.random.normal(0, 0.02),
            "warnings": [],
            "faults": []
        }

        # Bus results
        for idx in net.bus.index:
            if idx in net.res_bus.index:
                vm_pu = net.res_bus.at[idx, 'vm_pu']
                va_deg = net.res_bus.at[idx, 'va_degree']
                p_mw = net.res_bus.at[idx, 'p_mw'] if 'p_mw' in net.res_bus.columns else 0
                q_mvar = net.res_bus.at[idx, 'q_mvar'] if 'q_mvar' in net.res_bus.columns else 0

                bus_status = "NORMAL"
                if vm_pu < 0.95:
                    bus_status = "WARNING"
                if vm_pu < 0.90 or vm_pu > 1.10:
                    bus_status = "FAULT"
                    state["faults"].append(f"BUS_{idx}: voltage {vm_pu:.3f} pu out of range")

                state["buses"][f"BUS_{idx}"] = {
                    "vm_pu": round(float(vm_pu), 4),
                    "va_degree": round(float(va_deg), 2),
                    "p_mw": round(float(p_mw), 3),
                    "q_mvar": round(float(q_mvar), 3),
                    "vn_kv": float(net.bus.at[idx, 'vn_kv']),
                    "voltage_kv": round(float(vm_pu * net.bus.at[idx, 'vn_kv']), 2),
                    "status": bus_status,
                    "in_service": bool(net.bus.at[idx, 'in_service'])
                }

        # Line results
        for idx in net.line.index:
            if idx in net.res_line.index and net.line.at[idx, 'in_service']:
                loading = net.res_line.at[idx, 'loading_percent']
                i_ka = net.res_line.at[idx, 'i_ka']
                p_from = net.res_line.at[idx, 'p_from_mw']
                p_to = net.res_line.at[idx, 'p_to_mw']
                pl_mw = net.res_line.at[idx, 'pl_mw']

                line_status = "NORMAL"
                if loading > 80:
                    line_status = "WARNING"
                    state["warnings"].append(
                        f"LINE {net.line.at[idx, 'name']}: loading {loading:.1f}%")
                if loading > 95:
                    line_status = "OVERLOADED"
                if loading > 100:
                    line_status = "FAULT"
                    state["faults"].append(
                        f"LINE {net.line.at[idx, 'name']}: overloaded {loading:.1f}%")

                state["lines"][net.line.at[idx, 'name']] = {
                    "loading_percent": round(float(loading), 2),
                    "i_ka": round(float(i_ka), 4),
                    "p_from_mw": round(float(p_from), 3),
                    "p_to_mw": round(float(p_to), 3),
                    "pl_mw": round(float(pl_mw), 4),
                    "from_bus": int(net.line.at[idx, 'from_bus']),
                    "to_bus": int(net.line.at[idx, 'to_bus']),
                    "length_km": float(net.line.at[idx, 'length_km']),
                    "status": line_status,
                    "in_service": bool(net.line.at[idx, 'in_service'])
                }
            elif idx in net.line.index:
                state["lines"][net.line.at[idx, 'name']] = {
                    "loading_percent": 0.0,
                    "status": "DISCONNECTED",
                    "in_service": bool(net.line.at[idx, 'in_service']),
                    "from_bus": int(net.line.at[idx, 'from_bus']),
                    "to_bus": int(net.line.at[idx, 'to_bus']),
                }

        # Transformer results
        for idx in net.trafo.index:
            if idx in net.res_trafo.index and net.trafo.at[idx, 'in_service']:
                loading = net.res_trafo.at[idx, 'loading_percent']
                trafo_status = "NORMAL"
                if loading > 80:
                    trafo_status = "WARNING"
                if loading > 95:
                    trafo_status = "OVERLOADED"
                if loading > 100:
                    trafo_status = "FAULT"

                state["transformers"][net.trafo.at[idx, 'name']] = {
                    "loading_percent": round(float(loading), 2),
                    "hv_bus": int(net.trafo.at[idx, 'hv_bus']),
                    "lv_bus": int(net.trafo.at[idx, 'lv_bus']),
                    "status": trafo_status,
                    "in_service": bool(net.trafo.at[idx, 'in_service'])
                }

        # Load results
        total_load = 0
        for idx in net.load.index:
            if idx in net.res_load.index:
                p_mw = net.res_load.at[idx, 'p_mw']
                q_mvar = net.res_load.at[idx, 'q_mvar']
                total_load += p_mw
                comp = self.components.get(net.load.at[idx, 'name'], None)
                priority = comp.metadata.get('load_priority', 'NORMAL') if comp else 'NORMAL'

                state["loads"][net.load.at[idx, 'name']] = {
                    "p_mw": round(float(p_mw), 3),
                    "q_mvar": round(float(q_mvar), 3),
                    "bus": int(net.load.at[idx, 'bus']),
                    "priority": priority,
                    "in_service": bool(net.load.at[idx, 'in_service'])
                }

        # Generator results
        total_gen = 0
        for idx in net.gen.index:
            if idx in net.res_gen.index:
                p_mw = net.res_gen.at[idx, 'p_mw']
                q_mvar = net.res_gen.at[idx, 'q_mvar']
                total_gen += p_mw
                state["generators"][net.gen.at[idx, 'name']] = {
                    "p_mw": round(float(p_mw), 3),
                    "q_mvar": round(float(q_mvar), 3),
                    "vm_pu": float(net.gen.at[idx, 'vm_pu']),
                    "in_service": bool(net.gen.at[idx, 'in_service'])
                }

        # External grid
        for idx in net.ext_grid.index:
            if idx in net.res_ext_grid.index:
                p_mw = net.res_ext_grid.at[idx, 'p_mw']
                total_gen += p_mw

        state["total_generation"] = round(total_gen, 3)
        state["total_load"] = round(total_load, 3)
        state["total_loss"] = round(total_gen - total_load, 3)

        # Determine overall status
        if state["faults"]:
            state["status"] = "FAULT"
        elif state["warnings"]:
            state["status"] = "WARNING"

        return state

    def get_topology_graph(self) -> nx.Graph:
        """Build NetworkX graph from grid topology."""
        G = nx.Graph()

        for idx in self.net.bus.index:
            G.add_node(f"BUS_{idx}", type="bus",
                      vn_kv=float(self.net.bus.at[idx, 'vn_kv']),
                      name=self.net.bus.at[idx, 'name'])

        for idx in self.net.line.index:
            fb = int(self.net.line.at[idx, 'from_bus'])
            tb = int(self.net.line.at[idx, 'to_bus'])
            in_service = bool(self.net.line.at[idx, 'in_service'])
            G.add_edge(f"BUS_{fb}", f"BUS_{tb}",
                      line_name=self.net.line.at[idx, 'name'],
                      line_idx=idx,
                      in_service=in_service,
                      length_km=float(self.net.line.at[idx, 'length_km']))

        for idx in self.net.trafo.index:
            hv = int(self.net.trafo.at[idx, 'hv_bus'])
            lv = int(self.net.trafo.at[idx, 'lv_bus'])
            G.add_edge(f"BUS_{hv}", f"BUS_{lv}",
                      trafo_name=self.net.trafo.at[idx, 'name'],
                      trafo_idx=idx,
                      type="transformer")

        self.topology_graph = G
        return G

    def inject_line_fault(self, line_name: str) -> bool:
        """Take a line out of service to simulate failure."""
        for idx in self.net.line.index:
            if self.net.line.at[idx, 'name'] == line_name:
                self._original_values[f"line_{line_name}"] = {
                    "in_service": bool(self.net.line.at[idx, 'in_service'])
                }
                self.net.line.at[idx, 'in_service'] = False
                logger.warning(f"FAULT INJECTED: Line {line_name} taken out of service")
                return True
        logger.error(f"Line {line_name} not found")
        return False

    def inject_load_increase(self, load_name: str, factor: float) -> bool:
        """Increase load by a factor."""
        for idx in self.net.load.index:
            if self.net.load.at[idx, 'name'] == load_name:
                orig_p = float(self.net.load.at[idx, 'p_mw'])
                orig_q = float(self.net.load.at[idx, 'q_mvar'])
                self._original_values[f"load_{load_name}"] = {
                    "p_mw": orig_p, "q_mvar": orig_q
                }
                self.net.load.at[idx, 'p_mw'] = orig_p * factor
                self.net.load.at[idx, 'q_mvar'] = orig_q * factor
                logger.warning(f"FAULT INJECTED: Load {load_name} increased by {factor}x")
                return True
        return False

    def inject_trafo_fault(self, trafo_name: str) -> bool:
        """Take transformer out of service."""
        for idx in self.net.trafo.index:
            if self.net.trafo.at[idx, 'name'] == trafo_name:
                self._original_values[f"trafo_{trafo_name}"] = {
                    "in_service": bool(self.net.trafo.at[idx, 'in_service'])
                }
                self.net.trafo.at[idx, 'in_service'] = False
                logger.warning(f"FAULT INJECTED: Transformer {trafo_name} failed")
                return True
        return False

    def inject_generator_fault(self, gen_name: str) -> bool:
        """Take generator out of service."""
        for idx in self.net.gen.index:
            if self.net.gen.at[idx, 'name'] == gen_name:
                self._original_values[f"gen_{gen_name}"] = {
                    "in_service": bool(self.net.gen.at[idx, 'in_service'])
                }
                self.net.gen.at[idx, 'in_service'] = False
                logger.warning(f"FAULT INJECTED: Generator {gen_name} failed")
                return True
        return False

    def close_line(self, line_name: str) -> bool:
        """Bring a line into service (for recovery)."""
        for idx in self.net.line.index:
            if self.net.line.at[idx, 'name'] == line_name:
                self.net.line.at[idx, 'in_service'] = True
                logger.info(f"RECOVERY: Line {line_name} brought into service")
                return True
        return False

    def open_line(self, line_name: str) -> bool:
        """Take a line out of service."""
        for idx in self.net.line.index:
            if self.net.line.at[idx, 'name'] == line_name:
                self.net.line.at[idx, 'in_service'] = False
                return True
        return False

    def close_switch(self, switch_name: str) -> bool:
        """Close a switch/breaker."""
        for idx in self.net.switch.index:
            if self.net.switch.at[idx, 'name'] == switch_name:
                self.net.switch.at[idx, 'closed'] = True
                logger.info(f"RECOVERY: Switch {switch_name} closed")
                return True
        return False

    def open_switch(self, switch_name: str) -> bool:
        """Open a switch/breaker."""
        for idx in self.net.switch.index:
            if self.net.switch.at[idx, 'name'] == switch_name:
                self.net.switch.at[idx, 'closed'] = False
                return True
        return False

    def shed_load(self, load_name: str) -> bool:
        """Disconnect a load."""
        for idx in self.net.load.index:
            if self.net.load.at[idx, 'name'] == load_name:
                self._original_values[f"shed_{load_name}"] = {
                    "in_service": bool(self.net.load.at[idx, 'in_service'])
                }
                self.net.load.at[idx, 'in_service'] = False
                logger.info(f"Load shed: {load_name}")
                return True
        return False

    def restore_load(self, load_name: str) -> bool:
        """Reconnect a load."""
        for idx in self.net.load.index:
            if self.net.load.at[idx, 'name'] == load_name:
                self.net.load.at[idx, 'in_service'] = True
                return True
        return False

    def reset_grid(self):
        """Reset grid to original state."""
        if self.base_net is not None:
            self.net = copy.deepcopy(self.base_net)
            self._fault_states.clear()
            self._original_values.clear()
            logger.info("Grid reset to original state")

    def get_all_line_names(self) -> List[str]:
        return [self.net.line.at[idx, 'name'] for idx in self.net.line.index]

    def get_all_load_names(self) -> List[str]:
        return [self.net.load.at[idx, 'name'] for idx in self.net.load.index]

    def get_all_trafo_names(self) -> List[str]:
        return [self.net.trafo.at[idx, 'name'] for idx in self.net.trafo.index]

    def get_alternate_paths(self) -> List[str]:
        """Get names of alternate (normally open) lines."""
        alts = []
        for idx in self.net.line.index:
            comp_id = f"LINE_{self.net.line.at[idx, 'name']}"
            comp = self.components.get(comp_id)
            if comp and comp.metadata.get('alternate_path', False):
                alts.append(self.net.line.at[idx, 'name'])
        return alts

    def get_loads_by_priority(self) -> Dict[str, List[str]]:
        result = {"CRITICAL": [], "NORMAL": [], "NON_CRITICAL": []}
        for idx in self.net.load.index:
            name = self.net.load.at[idx, 'name']
            comp = self.components.get(name)
            if comp:
                priority = comp.metadata.get('load_priority', 'NORMAL')
                result[priority].append(name)
        return result
