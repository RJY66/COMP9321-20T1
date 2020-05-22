# python version 3.7.2
# pandas version 1.0.1
# matplotlib version 3.2.0
import ast
import json
import matplotlib.pyplot as plt
import pandas as pd
import sys
import os

studentid = os.path.basename(sys.modules[__name__].__file__)


#################################################
def my_percent_show(percent):
    if percent < 0.5:
        ""
    else:
        return '%.1f%%' % percent
#################################################


def log(question, output_df, other):
    print("--------------- {}----------------".format(question))
    if other is not None:
        print(question, other)
    if output_df is not None:
        print(output_df.head(5).to_string())


def question_1(movies, credits):
    """
    :param movies: the path for the movie.csv file
    :param credits: the path for the credits.csv file
    :return: df1
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    df_movies = pd.read_csv(movies)
    df_credits = pd.read_csv(credits)
    df1 = pd.merge(left=df_movies, right=df_credits, on="id")
    #################################################

    log("QUESTION 1", output_df=df1, other=df1.shape)
    return df1


def question_2(df1):
    """
    :param df1: the dataframe created in question 1
    :return: df2
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    df2 = df1[["id", "title", 'popularity', 'cast', 'crew', 'budget', 'genres', 'original_language', 'production_companies', 'production_countries', 'release_date', 'revenue', 'runtime', 'spoken_languages', 'vote_average', 'vote_count']]
    #################################################

    log("QUESTION 2", output_df=df2, other=(len(df2.columns), sorted(df2.columns)))
    return df2


def question_3(df2):
    """
    :param df2: the dataframe created in question 2
    :return: df3
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    df3 = df2.set_index(["id"])
    #################################################

    log("QUESTION 3", output_df=df3, other=df3.index.name)
    return df3


def question_4(df3):
    """
    :param df3: the dataframe created in question 3
    :return: df4
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    df4 = df3[df3['budget'] != 0]
    #################################################

    log("QUESTION 4", output_df=df4, other=(df4['budget'].min(), df4['budget'].max(), df4['budget'].mean()))
    return df4


def question_5(df4):
    """
    :param df4: the dataframe created in question 4
    :return: df5
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    df5 = df4.copy(deep=True)
    df5['success_impact'] = ((df5['revenue'] - df5['budget']) / df5['budget'])
    #################################################

    log("QUESTION 5", output_df=df5,
        other=(df5['success_impact'].min(), df5['success_impact'].max(), df5['success_impact'].mean()))
    return df5


def question_6(df5):
    """
    :param df5: the dataframe created in question 5
    :return: df6
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    df6 = df5.copy(deep=True)
    max_popularity = df6['popularity'].max()
    min_popularity = df6['popularity'].min()
    df6['popularity'] = ((df6['popularity'] - min_popularity) / (max_popularity - min_popularity)) * 100
    #################################################

    log("QUESTION 6", output_df=df6, other=(df6['popularity'].min(), df6['popularity'].max(), df6['popularity'].mean()))
    return df6


def question_7(df6):
    """
    :param df6: the dataframe created in question 6
    :return: df7
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    df7 = df6.copy(deep=True)
    df7['popularity'] = df7['popularity'].astype('int16')
    #################################################

    log("QUESTION 7", output_df=df7, other=df7['popularity'].dtype)
    return df7


def question_8(df7):
    """
    :param df7: the dataframe created in question 7
    :return: df8
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    df8 = df7.copy(deep=True)
    oj = json.loads(df8.cast.to_json())
    character_list = []
    character_collection = []
    idx = []
    for i in df8.index:
        idx.append(i)
    for v in oj.values():
        t = ast.literal_eval(v)
        for m in range(len(t)):
            character_list.append(t[m]['character'])
        character_per_movie = ",".join(sorted(character_list))
        character_collection.append(character_per_movie)
        character_list = []
    df8.cast = pd.DataFrame(character_collection, index=idx)
    #################################################

    log("QUESTION 8", output_df=df8, other=df8["cast"].head(10).values)
    return df8


def question_9(df8):
    """
    :param df9: the dataframe created in question 8
    :return: movies
            Data Type: List of strings (movie titles)
            Please read the assignment specs to know how to create the output
    """

    #################################################
    df9 = df8.copy(deep=True)
    cast_count = []
    l = df9.cast.str.split(", ")
    oj_t = json.loads(l.to_json())
    for v in oj_t.values():
        cast_names = v[0].split(",")
        t = len(cast_names)
        cast_count.append(t)
    df9['cast_count'] = cast_count
    df9.sort_values(by=['cast_count'], inplace=True, ascending=False)
    movies = df9.title.head(10).values
    #################################################

    log("QUESTION 9", output_df=None, other=movies)
    return movies


