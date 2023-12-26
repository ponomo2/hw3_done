from django.core.management.base import BaseCommand
from askme.models import *
from faker import Faker
import random
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'filling db'
    fake = Faker()

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Number of records to add to the database')

    def handle(self, **options):

        ratio = options['ratio']
        # self.create_users(ratio)
        # print('Users')
        self.create_questions(ratio)
        print('Questions')
        self.create_answers(ratio)
        print('Answers')
        # self.create_tags(ratio)
        # print('Tags')
        self.create_likes(ratio)
        print('Likes')
        self.create_questions_tags(ratio)
        print('End')

    def create_users(self, ratio):
        usernames = []
        while len(usernames) <= ratio:
            new_usernames = [self.fake.user_name() for _ in range(ratio)]
            usernames += new_usernames
            usernames = list(set(usernames))

        users = [User(password=self.fake.password(), username=usernames[i], email=self.fake.email()) for i in
                 range(ratio)]
        for user in users:
            user.save()
        profile = [Profile(user=users[i], nickname=usernames[i]) for i in range(len(users))]
        for prof in profile:
            prof.save()
        # User.objects.bulk_create(users)
        # Profile.objects.bulk_create(profile)

    def create_questions(self, ratio):
        user_num = ratio - 1
        ratio = ratio * 10
        authors = User.objects.all()
        print('num authors:')
        print(len(authors))
        question = [Question(author=authors[self.fake.random_int(min=1, max=user_num)], title=self.fake.sentence(nb_words=3),
                             text=self.fake.text()) for _ in range(ratio)]
        Question.new.bulk_create(question)

    def create_answers(self, ratio):
        questions_ = Question.new.all()
        authors_ = User.objects.all()
        print('num questions:')
        print(len(questions_))
        question_with_id = {}
        for question in questions_:
            question_with_id[question.id] = question

        questions_ratio = len(questions_) - 1
        authors_ratio = len(authors_) - 1
        ratio = ratio * 100
        answer = [Answer(text=self.fake.text(), question=questions_[self.fake.random_int(min=1, max=questions_ratio)],
                         author=authors_[self.fake.random_int(min=1, max=authors_ratio)], correct=self.fake.pybool())
                  for _ in range(ratio)]
        print('answers generated')
        Answer.objects.bulk_create(answer)
        print('answers inserted')
        answer = Answer.objects.all()
        for answ in answer:
            question_with_id[answ.question.id].answers_number += 1
            question_with_id[answ.question.id].save()

    def create_tags(self, ratio):
        ratio *= 2
        words = []
        while len(words) < ratio:
            new_words = [self.fake.word() for _ in range(ratio)]
            words += new_words
            new_words = [self.fake.first_name() for _ in range(ratio)]
            words += new_words
            new_words = [self.fake.last_name() for _ in range(ratio)]
            words += new_words
            words = list(set(words))
            print(len(words))

        tag = [Tag(text=words[i]) for i in range(ratio)]
        Tag.objects.bulk_create(tag)

    def create_likes(self, ratio):
        authors_ = Profile.objects.all()
        questions_ = Question.new.all()
        answers_ = Answer.objects.all()
        question_ratio = len(questions_) - 1
        like_ratio = ratio * 200
        answer_ratio = len(answers_) - 1
        question_dict = {}
        for question in questions_:
            question_dict[question.id] = question

        print('question and it id hash')
        answer_dict = {}
        for answer in answers_:
            answer_dict[answer.id] = answer

        print('answer dict')
        for i in range(len(questions_)):
            questions_[i].likes_ratio = 0
        print('question likes zero')

        for i in range(len(answers_)):
            answers_[i].likes_ratio = 0
        print('answer likes zero')

        for i in range(1000):
            if i % 2 == 0:
                like = [
                    Likes(like_or_dislike=random.randint(-1, 1), question=questions_[random.randint(1, question_ratio)],
                          author=authors_[random.randint(1, ratio - 1)]) for _ in range(like_ratio // 1002)]
            else:
                like = [Likes(like_or_dislike=random.randint(-1, 1), author=authors_[random.randint(1, ratio - 1)],
                              answer=answers_[random.randint(1, answer_ratio)]) for _ in range(like_ratio // 1002)]

            Likes.objects.bulk_create(like)
            print(f'done {i} likes')

            for likee in like:
                if likee.question:
                    question = question_dict[likee.question.id]
                    question.likes += likee.like_or_dislike
                    question.save()
                else:
                    answer = answer_dict[likee.answer.id]
                    answer.likes += likee.like_or_dislike
                    answer.save()

    def create_questions_tags(self, ratio):
        questions_ = Question.new.all()
        tags_ = Tag.objects.all()
        for question in questions_:
            for i in range(random.randint(0, 3)):
                question.tags.add(tags_[random.randint(1, 2 * ratio - 1)])
            question.save()