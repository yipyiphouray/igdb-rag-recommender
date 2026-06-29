from __future__ import annotations


def inject_global_styles() -> None:
    import streamlit as st

    st.markdown(
        """
        <style>
        :root {
            --cyber-bg: #070014;
            --cyber-panel: rgba(15, 0, 35, 0.92);
            --cyber-panel-2: rgba(25, 0, 55, 0.92);
            --cyber-cyan: #00E5FF;
            --cyber-pink: #FF2BD6;
            --cyber-purple: #8B5CF6;
            --cyber-yellow: #F9F871;
            --cyber-text: #F8FAFC;
            --cyber-muted: #B9A8D8;
            --cyber-border: rgba(0, 229, 255, 0.35);
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 12%, rgba(255, 43, 214, 0.18), transparent 28%),
                radial-gradient(circle at 85% 8%, rgba(0, 229, 255, 0.18), transparent 30%),
                linear-gradient(135deg, #070014 0%, #12002A 48%, #020617 100%);
            color: var(--cyber-text);
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3 {
            letter-spacing: 0.01em;
        }

        div[data-testid="stSidebarContent"] {
            background:
                linear-gradient(180deg, rgba(10, 0, 25, 0.98), rgba(26, 0, 51, 0.98));
            border-right: 1px solid rgba(0, 229, 255, 0.25);
        }

        div[data-testid="stMetric"] {
            border: 1px solid rgba(0, 229, 255, 0.22);
            border-radius: 14px;
            padding: 0.7rem 0.85rem;
            background: rgba(12, 0, 32, 0.75);
            box-shadow: 0 0 20px rgba(0, 229, 255, 0.08);
        }

        .section-kicker {
            color: var(--cyber-cyan);
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            font-size: 0.78rem;
            text-shadow: 0 0 12px rgba(0, 229, 255, 0.65);
        }

        .cyber-hero {
            padding: 1.2rem 1.35rem;
            border: 1px solid rgba(255, 43, 214, 0.32);
            border-radius: 18px;
            background:
                linear-gradient(135deg, rgba(255, 43, 214, 0.12), rgba(0, 229, 255, 0.08)),
                rgba(8, 0, 28, 0.88);
            box-shadow:
                0 0 28px rgba(255, 43, 214, 0.12),
                inset 0 0 30px rgba(0, 229, 255, 0.06);
            margin-bottom: 1.3rem;
        }

        .cyber-title {
            font-size: clamp(2.2rem, 6vw, 4.4rem);
            line-height: 0.95;
            font-weight: 900;
            color: var(--cyber-text);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            text-shadow:
                0 0 10px rgba(0, 229, 255, 0.80),
                0 0 24px rgba(255, 43, 214, 0.40);
            margin: 0.25rem 0 0.3rem 0;
        }

        .cyber-subtitle {
            color: var(--cyber-muted);
            font-size: 0.95rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        .menu-card-link {
            display: block;
            min-height: 136px;
            padding: 1.15rem;
            margin-bottom: 0.9rem;
            border-radius: 0;
            border: 1px solid rgba(0, 229, 255, 0.42);
            background:
                linear-gradient(135deg, rgba(0, 229, 255, 0.10), rgba(255, 43, 214, 0.08)),
                rgba(12, 0, 32, 0.92);
            box-shadow:
                0 0 20px rgba(0, 229, 255, 0.11),
                inset 0 0 18px rgba(255, 43, 214, 0.05);
            color: var(--cyber-text) !important;
            text-decoration: none !important;
            position: relative;
            overflow: hidden;
            transition: transform 140ms ease, border-color 140ms ease, box-shadow 140ms ease;
        }

        .menu-card-link:before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                repeating-linear-gradient(
                    0deg,
                    rgba(255, 255, 255, 0.04),
                    rgba(255, 255, 255, 0.04) 1px,
                    transparent 1px,
                    transparent 5px
                );
            opacity: 0.28;
            pointer-events: none;
        }

        .menu-card-link:hover {
            transform: translateY(-3px);
            border-color: rgba(255, 43, 214, 0.95);
            box-shadow:
                0 0 26px rgba(255, 43, 214, 0.28),
                0 0 36px rgba(0, 229, 255, 0.16);
        }

        .menu-card-title {
            position: relative;
            font-size: clamp(1.2rem, 2.6vw, 1.75rem);
            font-weight: 900;
            color: var(--cyber-cyan);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            text-shadow: 0 0 12px rgba(0, 229, 255, 0.70);
        }

        .menu-card-copy {
            position: relative;
            margin-top: 0.75rem;
            color: var(--cyber-text);
            font-size: 0.88rem;
            line-height: 1.35;
            opacity: 0;
            max-height: 0;
            transform: translateY(6px);
            transition: opacity 140ms ease, max-height 140ms ease, transform 140ms ease;
        }

        .menu-card-link:hover .menu-card-copy {
            opacity: 1;
            max-height: 120px;
            transform: translateY(0);
        }

        .menu-card-cta {
            position: absolute;
            right: 1rem;
            bottom: 0.85rem;
            color: var(--cyber-yellow);
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.10em;
            text-transform: uppercase;
        }

        .game-card {
            display: grid;
            grid-template-columns: 118px minmax(0, 1fr);
            gap: 1rem;
            padding: 0.9rem;
            margin-bottom: 0.85rem;
            border: 1px solid rgba(0, 229, 255, 0.28);
            background:
                linear-gradient(135deg, rgba(0, 229, 255, 0.07), rgba(255, 43, 214, 0.06)),
                rgba(10, 0, 30, 0.93);
            box-shadow: 0 0 22px rgba(0, 229, 255, 0.08);
        }

        .game-card:hover {
            border-color: rgba(255, 43, 214, 0.72);
            transform: translateY(-1px);
            transition: all 120ms ease-in-out;
        }

        .game-card.detailed {
            grid-template-columns: 150px minmax(0, 1fr);
        }

        .game-grid-card {
            min-height: 315px;
            padding: 0.75rem;
            margin-bottom: 0.85rem;
            border: 1px solid rgba(0, 229, 255, 0.28);
            background:
                linear-gradient(180deg, rgba(0, 229, 255, 0.08), rgba(255, 43, 214, 0.06)),
                rgba(10, 0, 30, 0.92);
            box-shadow: 0 0 18px rgba(0, 229, 255, 0.08);
        }

        .game-grid-card:hover {
            border-color: rgba(255, 43, 214, 0.75);
        }

        .game-cover {
            width: 110px;
            min-height: 145px;
            object-fit: cover;
            border: 1px solid rgba(0, 229, 255, 0.25);
            background: rgba(15, 23, 42, 0.95);
            box-shadow: 0 0 14px rgba(0, 229, 255, 0.12);
        }

        .game-card.detailed .game-cover {
            width: 140px;
            min-height: 185px;
        }

        .game-grid-card .game-cover {
            width: 100%;
            min-height: 215px;
            max-height: 245px;
        }

        .game-cover-placeholder {
            width: 110px;
            height: 145px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid rgba(0, 229, 255, 0.25);
            background: rgba(35, 0, 65, 0.75);
            color: var(--cyber-muted);
            font-size: 0.78rem;
            text-align: center;
        }

        .game-grid-card .game-cover-placeholder {
            width: 100%;
            height: 225px;
        }

        .game-title {
            font-size: 1.08rem;
            font-weight: 850;
            color: var(--cyber-text);
            margin-bottom: 0.15rem;
        }

        .game-grid-title {
            font-size: 0.95rem;
            font-weight: 850;
            color: var(--cyber-text);
            line-height: 1.2;
            margin-top: 0.55rem;
        }

        .game-subtitle {
            color: var(--cyber-muted);
            font-size: 0.82rem;
        }

        .game-summary {
            color: #D8D0EA;
            font-size: 0.9rem;
            line-height: 1.35;
            margin-top: 0.45rem;
            margin-bottom: 0.55rem;
        }

        .badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
            margin-top: 0.28rem;
        }

        .platform-badge,
        .tag-badge,
        .metric-badge,
        .hidden-badge {
            border-radius: 0;
            padding: 0.16rem 0.48rem;
            font-size: 0.72rem;
            font-weight: 750;
            white-space: nowrap;
            letter-spacing: 0.02em;
        }

        .platform-badge {
            background: rgba(0, 229, 255, 0.12);
            color: #9AF5FF;
            border: 1px solid rgba(0, 229, 255, 0.28);
        }

        .tag-badge {
            background: rgba(139, 92, 246, 0.16);
            color: #E9D5FF;
            border: 1px solid rgba(139, 92, 246, 0.25);
        }

        .metric-badge {
            background: rgba(255, 43, 214, 0.12);
            color: #FFD4F7;
            border: 1px solid rgba(255, 43, 214, 0.24);
        }

        .hidden-badge {
            background: rgba(249, 248, 113, 0.12);
            color: var(--cyber-yellow);
            border: 1px solid rgba(249, 248, 113, 0.32);
        }

        .detail-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 0.45rem;
            margin-top: 0.65rem;
        }

        .detail-item {
            border-left: 2px solid rgba(0, 229, 255, 0.45);
            background: rgba(255, 255, 255, 0.035);
            padding: 0.4rem 0.5rem;
        }

        .detail-item span {
            display: block;
            color: var(--cyber-muted);
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        .detail-item strong {
            color: var(--cyber-text);
            font-size: 0.82rem;
            font-weight: 700;
        }

        .card-explanation {
            margin-top: 0.65rem;
            padding: 0.55rem 0.65rem;
            border: 1px solid rgba(249, 248, 113, 0.28);
            color: #FFF9C4;
            background: rgba(249, 248, 113, 0.08);
            font-size: 0.84rem;
            line-height: 1.35;
        }

        .rule-box,
        .method-section,
        .wizard-panel,
        .insight-panel,
        .small-caveat {
            border: 1px solid rgba(0, 229, 255, 0.25);
            background:
                linear-gradient(135deg, rgba(0, 229, 255, 0.07), rgba(255, 43, 214, 0.05)),
                rgba(10, 0, 30, 0.86);
            box-shadow: 0 0 20px rgba(0, 229, 255, 0.06);
        }

        .rule-box {
            padding: 0.8rem 0.95rem;
            margin: 0.8rem 0 1rem 0;
        }

        .rule-box-title,
        .method-section-title,
        .wizard-step-label {
            color: var(--cyber-cyan);
            font-weight: 850;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.78rem;
            margin-bottom: 0.35rem;
        }

        .rule-box-body {
            color: var(--cyber-text);
            font-size: 0.92rem;
        }

        .method-section,
        .wizard-panel,
        .insight-panel {
            padding: 1rem 1.1rem;
            margin: 0.85rem 0;
        }

        .method-section-title {
            font-size: 0.92rem;
        }

        .method-section-body {
            color: #D8D0EA;
            font-size: 0.94rem;
            line-height: 1.5;
        }

        .small-caveat {
            margin-top: 1rem;
            padding: 0.55rem 0.75rem;
            color: #D8D0EA;
            border-left: 3px solid rgba(249, 248, 113, 0.75);
            font-size: 0.84rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
