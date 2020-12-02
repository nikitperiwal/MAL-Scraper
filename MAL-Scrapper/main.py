from top_anime_list import getTopAnimeData
from anime_reviews import getAllAnimeReviews
from top_anime_details import getAllAnimeData
from anime_recommendations import getAllAnimeRecommendations


def main():
    anime_df = getTopAnimeData(num=10)
    getAllAnimeData(anime_df)
    getAllAnimeReviews(anime_df)
    getAllAnimeRecommendations(anime_df)


if __name__ == "__main__":
    main()
