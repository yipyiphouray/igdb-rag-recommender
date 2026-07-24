from recommender_engine import ContentBasedRecommender


def questionnaire_recommendation(
    questionnaire,
    top_k=5,
    discovery="Balanced",
    quality_weight=0.5,
    playtime=None,
    playtime_weight=0.2,
    years_mode="boost",
    years_start=2010,
    years_end=2024,
    years_weight=0.15,
):
    merged_questionnaire = dict(questionnaire or {})
    merged_questionnaire.update(
        {
            "discovery": discovery,
            "quality_weight": quality_weight,
            "playtime": playtime,
            "playtime_weight": playtime_weight,
            "years_mode": years_mode,
            "years_start": years_start,
            "years_end": years_end,
            "years_weight": years_weight,
        }
    )
    recommender = ContentBasedRecommender()
    return recommender.recommend(questionnaire=merged_questionnaire, top_n=top_k)


if __name__ == "__main__":
    sample_questionnaire = {
        "platforms": ["Nintendo Switch"],
        "genres": ["Adventure", "Role-playing (RPG)"],
        "themes": ["Fantasy"],
        "rating": 80,
    }
    matches = questionnaire_recommendation(
        sample_questionnaire,
        top_k=5,
        discovery="Niche",
        quality_weight=0.6,
        playtime="Medium",
        playtime_weight=0.2,
        years_mode="boost",
        years_start=2010,
        years_end=2024,
        years_weight=0.15,
    )
    print("Top recommendations:")
    for i, match in enumerate(matches, start=1):
        print(
            f"{i}. {match['name']} "
            f"(final={match['final_score']:.4f}, cosine={match['cosine_similarity']:.4f})"
        )
