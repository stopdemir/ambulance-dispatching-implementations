# Inbound (RHS) vs Outbound (LHS) flow visuals for the toy MDP
# - Three inline plots (no files saved)
# - Shapes: circle = target node (s,e); triangle = predecessors (s',e',a'); diamond = actions a; square = next pre-state
# - Colors: blue = inbound (RHS), orange = outbound (LHS)

import matplotlib.pyplot as plt
import networkx as nx

# ----------------------------
# Model parameters (toy MDP)
# ----------------------------
lam = 1.2
P_loc = {1: 0.6, 2: 0.4}
P_pri = {"H": 0.5, "L": 0.5}
mu = {(1,"A"): 0.8, (2,"A"): 1.0, (1,"B"): 1.1, (2,"B"): 0.9}  # mean service time (hours)

rate = {(i,j): 1.0/mu[(i,j)] for i in [1,2] for j in ["A","B"]}
betaA = max(rate[(1,"A")], rate[(2,"A")])
betaB = max(rate[(1,"B")], rate[(2,"B")])
gamma = lam + betaA + betaB

EVENTS = [("H",1), ("L",1), ("H",2), ("L",2), "null"]

def P_event(e):
    """Uniformized per-stage probability of event e."""
    if e == "null":
        return 1.0 - lam/gamma
    pri, i = e
    return (lam/gamma) * P_loc[i] * P_pri[pri]

def avail_actions(s, e):
    """Feasible actions at node (s,e). If arrival: dispatch any free server; if none free use ∅; if null: ∅."""
    free = []
    if s[0] == 0: free.append("A")
    if s[1] == 0: free.append("B")
    if e == "null":
        return ["∅"]
    return free if free else ["∅"]

def next_state_after_dispatch(s, i, a):
    """Next pre-decision state after taking action a on an arrival from location i."""
    if a == "A":  return (i, s[1])
    if a == "B":  return (s[0], i)
    return s  # ∅ (no-dispatch)

def completion_from_null(s):
    """From (s,null) with null action: possible completions/silent with probabilities."""
    edges = []
    if s[0] in (1,2):  # A busy
        i = s[0]; p = rate[(i,"A")]/gamma
        edges.append(((0, s[1]), p, "A completes"))
    if s[1] in (1,2):  # B busy
        i = s[1]; p = rate[(i,"B")]/gamma
        edges.append(((s[0], 0), p, "B completes"))
    p_silent = 1.0 - lam/gamma - sum(p for _,p,_ in edges)
    p_silent = max(0.0, p_silent)
    edges.append((s, p_silent, "silent"))
    return edges  # list of (s_next, prob, label)

def predecessors_of_node(s_star, e_star):
    """All (s,e,a) that can land in node (s_star,e_star) in one stage, with probability weights."""
    preds = []
    for sA in [0,1,2]:
        for sB in [0,1,2]:
            s = (sA, sB)
            for e in EVENTS:
                for a in avail_actions(s, e):
                    if e == "null":
                        s_posts = completion_from_null(s)
                    else:
                        pri, i = e
                        s_next = next_state_after_dispatch(s, i, a)
                        s_posts = [(s_next, 1.0, "dispatch" if a != "∅" else "no-dispatch")]
                    for s_next, p_snext, _ in s_posts:
                        if s_next == s_star and p_snext > 0:
                            p_estar = P_event(e_star)
                            if p_estar > 0:
                                preds.append({
                                    "s": s, "e": e, "a": a,
                                    "p_to_node": p_snext * p_estar
                                })
    preds.sort(key=lambda d: -d["p_to_node"])
    return preds

def outbound_of_node(s_star, e_star):
    """Outbound from node (s*,e*): action splits to next pre-states (probabilities shown)."""
    out = []
    for a in avail_actions(s_star, e_star):
        if e_star == "null":
            for s_next, p, tag in completion_from_null(s_star):
                out.append({"a": a, "s_next": s_next, "p": p, "tag": tag})
        else:
            pri, i = e_star
            s_next = next_state_after_dispatch(s_star, i, a)
            out.append({"a": a, "s_next": s_next, "p": 1.0, "tag": "dispatch" if a!="∅" else "no-dispatch"})
    return out

