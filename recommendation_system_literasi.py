# -*- coding: utf-8 -*-
"""Recommendation_System_Literasi_(dengan_filter).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1yk7BxHWBbOcVSr7jLwN63hQcjTxJMLei
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

link_literasi = 'https://raw.githubusercontent.com/Capstone-Buddies/Machine-Learning/main/Dataset/SNBT%20Datasets%20-%20Literasi.csv'
link_answer_history_literasi = 'https://raw.githubusercontent.com/Capstone-Buddies/Machine-Learning/main/Dataset/SNBT%20Datasets%20-%20Answer_History_Literasi.csv'

user_history = pd.read_csv(link_answer_history_literasi)
literasi_question_data = pd.read_csv(link_literasi)

# Menghitung jumlah soal yang telah dijawab oleh user untuk setiap kategori
def get_total_questions_per_category(user_data):
    return user_data.groupby('Question_Category').size()

# Menghitung jumlah soal yang salah dijawab oleh user untuk setiap kategori
def get_mistakes_per_category(user_data):
    mistakes = user_data[user_data['USER_ANSWER'] != user_data['CORRECT_ANSWER']]
    return mistakes.groupby('Question_Category').size(), mistakes

# Menghitung similarity antara soal yang salah dijawab dengan soal lain dalam kategori yang sama
def calculate_similarity(mistakes, literasi_question_data_filtered):
    combined_descriptions = pd.concat([mistakes['Question_Description'], literasi_question_data_filtered['Questions_Descriptions']])

    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(combined_descriptions)

    # Pisahkan TF-IDF matrix untuk user_mistakes dan literasi_question_data
    tfidf_user_mistakes = tfidf_matrix[:len(mistakes)]
    tfidf_literasi_question_data = tfidf_matrix[len(mistakes):]

    # Hitung cosine similarity
    similarity_matrix = cosine_similarity(tfidf_user_mistakes, tfidf_literasi_question_data)

    # Menampilkan similarity matrix dalam bentuk DataFrame
    similarity_df = pd.DataFrame(similarity_matrix, columns=literasi_question_data_filtered.index)
    similarity_df.index = mistakes['ID_QUESTION'].values

    # Filter similarity berdasarkan kategori yang sama
    top_similar_questions = {}
    for idx, user_question in enumerate(similarity_df.index):
        category = mistakes.iloc[idx]['Question_Category']
        same_category_indices = literasi_question_data_filtered[literasi_question_data_filtered['Question_Category'] == category].index
        category_similarities = similarity_df.loc[user_question, same_category_indices]
        top_similar_questions[user_question] = category_similarities.nlargest(10) # mengambil top 10 yang paling mirip

    return top_similar_questions

# Menentukan proporsi soal berdasarkan kategori yang salah dijawab lebih banyak
def determine_proportion(mistakes_per_category, total_questions=10, min_questions_per_category=1):
   # Kategori yang ada
    all_categories = user_data['Question_Category'].unique()

    # Proporsi minimal untuk setiap kategori
    proportion = pd.Series(min_questions_per_category, index=all_categories)

    # Soal yang tersisa setelah distribusi minimal
    remaining_questions = total_questions - proportion.sum()

    # Proporsi berdasarkan kesalahan
    if remaining_questions > 0:
        mistakes_proportion = (mistakes_per_category / mistakes_per_category.sum() * remaining_questions).round().astype(int)
        for cat in mistakes_proportion.index:
            proportion[cat] += mistakes_proportion[cat]

    # Jika masih ada sisa soal yang belum terdistribusi, tambahkan ke kategori dengan kesalahan terbanyak
    remaining_questions = total_questions - proportion.sum()
    if remaining_questions > 0:
        most_mistakes_category = mistakes_per_category.idxmax()
        proportion[most_mistakes_category] += remaining_questions

    return proportion

# Menyusun kuis berdasarkan proporsi dan soal-soal dengan similarity tertinggi
def generate_quiz(proportion, top_similar_questions, mistakes, literasi_question_data_filtered, total_questions=10):
    quiz_questions = []

    # Soal yang salah dijawab berdasarkan similarity
    for category in proportion.index:
        questions_needed = proportion[category]
        if category in mistakes['Question_Category'].values:
            for user_question, similar_questions in top_similar_questions.items():
                if mistakes.loc[mistakes['ID_QUESTION'] == user_question]['Question_Category'].values[0] == category:
                    similar_question_ids = [literasi_question_data_filtered.loc[idx]['ID'] for idx in similar_questions.index]
                    selected_questions = literasi_question_data_filtered[literasi_question_data_filtered['ID'].isin(similar_question_ids) &
                                                                       (literasi_question_data_filtered['Question_Category'] == category)].head(questions_needed).to_dict('records')
                    quiz_questions.extend(selected_questions)
                    break

    # Soal yang dijawab benar secara acak
    for category in proportion.index:
        if category not in mistakes['Question_Category'].values:
            questions_needed = proportion[category]
            selected_questions = literasi_question_data_filtered[literasi_question_data_filtered['Question_Category'] == category].sample(questions_needed).to_dict('records')
            quiz_questions.extend(selected_questions)

    # Pastikan hanya ada 10 soal
    quiz_questions = quiz_questions[:total_questions]
    return quiz_questions

# Memeriksa apakah user baru
def is_new_user(user_id, user_history):
    return user_history[user_history['ID_USER'] == user_id].empty

# Menghasilkan soal untuk user baru secara merata per kategori
def generate_questions_for_new_user(literasi_question_data, total_questions=10):
    categories = literasi_question_data['Question_Category'].unique()
    questions_per_category = total_questions // len(categories)

    quiz_questions = []

    for category in categories:
        selected_questions = literasi_question_data[literasi_question_data['Question_Category'] == category].sample(questions_per_category).to_dict('records')
        quiz_questions.extend(selected_questions)

    # Jika ada sisa soal yang belum terdistribusi
    remaining_questions = total_questions - len(quiz_questions)
    if remaining_questions > 0:
        extra_questions = literasi_question_data[~literasi_question_data['ID'].isin([q['ID'] for q in quiz_questions])].sample(remaining_questions).to_dict('records')
        quiz_questions.extend(extra_questions)

    return quiz_questions

# Memfilter soal yang sudah dijawab oleh user sebelumnya
def filter_answered_questions(user_data, literasi_question_data):
    answered_question_ids = user_data['ID_QUESTION'].unique()
    return literasi_question_data[~literasi_question_data['ID'].isin(answered_question_ids)]

# Menyusun kuis sambil menghindari pengulangan soal berturut-turut
def generate_quiz_avoiding_repeats(proportion, top_similar_questions, mistakes, literasi_question_data_filtered, last_questions, total_questions=10):
    quiz_questions = []
    used_questions = set(last_questions)  # Set untuk menyimpan soal yang sudah digunakan dalam kuis sebelumnya

    # Soal yang salah dijawab berdasarkan similarity
    for category in mistakes_per_category.index:
        questions_needed = proportion[category]
        for user_question, similar_questions in top_similar_questions.items():
            if mistakes.loc[mistakes['ID_QUESTION'] == user_question]['Question_Category'].values[0] == category:
                 similar_question_ids = [literasi_question_data_filtered.loc[idx]['ID'] for idx in similar_questions.index]
                 selected_questions = literasi_question_data_filtered[literasi_question_data_filtered['ID'].isin(similar_question_ids) &
                                                                     (literasi_question_data_filtered['Question_Category'] == category) &
                                                                     (~literasi_question_data_filtered['ID'].isin(used_questions))].head(questions_needed).to_dict('records')
                 quiz_questions.extend(selected_questions)
                 used_questions.update([q['ID'] for q in selected_questions])
                 break

    # Soal yang dijawab benar secara acak
    for category in proportion.index:
        if category not in mistakes_per_category.index:
            questions_needed = proportion[category]
            selected_questions = literasi_question_data_filtered[literasi_question_data_filtered['Question_Category'] == category].sample(questions_needed).to_dict('records')
            quiz_questions.extend(selected_questions)

    # Pastikan hanya ada 10 soal
    quiz_questions = quiz_questions[:total_questions]
    return quiz_questions

# Merekomendasikan soal kepada user
def recommend_questions_for_user(user_id, user_history, literasi_question_data, last_questions, total_questions=10):
    if is_new_user(user_id, user_history):
        print("User baru, generate soal secara merata per kategori.")
        quiz_questions = generate_questions_for_new_user(literasi_question_data, total_questions)

    else:
        user_data = user_history[user_history['ID_USER'] == user_id]

        # Cek jika semua soal sudah pernah dijawab oleh user
        if len(user_data['ID_QUESTION'].unique()) == len(literasi_question_data):
            literasi_question_data_filtered = literasi_question_data.copy()
        else:
            literasi_question_data_filtered = filter_answered_questions(user_data, literasi_question_data)

        total_questions_per_category = get_total_questions_per_category(user_data)

        mistakes_per_category, mistakes = get_mistakes_per_category(user_data)

        top_similar_questions = calculate_similarity(mistakes, literasi_question_data_filtered)

        proportion = determine_proportion(mistakes_per_category, total_questions)
        print("\nProporsi soal yang akan ditampilkan untuk setiap kategori:")
        print(proportion)

        quiz_questions = generate_quiz_avoiding_repeats(proportion, top_similar_questions, mistakes, literasi_question_data_filtered, last_questions, total_questions)

    print("\nSoal yang akan ditampilkan dalam kuis:")
    for question in quiz_questions:
        print(question)

    return [q['ID'] for q in quiz_questions]  # Mengembalikan ID soal yang digunakan dalam kuis

# Menentukan ID user
user_id = 3
last_questions = []

# Menghitung jumlah soal untuk setiap kategori yang telah dijawab oleh user (untuk pengecekan)
user_data = user_history[user_history['ID_USER'] == user_id]
total_questions_per_category = user_data.groupby('Question_Category').size()
print("Jumlah soal untuk setiap kategori yang telah dijawab oleh user:")
print(total_questions_per_category)

# Menghitung jumlah soal yang salah dijawab oleh user untuk setiap kategori (untuk pengecekan)
mistakes = user_data[user_data['USER_ANSWER'] != user_data['CORRECT_ANSWER']]
mistakes_per_category = mistakes.groupby('Question_Category').size()
# print("\nJumlah soal yang salah dijawab oleh user untuk setiap kategori:")
# print(mistakes_per_category)

last_questions = recommend_questions_for_user(user_id, user_history, literasi_question_data, last_questions)
