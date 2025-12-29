import plotly.graph_objects as go
from typing import Dict, Any, List, Tuple
import networkx as nx

class RuleVisualizer:
    """Create interactive decision tree visualizations for rules"""

    # Color scheme: Red/Yellow/Green for risk levels
    COLORS = {
        'BLOCK': '#EF4444',      # Red
        'REVIEW': '#F59E0B',     # Yellow/Orange
        'ALLOW': '#10B981',      # Green
        'NODE': '#3B82F6',       # Blue (for decision nodes)
        'TEXT': '#1F2937',       # Dark gray
    }

    def __init__(self):
        pass

    def create_decision_tree(self, rules: List[Dict[str, Any]]) -> go.Figure:
        """Create interactive Plotly decision tree from rules"""

        # Create directed graph
        G = nx.DiGraph()

        # Add root node
        G.add_node("START", label="Transaction", node_type="root", level=0)

        # Build tree structure
        prev_node = "START"
        for idx, rule in enumerate(rules):
            rule_id = rule.get('id', f'RULE_{idx}')
            rule_name = rule.get('name', 'Unnamed Rule')
            decision = rule.get('outcome', {}).get('decision', 'UNKNOWN')
            risk_score = rule.get('outcome', {}).get('risk_score', 0)

            # Create condition node
            condition_node = f"cond_{rule_id}"
            conditions = rule.get('conditions', [])
            logic = rule.get('logic', 'AND')

            if logic == 'ALWAYS':
                condition_label = "DEFAULT\n(Always matches)"
            elif conditions:
                # Simplify condition display
                if len(conditions) == 1:
                    c = conditions[0]
                    condition_label = f"{c.get('field', '')}\n{c.get('operator', '')} {c.get('value', '')}"
                else:
                    condition_label = f"{rule_name}\n({len(conditions)} conditions, {logic})"
            else:
                condition_label = rule_name

            G.add_node(
                condition_node,
                label=condition_label,
                node_type="condition",
                level=idx + 1,
                rule_id=rule_id
            )

            # Create outcome node
            outcome_node = f"outcome_{rule_id}"
            outcome_label = f"{decision}\nRisk: {risk_score}"

            G.add_node(
                outcome_node,
                label=outcome_label,
                node_type="outcome",
                decision=decision,
                risk_score=risk_score,
                level=idx + 1,
                rule_id=rule_id
            )

            # Add edges
            G.add_edge(prev_node, condition_node, label="check")
            G.add_edge(condition_node, outcome_node, label="match")

            # Connect to next rule if not last
            if idx < len(rules) - 1:
                next_cond = f"cond_{rules[idx+1].get('id', f'RULE_{idx+1}')}"
                G.add_edge(condition_node, next_cond, label="no match")

        # Generate layout
        pos = self._generate_layout(G, rules)

        # Create plotly figure
        fig = self._create_plotly_figure(G, pos)

        return fig

    def _generate_layout(self, G: nx.DiGraph, rules: List[Dict[str, Any]]) -> Dict[str, Tuple[float, float]]:
        """Generate positions for nodes"""
        pos = {}

        # Start node at top
        pos["START"] = (0, len(rules) + 1)

        # Layout rules vertically with horizontal spacing for outcomes
        for idx, rule in enumerate(rules):
            rule_id = rule.get('id', f'RULE_{idx}')
            y_pos = len(rules) - idx

            # Condition node on left
            pos[f"cond_{rule_id}"] = (-1, y_pos)

            # Outcome node on right
            pos[f"outcome_{rule_id}"] = (1, y_pos)

        return pos

    def _create_plotly_figure(self, G: nx.DiGraph, pos: Dict[str, Tuple[float, float]]) -> go.Figure:
        """Create Plotly figure from graph and positions"""

        # Extract edge coordinates
        edge_x = []
        edge_y = []
        edge_text = []

        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        # Create edge trace
        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=2, color='#9CA3AF'),
            hoverinfo='none',
            mode='lines'
        )

        # Extract node coordinates and data
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_size = []

        for node in G.nodes(data=True):
            x, y = pos[node[0]]
            node_x.append(x)
            node_y.append(y)

            label = node[1].get('label', node[0])
            node_type = node[1].get('node_type', 'unknown')

            if node_type == 'root':
                node_text.append(label)
                node_color.append('#6B7280')
                node_size.append(30)
            elif node_type == 'condition':
                node_text.append(label)
                node_color.append(self.COLORS['NODE'])
                node_size.append(25)
            elif node_type == 'outcome':
                decision = node[1].get('decision', 'UNKNOWN')
                risk_score = node[1].get('risk_score', 0)
                node_text.append(f"{label}")
                node_color.append(self.COLORS.get(decision, '#6B7280'))
                node_size.append(30)

        # Create node trace
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="middle center",
            textfont=dict(size=10, color='white'),
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color='white')
            )
        )

        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace])

        fig.update_layout(
            title='Fraud Detection Decision Tree',
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white',
            height=600
        )

        return fig

    def create_simple_flowchart(self, rules: List[Dict[str, Any]]) -> str:
        """Create simple text-based flowchart for small displays"""
        lines = []
        lines.append("Transaction")
        lines.append("    ↓")

        for idx, rule in enumerate(rules):
            rule_name = rule.get('name', 'Unnamed')
            decision = rule.get('outcome', {}).get('decision', 'UNKNOWN')
            risk = rule.get('outcome', {}).get('risk_score', 0)

            lines.append(f"┌{'─' * 40}┐")
            lines.append(f"│ {rule_name:<38} │")
            lines.append(f"└{'─' * 40}┘")
            lines.append(f"    ↓ match")
            lines.append(f"  {decision} (Risk: {risk})")

            if idx < len(rules) - 1:
                lines.append("    ↓ no match")

        return "\n".join(lines)
