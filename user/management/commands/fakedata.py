from django.core.management.base import BaseCommand
from faker import Faker
import random

from user.models import CustomUser, City


class Command(BaseCommand):
    help = 'Generate fake user'
    fake = Faker()

    def handle(self, *args, **kwargs):
        cities_pool = list()
        for i in range(10):
            new_fake_city, _ = City.objects.get_or_create(
                name=self.fake.unique.city(),
            )
            cities_pool.append(new_fake_city)

        self.stdout.write(self.style.SUCCESS(f'Created {len(cities_pool)} cities pool'))


        for i in range(50):
            new_fake_user = CustomUser.objects.create_user(
                email=self.fake.unique.email(),
                password='12345',
                mailing_interval=24
            )

            num_of_cities = random.randint(1, 5)
            random_cities = random.sample(cities_pool, k=num_of_cities)


            new_fake_user.cities.add(*random_cities)
            self.stdout.write(
                self.style.SUCCESS(f'{i} user created')
            )
        
        self.stdout.write()
        self.stdout.write(
            self.style.SUCCESS('DB is filled with users')
        )