def draw_inbound_outbound(
    s_star, e_star,
    node_size_center=2600, node_size_pred=2400, node_size_act=2400, node_size_post=2000,
    font_size_nodes=14, font_size_edges=12, arrow_width=2.8,
    fig_w=18, fig_h=9, title=None
):
    """Draw one inline figure for the flow equality at node (s*,e*)."""
    G = nx.DiGraph()
    center = f"{s_star} | {('null' if e_star=='null' else e_star[0]+str(e_star[1]))}"
    G.add_node(center, kind="center")

    preds = predecessors_of_node(s_star, e_star)
    outs  = outbound_of_node(s_star, e_star)

    # Inbound: predecessors (triangles) -> center (circle)
    for d in preds:
        s, e, a, p = d["s"], d["e"], d["a"], d["p_to_node"]
        name = f"{s} | {('null' if e=='null' else e[0]+str(e[1]))} — a={a}"
        G.add_node(name, kind="pred")
        G.add_edge(name, center, kind="in", label=f"p={p:.3f}")

    # Outbound: center -> action diamonds -> next pre-states (squares)
    for d in outs:
        a = d["a"]; s_next = d["s_next"]; p = d["p"]
        act_node = f"{center} → a={a}"
        G.add_node(act_node, kind="act")
        G.add_edge(center, act_node, kind="out", label="")
        G.add_node(str(s_next), kind="post")
        G.add_edge(act_node, str(s_next), kind="out", label=f"P={p:.3f}")

    # Layout
    pos = {center:(0.0,0.0)}
    # Left stack for predecessors
    pred_nodes = [n for n,d in G.nodes(data=True) if d.get("kind")=="pred"]
    for i,n in enumerate(pred_nodes):
        pos[n] = (-7.5, (len(pred_nodes)-1)/2.0 - i)
    # Right stack for actions
    act_nodes = [n for n,d in G.nodes(data=True) if d.get("kind")=="act"]
    for i,n in enumerate(act_nodes):
        pos[n] = (5.0, (len(act_nodes)-1)/2.0 - i)
    # Next pre-states grouped per action
    parent_map = {}
    for u,v in G.edges():
        if G.nodes[u].get("kind")=="act" and G.nodes[v].get("kind")=="post":
            parent_map.setdefault(u, []).append(v)
    for act_n, succs in parent_map.items():
        y0 = pos[act_n][1]
        for k,v in enumerate(succs):
            pos[v] = (10.0, y0 - k*1.2)

    # Figure
    plt.figure(figsize=(fig_w, fig_h))
    center_nodes = [n for n,d in G.nodes(data=True) if d.get("kind")=="center"]
    pred_nodes   = [n for n,d in G.nodes(data=True) if d.get("kind")=="pred"]
    act_nodes    = [n for n,d in G.nodes(data=True) if d.get("kind")=="act"]
    post_nodes   = [n for n,d in G.nodes(data=True) if d.get("kind")=="post"]

    nx.draw_networkx_nodes(G, pos, nodelist=center_nodes, node_shape='o', node_size=node_size_center)
    nx.draw_networkx_nodes(G, pos, nodelist=pred_nodes,   node_shape='^', node_size=node_size_pred)
    nx.draw_networkx_nodes(G, pos, nodelist=act_nodes,    node_shape='D', node_size=node_size_act)
    nx.draw_networkx_nodes(G, pos, nodelist=post_nodes,   node_shape='s', node_size=node_size_post)

    in_edges  = [(u,v) for u,v,d in G.edges(data=True) if d.get("kind")=="in"]
    out_edges = [(u,v) for u,v,d in G.edges(data=True) if d.get("kind")=="out"]
    nx.draw_networkx_edges(G, pos, edgelist=in_edges,  arrows=True, edge_color="tab:blue",   width=arrow_width)
    nx.draw_networkx_edges(G, pos, edgelist=out_edges, arrows=True, edge_color="tab:orange", width=arrow_width)

    nx.draw_networkx_labels(G, pos, font_size=font_size_nodes)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=font_size_edges)

    import matplotlib.lines as mlines
    inbound_line  = mlines.Line2D([], [], color="tab:blue",   label="Inbound (RHS)")
    outbound_line = mlines.Line2D([], [], color="tab:orange", label="Outbound (LHS)")
    plt.legend(handles=[inbound_line, outbound_line], loc="upper right", fontsize=12)

    if title:
        plt.title(title, fontsize=15)
    plt.axis('off')
    plt.tight_layout()
    plt.show()


