from __future__ import annotations


def inject_global_styles() -> None:
    import streamlit as st

    st.markdown(
        """
        <style>
        .game-card {
            display: grid;
            grid-template-columns: 120px minmax(0, 1fr);
            gap: 1rem;
            padding: 0.85rem;
            margin-bottom: 0.75rem;
            border: 1px solid rgba(148, 163, 184, 0.25);
            border-radius: 14px;
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.20);
        }
        .game-card:hover {
            border-color: rgba(124, 58, 237, 0.85);
            transform: translateY(-1px);
            transition: all 120ms ease-in-out;
        }
        .game-cover {
            width: 110px;
            min-height: 145px;
            object-fit: cover;
            border-radius: 10px;
            background: rgba(15, 23, 42, 0.95);
        }
        .game-cover-placeholder {
            width: 110px;
            height: 145px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(51, 65, 85, 0.8);
            color: #94A3B8;
            font-size: 0.8rem;
            text-align: center;
        }
        .game-title {
            font-size: 1.08rem;
            font-weight: 700;
            color: #F8FAFC;
            margin-bottom: 0.15rem;
        }
        .game-subtitle {
            color: #CBD5E1;
            font-size: 0.82rem;
            margin-bottom: 0.45rem;
        }
        .game-summary {
            color: #CBD5E1;
            font-size: 0.9rem;
            line-height: 1.35;
            margin-top: 0.4rem;
            margin-bottom: 0.55rem;
        }
        .badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
            margin-top: 0.25rem;
        }
        .platform-badge,
        .tag-badge,
        .metric-badge,
        .hidden-badge {
            border-radius: 999px;
            padding: 0.16rem 0.48rem;
            font-size: 0.74rem;
            font-weight: 600;
            white-space: nowrap;
        }
        .platform-badge {
            background: rgba(14, 165, 233, 0.18);
            color: #7DD3FC;
            border: 1px solid rgba(125, 211, 252, 0.22);
        }
        .tag-badge {
            background: rgba(148, 163, 184, 0.14);
            color: #E2E8F0;
            border: 1px solid rgba(148, 163, 184, 0.18);
        }
        .metric-badge {
            background: rgba(124, 58, 237, 0.18);
            color: #DDD6FE;
            border: 1px solid rgba(196, 181, 253, 0.18);
        }
        .hidden-badge {
            background: rgba(245, 158, 11, 0.18);
            color: #FCD34D;
            border: 1px solid rgba(252, 211, 77, 0.25);
        }
        .menu-card {
            min-height: 150px;
            padding: 1.1rem;
            border-radius: 16px;
            border: 1px solid rgba(148, 163, 184, 0.23);
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.96), rgba(15, 23, 42, 0.96));
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.22);
            margin-bottom: 0.8rem;
        }
        .menu-card-title {
            font-size: 1.05rem;
            font-weight: 750;
            color: #F8FAFC;
            margin-bottom: 0.35rem;
        }
        .menu-card-copy {
            color: #CBD5E1;
            font-size: 0.9rem;
            min-height: 3.4rem;
        }
        .small-caveat {
            margin-top: 1rem;
            padding: 0.55rem 0.75rem;
            border-left: 3px solid rgba(148, 163, 184, 0.8);
            color: #CBD5E1;
            background: rgba(15, 23, 42, 0.55);
            border-radius: 8px;
            font-size: 0.84rem;
        }
        .section-kicker {
            color: #A78BFA;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            font-size: 0.78rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