def question_10(df8):
    """
    :param df8: the dataframe created in question 8
    :return: df10
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    df10 = df8.copy(deep=True)
    df10['release_date_parsed'] = pd.to_datetime(df10['release_date'], format="%y/%m/%d", infer_datetime_format=True)
    df10 = df10.sort_values(by=['release_date_parsed'], ascending=False)
    #################################################

    log("QUESTION 10", output_df=df10, other=df10["release_date"].head(5).to_string().replace("\n", " "))
    return df10


def question_11(df10):
    """
    :param df10: the dataframe created in question 10
    :return: nothing, but saves the figure on the disk
    """

    #################################################
    df11 = df10.copy(deep=True)
    genres = df11['genres'].to_dict()
    ratio = {}
    for v in genres.values():
        t = ast.literal_eval(v)
        for i in range(len(t)):
            if t[i]['name'] not in ratio:
                ratio[t[i]['name']] = 1
            else:
                ratio[t[i]['name']] = 1 + ratio[t[i]['name']]
    plt.pie(ratio.values(), rotatelabels=False, autopct=my_percent_show, pctdistance=1.22)
    plt.legend(ratio.keys(), bbox_to_anchor=(0.02, 1), borderaxespad=0.3)
    plt.title('Genres')
    #################################################

    plt.savefig("{}-Q11.png".format(studentid))


def question_12(df10):
    """
    :param df10: the dataframe created in question 10
    :return: nothing, but saves the figure on the disk
    """

    #################################################
    plt.clf()
    df12 = df10.copy(deep=True)
    country = df12['production_countries'].to_dict()
    ratio2 = {}
    ratio_t = {}
    for v in country.values():
        t = ast.literal_eval(v)
        for i in range(len(t)):
            if t[i]['name'] in ratio2:
                ratio2[t[i]['name']] = 1 + ratio2[t[i]['name']]
            else:
                ratio2[t[i]['name']] = 1
    for j in sorted(ratio2):
        ratio_t[j] = ratio2[j]
    plt.bar(x=ratio_t.keys(), height=ratio_t.values(), color='darkturquoise')
    plt.xticks(rotation=90, fontsize=4.5)
    plt.title('Production Country', loc='center')
    #################################################

    plt.savefig("{}-Q12.png".format(studentid))


def question_13(df10):
    """
    :param df10: the dataframe created in question 10
    :return: nothing, but saves the figure on the disk
    """

    #################################################
    plt.clf()
    df13 = df10.copy(deep=True)
    vote_avg = df13['vote_average'].values
    success_impact = df13['success_impact'].values
    language = df13['original_language'].values
    color_list = ['green', 'red', 'yellow', 'blue', 'black',
                  'orange', 'steelblue', 'salmon', 'lime', 'pink',
                  'purple', 'skyblue', 'violet', 'wheat', 'gray']
    idx = 0
    language_color_map = {}
    language_set = set()
    for m in language:
        language_set.add(m)
    language_list = sorted(language_set)
    for t in language_list:
        language_color_map[t] = color_list[idx]
        idx += 1
    for k in language_list:
        x_pos = []
        y_pos = []
        for p in range(len(vote_avg)):
            if k == language[p]:
                x_pos.append(vote_avg[p])
        for p in range(len(success_impact)):
            if k == language[p]:
                y_pos.append(success_impact[p])
        plt.scatter(x=x_pos, y=y_pos, label=k, s=10, c=language_color_map[k])
    plt.legend(language_color_map.keys(), loc='upper right')
    plt.title('vote_average vs. success_impact')
    plt.xlabel('vote_average')
    plt.ylabel('success_impact')
    plt.grid()
    ##################################
    plt.savefig("{}-Q13.png".format(studentid))


if __name__ == "__main__":
    df1 = question_1("movies.csv", "credits.csv")
    df2 = question_2(df1)
    df3 = question_3(df2)
    df4 = question_4(df3)
    df5 = question_5(df4)
    df6 = question_6(df5)
    df7 = question_7(df6)
    df8 = question_8(df7)
    movies = question_9(df8)
    df10 = question_10(df8)
    question_11(df10)
    question_12(df10)
    question_13(df10)
