from rag_engine import RAGAgent


def main():
    agent = RAGAgent()
    results = agent.search('It Takes Two', top_n=5, debug_scores=True)
    print(f"Results count: {len(results)}")
    for idx, item in enumerate(results[:5], start=1):
        print(f"{idx}. {item.get('name', 'Unknown')} | score={item.get('primary_rank_score', 0.0):.4f}")


if __name__ == '__main__':
    main()
