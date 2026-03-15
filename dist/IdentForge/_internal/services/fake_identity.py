from faker import Faker

class FakeIdentity:
    @staticmethod
    def generate():
        faker = Faker()
        return {
            'name': faker.name(),
            'username': faker.user_name(),
            'gender': faker.random_element(['Male', 'Female']),
            'address': faker.address(),
            'city': faker.city(),
            'country': faker.country(),
            'zip_code': faker.zipcode(),
            'phone': faker.phone_number(),
            'birthdate': faker.date_of_birth().isoformat(),
            'job_title': faker.job()
        }